"""
    MoreAPIs Sample Plugin
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

from mcdreforged.api.all import *

# on_load
def on_load(server: ServerInterface, old):
    # get MoreAPIs instance
    global MoreAPIs
    MoreAPIs = server.get_plugin_instance("moreapis")
    # register Event Listeners
    server.register_event_listener("moreapis.death_message", on_death_message)
    server.register_event_listener("moreapis.server_crashed", on_server_crashed)
    server.register_event_listener(
        "moreapis.player_made_advancement", on_player_made_advancement
    )

    # register command !!mcver
    server.register_command(Literal("!!mcver").runs(mcver_command))

    # register command !!force_stop
    server.register_command(Literal("!!force_stop").runs(force_stop_command))

    # register command !!ping_server <host> <port> [<timeout>]
    server.register_command(
        Literal("!!ping_server")
            .then(Text("host")
            .then(Text("port"))
            .then(Integer("timeout"))
            .runs(
                lambda src, ctx: ping_server_command(
                    src, ctx["host"], ctx["port"], ctx["timeout"]
                )
            )
        )
    )


# on death_message
def on_death_message(
    server: ServerInterface, death_message: str, player: str, killer: str
):
    server.broadcast(f"{killer} killed {player}!")


# on server_crashed
def on_server_crashed(server: ServerInterface, crash_report_path: str):
    with open(crash_report_path, "r", encoding="utf-8") as f:
        crash_report = f.read()
    server.logger.error(
        f"""Oh no! Server was crashed!
    Crash Report:
    {crash_report}"""
    )


# on player_made_advancement
def on_player_made_advancement(server: ServerInterface, player: str, advancement: str):
    server.broadcast(f"{player} got the advancement: §6[{advancement}]")


# !!mcver command
def mcver_command(source: CommandSource):
    server = source.get_server()
    version = MoreAPIs.get_server_version(server)
    source.reply(version)


# !!force_stop command
def force_stop_command(source: CommandSource):
    server = source.get_server()
    MoreAPIs.kill_server(server)


# !!ping_server command
def ping_server_command(source: CommandSource, host: str, port: int, timeout: int = 5):
    response=MoreAPIs.send_server_list_ping(host,port,timeout)
    source.reply(response)
