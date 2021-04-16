# More APIs

>   一个非常简单的插件，提供了一些(二次封装的)API与事件



## API 列表

`get_server_version()`

获取服务端的版本



`kill_server(server:ServerInterface)`

强制终止服务端

参数: `server`



`send_server_list_ping(host: str, port, timeout: int)`

发送 [Server List Ping](https://wiki.vg/Server_List_Ping) 至某个 Minecraft: Java Editon 服务器

引用了 [MarshalX](https://gist.github.com/MarshalX)/**[StatusPing.py](https://gist.github.com/MarshalX/40861e1d02cbbc6f23acd3eced9db1a0)**

参数:

`host`:  服务器IP

默认: `"localhost"`

`port`: 服务器端口

默认: `25565`

`timeout`: 超时时间(单位: 秒)

默认: `5`



---

## 事件列表

`more_apis.death_message`

玩家死亡显示死亡信息后触发(仅对原版死亡消息进行支持)

参数: `server`, `death_message`



`more_apis.player_made_advancement`

玩家获得了一个进度后触发

参数: `server`, `advancement`



`more_apis.server_crashed`

服务器崩溃后触发，判断崩溃方式与`CrashRestart`插件相同

参数: `server`, `crash_report_path`