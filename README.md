[![image](https://cdn.jsdelivr.net/gh/Ukenn2112/image/BangumiTelegramBot.png)](https://github.com/Ukenn2112/BangumiTelegramBot/)


# 功能

- [x] OAuth授权
  - [x] 授权登录
  - [x] 授权有效期刷新
- [x] 查询个人收藏统计
- [ ] 收视进度更新
  - [x] 更新动画的收视进度
  - [ ] 更新其他类型的收视进度
  - [ ] 批量更新收视进度
- [x] 观看完成最后一集后自动更新收藏状态为看过
- [x] 在看评分
- [x] 条目搜索
- [x] 管理收藏
- [x] 每日放送查询

......
# 使用方法

- 安装 [Redis](https://redis.io/)

  您可以参考 [Redis 安装教程](https://www.google.com/search?q=Redis%E5%AE%89%E8%A3%85%E6%95%99%E7%A8%8B)

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
my - Bangumi收藏统计/空格加username或uid不绑定查询
anime - Bangumi用户在看动画/空格加关键字查询
week - 查询当日/空格加数字查询每日放送
```

# 其它

- 这是我第一次写的Python项目，没系统学习过Python，许多细节上可能没有规范还请大佬们多多包涵，如您有更好的解决方式欢迎提交PR，谢谢^_^

- 本项目目前所有功能均通过 [Bangumi API](https://github.com/bangumi/api) 实现，由于API的限制可能部分功能无法实现，后续将可能通过模拟网页操作来完善。
