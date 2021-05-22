"""
    MoreAPIs
    Copyright (C) 2021  Huaji_MUR233

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


from psutil import Process
from parse import parse
from os import path

import uuid
import re

from ruamel import yaml
import javaproperties
import requests

from MoreAPIs.StatusPing import StatusPing

from mcdreforged.api.all import *


_plugin_id = "more_apis"
_plugin_version = "0.0.4"
_mc_version = None
_events = {
    "death_message": PluginEvent(_plugin_id + ".death_message"),
    "player_made_advancement": PluginEvent(_plugin_id + "advancement"),
    "server_crashed": PluginEvent(_plugin_id + ".server_crashed"),
    "saved_game": PluginEvent(_plugin_id + ".saved_game"),
}
_death_messages = {}
_config_path = path.join(".", "config", _plugin_id, "config.yml")
_default_cfg = """# MoreAPIs config
# online-mode (default: true)
online-mode: true
"""

PLUGIN_METADATA = {
    "id": _plugin_id,
    "version": _plugin_version,
    "name": "More APIs",
    "author": "HuajiMUR",
    "dependencies": {"mcdreforged": ">=1.0.0"},
}


def on_load(server: ServerInterface, old):
    global _death_messages
    if not path.exists(path.join(server.get_data_folder(), "death_messages.yml")):
        server.logger.warn("Downloading death_message.yml...")
        response = requests.get(
            "https://hub.fastgit.org/HuajiMUR233/MoreAPIs/releases/download/DeathMsgs/death_messages.yml"
        )
        with open(path.join(server.get_data_folder(), "death_messages.yml"), "wb") as f:
            f.write(response.content)
    with open(
        path.join(server.get_data_folder(), "death_messages.yml"), "r", encoding="utf-8"
    ) as f:
        _death_messages = yaml.safe_load(f)
    if not path.exists(_config_path):
        with open(_config_path, "w", encoding="utf-8") as f:
            f.write(_default_cfg)


def _get_online_uuid(player: str):
    api_url = "https://api.mojang.com/users/profiles/minecraft/"
    response = requests.get(api_url + player)
    if response != 200:
        return None
    else:
        return response.json["id"]


def _get_offline_uuid(player: str):
    return uuid.uuid3(player)


@new_thread
def on_info(server: ServerInterface, info: Info):
    # :)
    if info.is_user:
        return

    # ========== Events ==========

    # server_crashed event
    if info.logging_level == "ERROR" and info.content.startswith(
        "This crash report has been saved to:"
    ):
        path = parse("This crash report has been saved to: {path}", info.content)[
            "path"
        ]
        server.logger.warning(
            "A Crash Report was detected, the server may have crashed"
        )
        server.dispatch_event(_events["server_crashed"], (path,))

    # player_made_advancement event
    adv_parsed = parse("{player} has {action} [{advancement`}]", info.content)

    if (adv_parsed["player"] and adv_parsed["advancement"] is not None) and adv_parsed[
        "action"
    ] in ["made the advancement", "completed the challenge", "reached the goal"]:
        server.dispatch_event(
            _events["player_made_advancement"],
            (adv_parsed["player"], adv_parsed["advancement"]),
        )
    # death_message event
    for i in _death_messages["msgs"]:
        if re.fullmatch(i, info.content):
            server.dispatch_event(_events["death_message"], (i,))
            break

    # saved_game event
    if info.content == "Saved the game":
        server.dispatch_event(_events["saved_game"])

    # ========== API ==========
    # Get the server version
    mcversion_parsed = parse(
        "Starting minecraft server version {version}", info.content
    )["version"]
    if mcversion_parsed is not None:
        _mc_version = mcversion_parsed


# kill server
def kill_server(server: ServerInterface):
    server_process = Process(server.get_server_pid)
    server_process.kill()


# get server version
def get_server_version(server: ServerInterface) -> str:
    if not server.is_server_startup:
        raise RuntimeError("Cannot invoke get_server_version before server startup")
    return _mc_version


# send server list ping
def send_server_list_ping(
    host: str = "localhost", port: int = 25565, timeout: int = 5
) -> dict:
    response = StatusPing(host, port, timeout)
    return response.get_status()


# execute at
def execute_at(server: ServerInterface, player: str, command: str):
    server.execute(f"execute as {player} at {player} {command}")


# get mcdr config
def get_mcdr_config() -> dict:
    with open("config.yml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# get server.properties
def get_server_properties() -> dict:
    server_dir = get_mcdr_config()["working_directory"]
    with open(path.join(server_dir, "server.properties"), "r", encoding="utf-8") as f:
        return javaproperties.load(f)


# get uuid
def get_player_uuid(player: str, mode=None):
    with open(_config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if mode:
        player_uuid = _get_online_uuid(player)
        if player_uuid is None:
            raise f"Can't get {player}'s uuid"
    else:
        return _get_offline_uuid(player)

    if cfg["online-mode"] is True:
        player_uuid = _get_online_uuid(player)
        if player_uuid is None:
            raise f"Can't get {player}'s uuid"
        return player_uuid
    elif cfg["online-mode"] is False:
        return _get_offline_uuid(player)

    server_cfg = get_server_properties()
    if server_cfg["online-mode"]:
        player_uuid = _get_online_uuid(player)
        if player_uuid is None:
            raise f"Can't get {player}'s uuid"
        return player_uuid
    return _get_offline_uuid(player)
