import cv2
import numpy as np
import turtle
import math
from dataclasses import dataclass
from typing import List, Tuple, Union
import os


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

