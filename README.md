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
- [x] 图片搜索番剧
- [x] 与 [Bangumi.online](https://bangumi.online/) 联动的番剧更新提醒

......

# 使用方法

- 安装 [Redis](https://redis.io/)

  您可以参考 [Redis 安装教程](https://www.google.com/search?q=Redis%E5%AE%89%E8%A3%85%E6%95%99%E7%A8%8B)

- 安装 [Pipenv](https://pipenv.pypa.io/)  `可选｜Optional`

  您可以参考 [Pipenv 安装教程](https://pipenv.pypa.io/en/latest/#install-pipenv-today)

- 修改文件后缀 `config.py.example` 为 `config.py`

  根据文件内提示修改 `config.py` 配置文件

- 安装依赖
  > **Warning** 需要 Python >= 3.9
  ```
  pip3 install -r requirements.txt
  ```

  如使用 Pipenv `可选｜Optional`
  ```
  pipenv install --dev
  ```

- 运行Oauth验证绑定模块
  
  ```
  python3 oauth.py
  ```
  
  如使用 Pipenv `可选｜Optional`
  ```
  pipenv run python3 oauth.py
  ```

  - 如遇无法访问请检查服务器防火墙
  - 如果您想后续仅自己个人使用，您可以在验证绑定完成后关闭此模块运行

- 运行 Telegram Bot 模块
  
  ```
  python3 bot.py
  ```

  如使用 Pipenv `可选｜Optional`
  ```
  pipenv run python3 bot.py
  ```

- 通过 [@BotFather](https://t.me/botfather) 将inline功能开启

  `/mybots` -> `选择 bot` -> `Bot Settings` -> `Inline Mode` -> 按下 `Turn on` (画面显示 Inline mode is currently enabled for xxxx 就表示启用了)

- 如使用 Pipenv 格式化代码 (可选｜Optional)

  ```
  pipenv run black .
  ```

## 如使用 Docker Compose 运行

- 安装 [Docker Compose](https://docs.docker.com/compose/)

  您可以参考 [Docker Compose 安装教程](https://docs.docker.com/compose/install/)

- 准备数据目录

  `/data/BangumiTelegramBot`

- 修改文件后缀 `config.py.example` 为 `config.py`

  根据文件内提示修改 `config.py` 配置文件，并放置到 `/data/BangumiTelegramBot/config.py`

  `REDIS_HOST` 请设置为 `redis`

- 使用 Docker Compose 运行

  `cd misc && docker compose up -d`


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
isearch - 图片搜索
close - 关闭此对话
```

# inline 内联搜索使用方法

![image](https://cdn.jsdelivr.net/gh/Ukenn2112/image@1.0.0/inline_query.png)

# 文件树

```txt
BangumiTelegramBot   # 主目录
│
│  bot.py            # Bangumi Bot 模块
│  config.py         # 配置文件
│  oauth.py          # Bangumi Oauth 绑定验证模块
│  Pipfile           # Pipenv Python 依赖
│  requirements.txt  # Python 依赖
│
├─data  # 数据目录
│     bot.db   # Bangumi Bot 用户数据
│     run.log  # Bot 运行日志
│
├─plugins  # 功能
│  │  collection_list.py  # 查询 Bangumi 用户在看
│  │  help.py             # 使用帮助
│  │  info.py             # 根据 SubjectId 返回对应条目信息
│  │  search.py           # 搜索引导
│  │  start.py            # 查询/绑定 Bangumi
│  │  week.py             # 每日放送查询
│  │  unbind.py           # 解除绑定
│  │  close.py            # 关闭会话
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
├─model  # 模型
│     page_model.py # 页面模型
│
└─misc  # 杂项
      Dockerfile           # docker 镜像构建文件
      docker-compose.yaml  # docker compose 部署文件
```

# 其它

- 这是我第一次写的Python项目，没系统学习过Python，许多细节上可能没有规范还请大佬们多多包涵，如您有更好的解决方式欢迎提交PR，谢谢^_^

- 本项目大部分功能通过 [Bangumi API](https://github.com/bangumi/api) 实现，由于API的限制可能部分功能无法实现，后续将可能通过模拟网页操作来完善。
