import bpy
import math
import os
import struct
import tempfile

# S3D/WLD

DDS_MAGIC = b'DDS '
BMP_MAGIC = b'BM'

DDSCAPS_COMPLEX = 0x00000008
DDSCAPS2_CUBEMAP = 0x00000200
DDSCAPS2_CUBEMAP_ALLFACES = 0x0000FC00

def detect_texture_type(path):
    with open(path, 'rb') as f:
        header = f.read(4)

    if header[:4] == DDS_MAGIC:
        return "DDS"
    elif header[:2] == BMP_MAGIC:
        return "BMP"
    else:
        return "OTHER"

def _dds_level_size(width, height, fourcc, rgb_bits, dxgi_format=None):
    block8 = {
        b'DXT1', b'ATI1', b'BC4U', b'BC4S',
    }
    block16 = {
        b'DXT2', b'DXT3', b'DXT4', b'DXT5',
        b'ATI2', b'BC5U', b'BC5S',
    }

    if fourcc == b'DX10':
        if dxgi_format in {71, 72, 80, 81}:
            block_size = 8
        elif dxgi_format in {
            74, 75, 77, 78, 83, 84, 95, 96, 98, 99,
        }:
            block_size = 16
        elif dxgi_format in {28, 29, 87, 88, 91, 93}:
            return width * height * 4
        else:
            raise ValueError(
                f"Unsupported DX10 cubemap format: DXGI {dxgi_format}"
            )
    elif fourcc in block8:
        block_size = 8
    elif fourcc in block16:
        block_size = 16
    elif fourcc == b'\0\0\0\0':
        if rgb_bits == 0 or rgb_bits % 8:
            raise ValueError(
                f"Unsupported uncompressed cubemap bit depth: {rgb_bits}"
            )
        return width * height * (rgb_bits // 8)
    else:
        raise ValueError(
            f"Unsupported DDS cubemap compression: {fourcc!r}"
        )

    blocks_wide = max(1, (width + 3) // 4)
    blocks_high = max(1, (height + 3) // 4)
    return blocks_wide * blocks_high * block_size


def _read_dds_cubemap_info(path):
    with open(path, 'rb') as f:
        header = f.read(148)

    if len(header) < 128 or header[:4] != DDS_MAGIC:
        return None

    caps2 = struct.unpack_from('<I', header, 112)[0]
    if not caps2 & DDSCAPS2_CUBEMAP:
        return None
    if caps2 & DDSCAPS2_CUBEMAP_ALLFACES != DDSCAPS2_CUBEMAP_ALLFACES:
        raise ValueError("DDS cubemap does not contain all six faces")

    width = struct.unpack_from('<I', header, 16)[0]
    height = struct.unpack_from('<I', header, 12)[0]
    mip_count = max(1, struct.unpack_from('<I', header, 28)[0])
    fourcc = header[84:88]
    rgb_bits = struct.unpack_from('<I', header, 88)[0]
    header_size = 148 if fourcc == b'DX10' else 128
    dxgi_format = None

    if fourcc == b'DX10':
        if len(header) < 148:
            raise ValueError("Truncated DX10 DDS header")
        dxgi_format = struct.unpack_from('<I', header, 128)[0]
        array_size = struct.unpack_from('<I', header, 140)[0]
        if array_size != 1:
            raise ValueError(
                f"DDS cubemap arrays are not supported: {array_size} cubes"
            )

    face_size = 0
    mip_width, mip_height = width, height
    for _ in range(mip_count):
        face_size += _dds_level_size(
            mip_width,
            mip_height,
            fourcc,
            rgb_bits,
            dxgi_format,
        )
        mip_width = max(1, mip_width // 2)
        mip_height = max(1, mip_height // 2)

    file_size = os.path.getsize(path)
    required_size = header_size + face_size * 6
    if file_size < required_size:
        raise ValueError(
            f"Truncated DDS cubemap: expected at least {required_size} bytes, "
            f"found {file_size}"
        )

    return {
        "width": width,
        "height": height,
        "mip_count": mip_count,
        "fourcc": fourcc,
        "header_size": header_size,
        "face_size": face_size,
    }


def is_dds_cubemap(path):
    return _read_dds_cubemap_info(path) is not None


def _rgba_pixels(image):
    pixels = list(image.pixels[:])
    channels = image.channels
    if channels == 4:
        return pixels

    result = [0.0] * (image.size[0] * image.size[1] * 4)
    for pixel_index in range(image.size[0] * image.size[1]):
        source = pixel_index * channels
        target = pixel_index * 4
        red = pixels[source]
        result[target] = red
        result[target + 1] = (
            pixels[source + 1] if channels > 1 else red
        )
        result[target + 2] = (
            pixels[source + 2] if channels > 2 else red
        )
        result[target + 3] = (
            pixels[source + 3] if channels > 3 else 1.0
        )
    return result


def _cubemap_face_and_uv(x, y, z):
    abs_x, abs_y, abs_z = abs(x), abs(y), abs(z)

    if abs_x >= abs_y and abs_x >= abs_z:
        if x >= 0.0:
            face, u_axis, v_axis = 0, -z, -y
        else:
            face, u_axis, v_axis = 1, z, -y
        major = abs_x
    elif abs_y >= abs_x and abs_y >= abs_z:
        if y >= 0.0:
            face, u_axis, v_axis = 2, x, z
        else:
            face, u_axis, v_axis = 3, x, -z
        major = abs_y
    else:
        if z >= 0.0:
            face, u_axis, v_axis = 4, x, -y
        else:
            face, u_axis, v_axis = 5, -x, -y
        major = abs_z

    return (
        face,
        (u_axis / major + 1.0) * 0.5,
        (v_axis / major + 1.0) * 0.5,
    )


def _cubemap_to_equirectangular(face_pixels, face_width, face_height):
    output_width = face_width * 4
    output_height = face_height * 2
    output = [0.0] * (output_width * output_height * 4)

    for output_y in range(output_height):
        latitude = (
            (output_y + 0.5) / output_height - 0.5
        ) * math.pi
        latitude_cosine = math.cos(latitude)
        direction_y = math.sin(latitude)

        for output_x in range(output_width):
            longitude = (
                (output_x + 0.5) / output_width * 2.0 - 1.0
            ) * math.pi
            direction_x = latitude_cosine * math.sin(longitude)
            direction_z = latitude_cosine * math.cos(longitude)
            face, u, v = _cubemap_face_and_uv(
                direction_x,
                direction_y,
                direction_z,
            )

            source_x = min(
                face_width - 1,
                max(0, int(u * face_width)),
            )
            source_y = min(
                face_height - 1,
                max(0, face_height - 1 - int(v * face_height)),
            )
            source = (source_y * face_width + source_x) * 4
            target = (output_y * output_width + output_x) * 4
            output[target:target + 4] = face_pixels[face][source:source + 4]

    return output_width, output_height, output


def load_dds_cubemap(path, image_name=None):
    info = _read_dds_cubemap_info(path)
    if info is None:
        raise ValueError(f"Not a DDS cubemap: {path}")

    source_name = image_name or os.path.basename(path)
    converted_name = f"{source_name}__EQG_EQUIRECTANGULAR"
    existing = bpy.data.images.get(converted_name)
    if existing is not None:
        if existing.has_data:
            return existing
        bpy.data.images.remove(existing)

    invalid_source = bpy.data.images.get(source_name)
    if invalid_source is not None and not invalid_source.has_data:
        bpy.data.images.remove(invalid_source)

    with open(path, 'rb') as f:
        data = f.read()

    header_size = info["header_size"]
    face_size = info["face_size"]
    face_header = bytearray(data[:header_size])
    struct.pack_into('<I', face_header, 112, 0)

    if info["fourcc"] == b'DX10':
        misc_flags = struct.unpack_from('<I', face_header, 136)[0]
        struct.pack_into('<I', face_header, 136, misc_flags & ~0x4)

    caps = struct.unpack_from('<I', face_header, 108)[0]
    if info["mip_count"] == 1:
        struct.pack_into('<I', face_header, 108, caps & ~DDSCAPS_COMPLEX)

    loaded_faces = []
    face_pixels = []
    with tempfile.TemporaryDirectory(prefix="quail_dds_cube_") as temp_dir:
        try:
            for face_index in range(6):
                start = header_size + face_index * face_size
                end = start + face_size
                face_path = os.path.join(
                    temp_dir,
                    f"face_{face_index}.dds",
                )
                with open(face_path, 'wb') as f:
                    f.write(face_header)
                    f.write(data[start:end])

                face_image = bpy.data.images.load(
                    face_path,
                    check_existing=False,
                )
                loaded_faces.append(face_image)
                if tuple(face_image.size) != (
                    info["width"],
                    info["height"],
                ):
                    raise ValueError(
                        f"Cubemap face {face_index} has unexpected size "
                        f"{tuple(face_image.size)}"
                    )

                try:
                    face_image.colorspace_settings.name = "Non-Color"
                except TypeError:
                    pass
                face_pixels.append(_rgba_pixels(face_image))
        finally:
            for face_image in loaded_faces:
                bpy.data.images.remove(face_image)

    width, height, pixels = _cubemap_to_equirectangular(
        face_pixels,
        info["width"],
        info["height"],
    )
    image = bpy.data.images.new(
        converted_name,
        width=width,
        height=height,
        alpha=True,
    )
    image.pixels.foreach_set(pixels)
    image.alpha_mode = 'CHANNEL_PACKED'
    image.use_fake_user = True
    image["quail_cubemap_equirectangular"] = True
    image["quail_source_name"] = source_name
    image["quail_source_path"] = os.path.abspath(path)
    try:
        image.colorspace_settings.name = "sRGB"
    except TypeError:
        pass
    image.update()
    return image

def fix_dds_mipmap_flag(path):
    DDS_HEADER_SIZE = 128
    DDS_OFFSET_MIPMAPCOUNT = 28
    DDS_OFFSET_FLAGS = 8
    DDS_OFFSET_COMPRESSION = 84
    DDSD_MIPMAPCOUNT = 0x20000
    DXT1 = b'DXT1'
    DXT5 = b'DXT5'

    with open(path, 'rb+') as f:
        header = f.read(DDS_HEADER_SIZE)

        if len(header) < DDS_HEADER_SIZE or header[:4] != DDS_MAGIC:
            return

        mip_map_count = struct.unpack_from('<I', header, DDS_OFFSET_MIPMAPCOUNT)[0]
        flags = struct.unpack_from('<I', header, DDS_OFFSET_FLAGS)[0]
        compression = header[DDS_OFFSET_COMPRESSION:DDS_OFFSET_COMPRESSION+4]

        if (
            mip_map_count == 0 and
            (flags & DDSD_MIPMAPCOUNT) and
            compression in (DXT1, DXT5)
        ):
            print(f"Patching DDS mip flag: {path}")
            flags &= ~DDSD_MIPMAPCOUNT
            f.seek(DDS_OFFSET_FLAGS)
            f.write(struct.pack('<I', flags))


def flip_image_vertically(image):
    width, height = image.size
    channels = image.channels
    row_size = width * channels

    # Single copy only
    pixels = image.pixels[:]

    flipped = [0.0] * len(pixels)

    for y in range(height):
        src_start = y * row_size
        src_end = src_start + row_size

        dst_start = (height - 1 - y) * row_size
        dst_end = dst_start + row_size

        flipped[dst_start:dst_end] = pixels[src_start:src_end]

    image.pixels[:] = flipped
    image.update()

def extract_bmp_palette(path, image):
    with open(path, "rb") as f:
        header = f.read(54)

        if len(header) < 54 or header[:2] != BMP_MAGIC:
            print("Invalid BMP header")
            return

        bpp = struct.unpack_from("<H", header, 28)[0]
        if bpp != 8:
            print("Not 8-bit BMP, skipping palette")
            return

        clr_used = struct.unpack_from("<I", header, 46)[0]
        if clr_used == 0:
            clr_used = 256

        palette = []

        for i in range(clr_used):
            entry = f.read(4)
            if len(entry) < 4:
                break

            b, g, r, _ = struct.unpack("BBBB", entry)
            palette.append((r, g, b))

        while len(palette) < 256:
            palette.append((0, 0, 0))

        image["bmp_palette"] = palette

        # Store index 0 color normalized
        r0, g0, b0 = palette[0]
        image["bmp_index0_color"] = (
            r0 / 255.0,
            g0 / 255.0,
            b0 / 255.0
        )

def process_bmp_image(path, image):
    image.alpha_mode = 'CHANNEL_PACKED'

    # 🔹 Always extract + store palette first
    if not image.get("bmp_palette"):
        extract_bmp_palette(path, image)

    # Safety: make sure index0 exists
    if "bmp_index0_color" not in image:
        print(f"[WARN] No bmp_index0_color on {image.name}, skipping alpha bake")
        return

    # ----------------------------------------
    # Bake alpha into image
    # ----------------------------------------
    pixels = list(image.pixels)

    r0, g0, b0 = image["bmp_index0_color"]

    for i in range(0, len(pixels), 4):
        r, g, b = pixels[i], pixels[i+1], pixels[i+2]

        if (
            abs(r - r0) < 1e-5 and
            abs(g - g0) < 1e-5 and
            abs(b - b0) < 1e-5
        ):
            pixels[i+3] = 0.0
        else:
            pixels[i+3] = 1.0

    image.pixels[:] = pixels
    image.update()

    # Optional: mark as processed
    image["bmp_processed"] = True

def load_s3d_image(ctx, name: str) -> tuple[bpy.types.Image | None, str | None]:

    texture_path = os.path.join(ctx.parser.assets_path, name)

    if not os.path.exists(texture_path):
        return None, f"Texture not found: {texture_path}"

    abs_path = bpy.path.abspath(texture_path)

    for img in bpy.data.images:
        if bpy.path.abspath(img.filepath) == abs_path:
            return img, None

    tex_type = detect_texture_type(texture_path)

    if tex_type == "DDS":
        fix_dds_mipmap_flag(texture_path)

    try:
        image = bpy.data.images.load(texture_path)
        print(f"Loaded texture {texture_path}")
    except Exception as e:
        return None, f"Error loading texture {texture_path}: {e}"

    image["image_type"] = tex_type

    if tex_type == "BMP":
        if name.upper().endswith("PAL.BMP"):
            extract_bmp_palette(texture_path, image)
        else:
            process_bmp_image(texture_path, image)

    else:
        if not image.get("quail_flipped", False):
            try:
                flip_image_vertically(image)
                image["quail_flipped"] = True
                image.pack()
                image.gl_free()
            except Exception as e:
                return None, f"Error flipping {texture_path}: {e}"

    return image, None

def load_eqg_image(
    ctx,
    name: str | None,
    flip_tex: bool = False,
    non_color: bool = False,
) -> tuple[bpy.types.Image | None, str]:

    if not name or name == "None":
        return None, ""

    # Fallback: grid_standard.dds
    if name.lower() == "grid_standard.dds":
        img = bpy.data.images.get("grid_standard.dds")
        if img is None:
            img = bpy.data.images.new("grid_standard.dds", 1024, 1024)
            img.generated_type = 'COLOR_GRID'
            img.use_fake_user = True
        return img, ""

    assert ctx.parser.assets_path is not None

    texture_path = os.path.join(ctx.parser.assets_path, name)
    image_name = os.path.basename(name)
    if not os.path.exists(texture_path):
        return None, f"Texture not found: {texture_path}"

    tex_type = detect_texture_type(texture_path)
    try:
        is_cubemap = tex_type == "DDS" and is_dds_cubemap(texture_path)
    except Exception as e:
        return None, f"Error reading DDS cubemap {texture_path}: {e}"

    if is_cubemap:
        try:
            img = load_dds_cubemap(texture_path, image_name)
        except Exception as e:
            return None, f"Error converting DDS cubemap {texture_path}: {e}"
    else:
        img = bpy.data.images.get(name)
        if img is None:
            img = bpy.data.images.get(image_name)

        if img is None:
            try:
                img = bpy.data.images.load(
                    texture_path,
                    check_existing=True,
                )
                img.alpha_mode = 'CHANNEL_PACKED'
            except Exception as e:
                return None, f"Error loading texture {texture_path}: {e}"

    is_palette_bmp = (
        tex_type == "BMP"
        and name.upper().endswith("PAL.BMP")
    )

    if is_palette_bmp and "bmp_palette" not in img:
        try:
            extract_bmp_palette(texture_path, img)
        except Exception as e:
            return None, (
                f"Error extracting BMP palette "
                f"{texture_path}: {e}"
            )

    if non_color or is_palette_bmp:
        try:
            if img.colorspace_settings.name != "Non-Color":
                img.colorspace_settings.name = "Non-Color"
        except TypeError:
            pass

    if (
        flip_tex
        and not is_cubemap
        and not img.get("quail_flipped", False)
    ):
        try:
            flip_image_vertically(img)
            img["quail_flipped"] = True

            img.gl_free()
            img.update()

        except Exception as e:
            return None, f"Error flipping {name}: {e}"

    return img, ""