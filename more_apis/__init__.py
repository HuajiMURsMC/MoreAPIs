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

import time
import re
import os

from parse import parse
from ruamel import yaml
import javaproperties
import requests

from mcdreforged.api.all import *

from more_apis.StatusPing import StatusPing

_events = {
    "death_message": PluginEvent("more_apis.death_message"),
    "player_made_advancement": PluginEvent("more_apis.advancement"),
    "server_crashed": PluginEvent("more_apis.server_crashed"),
    "saved_game": PluginEvent("more_apis.saved_game"),
}


def on_load(server: PluginServerInterface, old):
    global api
    api = MoreAPIs(server)


@new_thread("More APIs' Handler")
def on_info(server: PluginServerInterface, info: Info):
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
            server.dispatch_event(_events["death_message"], (info.content,))
            break

    if info.content == "Saved the game":
        server.dispatch_event(_events["saved_game"],())


class MoreAPIs:
    tps: float

    def __getattribute__(self, item):
        if self.server.is_on_executor_thread():
            raise RuntimeError(f'Cannot invoke {item} on the task executor thread')
        return self.__dict__[item]

    def __init__(self, server: PluginServerInterface):
        self.server = server
        self.server_properties = self.get_server_properties()
        self.version_data = self.__data_remapper(
            "https://github.com/PrismarineJS/minecraft-data/raw/master/data/pc/common/protocolVersions.json"
        )
        self.yaml = yaml.YAML()
        self.getting_tps = False
        server.register_event_listener("mcdr.general_info", self.__tps_getter)

    def __tps_getter(self, server: PluginServerInterface, info: Info):
        if self.getting_tps:
            result = parse("Stopped debug profiling after {secs} seconds and {ticks} ticks ({tps} ticks per second)",
                           info.content)
            if result is not None:
                self.getting_tps = False
                self.tps = result['tps']

    @staticmethod
    def __data_remapper(data_url) -> dict:
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

    def get_server_version(self) -> str:
        if not self.server.is_server_startup:
            raise RuntimeError("Cannot invoke get_server_version before server startup")
        response = StatusPing(
            "localhost", int(self.server_properties["server-port"])
        ).get_status()
        version = response["version"]["protocol"]
        return self.version_data[version]

    def execute_at(self, player: str, command: str) -> None:
        self.server.execute(f"execute as {player} at {player} {command}")

    def get_server_properties(self) -> dict:
        server_dir = self.server.get_mcdr_config()["working_directory"]
        with open(
            os.path.join(server_dir, "server.properties"), "r", encoding="utf-8"
        ) as f:
            return javaproperties.load(f)

    def get_tps(self, secs: int = 1) -> float:
        if self.server_properties["enable-rcon"]:
            return self.__get_tps_rcon(secs)
        self.getting_tps = True
        while self.getting_tps:
            continue
        return self.tps

    def __get_tps_rcon(self, secs: int = 1) -> float:
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

    @staticmethod
    def send_server_list_ping(host: str = "localhost", port: int = 25565, timeout: int = 5) -> dict:
        response = StatusPing(host, port, timeout)
        return response.get_status()


def __get_death_messages(server: PluginServerInterface) -> dict:
    with server.open_bundled_file("death_messages.yml") as f:
        return yaml.safe_load(f)


api: MoreAPIs

if __name__ == "__main__":
    print("You must use it in MCDReforged")
    exit(1)
