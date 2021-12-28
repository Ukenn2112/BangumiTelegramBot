# Bangumi Telegram Bot

为了实现在 Telegram 上简单操作 [Bangumi](https://bgm.tv/)

# 功能

- [x] OAuth授权
  - [x] 授权登录
  - [x] 授权有效期刷新
- [x] 查询个人收藏统计
- [x] 更新收视进度
- [ ] 管理收藏
- [ ] 查询剧集信息

......
# 使用方法

- 修改文件后缀 `config.py.example` 为 `config.py`

  根据文件内提示修改 `config.py` 配置文件

- 修改文件后缀 `data_bgm.json.example` 为 `data_bgm.json`

- 安装依赖

  ```
  pip3 install -r requirements.txt
  ```

- 运行Oauth验证绑定模块

  ```
  python3 oauth.py
  ```
  
  - 如遇无法访问请检查服务器防火墙
  - 如果您想后续仅自己个人使用，您可以在验证绑定完成后关闭此模块运行

- 运行 Telegram Bot 模块

  ```
  python3 bot.py
  ```

# 命令列表

您可以通过 [@BotFather](https://t.me/botfather) 来设置您的机器人的命令建议。

```
start - 绑定Bangumi账号
my - Bangumi收藏统计
anime - Bangumi用户在看动画
```

# 其它

这是我第一次写的Python项目，没系统学习过Python，许多细节上可能没有规范还请大佬们多多包涵，如您有更好的解决方式欢迎提交PR，谢谢^_^