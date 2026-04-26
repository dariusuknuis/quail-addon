# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator

import os
import time
import tempfile
import shutil

from bpy_extras.wm_utils.progress_report import ProgressReport

from ...common import dialog, is_dev
from ...logger.error import error_clear
from ...encoder import wce_encode
from ...bin_quail.convert import convert


# ---------------------------------------------------------
# Blender metadata
# ---------------------------------------------------------
bl_info = {
    "name": "Export EQG",
    "blender": (2, 80, 0),
    "category": "Import-Export",
}


# ---------------------------------------------------------
# Operator
# ---------------------------------------------------------
class ExportEQG(Operator, ExportHelper):
    bl_idname = "export_scene.eqg"
    bl_label = "Export EQG"
    bl_options = {'PRESET'}

    filename_ext = ".eqg"

    filter_glob: StringProperty(
        default="*.eqg;*.s3d;*.wce",
        options={'HIDDEN'},
        maxlen=255,
    )  # type: ignore

    export_selected_only: BoolProperty(
        name="Selected Objects Only",
        description="Export only selected objects and their dependencies",
        default=True,
    ) # type: ignore

    export_as_wce: BoolProperty(
        name="Export as WCE only",
        description="Write raw WCE instead of packing into EQG/S3D",
        default=False,
    )  # type: ignore

    overwrite: BoolProperty(
        name="Overwrite Existing",
        default=True,
    )  # type: ignore

    def execute(self, context):
        return export_data(
            context,
            self.filepath,
            self.export_as_wce,
            self.export_selected_only
        )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# ---------------------------------------------------------
# Menu
# ---------------------------------------------------------
def menu_func_export(self, context):
    self.layout.operator(
        ExportEQG.bl_idname,
        text="EverQuest Archive (.eqg/.s3d/.wce)"
    )


def register():
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


# ---------------------------------------------------------
# Core Export Logic
# ---------------------------------------------------------
def export_data(context, filepath: str, export_as_wce: bool, selected_only: bool):

    error_clear()

    with ProgressReport() as progress:
        progress.enter_substeps(2, "Exporting Quail data...")

        start_time = time.time()

        # ---------------------------------------------------------
        # Validate path
        # ---------------------------------------------------------
        if not filepath:
            dialog.message_box("No output path specified", "Quail Error", 'ERROR')
            return {'CANCELLED'}

        # ----------------------------------------
        # Use collection name if available
        # ----------------------------------------
        col = context.collection

        if col:
            base_name = col.name.lower()
        else:
            base_name = os.path.splitext(os.path.basename(filepath))[0]

        ext = os.path.splitext(filepath)[1].lower()

        # ---------------------------------------------------------
        # Build temp working directory (.quail)
        # ---------------------------------------------------------
        tmp_root = os.path.join(
            tempfile.gettempdir(),
            "quail_export",
            base_name + ".quail"
        )

        if os.path.exists(tmp_root):
            shutil.rmtree(tmp_root)

        os.makedirs(tmp_root, exist_ok=True)

        # ---------------------------------------------------------
        # STEP 1: Encode Blender → .quail folder
        # ---------------------------------------------------------
        print("Encoding to quail folder:", tmp_root)

        err = wce_encode(tmp_root, context, selected_only)

        if err:
            dialog.message_box(f"Encode failed:\n{err}", "Quail Error", 'ERROR')
            return {'CANCELLED'}

        progress.step()

        root_wce_path = os.path.join(tmp_root, "_root.wce")

        # ---------------------------------------------------------
        # STEP 2: Output handling
        # ---------------------------------------------------------
        if export_as_wce or ext == ".wce":
            print("Exporting WCE:", filepath)

            if not os.path.exists(root_wce_path):
                dialog.message_box("_root.wce not found after encode", "Quail Error", 'ERROR')
                return {'CANCELLED'}

            # ----------------------------------------
            # Output folder should match .quail name
            # ----------------------------------------
            export_dir = os.path.join(
                os.path.dirname(filepath),
                base_name + ".quail"
            )

            print("Exporting full WCE folder:", export_dir)

            if os.path.exists(export_dir):
                shutil.rmtree(export_dir)

            shutil.copytree(tmp_root, export_dir)

        else:
            # -----------------------------------------------------
            # Convert .quail → EQG/S3D
            # -----------------------------------------------------
            print("Converting quail → archive:", filepath)

            result = convert(tmp_root, filepath)

            if result != "":
                dialog.message_box(f"Quail convert failed:\n{result}", "Quail Error", 'ERROR')
                return {'CANCELLED'}

        # ---------------------------------------------------------
        # Cleanup temp
        # ---------------------------------------------------------
        if not is_dev() and os.path.exists(tmp_root):
            print("Cleaning temp export folder")
            shutil.rmtree(tmp_root)

        print(f"Exported {base_name} in {time.time() - start_time:.3f}s")

        progress.leave_substeps("Finished!")

        return {'FINISHED'}