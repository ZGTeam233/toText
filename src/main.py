"""
Copyright(c) 2026 Zilin Zheng,
licensing under the Apache-2.0 License (see LICENSE for details).
"""
from img import *
from ascii_player import *

def image2text():
    img = Img("in.png")
    img.resizePercent(0.6, 0.2) # 修正 英文/半角 字符较为细长导致的变形
    tmp = open("test.txt","w")
    tmp.write(img.toText())
    tmp.close()

def multi2text(f):
    f = f.strip()
    n = int(f)
    width = len(f)
    for i in range(n):
        formatted_number = str(i).zfill(width)
        imgName = "./in/in_" + str(formatted_number) + ".jpg"
        textName = "./test/test_" + str(formatted_number) + ".txt"
        img = Img(imgName)
        img.resizePercent(0.6, 0.2)
        tmp = open(textName,"w")
        tmp.write(img.toText())
        tmp.close()

def ascii_player():
    player = AsciiAnimationPlayer()
    player.run()

def main():
    print("一个转字符画的小程序")
    print("功能列表：")
    print("1. 单张图片in.png转字符画")
    print("2. 多张图片in_{z0}.jpg转字符画")
    print("3. 字符动画播放器")
    print("0. 退出")
    choice = int(input("请选择："))
    if choice == 1:
        image2text()
        print("完成")
    elif choice == 2:
        multi2text(input("请输入图片数量："))
        print("完成")
    elif choice == 3:
        ascii_player()
    else:
        return

if __name__ == "__main__":
    main()