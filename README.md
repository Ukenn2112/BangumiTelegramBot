<img src="https://avatars.githubusercontent.com/u/7521082?s=200&v=4" align="left" width="65"> <h1>Bangumi Telegram Bot</h1>

## 功能

...

## 安装

- 安装 [Redis](https://redis.io/)

  您可以参考 [Redis 安装教程](https://www.google.com/search?q=Redis%E5%AE%89%E8%A3%85%E6%95%99%E7%A8%8B)

- 安装 [Pipenv](https://pipenv.pypa.io/)  `可选｜Optional`

  您可以参考 [Pipenv 安装教程](https://pipenv.pypa.io/en/latest/#install-pipenv-today)

- 修改文件后缀 `data/config.example.yaml` 为 `data/config.yaml`

  根据文件内提示修改 `config.yaml` 配置文件

  > 如需使用 Web 绑定功能需配置反代 `INVERSE_URL` 为 HTTPS `可选｜Optional`

- 安装依赖
  > **Warning** 需要 Python >= 3.9
  ```
  pip3 install -r requirements.txt
  ```

  如使用 Pipenv `可选｜Optional`
  ```
  pipenv install --dev
  ```

- 运行
  
  ```
  python3 main.py
  ```

  如使用 Pipenv `可选｜Optional`
  ```
  pipenv run python3 main.py
  ```

  - 如遇绑定链接无法访问请检查服务器防火墙

- 通过 [@BotFather](https://t.me/botfather) 将 Inline 功能开启

  `/mybots` -> `选择 bot` -> `Bot Settings` -> `Inline Mode` -> 按下 `Turn on` (画面显示 Inline mode is currently enabled for xxxx 就表示启用了)

- 如使用 Pipenv 格式化代码 (可选｜Optional)

  ```
  pipenv run black .
  ```

## 如使用 Docker Compose 运行

- 安装 [Docker Compose](https://docs.docker.com/compose/)

  您可以参考 [Docker Compose 安装教程](https://docs.docker.com/compose/install/)

- 修改文件后缀 `config.example.yaml` 为 `config.yaml`

  根据文件内提示修改 `config.yaml` 配置文件，并放置到 `/data/config.yaml`

  `REDIS_HOST` 请设置为 `redis`

- 使用 Docker Compose 运行

  `cd docker && docker compose up -d`

## 命令列表

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

## inline 内联搜索使用方法

![image](https://cdn.jsdelivr.net/gh/Ukenn2112/image@1.0.0/inline_query.png)
