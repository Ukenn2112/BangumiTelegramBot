import requests


def get_onair_data():
    """获取正在放送的番剧"""
    r = requests.get("https://raw.githubusercontent.com/ekibot/bangumi-link/master/calendar.json")
    if r.status_code != 200:
        return None
    return r.json()