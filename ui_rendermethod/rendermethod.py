# pyright: basic, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportCallIssue=false

import bpy
from bpy.types import Node, ShaderNodeTree
from bpy.props import EnumProperty, FloatProperty, FloatVectorProperty, StringProperty
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories
from nodeitems_builtins import ShaderNodeCategory

class QuailRenderMethodNode(Node):
    """Custom Shader Node for Surface Dropdown"""
    bl_idname = "ShaderNodeQuailRenderMethod"
    bl_label = "Quail Render Method"
    bl_icon = 'SHADING_RENDERED'
    bl_description = "Custom Quail Render Method"

    # Properties must be defined at the class level
    render_method: EnumProperty(
        name="Render Method",
        description="Select the rendering method",
        items=[
            ("METHOD1", "Method 1", "First rendering method"),
            ("METHOD2", "Method 2", "Second rendering method"),
            ("METHOD3", "Method 3", "Third rendering method")
        ],
        default="METHOD1"
    )

    rgb_pen: FloatVectorProperty(
        name="RGB PEN",
        description="Color picker",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0, 1.0),
        size=4
    )

    brightness: FloatProperty(
        name="Brightness",
        description="Control brightness",
        default=1.0,
        min=0.0,
        max=10.0
    )

    scaled_ambient: FloatProperty(
        name="Scaled Ambient",
        description="Control ambient scaling",
        default=0.5,
        min=0.0,
        max=1.0
    )

    sprite: StringProperty(
        name="Sprite",
        description="Reference to a sprite texture",
        default=""
    )

    def init(self, context):
        """Create the node inputs and outputs"""
        self.inputs.new("NodeSocketColor", "RGB PEN")
        self.inputs.new("NodeSocketFloat", "Brightness")
        self.inputs.new("NodeSocketFloat", "Scaled Ambient")
        self.outputs.new("NodeSocketShader", "Shader Output")

    def draw_buttons(self, context, layout):
        """Draw UI elements in the node"""
        layout.prop(self, "render_method", text="Render Method")
        layout.prop(self, "rgb_pen", text="RGB Pen")
        layout.prop(self, "brightness", text="Brightness")
        layout.prop(self, "scaled_ambient", text="Scaled Ambient")
        layout.prop(self, "sprite", text="Sprite Path")

