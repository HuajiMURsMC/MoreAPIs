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

import time
import re

from ruamel import yaml
import javaproperties
import requests

from MoreAPIs.StatusPing import StatusPing

from mcdreforged.api.all import *


_plugin_id = "more_apis"
_plugin_version = "0.0.6"
_mc_version = None
_events = {
    "death_message": PluginEvent(_plugin_id + ".death_message"),
    "player_made_advancement": PluginEvent(_plugin_id + "advancement"),
    "server_crashed": PluginEvent(_plugin_id + ".server_crashed"),
    "saved_game": PluginEvent(_plugin_id + ".saved_game"),
}
_death_messages = {}

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
    for action in [
        "made the advancement",
        "completed the challenge",
        "reached the goal",
    ]:
        match = re.fullmatch(r"\w{1,16} has %s \[.+\]" % action, info.content)
        if match is not None:
            player, rest = info.content.split(" ", 1)
            adv = re.search(r"(?<=%s \[).+(?=\])" % action, rest).group()
            server.dispatch_event(_events["player_made_advancement"], (player, adv))

    # death_message event
    for i in _death_messages["msgs"]:
        if re.fullmatch(i, info.content):
            server.dispatch_event(_events["death_message"], (i,))
            break

    # saved_game event
    if info.content == "Saved the game":
        server.dispatch_event(_events["saved_game"])

    # ========== API ==========
    # get minecraft version
    if (
        re.fullmatch(r"Starting minecraft server version /[a-z0-9.]/", info.content)
        is not None
    ):
        _mc_version = re.search(
            r"Starting minecraft server version /[a-z0-9.]/", info.content
        ).group()


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


def get_tps(server: ServerInterface, secs: int = 1) -> float:
    if not server.is_rcon_running():
        raise "Need open MCDR's RCON future"
    server.rcon_query("debug start")
    time.sleep(secs)
    response = server.rcon_query("debug stop")
    return float(parse("Stopped debug profiling after {tps}", response)["tps"])
