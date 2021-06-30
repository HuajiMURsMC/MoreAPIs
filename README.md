# More APIs

>   一个非常简单的插件，提供了一些(二次封装的)API与事件

&nbsp;

---

## Python 依赖

[javaproperties](https://pypi.org/project/javaproperties/)：解析 [server.properties](https://minecraft.fandom.com/zh/wiki/Server.properties)

[ruamel.yaml](https://pypi.org/project/ruamel.yaml/)：解析 MCDReforged 的配置文件与死亡消息文件

[request](https://pypi.org/project/requests/)：获取 [protocolVersions.json](https://github.com/PrismarineJS/minecraft-data/blob/master/data/pc/common/protocolVersions.json)

[parse](https://pypi.org/project/parse/)：解析 Minecraft 服务端输出的一些信息

[psutil](https://pypi.org/project/psutil/)：杀进程

**注**：除 javaproperties 以外，其它依赖已包含在MCDR中

&nbsp;

---

## API 列表

**注意**：以下API均在MoreAPIs类中，使用前需先进行实例化

&nbsp;

#### `MoreAPIs.get_server_version()`

获取服务端的版本，需在 Minecraft 服务端启动后才能获取

&nbsp;

#### `MoreAPIs.kill_server(server: ServerInterface)`

强制终止服务端

参数:

`server`：ServerInterface

&nbsp;

#### `MoreAPIs.send_server_list_ping(host: str, port, timeout: int)`

发送 [Server List Ping](https://wiki.vg/Server_List_Ping) 至某个 Minecraft：Java Editon 服务器

使用了 [MarshalX](https://gist.github.com/MarshalX)/**[StatusPing.py](https://gist.github.com/MarshalX/40861e1d02cbbc6f23acd3eced9db1a0)**

参数:

`host`： 服务器IP

默认：`"localhost"`

`port`：服务器端口

默认：`25565`

`timeout`：超时时间(单位：秒)

默认：`5`

&nbsp;

#### `MoreAPIs.execute_at(server: ServerInterface,player: str,command：str)`

在某个玩家执行某条指令

以 Bukkit 方式注册的指令可能不行

参数:

`server`：ServerInterface

`player`：玩家名称

`command`：要执行的指令

&nbsp;

#### `MoreAPIs.get_mcdr_config()`

获取 MCDReforged 的配置文件

&nbsp;

#### `MoreAPIs.get_server_properties()`

获取 Minecraft 的 `server.properties`

&nbsp;

#### `MoreAPIs.get_tps(secs: int = 1)`

获取服务器的 TPS

**需先配置好 Minecraft 的 [RCON](https://wiki.vg/RCON) 才能使用**

参数:

`secs`：测试时间(单位：秒)

&nbsp;

---

## 事件列表

#### `more_apis.death_message`

玩家死亡显示死亡信息后触发(仅对原版死亡消息进行支持)

参数：`ServerInterface`，`death_message`

&nbsp;

#### `more_apis.player_made_advancement`

玩家获得了一个进度后触发

参数：`ServerInterface`，`advancement`

&nbsp;

#### `more_apis.server_crashed`

服务器崩溃后触发，判断崩溃方式与 [CrashRestart](https://github.com/MCDReforged/CrashRestart) 插件相同

参数：`ServerInterface`，`crash_report_path`

&nbsp;

#### `more_apis.saved_game`

当服务端输出 `Saved the game` 后触发

参数：`ServerInterface`

&nbsp;

---

## 更新日志

### 0.2.0-beta

**注意：这是一个测试性版本，在实际运行中可能出现各种 Bug**

尝试修复了 [#3](https://github.com/HuajiMUR233/MoreAPIs/issues/3)

get_server_version 函数的 Minecraft 服务端版本获取方式更换为使用 [Server List Ping](https://wiki.vg/Server_List_Ping) 来获取

get_tps 函数改为直接通过获取 server.properties 中的 RCON 配置来进行获取

修复了各种各样因为没人用而没人发现的 Bug

&nbsp;

## 0.2.0-beta.1

**注意：这是一个测试性版本，在实际运行中可能出现各种 Bug**

再次尝试修复了 [#3](https://github.com/HuajiMUR233/MoreAPIs/issues/3) :-(

还试着修了 [#4](https://github.com/HuajiMUR233/MoreAPIs/issues/4)

## 0.2.0

\水版本好耶/

(这是个正式版本了，希望没Bug)

&nbsp;

## 0.2.1-rc

**注意：这是一个预发布版本，在实际运行中可能出现各种 Bug**

可能修复了 [#5](https://github.com/HuajiMUR233/MoreAPIs/issues/5)

&nbsp;

