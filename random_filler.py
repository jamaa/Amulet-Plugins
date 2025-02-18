from typing import TYPE_CHECKING
import amulet_nbt
import wx
import wx.grid
from amulet.api.block import Block
from amulet_map_editor.api.wx.ui.block_select import BlockDefine
from amulet_map_editor.programs.edit.api.behaviour import BlockSelectionBehaviour

from amulet_map_editor.programs.edit.api.operations import DefaultOperationUI
from amulet_map_editor.api.wx.ui.block_select.properties import EVT_PROPERTIES_CHANGE
from amulet_map_editor.programs.edit.api.events import EVT_SELECTION_CHANGE

if TYPE_CHECKING:
    from amulet.api.level import BaseLevel
    from amulet_map_editor.programs.edit.api.canvas import EditCanvas


class RandomFill(wx.Panel, DefaultOperationUI):

    def __init__(
            self,
            parent: wx.Window,
            canvas: "EditCanvas",
            world: "BaseLevel",
            options_path: str,

    ):
        wx.Panel.__init__(self, parent)
        DefaultOperationUI.__init__(self, parent, canvas, world, options_path)
        self.options = self._load_options({})
        self.toggle = True
        self.Freeze()
        self.arr = {}
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)
        self.saveload = wx.BoxSizer(wx.HORIZONTAL)
        self.snbt_text_data = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_BESTWRAP, size=(322, 300))

        self._run_buttonA = wx.Button(self, label="Apply")
        self._run_buttonA.Bind(wx.EVT_BUTTON, self._apply_changes)

        self.open_block_window = wx.Button(self, label="Select Blocks")
        self.open_block_window.Bind(wx.EVT_BUTTON, self.block_list)

        self.saveload.Add(self._run_buttonA, 0, wx.LEFT, 10)

        self._sizer.Add(self.open_block_window, 0, wx.LEFT, 70)
        self._sizer.Add(self.snbt_text_data)
        self._sizer.Fit(self)
        self.toggle_count = 0
        self.Layout()
        self.Thaw()

    def set_block(self, event, data ,toggle):

        x,y,z =self.canvas.selection.selection_group.min
        block, enty = self.world.get_version_block(x,y,z,self.canvas.dimension,
                (self.world.level_wrapper.platform, self.world.level_wrapper.version))# self.canvas.selection.selection_group.min
        the_snbt = f"{block.namespaced_name}" \
                   f"\n{amulet_nbt.from_snbt(str(block.properties)).to_snbt(1)}"
        try:
            e_block_u = self.world.get_block(x,y,z,self.canvas.dimension).extra_blocks[0]
            pf, vb = self.world.level_wrapper.platform, self.world.level_wrapper.version

            e_block =  self.world.translation_manager.get_version(pf, vb).block.from_universal(e_block_u)[0]
            the_extra_snbt = f"\n<Extra_Block>\n{e_block.namespaced_name}\n" \
                             f"{amulet_nbt.from_snbt(str(e_block.properties)).to_snbt(1)}"
            eblock =  the_extra_snbt
            self.extra_block_prop.SetValue(eblock)
        except:
            the_e = f"\n<Extra_Block>" \
                       f"\nNone"
            self.extra_block_prop.SetValue(the_snbt)
        self.block_prop.SetValue(the_snbt)
        data.block = block






    def get_block(self, event, data, toggle):
        the_snbt = f"{data.block.namespaced_name}" \
                   f"||{amulet_nbt.from_snbt(str(data.properties)).to_snbt()}"
        self.block_prop.SetValue(the_snbt)







    def block_list(self, _):
        self.window = wx.Frame(self.parent, title="Add Blocks", size=(550, 570),
                          style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.window.Centre()
        self.w_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.window.SetSizer(self.w_sizer)
        # if self.univeral_mode.GetValue():
        #     self.chosen_platform = "universal"
        #     self.chosen_name_space = "universal_minecraft"
        if True:

            self.chosen_platform = self.world.level_wrapper.platform
            self.chosen_name_space = "minecraft"
        self._block_define = BlockDefine(
            self.window,
            self.world.translation_manager,
            wx.VERTICAL,
            force_blockstate=False,
            #platform="universal",
            namespace=self.chosen_name_space,
            *(self.options.get("fill_block_options", []) or [self.chosen_platform]),
              #*(self.options.get("fill_block_options", []) or [self.world.level_wrapper.platform]),
            show_pick_block=False
        )

        self._block_define.Bind(EVT_PROPERTIES_CHANGE,lambda event:  self.get_block(event, self._block_define, True))

        self.canvas.Bind(EVT_SELECTION_CHANGE, lambda event: self.set_block(event, self._block_define, False))
        self.block_prop = wx.TextCtrl(
            self.window, style=wx.TE_MULTILINE | wx.TE_BESTWRAP, size=(300, 520)
        )


        self.copy_to_find_button = wx.Button(self.window, label="Add")


        self.copy_to_find_button.Bind(wx.EVT_BUTTON, self.copy_to_find)

        self.grid_top_ew = wx.GridSizer(1, 1, 0, 0)
        self.grid_top_ew.Add(self.copy_to_find_button, 0, wx.LEFT, 20)

        self.grid_box_pop = wx.BoxSizer(wx.VERTICAL)

        self.grid_box_pop.Add(self.grid_top_ew)

        self.grid_box_pop.Add(self.block_prop)



        #button.Bind(wx.EVT_BUTTON, lambda event: self.get_block(event, _block_define) )
        self.grid_left = wx.GridSizer(2,1,-470,0)

        self.grid_left.Add(self._block_define)
        self.w_sizer.Add(self.grid_left)
        self.w_sizer.Add(self.grid_box_pop )
        self._block_define.Fit()
        self._block_define.Layout()
        self.grid_box_pop.Layout()

        self.window.Bind(wx.EVT_CLOSE, lambda event: self.OnClose(event))
        self.window.Enable()

        self.window.Show(True)
    def copy_find_select(self, _):
        self.textSearch.SetValue(self._block_define.block_name + " ")

    def copy_to_find(self,_):

        self.snbt_text_data.SetValue(self.snbt_text_data.GetValue() +
                            self.block_prop.GetValue() +'\n')



    def OnClose(self, event):
        self.canvas.Unbind(EVT_SELECTION_CHANGE)
        self.window.Show(False)

    def block(self, block):
        self._picker.set_namespace(block.namespace)
        self._picker.set_name(block.base_name)
        self._update_properties()
        self.properties = block.properties

    def bind_events(self):
        super().bind_events()
        self._selection.bind_events()
        self._selection.enable()

    def enable(self):
        self._selection = BlockSelectionBehaviour(self.canvas)
        self._selection.enable()

    def _apply_changes(self, _):
        self.canvas.run_operation(self._run_job)

    def _run_job(self):
        import random
        platform = self.world.level_wrapper.platform
        version = self.world.level_wrapper.version
        data = self.snbt_text_data.GetValue()

        data = data.split("\n")

        blocks = []
        for c in range(0,len(data)):
            if "||" not in data[c]:
                break
            blks, props = data[c].split("||")
            blk_space,blk_name = blks.split(":")
            blk = Block(blk_space,blk_name,dict(amulet_nbt.from_snbt(props)))
            blocks.append(blk)

        selection = [x for x in self.canvas.selection.selection_group.blocks]
        random.shuffle(selection)
        random.shuffle(blocks)
        rng_inx = 0
        for s in range(0,len(selection),len(blocks)):
            for b in range(len(blocks)):
                if rng_inx > len(selection)-1:
                    break
                x,y,z = selection[rng_inx][0],selection[rng_inx][1],selection[rng_inx][2]
                rng_inx +=1
                self.world.set_version_block(x,y,z,self.canvas.dimension,(platform,version),blocks[b],None)


        #for blk in blocks:







export = dict(name="Random FIller v1.00", operation=RandomFill)  # By PremiereHell
