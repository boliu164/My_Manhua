import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import etree
import zipfile
import re
import os
import time
from concurrent.futures import ThreadPoolExecutor
import threading
import os
from smb_text import MySmb
from selenium.webdriver.chrome.service import Service
class ikuManhua:
    def __init__(self, root_path):
        self.pool_num = 5
        self.heads = {

            'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        self.prefs = {
            'profile.default_content_setting_values': {
                'images': 2,  # 屏蔽图片
            }
        }

        self.path_name = ""
        self.all_name = ""
        self.is_smb = 0
        chrome_options = Options()
        self.root_path = root_path
        chrome_options.add_experimental_option("prefs", self.prefs)
        chrome_options.add_argument('--headless')
        s = Service(os.path.join(self.root_path, "chromedriver.exe"))
        self.driver = webdriver.Chrome(service=s, options=chrome_options)
    def add_smb_config(self, host, username, password,share_dir_name, bookdir):
        self.is_smb = 1
        self.smb = MySmb(host,username,password,share_dir_name )
        self.smb_upload_file_path = bookdir
    def add_chrom_config_pool_thread(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", self.prefs)
        chrome_options.add_argument('--headless')
        s = Service(os.path.join(self.root_path, "chromedriver.exe"))
        return  webdriver.Chrome(service=s, options=chrome_options)
    def exist_file_filter(self, filename):
        res = self.smb.is_exist(self.smb_upload_file_path + "/{}".format(self.all_name),filename)
        return res
    def del_file(self, path_data):
        """
            删除文件夹下所有文件
        :param path_data:   文件夹路径，绝对路径
        :return:
        """
        if os.path.exists(path_data):
            for i in os.listdir(path_data):  # os.listdir(path_data)#返回一个列表，里面是当前目录下面的所有东西的相对路径
                file_data = path_data + "\\" + i  # 当前文件夹的下面的所有东西的绝对路径
                if os.path.isfile(file_data):  # os.path.isfile判断是否为文件,如果是文件,就删除.如果是文件夹.递归给del_file.
                    os.remove(file_data)
                else:
                    self.del_file(file_data)
            os.removedirs(path_data)
    def get_one_page(self, url):#获取一张网页图片地址
        driver = self.add_chrom_config_pool_thread()
        driver.get(url)
        html = driver.page_source
        driver.close()
        return self.ud_html_to_img_url(html)
    def by_url_write_picture(self, url, index):
        print("获取图片" + str(index) + "...................................")
        img_name = str(index) + '.jpg'
        img_path = os.path.join(self.path_name, img_name)
        if not os.path.exists(self.path_name):
            os.mkdir(self.path_name)
        if not os.path.exists(img_path):#断点下载，防止下载中断
            url = self.get_one_page(url)
            res = requests.get(url, headers=self.heads)
            if res.status_code == 200 or 304:
                print("下载图片成功")
            with open(os.path.join(self.path_name, img_name), "wb") as fs:
                fs.write(res.content)
            print("保存图片" + str(index) + '/' + str(self.img_num) + "成功...................................")
        else:
            print("图片已经存在")
    def decode_all_picture_url(self, url):
        print("解析图片地址")
        # try:

        self.driver.get(url)
        html = self.driver.page_source
        (self.img_num, self.name) = self.ud_decode_book_info(html)

        self.path_name = self.name.strip()
        self.path_name = os.path.join(self.all_name, self.path_name)#文件夹内才有压缩包,name代表当前文件夹临时文件夹
        print("解析成功,{},共{}张图片".format(self.path_name, self.img_num))
        self.not_root_all_path_file = self.path_name + '.zip'
        self.path_name = os.path.join(self.root_path, self.path_name)#path_name = root/a/b/c
        self.package_zip_name = self.name + '.zip'  #c.zip
        self.all_path_file_name = self.path_name + '.zip'  #root/a/b/c.zip
        if not os.path.exists(os.path.join(self.root_path, self.all_name)):   #创建文件夹
            os.mkdir(os.path.join(self.root_path, self.all_name))

        return self.ud_get_everpage_urls(url)
    def package(self, file_path, out_file_path):
        print("准备打包")
        with zipfile.ZipFile(out_file_path, 'a', zipfile.ZIP_DEFLATED) as zip_fs:
            for fs in os.listdir(file_path):
                zip_fs.write(os.path.join(file_path, fs), fs)
        print("打包结束")
        self.del_file(file_path)
    def packer_smb(self, file_path, out_file_path):
        print("准备打包")
        if os.path.exists(out_file_path):#文件已存在
            print("压缩包已存在，直接上传smb服务器")
            self.smb.upload(out_file_path, self.smb_upload_file_path + "/" + out_file_path)
            self.del_file(file_path)
            os.remove(out_file_path)
            print("删除缓存文件")
        else:
            with zipfile.ZipFile(out_file_path, 'a', zipfile.ZIP_DEFLATED) as zip_fs:
                for fs in os.listdir(file_path):
                    zip_fs.write(os.path.join(file_path, fs), fs)
            print("打包结束，上传smb服务器")
            self.smb.upload(out_file_path, self.smb_upload_file_path + "/" + self.not_root_all_path_file)#无根路径地址拼凑
            self.del_file(file_path)#删除所有图片，包括文件夹
            os.remove(out_file_path)
    def start_spider_one_book(self, url):
        urls = self.decode_all_picture_url(url)#可以优化
        if not os.path.exists(self.all_path_file_name):
            k = 1
            for i in urls:
                self.by_url_write_picture(i, k)
                # time.sleep(1)
                k = k + 1
            self.package(self.path_name, self.all_path_file_name)
        else:
            print(self.path_name + ", 已存在")
    def start_spider_one_book_smb(self,url):
        urls = self.decode_all_picture_url(url)  # 可以优化
        if not self.smb.is_exist(self.smb_upload_file_path, self.all_name):
            self.smb.make_dir(self.smb_upload_file_path + "/" + self.all_name)  # 远程服务器没有文件夹则创建
        if not self.smb.is_exist(self.smb_upload_file_path + "\\{}".format(self.all_name), self.package_zip_name) and not os.path.exists(self.all_path_file_name):  # smb没有文件且本地没有缓存则开始
            k = 1
            pool = ThreadPoolExecutor(max_workers=self.pool_num)

            for i in urls:
                pool.submit(self.by_url_write_picture, i, k)
                # self.by_url_write_picture(i, k)
                # time.sleep(1)
                k = k + 1
            pool.shutdown(wait=True)
            self.packer_smb(self.path_name, self.all_path_file_name)
        elif self.smb.is_exist(self.smb_upload_file_path + "/{}".format(self.all_name), self.package_zip_name) == 0 and os.path.exists(self.all_path_file_name) == 1:  # 本地有缓存，云服务器无缓存
                print(self.path_name + ", 存在本地缓存文件，准备上传")
                self.packer_smb(self.path_name, self.all_path_file_name)
    def start_spider_all_book(self, all_url):
        self.driver.get(all_url)
        html = self.driver.page_source
        root = etree.HTML(html)
        book_urls = root.xpath('//dl[@id="comiclistn"]/dd/a[2]/@href')
        self.all_name = root.xpath('/html/body/table[5]/tbody/tr/td[2]/table/tbody/tr[1]/td/table/tbody/tr[1]/td/text()')[0]
        self.all_name = re.findall(r"(.+?)漫画", self.all_name)[0]
        print("一共找到{}本书".format(str(len(book_urls))))
        for item in book_urls:
            self.start_spider_one_book(item)
    def start_spider_all_book_smb(self, all_url, host = "192.168.124.2",username = "liubo13145", password = "Lb119406450",share_dir_name = "共享", bookdir = "漫画"):
        self.add_smb_config(host, username, password, share_dir_name, bookdir)
        self.driver.get(all_url)
        html = self.driver.page_source
        (book_names, self.all_name, book_urls) = self.ud_geurl_to_book_infos(html)

        book_names = [i.replace(" ", '').replace(".", "").replace(".zip", "") for i in book_names]  # 去空格化
        if not self.smb.is_exist(self.smb_upload_file_path, self.all_name):
            self.smb.make_dir(self.smb_upload_file_path + "/" + self.all_name)  # 远程服务器没有文件夹则创建

        ok_urls = self.book_urls_filter(book_names, book_urls)
        print("一共找到{}本书".format(str(len(book_urls))),"去除重复的还需要下载{}本".format(str(len(ok_urls))))
        if len(ok_urls) == 0:
            return print("下载结束")
        for item in ok_urls:
            self.start_spider_one_book_smb(item)
        self.del_file(os.path.join(self.root_path, self.all_name) )
        print("下载结束")
    def book_urls_filter(self, names, urls):
        names_urls = list(zip(names, urls))
        current_files =  self.smb.get_all_dirlist(self.smb_upload_file_path + "/{}".format(self.all_name) )
        current_files = [i.replace(" ",'').replace(".zip", "").replace(".", "") for i in current_files] #去空格

        OK_url_name = list(filter(lambda x: x[0] not in current_files, names_urls))
        if len(OK_url_name)>1:
            ok_url = list(zip(*OK_url_name))[1]
            return ok_url
        elif len(OK_url_name) == 1:
            return [str(OK_url_name[0][1])]
        else: return []


    def ud_geurl_to_book_infos(self,html):
        root = etree.HTML(html)
        book_names = root.xpath('//dl[@id="comiclistn"]/dd/a[1]/text()')#给首页地址生成每个章节名字，返回列表
        all_name = root.xpath('/html/body/table[5]/tbody/tr/td[2]/table/tbody/tr[1]/td/table/tbody/tr[1]/td/text()')[0]
        all_name = re.findall(r"(.+?)漫画", all_name)[0] #allname = 'c'#给首页地址，返回整本漫画名，返回字符串
        urls = root.xpath('//dl[@id="comiclistn"]/dd/a[2]/@href')#给首页地址生成每个章节url，返回列表
        return (book_names, all_name, urls)
    def ud_decode_book_info(self, html):#给第一个地址生成图片总数和当前章节名字，返回二元组
        root = etree.HTML(html)
        res_info = root.xpath('/html/body/table[2]/tbody/tr/td/text()')[0]
        res_info_split = res_info.split('|')
        img_num = int(re.findall('共(.+)页', res_info_split[1])[0])#当前章节一共多少图片
        name = res_info_split[0].replace(" ", '').replace(".", "")#当前章节名字
        return (img_num, name)#给第一个地址生成每个图片网页地址地址#给第一个地址生成每个图片网页地址地址#给第一个地址生成每个图片网页地址地址
    def ud_get_everpage_urls(self, url):#给第一个地址生成每个图片网页地址地址，返回列表
        url = url.replace("/1.htm", "")
        urls = [url + "/{}.htm".format(i + 1) for i in range(self.img_num)]
        return urls
    def ud_html_to_img_url(self, html):#给网页,得图片地址,返回字符串
        root = etree.HTML(html)
        src = root.xpath("/html/body/table[2]/tbody/tr/td//img/@src")[0]
        return src
def multyple_son(url):
    myman = ikuManhua()
    myman.start_spider_all_book_smb(url)
def multyple_mon(*args):
    pool = ThreadPoolExecutor(max_workers=5)
    for i in args:
        pool.submit(multyple_son, i)
    pool.shutdown(wait = True)

if __name__ == "__main__":
    curPath = os.path.dirname(__file__)
    rootpath = str(curPath)
    url = input("请输入网址")
    myman = ikuManhua(rootpath)#x需要拿到文件路径
    myman.start_spider_all_book_smb(url)








#一拳超人 http://manhua.ikukudm.com/comiclist/2035/
#http://manhua.ikukudm.com/comiclist/2579/index.htm 悲惨的欺凌者漫画
#http://manhua.ikukudm.com/comiclist/3612/index.htm 龙锁之槛漫画
#http://manhua.ikukudm.com/comiclist/3671/index.htm 我不知道妹妹的朋友漫画
#只属于你的奴隶少女漫画 http://manhua.ikukudm.com/comiclist/3668/index.htm

#http://manhua.ikukudm.com/comiclist/3646/index.htm 后宫开在离婚时漫画
#http://manhua.ikukudm.com/comiclist/3222/index.htm 昨日勇者今为骨漫画
