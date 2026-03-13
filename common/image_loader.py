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

def extract_bmp_index0_color(path):
    with open(path, "rb") as f:
        header = f.read(54)

        if len(header) < 54 or header[:2] != BMP_MAGIC:
            return None

        # Bits per pixel at offset 28 (2 bytes, little endian)
        bpp = struct.unpack_from("<H", header, 28)[0]

        if bpp != 8:
            return None  # Not indexed

        # First palette entry immediately after 54-byte header
        palette = f.read(4)
        if len(palette) < 4:
            return None

        blue, green, red, _ = struct.unpack("BBBB", palette)

        return (
            red / 255.0,
            green / 255.0,
            blue / 255.0
        )

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

        index0 = extract_bmp_index0_color(texture_path)
        if index0:
            image["bmp_index0_color"] = index0

    else:
        if not image.get("quail_flipped", False):
            try:
                flip_image_vertically(image)
                image["quail_flipped"] = True
            except Exception as e:
                return None, f"Error flipping {texture_path}: {e}"

    return image, None