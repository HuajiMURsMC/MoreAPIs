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


from parse import parse
from ruamel import yaml
import javaproperties
import requests

import time
import re
import os

from More_APIs.StatusPing import StatusPing

from mcdreforged.mcdr_state import MCDReforgedFlag
from mcdreforged.api.all import *


_plugin_id = "more_apis"
_plugin_version = "1.0.0"
_events = {
    "death_message": PluginEvent(_plugin_id + ".death_message"),
    "player_made_advancement": PluginEvent(_plugin_id + "advancement"),
    "server_crashed": PluginEvent(_plugin_id + ".server_crashed"),
    "saved_game": PluginEvent(_plugin_id + ".saved_game"),
}

PLUGIN_METADATA = {
    "id": _plugin_id,
    "version": _plugin_version,
    "name": "More APIs",
    "author": "HuajiMUR",
    "dependencies": {"mcdreforged": ">=1.0.0"},
}


@new_thread("More APIs' Handler")
def on_info(server: ServerInterface, info: Info):
    if info.is_user:
        return
    death_message = __get_death_messages(server)
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

    for action in [
        "made the advancement",
        "completed the challenge",
        "reached the goal",
    ]:
        match = re.fullmatch(r"\w{1,16} has %s \[.+]" % action, info.content)
        if match is not None:
            player, rest = info.content.split(" ", 1)
            adv = re.search(r"(?<=%s \[).+(?=])" % action, rest).group()
            server.dispatch_event(_events["player_made_advancement"], (player, adv))

    for i in death_message["msgs"]:
        if re.fullmatch(i, info.content):
            server.dispatch_event(_events["death_message"], (info.content,match.group[1]))
            break

    if info.content == "Saved the game":
        server.dispatch_event(_events["saved_game"],())


class MoreAPIs:
    def __init__(self, server: ServerInterface):
        if server.is_on_executor_thread():
            raise RuntimeError('Cannot use More APIs on the task executor thread')
        self.server = server
        self.server_properties = self.get_server_properties()
        self.version_data = self.__data_remapper(
            "https://hub.fastgit.org/PrismarineJS/minecraft-data/raw/master/data/pc/common/protocolVersions.json"
        )
        try:
            self.mcdr_server=server._mcdr_server
        except:
            self.mcdr_server=server._ServerInterface__mcdr_server

    def __data_remapper(self, data_url) -> dict:
        datas = requests.get(data_url).json()
        mapped = {}
        for data in datas:
            if not data["version"] in mapped:
                mapped[data["version"]] = data["minecraftVersion"]
            else:
                mapped[data["version"]] += "," + data["minecraftVersion"]
        for protocol_ver in mapped:
            if "," in mapped[protocol_ver]:
                versions = mapped[protocol_ver].split(",")
                mapped[protocol_ver] = versions[-1] + "~" + versions[0]
        return mapped

    def kill_server(self) -> None:
        self.mcdr_server.remove_flag(MCDReforgedFlag.EXIT_AFTER_STOP)
        self.mcdr_server.stop(forced=True)

    def get_server_version(self) -> str:
        if not self.server.is_server_startup:
            raise RuntimeError("Cannot invoke get_server_version before server startup")
        response = StatusPing(
            "localhost", int(self.server_properties["server-port"])
        ).get_status()
        version = response["version"]["protocol"]
        return self.version_data[version]

    def send_server_list_ping(
        self, host: str = "localhost", port: int = 25565, timeout: int = 5
    ) -> dict:
        response = StatusPing(host, port, timeout)
        return response.get_status()

    def execute_at(self, player: str, command: str) -> None:
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

    def get_tps(self, secs: int = 1) -> float:
        if not self.server_properties["enable-rcon"]:
            raise RuntimeError("Need open Minecraft Server's RCON future")
        rcon = RconConnection(
            "localhost",
            int(self.server_properties["rcon.port"]),
            self.server_properties["rcon.password"],
        )
        rcon.connect()
        rcon.send_command("debug start")
        time.sleep(secs)
        response = rcon.send_command("debug stop")
        rcon.disconnect()
        return float(parse("Stopped debug profiling after {secs} seconds and {ticks} ticks ({tps} ticks per second)",
                           response)['tps'])


def __get_death_messages(server: ServerInterface) -> dict:
    with open(
        os.path.join(
            os.path.dirname(server.get_plugin_file_path(_plugin_id)),
            "More_APIs",
            "death_messages.yml",
        ),
        "r",
        encoding="utf-8",
    ) as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    print("You must use it in MCDReforged")
    exit(1)
