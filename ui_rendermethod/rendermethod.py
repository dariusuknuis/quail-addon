# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportCallIssue=false

import bpy
from bpy.types import Node
from bpy.props import EnumProperty, FloatProperty, FloatVectorProperty, StringProperty
from nodeitems_utils import NodeCategory, NodeItem, register_node_categories, unregister_node_categories
from nodeitems_builtins import SortedNodeCategory
import nodeitems_utils

class QuailRenderMethodNode(Node):
    """Custom Shader Node for Surface Dropdown"""
    bl_idname = "ShaderNodeQuailRenderMethod"
    bl_label = "Quail Render Method"
    bl_icon = 'SHADING_RENDERED'

    # Custom properties
    render_method:EnumProperty

    rgb_pen: FloatVectorProperty

    brightness: FloatProperty

    scaled_ambient: FloatProperty

    sprite: StringProperty

    def init(self, context):
        """Create the node inputs and outputs"""
        self.inputs.new("NodeSocketColor", "RGB PEN")
        self.inputs.new("NodeSocketFloat", "Brightness")
        self.inputs.new("NodeSocketFloat", "Scaled Ambient")
        self.outputs.new("NodeSocketShader", "Shader Output")
        self.render_method.name="Render Method",
        self.render_method.description="Select the rendering method",
        self.render_method.items=[
                ("METHOD1", "Method 1", "First rendering method"),
                ("METHOD2", "Method 2", "Second rendering method"),
                ("METHOD3", "Method 3", "Third rendering method")
            ],
        self.render_method.default="METHOD1"
        self.sprite = StringProperty(
            name="Sprite",
            description="Reference to a sprite texture",
            default=""
        )
        self.scaled_ambient = FloatProperty(
            name="Scaled Ambient",
            description="Control ambient scaling",
            default=0.5,
            min=0.0,
            max=1.0
        )
        self.brightness = FloatProperty(
            name="Brightness",
            description="Control brightness",
            default=1.0,
            min=0.0,
            max=10.0
        )
        self.rgb_pen = FloatVectorProperty(
            name="RGB PEN",
            description="Color picker",
            subtype='COLOR',
            default=(1.0, 1.0, 1.0, 1.0),
            size=4
        )

    def draw_buttons(self, context, layout):
        """Draw UI elements in the node"""
        layout.prop(self, "render_method", text="Render Method")
        layout.prop(self, "rgb_pen", text="RGB Pen")
        layout.prop(self, "brightness", text="Brightness")
        layout.prop(self, "scaled_ambient", text="Scaled Ambient")
        layout.prop(self, "sprite", text="Sprite Path")

# Define the node category correctly
class QuailNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ShaderNodeTree'


# Registering the node class and categories
def register():
    # bpy.utils.register_class(QuailRenderMethodNode)  # Register the node class

    node_categories = [
        NodeCategory("Quail", "Custom Nodes", items=[
            NodeItem("ShaderNodeQuailRenderMethod")
        ])
    ]

    nodeitems_utils.register_node_categories("Quail", node_categories)

def unregister():
    unregister_node_categories("Quail")
    bpy.utils.unregister_class(QuailRenderMethodNode)  # Unregister the node class

if __name__ == "__main__":
    register()
