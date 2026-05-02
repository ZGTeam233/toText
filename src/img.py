"""
处理图像为字符画的模块
Copyright(c) 2026 Zilin Zheng,
licensing under the Apache-2.0 License (see LICENSE for details).
"""

from PIL import Image

class Img():
    """处理图像为字符画的类"""

    def __init__(self, imgName):
        self.imgFile = Image.open(imgName).convert('RGB')
        self.width, self.height = self.imgFile.size
        """字符集，按照从密集到稀疏的顺序排列，越密集的字符表示灰度越高"""
        self.serarr = ['@', '%', '#', '&', '$',
                       'W', 'M', 'H', 'N', 'B',
                       'w', 'm', 'p', 'k', 'q',
                       'b', 'd', 'a', 'z', '*',
                       '?', '^', '~', '-', '_',
                       ':', ';', ',', '"', "'",
                       '`', '.', ' ']

    def resizePercent(self, w, h):
        self.width, self.height = int(self.width * w), int(self.height * h)
        self.imgFile = self.imgFile.resize((self.width, self.height))

    def toText(self):
        count = 255 / (len(self.serarr) - 1)
        asd = "" # 结果
        for h in range(self.height):
            for w in range(self.width):
                r, g, b = self.imgFile.getpixel((w, h))
                gray = r * 0.299 + g * 0.587 + b * 0.114
                asd += self.serarr[int(gray / count)]
            asd += "\n" # LF换行
        return asd