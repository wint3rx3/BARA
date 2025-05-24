import urllib.request, urllib.parse, json, html, re

client_id = "yqp_UdutO_s0dd2NVSjz"
client_secret = "U9CjVJnqPP"

def clean_html(raw_html):
    no_tags = re.sub('<.*?>', '', raw_html)
    return html.unescape(no_tags)

def search_recent_news(keyword):
    url = f"https://openapi.naver.com/v1/search/news.json?query={urllib.parse.quote(keyword)}&display=10"
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)
    res = urllib.request.urlopen(req)
    items = json.loads(res.read().decode("utf-8"))["items"]
    return [clean_html(i["title"]) for i in items]

def search_news_for_subtheme(keyword):
    url = f"https://openapi.naver.com/v1/search/news.json?query={urllib.parse.quote(keyword)}&display=1"
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)
    res = urllib.request.urlopen(req)
    items = json.loads(res.read().decode("utf-8"))["items"]
    return [{
        "제목": clean_html(i["title"]),
        "기사": clean_html(i["description"]),
        "링크": i["link"],
        "날짜": i["pubDate"]
    } for i in items]
