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

from mcstatus import MinecraftServer
from parse import parse
from ruamel import yaml
import javaproperties
import dns.resolver

from mcdreforged.api.types import PluginServerInterface, Info
from mcdreforged.plugin.plugin_event import MCDREvent
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rcon import RconConnection
from mcdreforged.api.event import PluginEvent


__events = {
    "death_message": MCDREvent("more_apis.death_message", "Death message", "on_death_message"),
    "player_made_advancement": MCDREvent("more_apis.player_made_advancement", "Player made advancement", "on_player_made_advancement"),
    "server_crashed": PluginEvent("more_apis.server_crashed"),
    "saved_game": PluginEvent("more_apis.saved_game"),
}


def on_load(server: PluginServerInterface, old):
    global api
    if old is not None:
        api = old.api
    else:
        api = MoreAPIs(server)


@new_thread("More APIs' Handler")
def on_info(server: PluginServerInterface, info: Info):
    if info.is_user:
        return
    death_messages = __get_death_messages(server)
    if info.logging_level == "ERROR" and info.content.startswith(
        "This crash report has been saved to:"
    ):
        path = parse("This crash report has been saved to: {path}", info.content)[
            "path"
        ]
        server.logger.warning(
            "A Crash Report was detected, the server may have crashed"
        )
        server.dispatch_event(__events["server_crashed"], (path,))

    for action in [
        "made the advancement",
        "completed the challenge",
        "reached the goal",
    ]:
        match = re.fullmatch(r"\w{1,16} has %s \[.+]" % action, info.content)
        if match is not None:
            player, rest = info.content.split(" ", 1)
            adv = re.search(r"(?<=%s \[).+(?=])" % action, rest).group()
            server.dispatch_event(__events["player_made_advancement"], (player, adv))

    for i in death_messages:
        if re.fullmatch(i, info.content):
            server.dispatch_event(__events["death_message"], (info.content,))
            break

    if info.content == "Saved the game":
        server.dispatch_event(__events["saved_game"],())


class MoreAPIs:
    tps: float

    def __init__(self, server: PluginServerInterface):
        self.server = server
        self.server_properties = self.get_server_properties()
        self.yaml = yaml.YAML()
        self.getting_tps = False
        server.register_event_listener("mcdr.general_info", self.__tps_listener)

    def __tps_listener(self, server: PluginServerInterface, info: Info):
        if self.getting_tps:
            if info.is_user:
                return
            result = parse("Stopped debug profiling after {secs} seconds and {ticks} ticks ({tps} ticks per second)",
                           info.content)
            if result is not None:
                self.getting_tps = False
                self.tps = result['tps']

    def execute_at(self, player: str, command: str) -> None:
        self.server.execute(f"execute as {player} at {player} {command}")

    def get_server_properties(self) -> dict:
        server_dir = self.server.get_mcdr_config()["working_directory"]
        with open(
            os.path.join(server_dir, "server.properties"), "r", encoding="utf-8"
        ) as f:
            return javaproperties.load(f)
        
    def send_server_list_ping(self, host: str = "localhost", port: int = 25565, tries: int = 3) -> dict:
        if self.server.is_on_executor_thread:
            raise RuntimeError('Cannot invoke send_server_list_ping on the task executor thread')
        server = MinecraftServer(host, port)
        response = server.status(tries)
        status = response.raw
        status['ping']=round(response.latency,2)
        return status
    
    def parse_srv(self, host: str):
        try:
            answers = dns.resolver.resolve("_minecraft._tcp." + host, "SRV")
            if len(answers):
                answer = answers[0]
                return str(answer.target).rstrip("."), int(answer.port)
        except:
            return None

    def get_tps(self, secs: int = 1) -> float:
        if self.server.is_on_executor_thread:
            raise RuntimeError('Cannot invoke get_tps on the task executor thread')
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


def __get_death_messages(server: PluginServerInterface) -> dict:
    with server.open_bundled_file("death_messages.yml") as f:
        death_messages = yaml.safe_load(f)
    return death_messages['now'] + death_messages['old']


api: MoreAPIs

if __name__ == "__main__":
    print("You must use it in MCDReforged")
    exit(1)
