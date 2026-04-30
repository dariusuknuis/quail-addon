import bpy
import math
import mathutils

def create_bsp_plane_mesh(name="BSPPlaneMesh", size=10000.0):
    half = size / 2.0

    verts = [
        (-half, -half, 0),
        ( half, -half, 0),
        ( half,  half, 0),
        (-half,  half, 0)
    ]
    faces = [(0, 1, 2, 3)]

    rot = mathutils.Euler((-math.pi/2, 0, 0), 'XYZ').to_matrix().to_4x4()
    verts_rot = [rot @ mathutils.Vector(v) for v in verts]

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts_rot, [], faces)
    mesh.update()
    return mesh


def create_leaf_mesh(name="LeafMesh"):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(0, 0, 0)], [], [])
    mesh.update()
    return mesh


def rotation_from_normal(normal):
    default_dir = mathutils.Vector((0, 1, 0))
    target_dir = mathutils.Vector(normal).normalized()
    quat = default_dir.rotation_difference(target_dir)
    return quat.to_euler()


def calculate_point_on_plane(normal, d):
    n = mathutils.Vector(normal).normalized()
    return -d * n