from tkinter import *
import os

class ManHuaGui:
    def __init__(self):
        self.root = Tk()
        self.root.title("First self.root")
        screenheight = self.root.winfo_screenheight()# screenheight 屏幕高度
        screenwidth = self.root.winfo_screenwidth()  # screenwidth 屏幕宽度
        size = self.tk_center(600, 300, screenwidth, screenheight)


        self.root.geometry(size)
        #根窗口完毕

        #第一组合框
        fr1 = Frame(self.root, relief='groove', bd=1, bg = "red")
        fr1.grid(column=0, row=0, columnspan = 1,padx=1)

        self.fr1_btn1 = Button(fr1,width=120, text="账号", bg="orange", fg="red", command=self.clicked_bt_1,padx=1)
        self.fr1_btn2 = Button(fr1,width=120, text="本地", bg="orange", fg="red", command=self.clicked_bt_1,padx=1)
        self.fr1_btn3 = Button(fr1,width=120, text="设置", bg="orange", fg="red", command=self.clicked_bt_1,padx=1)
        self.fr1_btn4 = Button(fr1,width=120, text="网页", bg="orange", fg="red", command=self.clicked_bt_1,padx=1)
        self.fr1_btn5 = Button(fr1,width=120, text="更新", bg="orange", fg="red", command=self.clicked_bt_1,padx=1)
        self.fr1_btn1.grid(column=0, row=0, columnspan=1)
        self.fr1_btn2.grid(column=1, row=0, columnspan=1)
        self.fr1_btn3.grid(column=2, row=0, columnspan=1)
        self.fr1_btn4.grid(column=3, row=0, columnspan=1)
        self.fr1_btn5.grid(column=4, row=0, columnspan=1)






        lbl = Label(self.root, text="Hello")
        lbl.grid(column=0, row=2)

        self.btn1 = Button(self.root,width=1, text="Click Me", bg="orange", fg="red", command=self.clicked_bt_1)
        self.btn1.grid(column=0, row=3, columnspan = 1) #columspan 占用多少列，column定位的列
        self.root.mainloop()

    def tk_center(self,width, height, screen_width, screen_height):
        x = int(screen_width / 2 - width / 2)
        y = int(screen_height / 2 - height / 2)
        size = '{}x{}+{}+{}'.format(width, height, x, y)
        return size
    def clicked_bt_1(self):
        # lbl.configure(text="Button was clicked!")
        # self.btn1.config(width = str(self.btn1.cget("width")+1))#获取组件信息
        self.root.update()
        print(self.fr1_btn1.winfo_width())
        print(self.root.winfo_width())



if __name__ == "__main__":
    myman = ManHuaGui()