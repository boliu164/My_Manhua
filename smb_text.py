from smb.SMBConnection import SMBConnection


class MySmb:
    def __init__(self, host, username, password,share_dir_name):
        self.share_dir_name = share_dir_name
        self.host = host # ip或域名，改成你自己的
        self.username = username  # 用户名，改成你自己的
        self.password = password  # 密码，改成你自己的
        self.conn = SMBConnection(self.username, self.password, "", "", use_ntlm_v2=True)
        self.conn.connect(self.host, 445)  # smb协议默认端口445
        print("sum服务器连接成功登录成功")
    def upload(self, local_path, upload_path):
        with open(local_path,"rb") as localFile:
            self.conn.storeFile(self.share_dir_name, upload_path, localFile)
            print("上传成功")
    def download(self, local_path, download_file_path):
        with open(local_path) as fs:
            self.conn.retrieveFile(self.share_dir_name, download_file_path, fs)
    def get_all_dirlist(self, dir_path):
        f_names = list()
        for e in self.conn.listPath(self.share_dir_name, dir_path):
            if e.filename[0] != '.':  # （会返回一些.的文件，需要过滤）
                f_names.append(e.filename)
        return f_names
    def is_exist(self,dir_name, file_name):
        return file_name in self.get_all_dirlist(dir_name)
    def make_dir(self, path):
        self.conn.createDirectory(self.share_dir_name, path = path)
    def close(self):
        self.conn.close()
if __name__ == "__main__":
    sb = MySmb(host = "192.168.124.2",username = "liubo13145", password = "Lb119406450",share_dir_name = "共享")
    li = sb.get_all_dirlist("漫画/昨日勇者今为骨")
    print(li)
    sb.close()



