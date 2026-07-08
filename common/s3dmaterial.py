import re, bpy, hashlib
from ..common import base_tag
from ..common.rendermethod import apply_userdefined, apply_transparent, sync_rendermethod_node

VARIATION_REGEX = re.compile(r'^[A-Z]{3}(CH|FA|FT|HE|HN|LG|MN|TA|TL|UA)\d{4}_MDF$')

def material_tag_parse(tag: str) -> str:

    tag = base_tag(tag)

    if len(tag) >= 5 and tag.startswith("CLK"):
        if tag[3:5].isdigit():
            return "CLK"

    if tag.startswith("CHR_EYE") and len(tag) >= len("CHR_EYE") + 3:
        digits = tag[-7:-4]
        if digits.isdigit():
            return tag[:-5]

    if VARIATION_REGEX.match(tag) and len(tag) == 13:
        sixth_seventh = int(tag[5:7])
        eighth_ninth = int(tag[7:9])

        if sixth_seventh > 0 or eighth_ninth > 10:
            return tag[:3]

    return ""

def update_userdefined(self, context):
    if not self.use_userdefined:
        return
    apply_userdefined(self, self.userdefined_index)
    mat = self.id_data
    # mat = context.material
    if not mat:
        return

def update_rendermethod_node(self, context):

    id_data = self.id_data

    # MaterialDefinition

    if isinstance(id_data, bpy.types.Material):

        mat = id_data

    # BlitSpriteDef

    elif isinstance(id_data, bpy.types.Object):

        mat = id_data.active_material

        if not mat:
            return

    else:
        return

    sync_rendermethod_node(mat, self)

def update_transparent(self, context):
    if not self.transparent_override:
        return
    apply_transparent(self)
    mat = getattr(context, "material", None)
    if mat is None:
        return

def sprite_items(self, context):

    items = [("NONE", "<None>", "", 0)]

    for ng in bpy.data.node_groups:

        if ng.get("quaildef") != "simplespritedef":
            continue

        enum_id = int(
            hashlib.md5(
                ng.name.encode("utf8")
            ).hexdigest()[:4],
            16
        )

        items.append(
            (
                ng.name,
                ng.name,
                "",
                enum_id
            )
        )

    return items

def update_simplesprite(self, context):

    valid = [i[0] for i in sprite_items(self, context)]

    if not self.simplespritetag or self.simplespritetag not in valid:
        self.simplespritetag = valid[0] if valid else "NONE"
        return

    id_data = self.id_data

    if isinstance(id_data, bpy.types.Material):
        mat = id_data

    elif isinstance(id_data, bpy.types.Object):

        mat = id_data.active_material

        if not mat:
            return

    else:
        return

    if not mat.use_nodes or not mat.node_tree:
        return

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # --------------------------------------------
    # Find RENDERMETHOD node
    # --------------------------------------------
    rm_node = None
    for n in nodes:
        if n.type == "GROUP" and n.node_tree and n.node_tree.name == "RENDERMETHOD":
            rm_node = n
            break

    if not rm_node:
        return

    # --------------------------------------------
    # Remove existing sprite node
    # --------------------------------------------
    for n in list(nodes):
        if n.get("quail_sprite_node"):
            nodes.remove(n)

    # If cleared in panel, stop here
    if not self.simplespritetag or self.simplespritetag == "NONE":
        return

    sprite_group = bpy.data.node_groups.get(self.simplespritetag)
    if not sprite_group:
        return

    # --------------------------------------------
    # Create new sprite node
    # --------------------------------------------
    sprite_node = nodes.new("ShaderNodeGroup")
    sprite_node.node_tree = sprite_group
    sprite_node.location = (-400, 0)
    sprite_node["quail_sprite_node"] = True

    links.new(sprite_node.outputs["sRGB Texture"], rm_node.inputs["sRGB Texture"])
    links.new(sprite_node.outputs["Alpha"], rm_node.inputs["Alpha"])

def update_twosided(self, context):
    mat = self.id_data
    if not isinstance(mat, bpy.types.Material):
        return

    # Two-Sided ON  → disable culling
    # Two-Sided OFF → enable culling
    mat.use_backface_culling = not self.twosided

def frame_signature(frame):
    """Return a stable hash describing the files used by this frame."""

    parts = []

    for f in frame.files:
        parts.append("|".join([
            f.file_name,
            f.image_name,
            f.texture_mode,
            str(getattr(f, "palette_index", 0)),
        ]))

    return hashlib.sha1("\n".join(parts).encode("utf-8")).hexdigest()