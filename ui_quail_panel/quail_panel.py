# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
import bpy
import os
import time
import tempfile
from ..common import dialog, quail, is_dev, version
import shutil
from bpy_extras.wm_utils.progress_report import ProgressReport
from ..bin_quail.convert import convert
from ..decoder import wce_decode
from ..logger.error import errors, error_clear

# First, add a global variable to store the currently selected error
current_error_message = ""

class QUAIL_OT_ImportOperator(bpy.types.Operator):
    bl_idname = "quail.import"
    bl_label = "Import"

    def execute(self, context):
        filepath = "/src/eq/rof2lite/mim_chr.s3d"
        #filepath = "/src/eq/rof2/it12043.eqg"

        error_clear()

        with ProgressReport() as progress:
            progress.enter_substeps(2, "Generating quail...")
            # check if file exists
            if not os.path.exists(filepath):
                filepath = filepath.replace(".eqg", ".s3d")

            base_name = os.path.basename(filepath)
            base_name = os.path.splitext(base_name)[0]

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

            for material in bpy.data.materials:
                bpy.data.materials.remove(material)

            for texture in bpy.data.textures:
                bpy.data.textures.remove(texture)


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
            dialog.message_box("Import successful",
                               "Quail Info", 'INFO')
            return {'FINISHED'}

class QUAIL_PT_Panel(bpy.types.Panel):
    bl_label = "Quail %s" % (version())
    bl_idname = "QUAIL_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Quail'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("quail.import", text="Import")
        row = layout.row()
        row.label(text="Error Log:")
        for error in errors():
            row = layout.row()
            # Truncate long messages for display
            display_text = "..." + error[-30:]  if len(error) > 30 else error
            row.label(text=display_text)
            # Use a custom operator instead of wm.call_menu
            op = row.operator("quail.show_error", text="", icon='ERROR')
            op.error_message = error  # type: ignore

# Create a custom operator to show the error
class QUAIL_OT_ShowError(bpy.types.Operator):
    bl_idname = "quail.show_error"
    bl_label = "Show Error Details"
    bl_options = {'REGISTER'}

    error_message: StringProperty(
        name="Error Message",
        description="The full error message to display",
        default=""
    ) #type: ignore

    def execute(self, context):
        global current_error_message
        current_error_message = self.error_message
        bpy.ops.wm.call_menu(name="QUAIL_MT_ErrorPopup")
        return {'FINISHED'}

class QUAIL_MT_ErrorPopup(bpy.types.Menu):
    bl_label = "Error Details"
    bl_idname = "QUAIL_MT_ErrorPopup"

    def draw(self, context):
        global current_error_message
        layout = self.layout

        # Split the error message into multiple lines by newlines first
        lines = current_error_message.split('\n')

        for line in lines:
            # Process each line
            segments = []

            # First, split on colons if they exist
            if ':' in line:
                parts = line.split(":")
                for i, part in enumerate(parts):
                    # Get the display text
                    display = part[:80].strip()
                    remaining = part[80:] if len(part) > 80 else ""
                    segments.append(display)

                # Continue processing the remaining part for length
                while remaining:
                    # Get next 80 chars or remainder if shorter
                    display = remaining[:80].strip()
                    remaining = remaining[80:] if len(remaining) > 80 else ""
                    segments.append(display)
            else:
                # No colon, just split based on length
                remaining = line
                while remaining:
                    # Get next 80 chars or remainder if shorter
                    display = remaining[:80].strip()
                    remaining = remaining[80:] if len(remaining) > 80 else ""
                    segments.append(display)

            # Draw all segments
            for segment in segments:
                if segment:  # Only add non-empty segments
                    layout.label(text=segment)
