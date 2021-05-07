"""
    MoreAPIs
    Copyright (C) 2021  HuajiMUR

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

import re
from MoreAPIs.StatusPing import StatusPing
from json import load
from psutil import Process
from parse import parse
from mcdreforged.api.all import *

_plugin_id = "more_apis"
_plugin_version = "0.0.2"
_mc_version = None
_events = {
    "death_message": PluginEvent(_plugin_id + ".death_message"),
    "player_made_advancement": PluginEvent(_plugin_id + "advancement"),
    "server_crashed": PluginEvent(_plugin_id + ".server_crashed"),
    "saved_game": PluginEvent(_plugin_id+".saved_game")
}
with open("plugins/MoreAPIs/death_message.json", "r", encoding="utf-8") as f:
    _death_messages: dict = load(f)

PLUGIN_METADATA = {
    "id": _plugin_id,
    "version": _plugin_version,
    "name": "More APIs",
    "author": "HuajiMUR",
    "dependencies": {"mcdreforged": ">=1.0.0"},
}


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
        if re.fullmatch(i,info.content):
            server.dispatch_event(
                _events["death_message"],
                (i,)
            )
            break
    
    # save_game event
    if info.content=="Saved the game":
        server.dispatch_event(
            _events['saved_game']
        )


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
def get_server_version(server: ServerInterface):
    if not server.is_server_startup:
        raise RuntimeError("Cannot invoke get_server_version before server startup")
    return _mc_version

# send server list ping
def send_server_list_ping(host:str="localhost",port:int=25565,timeout:int=5):
    response=StatusPing(host,port,timeout)
    return response.get_status()

# execute at
def execute_atas(server:ServerInterface,player:str,command:str):
    server.execute(f"execute as {player} at {player} {command}")