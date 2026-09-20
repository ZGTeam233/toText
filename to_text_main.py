#
# Copyright(c) 2026 ZGTeam233.
# licensing under the Apache-2.0 License.
# See LICENSE for details
#

"""
以下包含

1. 处理图像为字符画的模块

2. 字符动画播放器 - 基于 Pygame
功能：播放 /src/test/test_{z0}.txt 序列字符画文件
使用：运行后通过 CLI 交互设置参数，播放完自动退出
"""

from PIL import Image
import os
import sys
import time
from pathlib import Path
import cv2
import numpy as np
import turtle
import math
from dataclasses import dataclass
from typing import List, Tuple, Union

try:
    import pygame
    from pygame.locals import *
except ImportError:
    print("错误: 需要安装 Pygame 库")
    print("请运行: pip install pygame")
    sys.exit(1)

class AsciiAnimationPlayer:
    """ASCII 字符动画播放器"""

    def __init__(self):
        self.screen = None
        self.clock = None
        self.font = None
        self.running = False

        # 默认参数
        self.params = {
            "font_size": 8,  # 字号
            "total_frames": 0,  # 总帧数
            "fps": 24,  # 帧率
        }

        # 字符画帧缓存
        self.frames = []

    def cli_interact(self):
        """命令行交互获取参数"""
        print("=" * 50)
        print("ASCII 字符动画播放器")
        print("=" * 50)
        print("字符画文件路径: ./test/test_*.txt")
        print()

        # 获取参数
        while True:
            try:
                font_size = input("请输入字号 (默认 8): ").strip()
                self.params["font_size"] = int(font_size) if font_size else 8
                if self.params["font_size"] <= 0:
                    print("字号必须大于 0")
                    continue
                break
            except ValueError:
                print("请输入有效的数字")

        while True:
            try:
                total_frames = input("请输入总帧数 (必需): ").strip()
                self.params["total_frames"] = int(total_frames)
                if self.params["total_frames"] <= 0:
                    print("总帧数必须大于 0")
                    continue
                break
            except ValueError:
                print("请输入有效的数字")

        while True:
            try:
                fps = input("请输入播放帧率 (默认 24): ").strip()
                self.params["fps"] = int(fps) if fps else 24
                if self.params["fps"] <= 0:
                    print("帧率必须大于 0")
                    continue
                break
            except ValueError:
                print("请输入有效的数字")

        # 确认播放
        print("\n播放设置:")
        print(f"  字号: {self.params['font_size']}")
        print(f"  总帧数: {self.params['total_frames']}")
        print(f"  帧率: {self.params['fps']} FPS")
        print()

        confirm = input("确认开始播放? (y/N): ").strip().lower()
        if confirm != 'y':
            print("播放已取消")
            sys.exit(0)

    def load_frames(self):
        """加载字符画帧（支持自动补零格式）"""
        print(f"\n正在加载 {self.params['total_frames']} 帧...")

        # 计算数字部分需要的宽度（即需要补几个零）
        # 例如：总帧数=255 -> 最大索引=254 -> 位数=3 -> 格式为 001, 002, ..., 254
        max_index = self.params["total_frames"] - 1
        num_width = len(str(max_index))  # 计算最大数字的位数

        print(
            f"文件名格式: test_{{0:{num_width}d}}.txt (例如: test_{0:0{num_width}d}.txt 到 test_{max_index:0{num_width}d}.txt)")

        for i in range(self.params["total_frames"]):
            # 使用动态计算的宽度进行补零格式化
            file_name = f"test_{i:0{num_width}d}.txt"
            file_path = Path(f"./test/{file_name}")

            if not file_path.exists():
                # 如果补零格式找不到，尝试不补零的旧格式（向后兼容）
                old_file_path = Path(f"./test/test_{i}.txt")
                if old_file_path.exists():
                    print(f"注意: 使用旧格式文件 test_{i}.txt")
                    file_path = old_file_path
                else:
                    print(f"错误: 找不到文件 {file_name} 或 test_{i}.txt")
                    return False

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.frames.append(content)
            except Exception as e:
                print(f"错误: 无法读取文件 {file_path}: {e}")
                return False

        print(f"加载完成，共 {len(self.frames)} 帧")
        return True

    def init_pygame(self):
        """初始化 Pygame"""
        pygame.init()

        # 设置全屏
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("ASCII 字符动画播放器")

        # 设置时钟
        self.clock = pygame.time.Clock()

        # 加载字体
        font_used = "未知字体"
        try:
            # 尝试使用 Consolas，这是 Windows 上优秀的等宽字体
            self.font = pygame.font.SysFont("Consolas", self.params["font_size"])
            font_used = "Consolas"
        except:
            try:
                # 回退到 Courier New
                self.font = pygame.font.SysFont("Courier New", self.params["font_size"])
                font_used = "Courier New"
            except:
                # 最后使用默认字体
                self.font = pygame.font.SysFont(None, self.params["font_size"])
                font_used = "默认字体"

        print(f"使用字体: {font_used}, 字号: {self.params['font_size']}")

    def render_frame(self, frame_index):
        """渲染一帧字符画"""
        if frame_index >= len(self.frames):
            return False

        # 清屏
        self.screen.fill((255, 255, 255))  # 白色背景

        # 获取字符画内容
        frame_content = self.frames[frame_index]
        lines = frame_content.split('\n')

        # 计算起始位置（居中显示）
        line_height = self.font.get_linesize()
        total_height = len(lines) * line_height

        # 如果字符画太高，从顶部开始显示
        start_y = 0

        # 渲染每一行
        for i, line in enumerate(lines):
            if line:  # 只渲染非空行
                # 黑色字符
                text_surface = self.font.render(line, True, (0, 0, 0))
                self.screen.blit(text_surface, (0, start_y + i * line_height))

        # 更新显示
        pygame.display.flip()

        return True

    def play_animation(self):
        """播放动画"""
        print("\n开始播放...")
        print("提示: 按 ESC 键可提前结束播放")

        frame_delay = 1000 / self.params["fps"]  # 每帧的毫秒数
        start_time = pygame.time.get_ticks()
        frame_count = 0
        self.running = True

        while self.running and frame_count < len(self.frames):
            # 处理事件
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False

            # 渲染当前帧
            if self.render_frame(frame_count):
                frame_count += 1

            # 控制帧率
            self.clock.tick(self.params["fps"])

        # 播放完成
        end_time = pygame.time.get_ticks()
        duration = (end_time - start_time) / 1000.0

        print(f"\n播放完成!")
        print(f"播放帧数: {frame_count}")
        print(f"实际时长: {duration:.2f} 秒")
        print(f"平均帧率: {frame_count / duration:.2f} FPS")

        # 等待 3 秒
        print("3秒后自动退出...")
        pygame.time.wait(3000)

    def run(self):
        """运行播放器"""
        # CLI 交互
        self.cli_interact()

        # 加载帧
        if not self.load_frames():
            print("错误: 加载帧失败")
            return

        # 初始化 Pygame
        self.init_pygame()

        # 播放动画
        self.play_animation()

        # 清理
        pygame.quit()
        print("\n播放器已退出")

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

