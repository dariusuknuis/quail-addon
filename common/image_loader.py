import bpy
import struct
import os

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
    _ = image.pixels[:]

    pixels = list(image.pixels[:])
    channels = image.channels
    row_size = width * channels

    flipped = []
    for y in reversed(range(height)):
        start = y * row_size
        end = start + row_size
        flipped.extend(pixels[start:end])

    image.pixels[:] = flipped
    image.update()

def load_texture(ctx, name: str) -> str:
    texture_path = f"{ctx.parser.path}/assets/{name}"

    if not os.path.exists(texture_path):
        return f"Texture not found: {texture_path}"

    # Detect actual type from header
    tex_type = detect_texture_type(texture_path)

    # Fix DDS mipmap header if needed
    if tex_type == "DDS":
        fix_dds_mipmap_flag(texture_path)

    try:
        image = bpy.data.images.load(texture_path)
        print(f"Loaded texture {texture_path}")
    except Exception as e:
        return f"Error loading texture {texture_path}: {e}"

    # Store detected type
    image["image_type"] = tex_type

    # Flip BMP once only
    if tex_type == "BMP":
        if not image.get("quail_flipped", False):
            try:
                flip_image_vertically(image)
                image["quail_flipped"] = True
            except Exception as e:
                return f"Error flipping BMP {texture_path}: {e}"

    return ""