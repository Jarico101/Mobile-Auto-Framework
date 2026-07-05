"""
Action Layer - 动作执行层
执行具体的操作：点击、滑动、等待等
支持拟人化轨迹（贝塞尔曲线）
"""
import time
import random
import numpy as np
from typing import Tuple, List, Optional


class BezierCurve:
    """贝塞尔曲线生成器"""

    @staticmethod
    def cubic_bezier(p0: Tuple[float, float], p1: Tuple[float, float],
                    p2: Tuple[float, float], p3: Tuple[float, float],
                    num_points: int = 50) -> List[Tuple[int, int]]:
        """
        生成三阶贝塞尔曲线
        :param p0: 起点
        :param p1: 控制点1
        :param p2: 控制点2
        :param p3: 终点
        :param num_points: 采样点数量
        :return: 轨迹点列表
        """
        points = []
        for i in range(num_points):
            t = i / (num_points - 1)
            # 三阶贝塞尔公式
            x = (1-t)**3 * p0[0] + 3*(1-t)**2*t * p1[0] + 3*(1-t)*t**2 * p2[0] + t**3 * p3[0]
            y = (1-t)**3 * p0[1] + 3*(1-t)**2*t * p1[1] + 3*(1-t)*t**2 * p2[1] + t**3 * p3[1]
            points.append((int(x), int(y)))
        return points

    @staticmethod
    def generate_humanlike_curve(start: Tuple[int, int], end: Tuple[int, int],
                                 num_points: int = 50) -> List[Tuple[int, int]]:
        """
        生成拟人化轨迹
        :param start: 起点
        :param end: 终点
        :param num_points: 采样点数量
        :return: 轨迹点列表
        """
        x0, y0 = start
        x3, y3 = end

        # 随机生成控制点（偏离直线）
        distance = np.sqrt((x3-x0)**2 + (y3-y0)**2)
        deviation = distance * random.uniform(0.1, 0.3)  # 偏离度

        # 控制点1：靠近起点
        angle1 = random.uniform(-np.pi/4, np.pi/4)
        x1 = x0 + (x3-x0)*0.33 + deviation * np.cos(angle1)
        y1 = y0 + (y3-y0)*0.33 + deviation * np.sin(angle1)

        # 控制点2：靠近终点
        angle2 = random.uniform(-np.pi/4, np.pi/4)
        x2 = x0 + (x3-x0)*0.66 + deviation * np.cos(angle2)
        y2 = y0 + (y3-y0)*0.66 + deviation * np.sin(angle2)

        return BezierCurve.cubic_bezier((x0, y0), (x1, y1), (x2, y2), (x3, y3), num_points)


