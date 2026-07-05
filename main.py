"""
Main Loop - 主控制循环
整合所有模块，实现感知-决策-执行闭环
"""
import time
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.device.device_controller import DeviceController
from src.capture.screen_capture import ScreenCapture
from src.perception.perception_engine import PerceptionEngine
from src.world.world_model import WorldModel
from src.fsm.game_fsm import GameFSM
from src.rules.rule_engine import GameRuleEngine
from src.action.action_executor import ActionExecutor, ActionPlanner


class GameBot:
    """游戏机器人主控制器"""

    def __init__(self, config: dict = None):
        """
        初始化机器人
        :param config: 配置字典
        """
        self.config = config or {}
        self.running = False

        # 初始化各层
        print("[Bot] Initializing modules...")
        self.device = DeviceController()
        self.capture = ScreenCapture()
        self.perception = PerceptionEngine()
        self.world = WorldModel()
        self.fsm = GameFSM()
        self.rule_engine = GameRuleEngine()
        self.executor = ActionExecutor(self.device)
        self.planner = ActionPlanner(self.executor)

        # 统计信息
        self.stats = {
            'loops': 0,
            'actions': 0,
            'errors': 0,
            'start_time': None
        }

    def start(self) -> bool:
        """
        启动机器人
        :return: 是否成功启动
        """
        print("[Bot] Starting...")

        # 连接设备
        if not self.device.connect():
            print("[Bot] Failed to connect device")
            return False

        # 获取屏幕信息
        screen_size = self.device.get_screen_size()
        if screen_size:
            print(f"[Bot] Screen size: {screen_size}")
            self.config['screen_width'] = screen_size[0]
            self.config['screen_height'] = screen_size[1]
        else:
            print("[Bot] Warning: Could not get screen size")

        self.running = True
        self.stats['start_time'] = time.time()
        print("[Bot] Started successfully")

        return True

    def stop(self):
        """停止机器人"""
        print("[Bot] Stopping...")
        self.running = False
        self.device.disconnect()
        self._print_stats()
        print("[Bot] Stopped")

    def run(self, max_loops: int = None):
        """
        运行主循环
        :param max_loops: 最大循环次数（None=无限）
        """
        if not self.start():
            return

        print("[Bot] Entering main loop...")
        print("=" * 50)

        try:
            while self.running:
                # 检查循环次数限制
                if max_loops and self.stats['loops'] >= max_loops:
                    print(f"[Bot] Reached max loops: {max_loops}")
                    break

                # 执行一次循环
                self._loop_iteration()

                # 循环延迟
                loop_delay = self.config.get('loop_delay', 1.0)
                time.sleep(loop_delay)

        except KeyboardInterrupt:
            print("\n[Bot] Interrupted by user")
        except Exception as e:
            print(f"[Bot] Fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop()

    def _loop_iteration(self):
        """单次循环迭代"""
        self.stats['loops'] += 1
        print(f"\n[Bot] Loop #{self.stats['loops']}")
        print("-" * 50)

        try:
            # 1. Capture - 截图
            image = self.capture.screenshot_fast()
            if image is None:
                print("[Bot] Screenshot failed, skipping")
                self.stats['errors'] += 1
                return

            # 2. Perception - 感知
            perception_result = self.perception.perceive(image)
            print(f"[Bot] Detected {len(perception_result['detections'])} objects")

            # 3. World State - 更新世界状态
            self.world.update_from_perception(perception_result)

            # 4. FSM - 更新状态机
            context = {
                'world': self.world,
                'fsm': self.fsm,
                'image': image
            }
            self.fsm.update(context)
            print(f"[Bot] Current state: {self.fsm.get_current_state().value}")

            # 5. Rule Engine - 决策
            decision = self.rule_engine.decide(context)

            if decision is None:
                print("[Bot] No decision made, idle")
                return

            # 6. Action - 执行动作
            print(f"[Bot] Decision: {decision}")
            self._execute_action(decision)
            self.stats['actions'] += 1

        except Exception as e:
            print(f"[Bot] Loop error: {e}")
            self.stats['errors'] += 1

    def _execute_action(self, decision):
        """
        执行决策动作
        :param decision: 决策对象
        """
        action = decision.action
        params = decision.params

        # 根据动作类型执行
        if action == "harvest":
            # 收获成熟作物
            crops = self.world.get_mature_crops()
            if crops:
                self.planner.harvest_crop(crops[0])

        elif action == "harvest_mutated":
            # 收获变异作物
            crops = self.world.get_mutated_crops()
            if crops:
                self.planner.harvest_crop(crops[0])

        elif action == "next_friend":
            # 访问下一个好友
            w = self.config.get('screen_width', 1080)
            h = self.config.get('screen_height', 1920)
            self.planner.visit_next_friend(w, h)

        elif action == "wait":
            # 等待
            duration = params.get('duration', 1.0)
            self.executor.wait(duration)

        elif action == "explore":
            # 探索（随机点击）
            print("[Bot] Exploring...")
            self.executor.wait_random(1.0, 3.0)

        else:
            print(f"[Bot] Unknown action: {action}")

    def _print_stats(self):
        """打印统计信息"""
        print("\n" + "=" * 50)
        print("[Bot] Statistics:")
        print(f"  Total loops: {self.stats['loops']}")
        print(f"  Total actions: {self.stats['actions']}")
        print(f"  Errors: {self.stats['errors']}")

        if self.stats['start_time']:
            duration = time.time() - self.stats['start_time']
            print(f"  Runtime: {duration:.2f}s")
            if duration > 0:
                print(f"  Loop rate: {self.stats['loops']/duration:.2f} loops/s")
        print("=" * 50)


def main():
    """主入口"""
    print("""
╔════════════════════════════════════════════════╗
║   Mobile Automation Framework                 ║
║   感知-决策-执行闭环系统                        ║
╚════════════════════════════════════════════════╝
    """)

    # 配置
    config = {
        'loop_delay': 0.5,  # 循环延迟（秒）
        'yolo_model': 'data/models/best.pt',
    }

    # 创建并运行机器人
    bot = GameBot(config)
    bot.run(max_loops=100)  # 运行100次循环测试


if __name__ == '__main__':
    main()
