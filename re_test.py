import re
import requests
a = "从痴汉手中救下的S级美少女1话"
b = "从痴汉手中救下的S级美少女 1话"

c = b.replace(" ",'')
d = re.findall("", c)

e = [(0,1)]


def f():
    return (0, 1)

(a,b) = f()
heads = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
            "Referer": "https://m.zxkai.com/"
        }
url = "https://m.zxkai.com/comic/8777/882691.html"
res = requests.get(url, headers=heads)


print(res.content)

