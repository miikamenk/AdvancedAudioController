# Import StreamController modules
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport

import sys
import os
import dbus
from loguru import logger as log

# Add plugin to sys.paths
sys.path.append(os.path.dirname(__file__))

# Import actions
from .actions.Volume.Volume import Volume 

class AdvancedAudioControl(PluginBase):
    def __init__(self):
        super().__init__()

        self.session_bus = dbus.SessionBus()
        self.mpris_players = []

        self.lm = self.locale_manager

        ## Register actions
        self.volume_holder = ActionHolder(
            plugin_base = self,
            action_base = Volume,
            action_id = "com_miikamenk_advanced_audio::Volume", # Change this to your own plugin id
            action_name = self.lm.get("actions.volume.name"),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED
            }
        )
        self.add_action_holder(self.volume_holder)

    def updatePlayers(self):
        mpris_players = []
        try:
            for i in self.session_bus.list_names():
                if str(i)[:22] == "org.mpris.MediaPlayer2":
                    mpris_players += [self.session_bus.get_object(i, '/org/mpris/MediaPlayer2')]
        except Exception as e:
            log.error("Could not connect to D-Bus session bus. Is the D-Bus daemon running?", e)
            return
        self.mpris_players = mpris_players

    def getPlayer(self) -> string:
        names = []
        try:
            for player in self.mpris_players:
                properties = dbus.Interface(player, 'org.freedesktop.DBus.Properties')
                name = properties.Get('org.mpris.MediaPlayer2', 'Identity')
                if name in names:
                    continue
                names.append(str(name))
        except Exception as e:
            log.error("Could not connect to D-Bus session bus. Is the D-Bus daemon running?", e)
        return names

    def getMatchingIfaces(self, player_name: str = None) -> list[dbus.Interface]:
        self.update_players()
        """
        Retrieves a list of dbus interfaces that match the given player name.

        Args:
            player_name (str, optional): The name of the player to match. Defaults to None.
            If not provided, all interfaces will be returned.

        Returns:
            list[dbus.Interface]: A list of dbus interfaces that match the given player name.
        """
        ifaces = []
        for player in self.mpris_players:
            properties = dbus.Interface(player, 'org.freedesktop.DBus.Properties')
            try:
                if player_name in [None, "", properties.Get('org.mpris.MediaPlayer2', 'Identity')]:
                    iface = dbus.Interface(player, 'org.mpris.MediaPlayer2.Player')
                    ifaces.append(iface)
            except dbus.exceptions.DBusException as e:
                log.warning(e)
        return ifaces
