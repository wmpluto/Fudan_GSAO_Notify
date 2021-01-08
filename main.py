from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
import requests
import os


PUSH_KEY = os.getenv("PUSH_KEY")
GSAO_URL = "http://www.gsao.fudan.edu.cn"
GSAO_BULLETIN_URL = "http://www.gsao.fudan.edu.cn/15014/list.htm"
IT_URL = "http://www.it.fudan.edu.cn"
IT_BULLETIN_URL = "http://www.it.fudan.edu.cn/Data/List/zxdt"


def get_session(_url):
    _session = requests.Session()
    _session.headers["User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.18(0x17001229) NetType/WIFI Language/zh_CN miniProgram"

    _response = _session.get(_url)
    _response.encoding = 'utf-8'

    return BeautifulSoup(_response.text, "html.parser")


def gsao_msg(_date):
    _soup = get_session(GSAO_BULLETIN_URL)

    _msg_list = []
    for _li in _soup.find_all("li", class_="cols"):
        _li_date = _li.find_all("span")[3].text
        _li_title = _li.find_all("span")[0].a['title']
        _li_href = _li.find_all("span")[0].a['href']

        if "http" not in _li_href:
            _li_href = f"{GSAO_URL}{_li_href}"

        if _li_date == _date:
            _msg_list.append(f"[{_li_title}]({_li_href})")

    return _msg_list


def it_msg(_date):
    _soup = get_session(IT_BULLETIN_URL)

    _msg_list = []
    _ul = _soup.find_all("ul", class_="data-list")[0]
    for _li in _ul.find_all("li"):
        _li_date = _li.span.text.strip()
        _li_title = _li.a.text.strip()
        _li_href = _li.a['href']

        if "http" not in _li_href:
            _li_href = f"{IT_URL}{_li_href}"

        if _li_date == _date:
            _msg_list.append(f"[{_li_title}]({_li_href})")

    return _msg_list


def notify(_title, _message=None):
    if not PUSH_KEY:
        print("未配置PUSH_KEY！")
        return

    if not _message:
        _message = _title

    _response = requests.post(
        f"https://sc.ftqq.com/{PUSH_KEY}.send", {"text": _title, "desp": _message})

    if _response.status_code == 200:
        print(f"发送通知状态：{_response.content.decode('utf-8')}")
    else:
        print(f"发送通知失败：{_response.status_code}")


def main():
    _tz = timezone(+timedelta(hours=8))
    today = datetime.now(_tz).strftime("%Y-%m-%d")
    print(datetime.now(_tz).strftime("%Y-%m-%d %H:%M"))

    msg = "\r\n\r\n".join(gsao_msg(today)) + "\r\n\r\n" + \
        "\r\n\r\n".join(it_msg(today))

    if len(msg.strip()):
        print(msg)
        notify(f"{today} 复旦消息提示", msg)
    else:
        print("None content today")


if __name__ == "__main__":
    main()
