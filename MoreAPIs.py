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

<<<<<<< HEAD
from MoreAPIs.StatusPing import StatusPing
from psutil import Process
from parse import parse
from os import path

import shutil
import re

=======
import re

from json import load
from psutil import Process
from parse import parse
>>>>>>> a0256b9a5e0eef0b925b2097001b50ab3bc05c24
from ruamel import yaml

from mcdreforged.api.all import *

from MoreAPIs.StatusPing import StatusPing

_plugin_id = "more_apis"
_plugin_version = "0.0.2"
_mc_version = None
_events = {
    "death_message": PluginEvent(_plugin_id + ".death_message"),
    "player_made_advancement": PluginEvent(_plugin_id + "advancement"),
    "server_crashed": PluginEvent(_plugin_id + ".server_crashed"),
    "saved_game": PluginEvent(_plugin_id+".saved_game")
}
_death_messages={}

PLUGIN_METADATA = {
    "id": _plugin_id,
    "version": _plugin_version,
    "name": "More APIs",
    "author": "HuajiMUR",
    "dependencies": {"mcdreforged": ">=1.0.0"},
}


# Only for move death_message.yml to data folder
def on_load(server:ServerInterface,old):
    global _death_messages
    if path.exists(path.join(server.get_plugin_file_path(_plugin_id),"..","MoreAPIs","death_message.yml")):
        shutil.move(path.join(server.get_plugin_file_path(_plugin_id),"..","MoreAPIs","death_message.yml"),path.join(server.get_data_folder,"death_message.yml"))
    if not path.exists(path.join(server.get_data_folder,"death_message.yml")):
        server.logger.error("Can't find death_message.yml")
        server.unload_plugin(_plugin_id)
    with open(path.join(server.get_data_folder,"death_message.yml"),"r",encoding="utf-8") as f:
        _death_messages=yaml.safe_load(f)


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
    
    # saved_game event
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
def get_server_version(server: ServerInterface) -> str:
    if not server.is_server_startup:
        raise RuntimeError("Cannot invoke get_server_version before server startup")
    return _mc_version

# send server list ping
def send_server_list_ping(host:str="localhost",port:int=25565,timeout:int=5) -> dict:
    response=StatusPing(host,port,timeout)
    return response.get_status()

# execute at
def execute_at(server:ServerInterface,player:str,command:str):
    server.execute(f"execute as {player} at {player} {command}")

<<<<<<< HEAD
# get uuid
def get_uuid(player:str):
    with open("config.yml","r",encoding="utf-8") as f:
        mcdr_cfg=yaml.safe_load(f)
    server_dir=mcdr_cfg['server']
=======
# get mcdr config
def get_mcdr_config() -> dict:
    with open("config.yml","r",encoding="utf-8") as f:
        return yaml.safe_load(f)
>>>>>>> a0256b9a5e0eef0b925b2097001b50ab3bc05c24
