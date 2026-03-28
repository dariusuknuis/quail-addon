import bpy
import struct
import os

# S3D/WLD

DDS_MAGIC = b'DDS '
BMP_MAGIC = b'BM'

def detect_texture_type(path):
    with open(path, 'rb') as f:
        header = f.read(4)

    if header[:4] == DDS_MAGIC:
        return "DDS"
    elif header[:2] == BMP_MAGIC:
        return "BMP"
    else:
        return "OTHER"


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

def process_bmp_image(path, image):
    image.alpha_mode = 'CHANNEL_PACKED'
    with open(path, "rb") as f:
        header = f.read(54)

        if len(header) < 54 or header[:2] != BMP_MAGIC:
            return

        width = struct.unpack_from("<I", header, 18)[0]
        height = struct.unpack_from("<I", header, 22)[0]
        bpp = struct.unpack_from("<H", header, 28)[0]

        if bpp != 8:
            return  # not indexed BMP

        # ----------------------------------------
        # Read palette (256 entries)
        # ----------------------------------------
        # Read palette size from header
        clr_used = struct.unpack_from("<I", header, 46)[0]

        if clr_used == 0:
            clr_used = 256  # default for 8-bit

        palette = []

        for i in range(clr_used):
            entry = f.read(4)
            if len(entry) < 4:
                break  # safety

            b, g, r, _ = struct.unpack("BBBB", entry)
            palette.append((r, g, b))

        # Pad to 256 if needed (important for indexing)
        while len(palette) < 256:
            palette.append((0, 0, 0))

        # ----------------------------------------
        # Store palette
        # ----------------------------------------
        image["bmp_palette"] = palette

        # ----------------------------------------
        # Index 0 color
        # ----------------------------------------
        r0, g0, b0 = palette[0]
        index0 = (r0 / 255.0, g0 / 255.0, b0 / 255.0)
        image["bmp_index0_color"] = index0

    # ----------------------------------------
    # Bake alpha into image
    # ----------------------------------------
    pixels = list(image.pixels)

    r0, g0, b0 = index0

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

    texture_path = f"{ctx.parser.path}/assets/{name}"

    if not os.path.exists(texture_path):
        return None, f"Texture not found: {texture_path}"

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
        if not name.upper().endswith("PAL.BMP"):
            process_bmp_image(texture_path, image)

    else:
        if not image.get("quail_flipped", False):
            try:
                flip_image_vertically(image)
                image["quail_flipped"] = True
            except Exception as e:
                return None, f"Error flipping {texture_path}: {e}"

    return image, None