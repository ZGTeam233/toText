from img import Img

def image2text():
    img = Img("in.png")
    img.resizePercent(0.6, 0.2) # 修正 英文/半角 字符较为细长导致的变形
    tmp = open("test.txt","w")
    tmp.write(img.toText())
    tmp.close()

def main():
    image2text()

if __name__ == "__main__":
    main()