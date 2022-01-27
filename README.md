[![image](https://cdn.jsdelivr.net/gh/Ukenn2112/image/BangumiTelegramBot.png)](https://github.com/Ukenn2112/BangumiTelegramBot/)


# 功能

- [x] OAuth授权
  - [x] 授权登录
  - [x] 授权有效期刷新
- [x] 查询个人收藏统计
- [ ] 收视进度更新
  - [x] 更新动画的收视进度
  - [x] 更新其他类型的收视进度
  - [ ] 批量更新收视进度
- [x] 观看完成最后一集后自动更新收藏状态为看过
- [x] 在看评分
- [x] 通过 Telegram Inline 功能进行条目搜索
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

- 通过 [@BotFather](https://t.me/botfather) 将inline功能开启

  `/mybots` -> `选择 bot` -> `Bot Settings` -> `Inline Mode` -> 按下 `Turn on` (画面显示 Inline mode is currently enabled for xxxx 就表示启用了)

# 命令列表

```
start - 绑定Bangumi账号
my - Bangumi收藏统计/空格加username或uid不绑定查询
book - Bangumi用户在读书籍
anime - Bangumi用户在看动画
game - Bangumi用户在玩动画
real - Bangumi用户在看剧集
week - 空格加数字查询每日放送
week - 查询当日/空格加数字查询每日放送
search - 搜索条目
```

# 文件树

```txt
BangumiTelegramBot   # 主目录
│
│  bgm_data.json     # Bangumi 用户密钥
│  bot.py            # BangumiBot 主模块
│  config.py         # 配置文件
│  oauth.py          # Bangumi Oauth 绑定验证模块
│  requirements.txt  # Python 所需依赖
│  
├─plugins  # 功能
│  │  doing_page.py  # 查询 Bangumi 用户在看
│  │  info.py        # 根据subjectId 返回对应条目信息
│  │  my.py          # 查询 Bangumi 用户收藏统计
│  │  search.py      # 搜索引导
│  │  start.py       # 查询/绑定 Bangumi
│  │  week.py        # 每日放送查询
│  │  
│  ├─callback  # 按钮查询
│  │      collection.py      # 收藏
│  │      letest_eps.py      # 已看最新
│  │      now_do.py          # 在看详情
│  │      rating_call.py     # 评分
│  │      search_details.py  # 搜索详情
│  │      summary_call.py    # 简介
│  │      week_back.py       # 每日放送查询返回
│  │      
│  └─inline  # 消息框内联查询
│          public.py  # 公共内联搜索
│          sender.py  # 私聊搜索或者在任何位置搜索前使用@内联搜索
│          
├─templates  # Oauth 认证提示页面模板
│      error.html     # 绑定出错
│      verified.html  # 重复验证
│      
└─utils  # 通用
        api.py       # API 调用
        converts.py  # 数据转换
```

# 其它

- 这是我第一次写的Python项目，没系统学习过Python，许多细节上可能没有规范还请大佬们多多包涵，如您有更好的解决方式欢迎提交PR，谢谢^_^

- 本项目目前所有功能均通过 [Bangumi API](https://github.com/bangumi/api) 实现，由于API的限制可能部分功能无法实现，后续将可能通过模拟网页操作来完善。
