# Copyright (c) 2018-2021, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#

from abc import abstractmethod
import omni.ext
import omni.ui as ui
from omni.kit.menu.utils import add_menu_items, remove_menu_items, MenuItemDescription
import weakref
from omni.isaac.ui.ui_utils import setup_ui_headers, get_style, btn_builder, scrolling_frame_builder
import asyncio
from omni.isaac.rift.base_sample import BaseSample
from omni.isaac.core import World

class BaseSampleExtension(omni.ext.IExt):
    def on_startup(self, ext_id: str):
        self._menu_items = None
        self._buttons = None
        self._ext_id = ext_id
        self._sample = None
        self._extra_frames = []
        return

    def start_extension(
        self,
        menu_name: str,
        submenu_name: str,
        name: str,
        title: str,
        doc_link: str,
        overview: str,
        file_path: str,
        sample=None,
        number_of_extra_frames=1,
        window_width=350,
    ):
        if sample is None:
            self._sample = BaseSample()
        else:
            self._sample = sample

        menu_items = [MenuItemDescription(name=name, onclick_fn=lambda a=weakref.proxy(self): a._menu_callback())]
        if menu_name == "" or menu_name is None:
            self._menu_items = menu_items
        elif submenu_name == "" or submenu_name is None:
            self._menu_items = [MenuItemDescription(name=menu_name, sub_menu=menu_items)]
        else:
            self._menu_items = [
                MenuItemDescription(
                    name=menu_name, sub_menu=[MenuItemDescription(name=submenu_name, sub_menu=menu_items)]
                )
            ]
        add_menu_items(self._menu_items, "Isaac Examples")

        self._buttons = dict()
        self._build_ui(
            name=name,
            title=title,
            doc_link=doc_link,
            overview=overview,
            file_path=file_path,
            number_of_extra_frames=number_of_extra_frames,
            window_width=window_width,
        )
        if self.get_world() is not None:
            self._on_load_world()

        return

    @property
    def sample(self):
        return self._sample

    def get_frame(self, index):
        if index >= len(self._extra_frames):
            raise Exception("there were {} extra frames created only".format(len(self._extra_frames)))
        return self._extra_frames[index]

    def get_world(self):
        return World.instance()

    def get_buttons(self):
        return self._buttons

    def _build_ui(self, name, title, doc_link, overview, file_path, number_of_extra_frames, window_width):
        self._window = omni.ui.Window(
            name, width=window_width, height=0, visible=True, dockPreference=ui.DockPreference.RIGHT_BOTTOM
        )
        with self._window.frame:
            with ui.VStack(spacing=5, height=0):
                setup_ui_headers(self._ext_id, file_path, title, doc_link, overview)
                self._controls_frame = ui.CollapsableFrame(
                    title="World Controls",
                    width=ui.Fraction(1),
                    height=0,
                    collapsed=False,
                    style=get_style(),
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                )
                with ui.VStack(style=get_style(), spacing=5, height=0):
                    for i in range(number_of_extra_frames):
                        self._extra_frames.append(
                            ui.CollapsableFrame(
                                title="",
                                width=ui.Fraction(0.33),
                                height=0,
                                visible=False,
                                collapsed=False,
                                style=get_style(),
                                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_AS_NEEDED,
                                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                            )
                        )
                with self._controls_frame:
                    with ui.VStack(style=get_style(), spacing=5, height=0):
                        dict = {
                            "label": "Load World",
                            "type": "button",
                            "text": "Load",
                            "tooltip": "Load World and Task",
                            "on_clicked_fn": self._on_load_world,
                        }
                        self._buttons["Load World"] = btn_builder(**dict)
                        self._buttons["Load World"].enabled = True
                        dict = {
                            "label": "Reset",
                            "type": "button",
                            "text": "Reset",
                            "tooltip": "Reset robot and environment",
                            "on_clicked_fn": self._on_reset,
                        }
                        self._buttons["Reset"] = btn_builder(**dict)
                        self._buttons["Reset"].enabled = False
                        dict = {
                            "label": "Clear",
                            "type": "button",
                            "text": "Clear",
                            "tooltip": "Clear the full environment",
                            "on_clicked_fn": self._on_clear,
                        }
                        self._buttons["Clear"] = btn_builder(**dict)
                        self._buttons["Clear"].enabled = True
                        dict = {
                            "label": "Load Game Piece",
                            "type": "button",
                            "text": "Game Piece",
                            "tooltip": "Populate the substation with game pieces",
                            "on_clicked_fn": self._on_load_game_piece,
                        }
                        self._buttons["Load Game Piece"] = btn_builder(**dict)
                        self._buttons["Load Game Piece"].enabled = True
        return

    def _set_button_tooltip(self, button_name, tool_tip):
        self._buttons[button_name].set_tooltip(tool_tip)
        return

    def _on_load_world(self):
        async def _on_load_world_async():
            await self._sample.load_world_async()
            await omni.kit.app.get_app().next_update_async()
            self._sample._world.add_stage_callback("stage_event_1", self.on_stage_event)
            self._enable_all_buttons(True)
            self._buttons["Load World"].enabled = False
            self.post_load_button_event()
            self._sample._world.add_timeline_callback("stop_reset_event", self._reset_on_stop_event)

        asyncio.ensure_future(_on_load_world_async())
        return


    def _on_load_game_piece(self):
        async def _on_load_game_piece_async():
            await self._sample.load_game_piece_async()
            await omni.kit.app.get_app().next_update_async()
            # self._sample._world.add_stage_callback("stage_event_2", self.on_stage_event)
            # self.post_load_game_piece_button_event()
            # self._sample._world.add_timeline_callback("stop_reset_event_2", self._reset_on_stop_event)

        asyncio.ensure_future(_on_load_game_piece_async())
        return

    def _on_reset(self):
        async def _on_reset_async():
            await self._sample.reset_async()
            await omni.kit.app.get_app().next_update_async()
            self.post_reset_button_event()

        asyncio.ensure_future(_on_reset_async())
        return

    def _on_clear(self):
        async def _on_clear_async():
            await self._sample.clear_async()
            await omni.kit.app.get_app().next_update_async()
            self.post_clear_button_event()
            self._buttons["Load World"].enabled = True

        asyncio.ensure_future(_on_clear_async())
        return
    
    @abstractmethod
    def post_load_game_piece_button_event(self):
        return

    @abstractmethod
    def post_reset_button_event(self):
        return

    @abstractmethod
    def post_load_button_event(self):
        return

    @abstractmethod
    def post_clear_button_event(self):
        return

    def _enable_all_buttons(self, flag):
        for btn_name, btn in self._buttons.items():
            if isinstance(btn, omni.ui._ui.Button):
                btn.enabled = flag
        return

    def _menu_callback(self):
        self._window.visible = not self._window.visible
        return

    def _on_window(self, status):
        # if status:
        return

    def on_shutdown(self):
        self._extra_frames = []
        if self._sample._world is not None:
            self._sample._world_cleanup()
        if self._menu_items is not None:
            self._sample_window_cleanup()
        if self._buttons is not None:
            self._buttons["Load World"].enabled = True
            self._enable_all_buttons(False)
        self.shutdown_cleanup()
        return

    def shutdown_cleanup(self):
        return

    def _sample_window_cleanup(self):
        remove_menu_items(self._menu_items, "Isaac Examples")
        self._window = None
        self._menu_items = None
        self._buttons = None
        return

    def on_stage_event(self, event):
        if event.type == int(omni.usd.StageEventType.CLOSED):
            if World.instance() is not None:
                self.sample._world_cleanup()
                self.sample._world.clear_instance()
                if hasattr(self, "_buttons"):
                    if self._buttons is not None:
                        self._enable_all_buttons(False)
                        self._buttons["Load World"].enabled = True
        return

    def _reset_on_stop_event(self, e):
        if e.type == int(omni.timeline.TimelineEventType.STOP):
            self._buttons["Load World"].enabled = False
            self._buttons["Reset"].enabled = True
            self.post_clear_button_event()
        return
