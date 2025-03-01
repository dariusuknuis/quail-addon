# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
import bpy
import os
import time
import tempfile
from ..common import dialog, quail, is_dev
import shutil
import io
from bpy_extras.wm_utils.progress_report import ProgressReport
from ..bin_quail.convert import convert
from ..decoder import wce_decode

bl_info = {
    "name": "Import EQG",
    "blender": (2, 80, 0),
    "category": "Import-Export",
}

class ImportEQG(bpy.types.Operator):
    bl_idname = "import_scene.eqg"
    bl_label = "Import EQG"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".eqg"

    filter_glob: bpy.props.StringProperty(
        default="*.eqg;*.s3d",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for importing the EQG file",
        maxlen=1024,
        default="",
    )

    is_scene_cleared: BoolProperty(
        name="Clear Scene Before Import",
        description="Clears the scene before importing, removing all objects, materials, collections etc",
        default=True,
    )

    is_scene_modified: BoolProperty(
        name="Modify Scene for Import",
        description="Sets view clip to 5000 (for large zones), other misc tweaks",
        default=True,
    )

    def execute(self, context):
        return import_data(context,
                           self.filepath,
                           self.is_scene_cleared,
                           self.is_scene_modified)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_import(self, context):
    self.layout.operator(ImportEQG.bl_idname,
                         text="EverQuest Archive (.eqg/.s3d/.wce)")

def register():
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()


def import_data(context, filepath, is_scene_cleared: bool = True, is_scene_modified: bool = True):

    with ProgressReport() as progress:
        progress.enter_substeps(2, "Generating quail...")
        # check if file exists
        if not os.path.exists(filepath):
            filepath = filepath.replace(".eqg", ".s3d")

        base_name = os.path.basename(filepath)

        # get base of filepath
        pfs_tmp = tempfile.gettempdir() + "/quail/" + base_name + ".quail"
        start_time = time.time()

        result = convert(filepath, pfs_tmp)
        if result != "":
            msg = "Quail Failed: " + result
            print(msg)
            dialog.message_box(msg,
                               "Quail Error", 'ERROR')
            return {'CANCELLED'}
        progress.step()

        if is_scene_cleared:
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

        if is_scene_modified:
            # bpy.context.space_data.clip_end = 15000
            pass

        base_name = os.path.basename(filepath)
        path = pfs_tmp

        print("Checking for", path)
        # check if path exists
        if not os.path.exists(path):
            dialog.message_box("File does not exist",
                               "Quail Error", 'ERROR')

        wce_decode(path)

        for img in bpy.data.images:
            if img.users > 0 and os.path.exists(img.filepath):
                img.pack()

        if os.path.exists(pfs_tmp) and not is_dev():
            print("Removing cache")
            shutil.rmtree(pfs_tmp)

        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        print("Full path: %s" % pfs_tmp)
        print("Importing %s took %s seconds" %
              (base_name, time.time() - start_time))
        progress.leave_substeps("Finished!")
        return {'FINISHED'}