class ActionExecutor:
    """动作执行器"""

    def __init__(self, device_controller):
        """
        初始化动作执行器
        :param device_controller: 设备控制器实例
        """
        self.device = device_controller
        self.last_action_time = time.time()

    def tap(self, x: int, y: int, humanlike: bool = True) -> bool:
        """
        点击屏幕
        :param x: X坐标
        :param y: Y坐标
        :param humanlike: 是否使用拟人化延迟
        :return: 是否成功
        """
        # 拟人化延迟
        if humanlike:
            delay = self._human_delay()
            time.sleep(delay)

        # 添加随机偏移（模拟手指点击不精确）
        if humanlike:
            x += random.randint(-5, 5)
            y += random.randint(-5, 5)

        result = self.device.tap(x, y)
        self.last_action_time = time.time()

        print(f"[Action] Tap at ({x}, {y})")
        return result

    def swipe_bezier(self, start: Tuple[int, int], end: Tuple[int, int],
                    duration: Optional[float] = None) -> bool:
        """
        使用贝塞尔曲线滑动
        :param start: 起点
        :param end: 终点
        :param duration: 持续时间（秒），None则随机
        :return: 是否成功
        """
        # 拟人化延迟
        delay = self._human_delay()
        time.sleep(delay)

        # 生成贝塞尔曲线轨迹
        if duration is None:
            distance = np.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
            duration = random.uniform(0.3, 0.8)  # 根据距离调整

        num_points = int(duration * 60)  # 假设60fps
        trajectory = BezierCurve.generate_humanlike_curve(start, end, num_points)

        # ADB一次性滑动（简化版，实际可以分段模拟）
        duration_ms = int(duration * 1000)
        result = self.device.swipe(start[0], start[1], end[0], end[1], duration_ms)

        self.last_action_time = time.time()
        print(f"[Action] Swipe from {start} to {end} (duration={duration:.2f}s)")

        return result

    def swipe(self, start: Tuple[int, int], end: Tuple[int, int],
             duration: int = 300) -> bool:
        """
        简单滑动（直线）
        :param start: 起点
        :param end: 终点
        :param duration: 持续时间（毫秒）
        :return: 是否成功
        """
        return self.device.swipe(start[0], start[1], end[0], end[1], duration)

    def wait(self, duration: float):
        """
        等待
        :param duration: 等待时长（秒）
        """
        print(f"[Action] Wait {duration:.2f}s")
        time.sleep(duration)
        self.last_action_time = time.time()

    def wait_random(self, min_sec: float = 0.5, max_sec: float = 2.0):
        """
        随机等待
        :param min_sec: 最小等待时间
        :param max_sec: 最大等待时间
        """
        duration = random.uniform(min_sec, max_sec)
        self.wait(duration)

    def tap_object(self, game_object, humanlike: bool = True) -> bool:
        """
        点击游戏对象（使用对象的中心点）
        :param game_object: GameObject实例
        :param humanlike: 是否拟人化
        :return: 是否成功
        """
        x, y = game_object.position
        return self.tap(x, y, humanlike)

    def _human_delay(self, min_ms: int = 100, max_ms: int = 500) -> float:
        """
        生成拟人化延迟（高斯分布）
        :param min_ms: 最小延迟（毫秒）
        :param max_ms: 最大延迟（毫秒）
        :return: 延迟时间（秒）
        """
        # 高斯分布生成延迟
        mean = (min_ms + max_ms) / 2
        std = (max_ms - min_ms) / 6  # 99.7%落在范围内
        delay_ms = np.random.normal(mean, std)

        # 限制在范围内
        delay_ms = np.clip(delay_ms, min_ms, max_ms)

        return delay_ms / 1000.0  # 转为秒

    def time_since_last_action(self) -> float:
        """返回距离上次操作的时间（秒）"""
        return time.time() - self.last_action_time


class ActionPlanner:
    """动作规划器（高级操作组合）"""

    def __init__(self, action_executor: ActionExecutor):
        """
        初始化动作规划器
        :param action_executor: 动作执行器实例
        """
        self.executor = action_executor

    def harvest_crop(self, crop_object) -> bool:
        """
        收获作物（点击+等待）
        :param crop_object: 作物对象
        :return: 是否成功
        """
        print(f"[Action] Harvesting crop: {crop_object.type}")

        # 点击作物
        if not self.executor.tap_object(crop_object):
            return False

        # 等待动画
        self.executor.wait_random(0.5, 1.0)

        return True

    def visit_next_friend(self, screen_width: int, screen_height: int) -> bool:
        """
        访问下一个好友（滑动好友列表）
        :param screen_width: 屏幕宽度
        :param screen_height: 屏幕高度
        :return: 是否成功
        """
        print("[Action] Visiting next friend")

        # 向上滑动好友列表
        start = (screen_width // 2, screen_height * 3 // 4)
        end = (screen_width // 2, screen_height // 4)

        return self.executor.swipe_bezier(start, end)

    def go_back(self, screen_width: int) -> bool:
        """
        返回上一页（点击返回按钮，通常在左上角）
        :param screen_width: 屏幕宽度
        :return: 是否成功
        """
        print("[Action] Going back")
        return self.executor.tap(50, 100)  # 假设返回按钮位置


if __name__ == '__main__':
    # 测试贝塞尔曲线
    trajectory = BezierCurve.generate_humanlike_curve((100, 100), (500, 800), 30)
    print(f"Generated trajectory with {len(trajectory)} points")
    print(f"First 5 points: {trajectory[:5]}")
