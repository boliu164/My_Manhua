import os

from ikuManhua import ikuManhua
from  ZxkaManhua import  ZxkaManhua



if __name__ == "__main__":
    curPath = os.path.dirname(__file__)
    rootpath = str(curPath)
    url = input("请输入网址")
    myman = ikuManhua(rootpath)#x需要拿到文件路径
    myman.start_spider_all_book_smb(url)
