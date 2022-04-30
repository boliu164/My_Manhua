import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import etree
import zipfile
import re
from tkinter import *
import os
import time
from concurrent.futures import ThreadPoolExecutor
import threading
chrome_options = Options()
import os
from smb_text import MySmb
class aiManhua:
    def __init__(self):
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
        chrome_options.add_experimental_option("prefs", self.prefs)

        chrome_options.add_argument('--headless')

        self.driver = webdriver.Chrome(options=chrome_options)

    def del_file(self, path_data):
        """
            删除文件夹下所有文件
        :param path_data:   文件夹路径，绝对路径
        :return:
        """
        for i in os.listdir(path_data):  # os.listdir(path_data)#返回一个列表，里面是当前目录下面的所有东西的相对路径
            file_data = path_data + "\\" + i  # 当前文件夹的下面的所有东西的绝对路径
            if os.path.isfile(file_data):  # os.path.isfile判断是否为文件,如果是文件,就删除.如果是文件夹.递归给del_file.
                os.remove(file_data)
            else:
                self.del_file(file_data)
        os.removedirs(path_data)

    def get_one_page(self, url):
        self.driver.get(url)
        html = self.driver.page_source

        root = etree.HTML(html)

        res = root.xpath("//tbody/tr/td/img/@src")
        src = "https:" + res[0]
        return src
    def by_url_write_picture(self, url, index):
        print("获取图片" + str(index )+ "...................................")
        img_name = str(index) + '.jpg'
        res = requests.get(url, headers= self.heads)
        if res.status_code == 200 or 304:
            print("下载图片成功")
        if not os.path.exists(self.path_name):
          os.mkdir(self.path_name)
        with open(os.path.join(self.path_name, img_name), "wb") as fs:
            fs.write(res.content)
        print("保存图片" + str(index) + '/' + self.img_num +"成功...................................")
    def decode_all_picture_url(self, url):
        print("解析图片地址")
        self.driver.get(url)
        html = self.driver.page_source
        root = etree.HTML(html)
        res = root.xpath('//span[@id="k_total"]/text()')

        self.path_name = root.xpath('/html/body/div[2]/h1/a/text()')[0] + root.xpath('/html/body/div[2]/h2/text()')[0]
        print("解析成功,{},共{}张图片".format(self.path_name, res[0]))
        self.img_num = res[0]
        return [url + "?p={}".format(i+1) for i in range(int(res[0]))]
    def package(self, file_path, out_file_path):
        print("准备打包")
        with zipfile.ZipFile(out_file_path, 'a', zipfile.ZIP_DEFLATED) as zip_fs:
            for fs in os.listdir(file_path):
                zip_fs.write(os.path.join(file_path, fs), fs)
        print("打包结束")
        self.del_file(file_path)
    def start_spider_on_book(self, url):
      urls = self.decode_all_picture_url(url)
      k = 1
      for i in urls:
          picture_url = self.get_one_page(i)
          self.by_url_write_picture(picture_url, k)
          # time.sleep(1)
          k = k + 1
      self.package(self.path_name, self.path_name + ".zip")

