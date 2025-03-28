import bpy
from .panel_eqgmodeldef import OBJECT_OT_add_quail_eqgmodeldef
from .panel_actordef import OBJECT_OT_add_quail_actordef
from .panel_eqgterdef import OBJECT_OT_add_quail_eqgterdef

# Create a new Quail menu class
class VIEW3D_MT_quail_add(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_quail_add"
    bl_label = "Quail"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_add_quail_eqgmodeldef.bl_idname, icon='IMAGE_DATA')
        layout.operator(OBJECT_OT_add_quail_actordef.bl_idname, icon='IMAGE_DATA')
        layout.operator(OBJECT_OT_add_quail_eqgterdef.bl_idname, icon='IMAGE_DATA')

# Function to add the Quail menu to the Add menu
def add_quail_menu(self, context):
    self.layout.menu(VIEW3D_MT_quail_add.bl_idname, icon='GHOST_ENABLED')


def register():
    bpy.types.VIEW3D_MT_add.append(add_quail_menu)

def unregister():
    bpy.types.VIEW3D_MT_add.remove(add_quail_menu)
    del bpy.types.Object.quail_actordef
