"""
字符动画播放器 - 基于 Pygame
功能：播放 /src/test/test_{z0}.txt 序列字符画文件
使用：运行后通过 CLI 交互设置参数，播放完自动退出
"""

import os
import sys
import time
from pathlib import Path

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
