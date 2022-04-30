from  ikuManhua import  ikuManhua
from lxml import etree
import os

class ZxkaManhua(ikuManhua):
    def ud_geurl_to_book_infos(self,html):
        root = etree.HTML(html)
        book_names = root.xpath("/html/body/div[1]/div[1]/div[6]/div/div[2]/div/ul/li/a/span/text()")
        urls = root.xpath("/html/body/div[1]/div[1]/div[6]/div/div[2]/div/ul/li/a/@href")
        urls = ["https://m.zxkai.com" + i for i in urls]
        all_name = root.xpath("/html/body/div[1]/div[1]/div[3]/div/text()")[0]
        urls = urls[::-1]
        book_names = book_names[::-1]
        return (book_names, all_name, urls)
    def ud_decode_book_info(self, html):
        root = etree.HTML(html)
        img_num = int(root.xpath('/html/body/div[1]/div[13]/div[1]/div[3]/any/text()')[0])
        name = root.xpath("/html/body/div[1]/div[2]/a[2]/text()")[0]
        name = name.replace(" ", '').replace(".", "")  # 当前章节名字
        return (img_num, name)
    def ud_get_everpage_urls(self, url):
        return [url + "?p={}".format(str(i+1)) for i in range(self.img_num)]
    def ud_html_to_img_url(self, html):#给网页,得图片地址,返回字符串
        root = etree.HTML(html)
        src = root.xpath("/html/body/div[1]/div[4]/img/@src")[0]
        return str(src)
if __name__ == "__main__":
    # curPath = os.path.dirname(__file__)
    # rootpath = str(curPath)
    # myman = ZxkaManhua(rootpath)#x需要拿到文件路径
    # myman.pool_num = 5
    # myman.start_spider_all_book_smb("https://m.zxkai.com/comic/8777.html")
    pass

#惊爆游戏 https://m.zxkai.com/comic/8777.html
#妖神记 https://m.zxkai.com/comic/9329.html
#女子学院的男生 https://m.zxkai.com/comic/11247.html
#
#