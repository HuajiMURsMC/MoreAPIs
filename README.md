# 这是适用于 MCDR 2.x 的版本，如果你正在使用 MCDR 1.x，请切换至 [MCDR-1.x](https://github.com/HuajiMUR233/MoreAPIs/tree/MCDR-1.x) 分支

# More APIs

>   给 MCDReforged 添加了一些 API

---

## 包依赖

| Python 包      | 依赖需求  |
| -------------- | --------- |
| ruamel.yaml    | >=0.16.12 |
| javaproperties | >=0.8.0   |
| mcdreforged    | >=2.0.0   |
| parse          | >=1.18.0  |

---

## API 列表

#### `api.send_server_list_ping(host: str, port, timeout: int)`

发送 [Server List Ping](https://wiki.vg/Server_List_Ping) 至某个 Minecraft：Java Editon 服务器

使用了 [MarshalX](https://gist.github.com/MarshalX)/**[StatusPing.py](https://gist.github.com/MarshalX/40861e1d02cbbc6f23acd3eced9db1a0)**

**注意**：**此函数不可在主线程调用**

参数:

`host`： 服务器IP

默认：`"localhost"`

`port`：服务器端口

默认：`25565`

`timeout`：超时时间(单位：秒)

默认：`5`

&nbsp;

#### `api.execute_at(server: ServerInterface, player: str, command: str)`

在某个玩家执行某条指令

参数:

`server`：ServerInterface

`player`：玩家名称

`command`：要执行的指令

&nbsp;

#### `api.get_server_properties()`

获取 Minecraft 的 `server.properties`

&nbsp;

#### `api.get_tps(secs: int = 1)`

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

**默认函数名称**：on_death_message

&nbsp;

#### 玩家取得得了一个进度

**事件ID**：more_apis.player_made_advancement

**回调参数**：`ServerInterface`，`advancement`

其中 `advancement` 表示成就内容

**默认函数名称**：on_player_made_advancement

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

