import struct
import collections
from typing import TYPE_CHECKING, Type, Any, Callable, Tuple,  BinaryIO, Optional
from amulet_map_editor.programs.edit.api.operations import DefaultOperationUI
from amulet_map_editor.programs.edit.api.behaviour import BlockSelectionBehaviour
import wx
import re
from amulet_map_editor.api.wx.ui.base_select import BaseSelect
from amulet.api.block import Block
if TYPE_CHECKING:
    from amulet.api.level import BaseLevel
    from amulet_map_editor.programs.edit.api.canvas import EditCanvas

class PluginClassName(wx.Panel, DefaultOperationUI):
    def __init__(
            self,
            parent: wx.Window,
            canvas: "EditCanvas",
            world: "BaseLevel",
            options_path: str,
    ):
        platform = world.level_wrapper.platform
        world_version = world.level_wrapper.version
        plat = (platform, world_version)

        wx.Panel.__init__(self, parent)
        DefaultOperationUI.__init__(self, parent, canvas, world, options_path)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.text = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(280, 650), pos=(30,30))
        self.test = wx.Button(self, label="Get Materials count", pos=(0,0))
        self.test.Bind(wx.EVT_BUTTON, self._run_count)
        self._sizer.Add(self.test)
        self._sizer.Add(self.text)

    def _run_count(self, _):

        # list of block properties to consider
        properties = [
            "material",
            "color",
            "plant_type",
            "stripped",
        ]

        block_version = self.world.level_wrapper.version

        block_platform = "universal"

        materials = collections.defaultdict(int)
        selection = self.canvas.selection.selection_group.selection_boxes

        for g in selection:
            for b in g:
                block, ent = self.world.get_version_block(b[0],b[1],b[2],self.canvas.dimension, (block_platform, block_version))

                name = block.base_name

                if isinstance(block, Block):

                    # collect block properties
                    block_props = {}
                    for prop_name in properties:
                        if prop_name in block.properties:
                            block_props[prop_name] = block.properties[prop_name]

                    if len(block_props) > 0:
                        # format properties as a nice string and add it to the name
                        name += " {"
                        name += ", ".join([f"{prop}: {value}" for prop, value in block_props.items()])
                        name += "}"
                
                else:
                    # block entities and entities have no properties
                    pass

                # increment counter
                materials[name] += 1

        # output materials sorted alphabetically
        text = ''
        for name in sorted(list(materials.keys())):
            text += f"{name}: {materials[name]}\n"

        self.text.SetValue(text)

    def bind_events(self):
        super().bind_events()
        self._selection.bind_events()
        self._selection.enable()

    def enable(self):
        self._selection = BlockSelectionBehaviour(self.canvas)
        self._selection.enable()
    pass


# simple export options.
export = dict(name="A Materials Counter", operation=PluginClassName) # by PremiereHell