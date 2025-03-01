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

class QUAIL_OT_ImportOperator(bpy.types.Operator):
    bl_idname = "quail.import"
    bl_label = "Import"

    def execute(self, context):
        filepath = "/src/eq/rof2lite/mim_chr.s3d"
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
        row = layout.row()
        row.label(text="Log Test", icon='NONE', translate=False)
        row = layout.row()
        row.label(text="Log Test2", icon='NONE', translate=False)

