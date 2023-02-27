<img src="https://avatars.githubusercontent.com/u/7521082?s=200&v=4" align="left" width="65"> <h1>Bangumi Telegram Bot</h1>

## 功能

- [x] Web 登录
- [x] OAuth授权
  - [x] 授权登录
  - [x] 授权有效期刷新
- [x] 查询个人收藏统计
- [x] 收视进度更新
- [x] 在看评分
- [x] 通过 Telegram Inline 功能进行条目搜索
- [x] 管理收藏
- [x] 每日放送查询
- [x] 图片搜索条目
- [x] 章节评论发送
- [x] 圣地巡礼数据查询 数据来自 [Anitabi.cn](https://anitabi.cn/)
- [x] 与 [Bangumi.online](https://bangumi.online/) 联动的番剧更新提醒

......

## 功能展示

  | 功能 | 展示 | 功能 | 展示 | 功能 | 展示 |
  | :---: | :---: | :---: | :---: | :---: | :---: |
  | 登录授权 | ![登录授权](https://user-images.githubusercontent.com/60847880/221489586-7d630b50-fd4f-412a-80bd-6176fb9df62a.gif) | Oauth 授权 | ![Oauth 授权](https://user-images.githubusercontent.com/60847880/221490098-34d0e993-cccf-420a-ae90-6a89980cc530.gif) | 收藏列表 | ![收藏列表](https://user-images.githubusercontent.com/60847880/221491257-799efdc8-fb46-4052-9873-c90ba9293d44.gif)
  | 条目展示 | ![条目展示](https://user-images.githubusercontent.com/60847880/221491539-8854c89c-dcbd-4feb-9c48-22061f2fcab5.gif) | 章节展示 |![章节展示](https://user-images.githubusercontent.com/60847880/221491762-5f3c37c7-1c6e-4234-b7d2-d60d86cead5d.gif) | 每日放送 | ![每日放送](https://user-images.githubusercontent.com/60847880/221492430-bbc4f15d-1d81-4306-b5f3-8f3499310065.gif)!
  | 条目搜索 (Bot 内) |  ![条目搜索-Bot内](https://user-images.githubusercontent.com/60847880/221493670-cf1dfc97-c945-4a45-9e2f-e867ed47acad.gif) | 条目搜索 (Bot 外) | ![条目搜索-Bot外](https://user-images.githubusercontent.com/60847880/221495161-85fa2249-f9ab-449d-85bb-7cf5cae6435c.gif) | 条目搜索(在有Bot群组) | ![条目搜索-在有Bot群组](https://user-images.githubusercontent.com/60847880/221494280-e091da80-40f6-4372-8d48-88ff5f47fc63.gif)
  | 角色搜索 |![虚拟人物搜索](https://user-images.githubusercontent.com/60847880/221498599-3365918f-a5d1-4483-93ef-4eca1ca3bfdb.gif) | 巡礼地图 | ![巡礼地图](https://user-images.githubusercontent.com/60847880/221502756-32ac0770-d95a-4a11-800d-2c7f2b17be16.gif) | 图片搜索条目 | ![图片搜索条目](https://user-images.githubusercontent.com/60847880/221498889-85102ed1-58e9-4b95-a703-f6e44353ef17.gif)
  
> 更多搜索方法见下

## inline 内联搜索使用方法

![inline内联搜索方法](https://user-images.githubusercontent.com/60847880/221499459-862a2e71-6f87-4860-9642-e666c5657ccb.png)

## 安装

- 安装 [Redis](https://redis.io/)

  您可以参考 [Redis 安装教程](https://www.google.com/search?q=Redis%E5%AE%89%E8%A3%85%E6%95%99%E7%A8%8B)

- 安装 [Pipenv](https://pipenv.pypa.io/)  `可选｜Optional`

  您可以参考 [Pipenv 安装教程](https://pipenv.pypa.io/en/latest/#install-pipenv-today)

- 修改文件后缀 `data/config.example.yaml` 为 `data/config.yaml`

  根据文件内提示修改 `config.yaml` 配置文件

  > 如需使用 Web 绑定功能需配置反代 `WEBSITE_BASE` 必须为 HTTPS `可选｜Optional`

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
