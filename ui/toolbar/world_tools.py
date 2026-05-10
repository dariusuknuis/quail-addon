import bpy

class VIEW3D_PT_EQ_world_tools(bpy.types.Panel):
    bl_label = "EverQuest World Tools"
    bl_idname = "VIEW3D_PT_EQ_world_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Quail'
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        layout.operator(
            "object.generate_outdoor_world",
            text="Generate Outdoor World",
            icon='VIEW3D'
        )
        # layout.operator(
        #     "object.generate_radial_visibility",
        #     text="Generate Radial Visibility",
        #     icon='ONIONSKIN_ON'
        # )
        layout.operator(
            "object.format_world",
            text="Format World",
            icon='OBJECT_DATA'
        )