class ikuManhua:
    def __init__(self):
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
        chrome_options.add_experimental_option("prefs", self.prefs)
        self.is_smb = 0
        chrome_options.add_argument('--headless')

        self.driver = webdriver.Chrome(options=chrome_options)
    def add_smb_config(self, host, username, password,share_dir_name, bookdir):
        self.is_smb = 1
        self.smb = MySmb(host,username,password,share_dir_name )
        self.smb_upload_file_path = bookdir
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
        self.driver.get(url)
        html = self.driver.page_source

        root = etree.HTML(html)

        src = root.xpath("/html/body/table[2]/tbody/tr/td//img/@src")[0]
        return src
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
        try:
            self.driver.get(url)
            html = self.driver.page_source
            root = etree.HTML(html)
            res_info = root.xpath('/html/body/table[2]/tbody/tr/td/text()')[0]
        except IndexError as err:
            print("切换图片地址")
            url = url.replace("//a", "//b")
            self.driver.get(url)
            html = self.driver.page_source
            root = etree.HTML(html)
            res_info = root.xpath('/html/body/table[2]/tbody/tr/td/text()')[0]

        res_info_split = res_info.split('|')
        self.img_num = int(re.findall('共(.+)页', res_info_split[1])[0])
        self.name = res_info_split[0].replace(" ",'')#去空格
        if not os.path.exists(self.all_name):   #创建文件夹
            os.mkdir(self.all_name)
        self.path_name = self.name.strip()
        self.path_name = os.path.join(self.all_name, self.path_name)#文件夹内才有压缩包,name代表当前文件夹临时文件夹
        print("解析成功,{},共{}张图片".format(self.path_name, self.img_num))
        url = url.replace("/1.htm","")    #path_name = a/b/c
        self.package_zip_name = self.name + '.zip'  #c.zip
        self.all_path_file_name = self.path_name + '.zip'  #a/b/c.zip
        return [url + "/{}.htm".format(i + 1) for i in range(self.img_num)]

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
            self.smb.upload(out_file_path, self.smb_upload_file_path + "/" + out_file_path)
            self.del_file(file_path)
            os.remove(out_file_path)
    def start_spider_one_book(self, url):
        urls = self.decode_all_picture_url(url)#可以优化
        if not os.path.exists(self.path_name + ".zip"):
            k = 1

            for i in urls:
                self.by_url_write_picture(i, k)
                # time.sleep(1)
                k = k + 1

            self.package(self.path_name, self.path_name + ".zip")
        else:
            print(self.path_name + ", 已存在")
    def start_spider_one_book_smb(self,url):
        urls = self.decode_all_picture_url(url)  # 可以优化
        if not self.smb.is_exist(self.smb_upload_file_path, self.all_name):
            self.smb.make_dir(self.smb_upload_file_path + "/" + self.all_name)  # 远程服务器没有文件夹则创建
        if not self.smb.is_exist(self.smb_upload_file_path + "\\{}".format(self.all_name), self.package_zip_name) and not os.path.exists(self.all_path_file_name):  # smb没有文件且本地没有缓存则开始
            k = 1
            # pool = ThreadPoolExecutor(max_workers=5)

            for i in urls:
                # pool.submit(self.by_url_write_picture, i, k)
                self.by_url_write_picture(i, k)
                # time.sleep(1)
                k = k + 1
            # pool.shutdown(wait=True)
            self.packer_smb(self.path_name, self.path_name + ".zip")
        elif self.smb.is_exist(self.smb_upload_file_path + "/{}".format(self.all_name), self.package_zip_name) == 0 and os.path.exists(self.all_path_file_name) == 1:  # 本地有缓存，云服务器无缓存
                print(self.path_name + ", 存在本地缓存文件，准备上传")
                self.packer_smb(self.path_name, self.path_name + ".zip")

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
        root = etree.HTML(html)
        book_names = root.xpath('//dl[@id="comiclistn"]/dd/a[1]/text()')
        book_names = [i.replace(" ",'') + ".zip" for i in book_names]
        self.all_name = root.xpath('/html/body/table[5]/tbody/tr/td[2]/table/tbody/tr[1]/td/table/tbody/tr[1]/td/text()')[0]

        self.all_name = re.findall(r"(.+?)漫画", self.all_name)[0]

        if not self.smb.is_exist(self.smb_upload_file_path, self.all_name):
            self.smb.make_dir(self.smb_upload_file_path + "/" + self.all_name)  # 远程服务器没有文件夹则创建
        book_urls = root.xpath('//dl[@id="comiclistn"]/dd/a[2]/@href')
        ok_urls = self.book_urls_filter(book_names, book_urls)
        print("一共找到{}本书".format(str(len(book_urls))),"去除重复的还需要下载{}本".format(str(len(ok_urls))))
        if len(ok_urls) == 0:
            return print("下载结束")
        for item in ok_urls:
            self.start_spider_one_book_smb(item)
        self.del_file(self.all_name)
        print("下载结束")
    def book_urls_filter(self, names, urls):
        names_urls = list(zip(names, urls))
        current_files =  self.smb.get_all_dirlist(self.smb_upload_file_path + "/{}".format(self.all_name) )
        current_files = [i.replace(" ",'') for i in current_files] #去空格
        OK_url_name = list(filter(lambda x: x[0] not in current_files, names_urls))
        if len(OK_url_name)>1:
            ok_url = list(zip(*OK_url_name))[1]
            return ok_url
        elif len(OK_url_name) == 1:
            return OK_url_name[0][1]
        else: return []
def multyple_son(url):
    myman = ikuManhua()
    myman.start_spider_all_book_smb(url)
def multyple_mon(*args):
    pool = ThreadPoolExecutor(max_workers=5)
    for i in args:
        pool.submit(multyple_son, i)
    pool.shutdown(wait = True)

if __name__ == "__main__":
    pass
    # myman = ikuManhua()
    # myman.start_spider_all_book_smb("http://manhua.ikukudm.com/comiclist/2384/")
    # multyple_mon("http://manhua.ikukudm.com/comiclist/3646/index.htm","http://manhua.ikukudm.com/comiclist/3222/index.htm","http://manhua.ikukudm.com/comiclist/2579/index.htm", "http://manhua.ikukudm.com/comiclist/3612/index.htm ", "http://manhua.ikukudm.com/comiclist/3671/index.htm")






#用无敌的扭蛋运成名漫画  http://manhua.ikukudm.com/comiclist/3224/index.htm
#http://manhua.ikukudm.com/comiclist/2579/index.htm 悲惨的欺凌者漫画
#http://manhua.ikukudm.com/comiclist/3612/index.htm 龙锁之槛漫画
#http://manhua.ikukudm.com/comiclist/3671/index.htm 我不知道妹妹的朋友漫画
#只属于你的奴隶少女漫画 http://manhua.ikukudm.com/comiclist/3668/index.htm

#http://manhua.ikukudm.com/comiclist/3646/index.htm 后宫开在离婚时漫画
#http://manhua.ikukudm.com/comiclist/3222/index.htm 昨日勇者今为骨漫画