def turtle_line():
    TARGET_IMAGE = "in.png"
    if not os.path.exists(TARGET_IMAGE):
        print(f"提示: 未找到 '{TARGET_IMAGE}'。请放置图片或修改路径。")
    else:
        app = App(TARGET_IMAGE)
        app.run()

# ==========================================
# 1. 数据模型定义
# ==========================================
@dataclass
class MoveToStep:
    x: float
    y: float


@dataclass
class DrawToStep:
    distance: float
    angle: float
    x: float
    y: float


Path = List[Union[MoveToStep, DrawToStep]]


# ==========================================
# 2. 图像处理类
# ==========================================
class ImageVectorizer:
    def __init__(self, image_path: str, max_width: int = 1000):
        self.image_path = image_path
        # 提高 max_width 以保留更多原始细节，避免缩放导致的模糊
        self.max_width = max_width
        self.img_width = 0
        self.img_height = 0

    def extract_paths(self) -> Tuple[List[Path], int, int]:
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"找不到图片文件: {self.image_path}")

        img = cv2.imread(self.image_path)
        h, w = img.shape[:2]
        self.img_width, self.img_height = w, h

        if w > self.max_width:
            scale = self.max_width / w
            img = cv2.resize(img, (int(w * scale), int(h * scale)))
            self.img_width, self.img_height = img.shape[1], img.shape[0]

        # 1. 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. 高斯模糊：轻微模糊以消除图片压缩带来的高频噪点，使线条更平滑
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        # 3. 自适应二值化：比 Canny 更适合提取线稿。
        # 它能根据局部邻域计算阈值，提取出单像素宽度的纯净线条，避免 Canny 产生的“双线”问题。
        # 参数 11 是邻域大小，2 是常数偏移量（值越大，提取的线条越细）
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )

        # 4. 提取轮廓
        contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        all_paths: List[Path] = []

        for contour in contours:
            # 过滤掉极小的噪点
            if cv2.contourArea(contour) < 10:
                continue

            # 5. 降低 epsilon 值以提高曲线拟合精度。
            # 值越小，保留的拐点越多，线条越平滑细腻；值越大，折线感越强。
            epsilon = 0.05 # 注：原来0.5
            approx = cv2.approxPolyDP(contour, epsilon, True)

            current_path: Path = []

            for i, point in enumerate(approx):
                x_cv, y_cv = point[0]
                x_t = x_cv - self.img_width / 2
                y_t = -(y_cv - self.img_height / 2)

                if i == 0:
                    current_path.append(MoveToStep(x=x_t, y=y_t))
                else:
                    prev_step = current_path[-1]
                    dx = x_t - prev_step.x
                    dy = y_t - prev_step.y

                    distance = math.hypot(dx, dy)
                    angle = math.degrees(math.atan2(dy, dx))

                    current_path.append(DrawToStep(
                        distance=distance,
                        angle=angle,
                        x=x_t,
                        y=y_t
                    ))

            if len(current_path) > 1:
                all_paths.append(current_path)

        return all_paths, self.img_width, self.img_height


