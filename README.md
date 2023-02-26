<img src="https://avatars.githubusercontent.com/u/7521082?s=200&v=4" align="left" width="65"> <h1>Bangumi Telegram Bot</h1>

## 功能

...

## 安装

## 使用方法

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
