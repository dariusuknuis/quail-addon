import io
import shlex
import bpy
import os
import bmesh
from typing import Tuple

path = "/src/quail/test/arena.quail/r/r.original.mod"

def message_box(message:str, title:str, icon:str='INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def parse(path:str=""):
    file_reader = open(path, "r")
    data = file_reader.read()
    r = io.StringIO(data)
    try:
        parse_definitions(r)
    except Exception as e:
        raise Exception(f"parse_definitions: {e}") from e


def parse_definitions(r:io.TextIOWrapper=None):
    if r is None:
        raise Exception("reader is none")

    for line in r:
        line = line.strip()
        if line == "":
            continue
        if line.startswith("//"):
            continue
        # if line == "3DSPRITEDEF":
        #     err = parse_3dspritedef(r)
        #     if err:
        #         return err
        #     continue
        # if line == "ACTORDEF":
        #     parse_actordef(r)
        #     if err:
        #         return err
        #     continue
        # if line == "ACTORINST":
        #     parse_actorinst(r)
        #     if err:
        #         return err
        #     continue
        # if line == "AMBIENTLIGHT":
        #     parse_ambientlight(r)
        #     if err:
        #         return err
        #     continue
        # if line == "BLITSPRITEDEFINITION":
        #     parse_blitspritedefinition(r)
        #     if err:
        #         return err
        #     continue
        if line == "DMSPRITEDEF2":
            try:
                parse_dmspritedef2(r)
            except Exception as e:
                raise Exception(f"parse_dmspritedef2: {e}") from e
        # if line == "DMSPRITEDEFINITION":
        #     parse_dmspritedefinition(r)
        #     if err:
        #         return err
        #     continue
        # if line == "GLOBALAMBIENTLIGHTDEF":
        #     parse_globalambientlightdef(r)
        #     if err:
        #         return err
        #     continue
        # if line == "HIERARCHICALSPRITEDEF":
        #     parse_hierarchicalspritedef(r)
        #     if err:
        #         return err
        #     continue
        # if line == "LIGHTDEFINITION":
        #     parse_lightdefinition(r)
        #     if err:
        #         return err
        #     continue
        # if line == "MATERIALDEFINITION":
        #     parse_materialdefinition(r)
        #     if err:
        #         return err
        #     continue
        # if line == "MATERIALPALETTE":
        #     parse_materialpalette(r)
        #     if err:
        #         return err
        #     continue
        # if line == "PARTICLECLOUDDEF":
        #     parse_particleclouddef(r)
        #     if err:
        #         return err
        #     continue
        # if line == "POINTLIGHT":
        #     parse_pointlight(r)
        #     if err:
        #         return err
        #     continue
        # if line == "POLYHEDRONDEFINITION":
        #     parse_polyhedrondefinition(r)
        #     if err:
        #         return err
        #     continue
        # if line == "REGION":
        #     parse_region(r)
        #     if err:
        #         return err
        #     continue
        # if line == "RGBDEFORMATIONTRACKDEF":
        #     parse_rgbdeformationtrackdef(r)
        #     if err:
        #         return err
        #     continue
        # if line == "SIMPLESPRITEDEF":
        #     parse_simplespritedef(r)
        #     if err:
        #         return err
        #     continue
        # if line == "SPRITE2DDEF":
        #     parse_sprite2ddef(r)
        #     if err:
        #         return err
        #     continue
        # if line == "TRACKDEFINITION":
        #     parse_trackdefinition(r)
        #     if err:
        #         return err
        #     continue
        # if line == "TRACKINSTANCE":
        #     parse_trackinstance(r)
        #     if err:
        #         return err
        #     continue
        # if line == "WORLDDEF":
        #     parse_worlddef(r)
        #     if err:
        #         return err
        #     continue
        # if line == "WORLDTREE":
        #     parse_worldtree(r)
        #     if err:
        #         return err
        #     continue
        # if line == "ZONE":
        #     parse_zone(r)
        #     if err:
        #         return err
        #     continue
        #return "Unknown definition: " + line
    return ""

def parse_property(r:io.TextIOWrapper=None, property:str="", num_args:int=-1) -> list[str]:
    if r is None:
        raise Exception("reader is none")
    if property == "":
        raise Exception("empty property")
    for line in r:
        if line.find("//"):
            line = line.split("//")[0]
        line = line.strip()
        if line == "":
            continue
        records = shlex.split(line)
        if len(records) == 0:
            raise Exception("%s: empty records (%s)" % (property, line))
        if records[0] != property:
            raise Exception("%s: expected property %s got %s" % (property, property, records[0]))
        if num_args != -1 and len(records)-1 != num_args:
            raise Exception("%s: expected %d arguments, got %d" % (property, len(records)-1, num_args))
        return records

def parse_dmspritedef2(tag:str, r:io.TextIOWrapper=None):
    if r is None:
        raise Exception("reader is none")

    base_tag = tag.split("_DMSPRITEDEF")[0]

    print("Reading %s" % tag)
    mesh = bpy.data.meshes.new(tag)

    records = parse_property(r, "CENTEROFFSET", 3)
    mesh["centeroffset"] = (float(records[1]), float(records[2]), float(records[3]))

    if base_tag == "R1":
        print(mesh["centeroffset"][0], mesh["centeroffset"][1], mesh["centeroffset"][2])
    records = parse_property(r, "NUMVERTICES", 1)
    vert_count = int(records[1])
    mesh_verts = []
    for i in range(vert_count):
        records = parse_property(r, "XYZ", 3)
        mesh_verts.append((float(records[1]), float(records[2]), float(records[3])))


    records = parse_property(r, "NUMUVS", 1)
    uv_count = int(records[1])
    mesh_uvs = []
    for i in range(uv_count):
        records = parse_property(r, "UV", 2)
        mesh_uvs.append((float(records[1]), float(records[2])))

    records = parse_property(r, "NUMVERTEXNORMALS", 1)
    normal_count = int(records[1])
    mesh_normals = []
    for i in range(normal_count):
        records = parse_property(r, "XYZ", 3)
        mesh_normals.append((float(records[1]), float(records[2]), float(records[3])))

    records = parse_property(r, "NUMVERTEXCOLORS", 1)
    color_count = int(records[1])
    mesh_colors = []
    for i in range(color_count):
        records = parse_property(r, "RGBA", 4)
        mesh_colors.append((float(records[1])/255, float(records[2])/255, float(records[3])/255, float(records[4])/255))

    records = parse_property(r, "SKINASSIGNMENTGROUPS", -1)
    records = parse_property(r, "MATERIALPALETTE", 1)
    mesh["materialpalette"] = records[1]

    records = parse_property(r, "POLYHEDRON", 0)

    records = parse_property(r, "DEFINITION", 1)
    mesh["definition"] = records[1]

    print("definition %s" % mesh["definition"])

    records = parse_property(r, "NUMFACE2S", 1)
    face_count = int(records[1])

    mesh_faces = []
    mesh_passable = []
    for i in range(face_count):
        records = parse_property(r, "DMFACE2", 0)
        records = parse_property(r, "PASSABLE", 1)
        mesh_passable.append(int(records[1]))
        records = parse_property(r, "TRIANGLE", 3)
        mesh_faces.append((int(records[1]), int(records[2]), int(records[3])))

    records = parse_property(r, "NUMMESHOPS", 1)

    records = parse_property(r, "FACEMATERIALGROUPS", -1)
    if len(records) < 2:
        return "FACEMATERIALGROUPS: expected at least 2 records"
    face_material_count = int(records[1])
    mesh["facematerialgroups"] = " ".join(records[1:])
    mesh_face_materials = []
    for i in range(0, face_material_count*2, 2):
        mesh_face_materials.append(records[i+2])
        mesh_face_materials.append(records[i+3])

    records = parse_property(r, "VERTEXMATERIALGROUPS", -1)
    if len(records) < 2:
        return "VERTEXMATERIALGROUPS: expected at least 2 records"
    mesh["vertexmaterialgroups"] = " ".join(records[1:])
    vertex_material_count = int(records[1])
    mesh_vertex_materials = []
    for i in range(0, vertex_material_count*2,2):
        mesh_vertex_materials.append(records[i+2])
        mesh_vertex_materials.append(records[i+3])

    records = parse_property(r, "BOUNDINGBOXMIN", 3)
    mesh["boundingboxmin"] = (float(records[1]), float(records[2]), float(records[3]))

    records = parse_property(r, "BOUNDINGBOXMAX", 3)
    mesh["boundingboxmax"] = (float(records[1]), float(records[2]), float(records[3]))

    records = parse_property(r, "BOUNDINGRADIUS", 1)

    mesh["boundingradius"] = float(records[1])

    records = parse_property(r, "FPSCALE", 1)
    mesh["fpscale"] = float(records[1])

    print("parse")
    records = parse_property(r, "HEXONEFLAG", 1)
    mesh["hexoneflag"] = int(records[1])

    records = parse_property(r, "HEXTWOFLAG", 1)
    mesh["hextwoflag"] = int(records[1])

    records = parse_property(r, "HEXFOURTOUSANDFLAG", 1)
    mesh["hexfourthousandflag"] = int(records[1])

    records = parse_property(r, "HEXEIGHTTOUSANDFLAG", 1)
    mesh["hexeightthousandflag"] = int(records[1])

    records = parse_property(r, "HEXTENTHOUSANDFLAG", 1)
    mesh["hextenthousandflag"] = int(records[1])

    records = parse_property(r, "HEXTWENTYTHOUSANDFLAG", 1)
    mesh["hextwentythousandflag"] = int(records[1])

    #print(mesh_verts)
    mesh.from_pydata(mesh_verts, [], mesh_faces)
    #mesh.update(calc_edges=True)
    mesh.update()
    #mesh.use_auto_smooth = True
    #mesh.normals_split_custom_set_from_vertices(mesh_normals)

    uv_layer = mesh.uv_layers.new(name="%s_uv" % base_tag)
    color_layer = mesh.vertex_colors.new(name="%s_color" % base_tag)

    for i in range(vert_count):
        uv_layer.data[i].uv = (mesh_uvs[i][0], mesh_uvs[i][1])
        color_layer.data[i].color = mesh_colors[i]

    # for triangle in mesh.polygons:
    #     vertices = list(triangle.vertices)
    #     i = 0
    #     for index in vertices:
    #         uv_layer.data[triangle.loop_indices[i]].uv = (mesh_uvs[index][0], mesh_uvs[index][1]-1)
    #         color_layer.data[triangle.loop_indices[i]].color = mesh_colors[index]
    #         i += 1


    # for i in range(len(mesh.polygons)):
    #     poly = mesh.polygons[i]
    #     if len(mesh_materials) > i:
    #         poly.material_index = mesh_materials[i]

    faces = {}
    mesh_obj = bpy.data.objects.new(base_tag, mesh)
    mesh_obj.location = mesh["centeroffset"]

    #collection = bpy.data.collections.new(tag)
    #collection.objects.link(mesh_obj)
    bpy.context.scene.collection.objects.link(mesh_obj)

    for face in faces:
        if face not in mesh_obj.face_maps:
            face_map = mesh_obj.face_maps.new(name=face)
        face_map = mesh_obj.face_maps[face]
        face_map.add(faces[face])

    bm = bmesh.new()
    if bpy.context.mode == 'EDIT_MESH':
        bm.from_edit_mesh(mesh)
    else:
        bm.from_mesh(mesh)

    bm.faces.ensure_lookup_table()
    passable_layer = bm.faces.layers.int.new("passable")
    for i in range(len(bm.faces)):
        bm.faces[i][passable_layer] = mesh_passable[i]
    # for i in range(len(mesh.polygons)):
    #     poly = mesh.polygons[i]
    #     # iterate every vertice in the polygon
    #     for index in poly.vertices:
    #         # get the vertex
    #         vert = mesh.vertices[index]
    #         vert["passable"] = mesh_passable[i]
    #     #if len(mesh_materials) > i:
    #     #    poly.material_index = mesh_materials[i]
    #     poly["passable"] = mesh_passable[i]
    print("end of layers?")
    bm.to_mesh(mesh)
    print("free")
    bm.free()
    mesh_obj.data.update()
    return ""


for collection in bpy.data.collections:
                bpy.data.collections.remove(collection)

for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh)

# remove orphed objects
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj)

for bone in bpy.data.armatures:
    bpy.data.armatures.remove(bone)

for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)

for img in bpy.data.images:
    bpy.data.images.remove(img)

for bone in bpy.data.armatures:
    bpy.data.armatures.remove(bone)

for action in bpy.data.actions:
    bpy.data.actions.remove(action)


if not os.path.exists(path):
    message_box("File does not exist", "Quail Error", 'ERROR')
    exit

ext = os.path.splitext(path)[1]
if ext != ".mod":
    message_box("Expected .mod, got extension " + ext, "Quail Error", 'ERROR')
    exit

parse(path)
print("Read successful")
