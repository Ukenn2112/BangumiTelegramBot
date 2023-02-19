# Thanks By @liurui39660
from bisect import bisect_left
from colorsys import hsv_to_rgb, rgb_to_hsv
from io import BytesIO
from itertools import accumulate
from operator import truediv

import PIL.Image
from PIL.ImageDraw import Draw
from PIL.ImageEnhance import Brightness
from PIL.ImageFilter import GaussianBlur
from PIL.ImageFont import FreeTypeFont, truetype
from requests import get


def subject_image(subject_info: dict) -> bytes:
    """生成剧集图片"""
    fontS = truetype("utils/font/NotoSansSymbols2-Regular.ttf", 60)
    font1 = truetype("utils/font/NotoSansSC-Medium.otf", 22)
    font2 = font1.font_variant(size=70)
    font3 = font1.font_variant(size=30)
    font4 = font1.font_variant(size=60)

    image = PIL.Image.new("RGB", (1200, 628), "#222526")
    draw = Draw(image)
    xl = 60 # 左边留白
    yt = 50 # 顶部留白
    margin = 14 # 行间距
    width = 610 # 文字宽度

    # 海报
    # ----------------------------------------
    with PIL.Image.open(BytesIO(get(subject_info["images"]["large"]).content)) as thumb:
        color = Color(thumb) # 海报主色调
        size = (760, 628)  # TODO: Don"t hardcode
        r = 0.5 * min(map(truediv, thumb.size, size))
        w = r * size[0]
        h = r * size[1]
        l = max(0, (thumb.size[0] - w) / 2)
        t = max(0, (thumb.size[1] - h) / 2)
        r = min(thumb.size[0], (thumb.size[0] + w) / 2)
        b = min(thumb.size[1], (thumb.size[1] + h) / 2)
        image.paste(Brightness(thumb.resize(size, 1, (l, t, r, b), 2)).enhance(0.25).filter(GaussianBlur(9)))

        size = (440, 628)  # Thumbnail size
        r = min(map(truediv, thumb.size, size))
        w = r * size[0]
        h = r * size[1]
        l = max(0, (thumb.size[0] - w) / 2)
        t = max(0, (thumb.size[1] - h) / 2)
        r = min(thumb.size[0], (thumb.size[0] + w) / 2)
        b = min(thumb.size[1], (thumb.size[1] + h) / 2)
        image.paste(thumb.resize(size, 1, (l, t, r, b), 2), (760, 0))

    # 年份 · 类型
    # ----------------------------------------
    _, t, _, b = font1.getbbox("A")
    yt += b - t
    subject_type = {1: "Book", 2: "Anime", 3: "Music", 4: "Game", 6: "Real"}
    text = f"{subject_type.get(subject_info['type'], 'Anime')} Fall {subject_info['date'][:4] if subject_info['date'] else '????'}"
    if subject_info["eps"] != 0:
        text += f"·{subject_info['eps']} episodes"
    draw.text((xl, yt), text, (168, 168, 168), font1, "ls")
    yt += margin - 1

    # 标题
    # ----------------------------------------
    title = Wrap(subject_info["name"], width, font2)
    _, t, _, b = font2.getbbox("A")
    spacing = 25
    yt += b - t + spacing
    lines = len(title)
    if lines > 4:
        title = title[:4]
        title[-1] = title[-1][:-1] + "…"
    draw.multiline_text((xl - 10, yt), "\n".join(title), "white", font2, "ls", spacing - t)
    _lines = lines if lines != 1 else 0
    yt += _lines * (b - t) + margin
    if lines == 2: yt -= 25
    if subject_info["name_cn"] and lines < 4:
        title_cn = Wrap(subject_info["name_cn"], width, font3)
        _, t, _, b = font3.getbbox("A")
        spacing = 10
        yt += b - t + spacing
        draw.multiline_text((xl - 5, yt), "\n".join(title_cn), color, font3, "ls", spacing - t)

    # 评分
    # ----------------------------------------
    y = 550
    if score := subject_info["rating"]["score"]:
        draw.text((xl - 5, y - 60), "\u2730", score >= 6 and "gold" or score >= 5 and "silver" or "Sienna", fontS, "ls")
        draw.text((xl + 60, y - 60), f"{subject_info['rating']['score']}", "white", font4, "ls")

    # Tags
    # ----------------------------------------
    border = 7
    xr = xl + width
    h, s, v = rgb_to_hsv(*color)
    rgb = tuple(map(round, hsv_to_rgb(h, s, v * 0.6)))
    for tag in subject_info["tags"]:
        l, t, r, b = draw.textbbox((xl, y), tag["name"], font1, "ls")
        if r + 2 * border > xr: break  # 超出的标签被放弃
        draw.rectangle((l, y - border, r + 2 * border, y + border), rgb)
        draw.text((l + border, y), tag["name"], "white", font1, "ls")
        xl += r - l + border * 4  # Move right

    # 输出
    # ----------------------------------------
    file = BytesIO()
    image.save(file, "PNG")  # .tobytes() is not for this
    out = file.getvalue()
    return out

def Wrap(text: str, width: float, font: FreeTypeFont, line=-1) -> list[str]:
    space = font.getlength(" ")
    dots = font.getlength("[...]")
    words = [text[i:i+2] for i in range(0, len(text), 2)]
    lens = tuple(accumulate(map(space.__add__, map(font.getlength, words))))  # Widths of words, each plus a space
    out = []
    w = width + space
    while line and words:
        i = bisect_left(lens, w)
        if line == 1:
            for j in reversed(range(i)):
                dots -= lens[j]
                if dots > 0:
                    words[j] = ""
                else:
                    words[j] = "[...]"
                    break
        out.append("".join(words[:i]))
        w = width + lens[i - 1] + space  # Ignore space at line end
        words = words[i:]
        lens = lens[i:]
        line -= 1
    for n, o in enumerate(out):
        if o.startswith("！") or o.startswith("？") or o.startswith("。") or o.startswith("、"):
            out[n] = o[1:]
            out[n - 1] += o[0]
    if len(out) == 2:
        if any(punct in out[1] for punct in "！？。"):
            pass
        elif len(out[1]) > 2:
            pass
        else:
            out = [out[0] + out[1]] 
    return out


def Color(image: PIL.Image.Image):
    """要提取的主要颜色"""
    try:
        num_colors = 20 
        small_image = image.resize((80, 80))
        result = small_image.convert("P", palette=PIL.Image.Palette.ADAPTIVE, colors=num_colors)
        result = result.convert("RGB")
        main_colors = result.getcolors()
        main_color = sorted(main_colors, key=lambda x: x[0], reverse=True)[0][1]
        if main_color[0] < 120:
            main_color = (150, main_color[1], main_color[2])
        if main_color[1] > 160:
            main_color = (main_color[0], 150, main_color[2])
    except:
        return None
    return main_color