# ==========================================
# 3. Turtle 绘制类
# ==========================================
class TurtleRenderer:
    def __init__(self, width: int, height: int, bg_color: str = "white", pen_color: str = "black"):
        self.width = width
        self.height = height

        self.screen = turtle.Screen()
        self.screen.setup(width=self.width + 100, height=self.height + 100)
        self.screen.title("High-Precision Turtle Drawing")
        self.screen.bgcolor(bg_color)

        self.pen = turtle.Turtle()
        # 线条变细了，画笔粗细也相应调细，以匹配高精度
        self.pen.pensize(1.5) # 原来1.0
        self.pen.pencolor(pen_color)
        self.pen.speed(0)

    def draw(self, paths: List[Path], use_relative_movement: bool = False, update_interval: int = 1):
        """
        :param update_interval: 每绘制多少步刷新一次屏幕
                                值越小，动画越细腻但越慢
        """
        self.screen.tracer(0, 0)

        step_counter = 0
        total_steps = sum(len(path) for path in paths)
        print(f"开始绘制，共 {total_steps} 个绘制步骤。")

        for path in paths:
            start_step = path[0]
            self.pen.penup()
            self.pen.goto(start_step.x, start_step.y)
            self.pen.pendown()

            for step in path[1:]:
                if isinstance(step, DrawToStep):
                    if use_relative_movement:
                        self.pen.setheading(step.angle)
                        self.pen.forward(step.distance)
                    else:
                        self.pen.goto(step.x, step.y)

                    step_counter += 1
                    if step_counter >= update_interval:
                        self.screen.update()
                        step_counter = 0

        self.screen.update()
        print("绘制完成！")

    def keep_alive(self):
        turtle.done()


# ==========================================
# 4. 主控类
# ==========================================
class App:
    def __init__(self, image_path: str):
        self.image_path = image_path

    def run(self):
        try:
            print(f"正在处理图片: {self.image_path} ...")
            # 使用更高的 max_width 保留细节
            vectorizer = ImageVectorizer(self.image_path, max_width=1400) # 注：原来1000
            paths, w, h = vectorizer.extract_paths()
            print(f"提取完成！共找到 {len(paths)} 条独立线条路径。")

            if not paths:
                print("未检测到有效线条，请尝试更换对比度更高的图片。")
                return

            print("正在启动 Turtle 绘制引擎...")
            renderer = TurtleRenderer(width=w, height=h, bg_color="white", pen_color="black")

            # 精度提高后，点数可能会增加
            # 注：原来update_interval=50
            renderer.draw(paths, use_relative_movement=False, update_interval=80)
            renderer.keep_alive()

        except Exception as e:
            print(f"运行出错: {e}")

def main():
    print("一个转字符画的小程序")
    print("功能列表：")
    print("1. 单张图片in.png转字符画")
    print("2. 多张图片in_{z0}.jpg转字符画")
    print("3. 字符动画播放器")
    print("4. turtle绘画")
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
    elif choice == 4:
        turtle_line()
    else:
        return

if __name__ == "__main__":
    main()