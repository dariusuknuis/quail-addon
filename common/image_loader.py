import bpy
import struct

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


def patch_dds_header(path):
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


def load_image(path):

    texture_type = detect_texture_type(path)

    if texture_type == "DDS":
        patch_dds_header(path)

    image = bpy.data.images.load(path)

    # Prevent double flipping
    if image.get("quail_normalized"):
        return image, texture_type

    if texture_type == "BMP":
        image = image.copy()
        flip_image_vertically(image)

    image["quail_normalized"] = True

    return image, texture_type