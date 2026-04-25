# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

# import bpy
# from bpy.props import StringProperty, FloatProperty, FloatVectorProperty,BoolProperty, PointerProperty, IntProperty, EnumProperty, CollectionProperty
# from ...decoder.track import get_or_create_track_props

# class QuailTrackProperties(bpy.types.PropertyGroup):

#     tag: StringProperty(name="Tag")

#     interpolate: IntProperty(name="Interpolate", default=0)
#     reverse: IntProperty(name="Reverse", default=0)

#     has_sleep: BoolProperty(name="Has Sleep", default=False)
#     sleep: IntProperty(name="Sleep", default=0)

#     numframes: IntProperty(name="Num Frames", default=0)

# class QUAIL_PT_track_panel(bpy.types.Panel):
#     bl_label = "Quail Track"
#     bl_space_type = 'DOPESHEET_EDITOR'
#     bl_region_type = 'UI'
#     bl_category = 'Quail'

#     @classmethod
#     def poll(cls, context):
#         return context.active_action_group is not None

#     def draw(self, context):
#         layout = self.layout

#         group = context.active_action_group
#         action = context.active_action

#         if not group or not action:
#             layout.label(text="No track selected")
#             return

#         track = get_or_create_track_props(action, group)

#         # ----------------------------------------
#         # Tag (sync with group name)
#         # ----------------------------------------
#         layout.prop(group, "name", text="Tag")

#         # ----------------------------------------
#         # Track properties
#         # ----------------------------------------
#         box = layout.box()
#         box.label(text="Track Properties")

#         box.prop(track, "interpolate")
#         box.prop(track, "reverse")

#         # Nullable sleep (like your system)
#         row = box.row(align=True)
#         row.prop(track, "has_sleep", text="")
#         sub = row.row()
#         sub.enabled = track.has_sleep
#         sub.prop(track, "sleep", text="Sleep")

#         # ----------------------------------------
#         # Derived
#         # ----------------------------------------
#         layout.separator()

#         num_frames = self.get_num_frames(group)
#         track.numframes = num_frames

#         layout.label(text=f"Num Frames: {num_frames}")

#     def get_num_frames(self, group):
#         max_frame = 0

#         for fc in group.channels:
#             if fc.keyframe_points:
#                 max_frame = max(max_frame, int(fc.keyframe_points[-1].co.x))

#         return max_frame

# def register():
#     bpy.types.Action.quail_tracks = CollectionProperty(type=QuailTrackProperties)
#     bpy.types.Action.quail_active_track = IntProperty(default=-1)


# def unregister():
#     del bpy.types.Action.quail_tracks
#     del bpy.types.Action.quail_active_track