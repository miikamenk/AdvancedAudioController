# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.DeckManagement.InputIdentifier import Input, InputEvent, InputIdentifier

# Import python modules
import os
from loguru import logger as log

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import GObject, Gtk, Adw

class Volume(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.has_configuration = True

    def on_tick(self):
        settings = self.get_settings()
        icon_path = os.path.join(self.plugin_base.PATH, "assets", "vts.png")
        self.set_media(media_path=icon_path, size=0.75)

    def event_callback(self, event: InputEvent, data: dict = None):
        if event == Input.Key.Events.SHORT_UP:
            self.on_key_down()
        elif event == Input.Key.Events.HOLD_START or event == Input.Dial.Events.HOLD_START:
            self.on_key_hold_start()
        elif event == Input.Dial.Events.TURN_CW:
            self.on_dial_turn(+1)
        elif event == Input.Dial.Events.TURN_CCW:
            self.on_dial_turn(-1)
        elif event == Input.Dial.Events.SHORT_UP:
            self.on_key_down()
        
    def on_ready(self) -> None:
        self.on_tick()

    def on_key_down(self) -> None:

    def on_key_hold_start(self) -> None:
    
    def get_config_rows(self) -> list:
        self.player_model = Gtk.StringList()
        self.player_row = Adw.ComboRow(title=self.plugin_base.lm.get("actions.volume.player"), subtitle=self.plugin_base.lm.get("actions.volume.player.subtitle"), model=self.hotkey_model)
        self.player_row.set_enable_search(True)

        self.load_player_model()

        self.player_row.connect("notify::selected-item", self.on_player_change)

        self.load_config_settings()

        return [self.player_row]

    def load_player_model(self):
        players = self.plugin_base.getPlayers()
        for i in range(self.player_model.get_n_items()):
            self.player_model.remove(0)
        for player in players:
            self.player_model.append(player)
 
    def load_config_settings(self):
        settings = self.get_settings()
        log.info(f"Loaded settings: {settings}")
        if settings == None:
            return
        player = settings.get("player")
        for i, player_model in enumerate(self.player_model):
            if player_model.get_string() == player:
                self.player_row.set_selected(i)
                return
 
    def on_player_change(self, combo, *args):
        hotkey = combo.get_selected_item().get_string()

        settings = self.get_settings()
        settings["hotkey"] = hotkey 

        self.set_settings(settings)
