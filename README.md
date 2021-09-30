# 这是适用于 MCDR 2.x 的版本，如果你正在使用 MCDR 1.x，请切换至 [legacy/MCDR-1.x](https://github.com/HuajiMUR233/MoreAPIs/tree/legacy/MCDR-1.x) 分支

# More APIs

>   给 MCDReforged 添加了一些 API

---

## 包依赖

| Python 包      | 依赖需求  |
| -------------- | --------- |
| ruamel.yaml    | >=0.16.12 |
| javaproperties | >=0.8.0   |
| mcdreforged    | >=2.0.0   |
| dnspython      | >=2.1.0   |
| mcstatus       | >=6.5.0   |
| parse          | >=1.18.0  |

---

## API 列表

### MoreAPIs

所有 API 都在这个类下，使用前请先实例化它

#### `MoreAPIs.send_server_list_ping(host: str, port, tries: int) -> dict`

发送 [Server List Ping](https://wiki.vg/Server_List_Ping) 至某个 Minecraft：Java Editon 服务器

使用了 [MarshalX](https://gist.github.com/MarshalX)/**[StatusPing.py](https://gist.github.com/MarshalX/40861e1d02cbbc6f23acd3eced9db1a0)**

**注意**：**此函数不可在主线程调用**

参数:

`host`： 服务器IP

默认：`"localhost"`

`port`：服务器端口

默认：`25565`

`tries`：尝试次数

默认：`3`

&nbsp;

#### `MoreAPIs.execute_at(server: ServerInterface, player: str, command: str) -> None`

在某个玩家执行某条指令

参数:

`server`：[ServerInterface](https://mcdreforged.readthedocs.io/zh_CN/latest/plugin_dev/classes/ServerInterface.html)

`player`：玩家名称

`command`：要执行的指令

&nbsp;

#### `MoreAPIs.get_server_properties() -> dict`

获取 Minecraft 的 `server.properties`

&nbsp;

#### `MoreAPIs.parse_srv(host: str) -> Tuple[str, int]`

解析使用 `SRV 解析` 的 `Minecraft 服务端 IP` 为 IP 与 端口

&nbsp;

#### `MoreAPIs.get_tps(secs: int = 1) -> float`

获取服务器的 TPS

**注意**：**此函数不可在主线程调用**

参数:

`secs`：测试时间(单位：秒)

---

## 事件列表

#### 玩家死亡显示死亡信息

**事件ID**：more_apis.death_message

**回调参数**：`ServerInterface`，`death_message`

其中 `death_message` 表示死亡信息

&nbsp;

#### 玩家取得得了一个进度

**事件ID**：more_apis.player_made_advancement

**回调参数**：`ServerInterface`，`advancement`

其中 `advancement` 表示成就内容

&nbsp;

#### 服务器崩溃后

**事件ID**：more_apis.server_crashed

**回调参数**：`ServerInterface`，`crash_report_path`

其中 `crash_report_path` 表示崩溃报告的位置

PS：判断崩溃方式与 [CrashRestart](https://github.com/MCDReforged/CrashRestart) 插件相同

&nbsp;

#### 存档保存完毕

**事件ID**：more_apis.saved_game

**回调参数**：`ServerInterface`

