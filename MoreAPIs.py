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


from typing import Any
from psutil import Process

import time
import re
import os

from ruamel import yaml

import javaproperties
import parse

from .More_APIs.StatusPing import StatusPing

from mcdreforged.api.all import *


_plugin_id = "more_apis"
_plugin_version = "0.1.1-dev"
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
    with open(
        os.path.join(
            server.get_plugin_file_path(_plugin_id),
            "..",
            "More_APIs",
            "death_messages.yml",
        ),
        "r",
        encoding="utf-8",
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
        path = parse.parse("This crash report has been saved to: {path}", info.content)[
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
            server.dispatch_event(_events["death_message"], (info.content,))
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


class MoreAPIs():
    def __init__(self, server: ServerInterface):
        self.server = server

    def kill_server(self) -> Any:
        server_process = Process(self.server.get_server_pid)
        server_process.kill()

    def get_server_version(self) -> str:
        if not self.server.is_server_startup:
            raise RuntimeError("Cannot invoke get_server_version before server startup")
        return _mc_version

    def send_server_list_ping(
        host: str = "localhost", port: int = 25565, timeout: int = 5
    ) -> dict:
        response = StatusPing(host, port, timeout)
        return response.get_status()

    def execute_at(self, player: str, command: str):
        self.server.execute(f"execute as {player} at {player} {command}")

    def get_mcdr_config(self) -> dict:
        with open("config.yml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_server_properties(self) -> dict:
        server_dir = self.get_mcdr_config()["working_directory"]
        with open(
            os.path.join(server_dir, "server.properties"), "r", encoding="utf-8"
        ) as f:
            return javaproperties.load(f)

    def get_tps(server: ServerInterface, secs: int = 1) -> float:
        if not server.is_rcon_running():
            raise RuntimeError("Need open MCDR's RCON future")
        server.rcon_query("debug start")
        time.sleep(secs)
        response = server.rcon_query("debug stop")
        return float(
            parse.parse("Stopped debug profiling after {tps}", response)["tps"]
        )

if __name__=="__main__":
    print("You must use it in MCDReforged")
    exit(1)