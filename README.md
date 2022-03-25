> **从此版本开始我们将用户数据 `bgm_data.json` 改用 SQLite 存储，您可以使用 `json_to_db.py` 进行数据转换**

[![image](https://cdn.jsdelivr.net/gh/Ukenn2112/image/BangumiTelegramBot.png)](https://github.com/Ukenn2112/BangumiTelegramBot/)


# 功能 <img src="https://cdn.jsdelivr.net/gh/Ukenn2112/image/IMG_4622.gif" alt="输入框查询发送" width="200" align='right'><img src="https://cdn.jsdelivr.net/gh/Ukenn2112/image/IMG_4643.gif" alt="动画再看更新" width="200" align='right'>

- [x] OAuth授权
  - [x] 授权登录
  - [x] 授权有效期刷新
- [x] 查询个人收藏统计
- [x] 收视进度更新
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

- 安装依赖 **注意：Python >= 3.8**

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
help - 使用帮助
book - Bangumi用户在读书籍
anime - Bangumi用户在看动画
game - Bangumi用户在玩游戏
real - Bangumi用户在看剧集
week - 查询当日/空格加数字查询每日放送
search - 搜索条目
close - 关闭此对话
```

# Bangumi Telegram Bot inline 内联搜索使用方法

![image](https://cdn.jsdelivr.net/gh/Ukenn2112/image@1.0.0/inline_query.png)

# 文件树

```txt
BangumiTelegramBot   # 主目录
│
│  bot.db            # Bangumi Bot 用户数据
│  bot.py            # Bangumi Bot 模块
│  config.py         # 配置文件
│  oauth.py          # Bangumi Oauth 绑定验证模块
│  requirements.txt  # Python 依赖
│  
├─plugins  # 功能
│  │  collection_list.py  # 查询 Bangumi 用户在看
│  │  help.py             # 使用帮助
│  │  info.py             # 根据 SubjectId 返回对应条目信息
│  │  search.py           # 搜索引导
│  │  start.py            # 查询/绑定 Bangumi
│  │  week.py             # 每日放送查询
│  │  
│  ├─callback  # 按钮查询
│  │      collection_list_page.py       # 用户在看
│  │      edit_collection_type_page.py  # 收藏
│  │      edit_eps_page.py              # 点格子
│  │      edit_rating_page.py           # 评分
│  │      subject_eps_page.py           # 章节详情
│  │      subject_page.py               # 章节
|  |      summary_page.py               # 简介
│  │      week_back.py                  # 每日放送查询返回
│  │      
│  └─inline  # 消息框内联查询
│          mybgm.py   # 查询 Bangumi 用户收藏统计
│          public.py  # 公共内联搜索
│          sender.py  # 私聊搜索或者在任何位置搜索前使用@内联搜索
│          
├─templates  # Oauth 认证提示页面模板
│      error.html     # 绑定出错
|      expired.html   # 请求过期
│      verified.html  # 重复验证
│      
├─utils  # 通用
|      api.py       # API 调用
|      converts.py  # 数据转换
│
└─model  # 模型
      page_model.py # 页面模型
```

# 其它

- 这是我第一次写的Python项目，没系统学习过Python，许多细节上可能没有规范还请大佬们多多包涵，如您有更好的解决方式欢迎提交PR，谢谢^_^

- 本项目大部分功能通过 [Bangumi API](https://github.com/bangumi/api) 实现，由于API的限制可能部分功能无法实现，后续将可能通过模拟网页操作来完善。
