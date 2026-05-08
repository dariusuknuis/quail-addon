# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
import bpy
import os
import time
import tempfile
from ...common import dialog, quail, is_dev
import shutil
import io
from bpy_extras.wm_utils.progress_report import ProgressReport
from ...bin_quail.convert import convert
from ...decoder import wce_decode
from ...logger.error import errors, error_clear

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
        default="*.eqg;*.s3d;*.wce",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    ) # type: ignore

    filepath: bpy.props.StringProperty(
        name="File Path",
        description="Filepath used for importing the EQG file",
        maxlen=1024,
        default="",
    ) # type: ignore

    is_scene_cleared: BoolProperty(
        name="Clear Scene Before Import",
        description="Clears the scene before importing, removing all objects, materials, collections etc",
        default=True,
    ) # type: ignore

    is_scene_modified: BoolProperty(
        name="Modify Scene for Import",
        description="Sets view clip to 5000 (for large zones), other misc tweaks",
        default=True,
    ) # type: ignore

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

    error_clear()

    with ProgressReport() as progress:
        progress.enter_substeps(2, "Generating quail...")

        # ---------------------------------------------------------
        # Validate file exists
        # ---------------------------------------------------------
        if not os.path.exists(filepath):
            dialog.message_box(f"File not found: {filepath}", "Quail Error", 'ERROR')
            return {'CANCELLED'}

        # ---------------------------------------------------------
        # Extract base name and extension safely
        # ---------------------------------------------------------
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        ext = os.path.splitext(filepath)[1].lower()

        # ---------------------------------------------------------
        # Build temp path (for converted archives)
        # ---------------------------------------------------------
        pfs_tmp = os.path.join(tempfile.gettempdir(), "quail", base_name + ".quail")
        start_time = time.time()

        # ---------------------------------------------------------
        # Handle input types
        # ---------------------------------------------------------
        if ext in (".eqg", ".s3d"):
            result = convert(filepath, pfs_tmp)
            if result != "":
                msg = "Quail Failed: " + result
                print(msg)
                dialog.message_box(msg, "Quail Error", 'ERROR')
                return {'CANCELLED'}

            decode_path = pfs_tmp

        elif ext == ".wce":
            decode_path = filepath

        else:
            dialog.message_box(f"Unsupported file type: {ext}", "Quail Error", 'ERROR')
            return {'CANCELLED'}

        progress.step()

        # ---------------------------------------------------------
        # Clear scene if requested
        # ---------------------------------------------------------
        if is_scene_cleared:
            for collection in bpy.data.collections:
                bpy.data.collections.remove(collection)

            for mesh in bpy.data.meshes:
                bpy.data.meshes.remove(mesh)

            for obj in bpy.data.objects:
                if obj.type == 'CAMERA':
                    continue
                bpy.data.objects.remove(obj)

            for arm in bpy.data.armatures:
                bpy.data.armatures.remove(arm)

            for mat in bpy.data.materials:
                bpy.data.materials.remove(mat)

            for img in bpy.data.images:
                bpy.data.images.remove(img)

            for action in bpy.data.actions:
                bpy.data.actions.remove(action)

        # ---------------------------------------------------------
        # Scene tweaks (optional)
        # ---------------------------------------------------------
        if is_scene_modified:
            # bpy.context.space_data.clip_end = 15000
            pass

        # ---------------------------------------------------------
        # Decode
        # ---------------------------------------------------------
        print("Checking for", decode_path)

        if not os.path.exists(decode_path):
            dialog.message_box("File does not exist", "Quail Error", 'ERROR')
            return {'CANCELLED'}

        # wce_decode(decode_path)

        if os.path.isdir(decode_path):

            root_name = os.path.splitext(os.path.basename(decode_path))[0]

            main_collection = bpy.data.collections.new(root_name)
            context.scene.collection.children.link(main_collection)

            wce_decode(decode_path, main_collection)

            objects_path = os.path.join(decode_path, "_objects")
            lights_path = os.path.join(decode_path, "_lights")

            if os.path.exists(objects_path):
                wce_decode(objects_path, main_collection)

            if os.path.exists(lights_path):
                wce_decode(lights_path, main_collection)

        else:
            wce_decode(decode_path)

        # ---------------------------------------------------------
        # Pack images
        # ---------------------------------------------------------
        for img in bpy.data.images:
            if img.users > 0 and os.path.exists(img.filepath):
                img.pack()

        # ---------------------------------------------------------
        # Cleanup temp data
        # ---------------------------------------------------------
        if ext in (".eqg", ".s3d") and os.path.exists(pfs_tmp) and not is_dev():
            print("Removing cache")
            shutil.rmtree(pfs_tmp)

        # ---------------------------------------------------------
        # Ensure object mode
        # ---------------------------------------------------------
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        print("Full path: %s" % decode_path)
        print("Importing %s took %s seconds" % (base_name, time.time() - start_time))

        progress.leave_substeps("Finished!")
        return {'FINISHED'}