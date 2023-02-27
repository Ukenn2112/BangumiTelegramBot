import requests


def get_image_search(img_url: str):
    """图片搜索"""
    r = requests.get(f"https://api.trace.moe/search?cutBorders&anilistInfo&url={img_url}")
    if r.status_code != 200:
        return None
    return r.json()["result"][0]