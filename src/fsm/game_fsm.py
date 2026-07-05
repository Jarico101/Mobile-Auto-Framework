"""
FSM - 有限状态机
管理游戏页面/状态的识别和转换
"""
from enum import Enum
from typing import Optional, Callable, Dict
import time


class State(Enum):
    """状态枚举"""
    UNKNOWN = "unknown"
    MAIN_MENU = "main_menu"
    FRIEND_LIST = "friend_list"
    FARM_VIEW = "farm_view"
    SHOP_VIEW = "shop_view"
    LOADING = "loading"
    ERROR = "error"


class Transition:
    """状态转换"""
    def __init__(self, from_state: State, to_state: State,
                 condition: Callable, action: Optional[Callable] = None):
        """
        :param from_state: 源状态
        :param to_state: 目标状态
        :param condition: 转换条件（返回bool的函数）
        :param action: 转换时执行的动作（可选）
        """
        self.from_state = from_state
        self.to_state = to_state
        self.condition = condition
        self.action = action


class FSM:
    """有限状态机"""

    def __init__(self, initial_state: State = State.UNKNOWN):
        """
        初始化状态机
        :param initial_state: 初始状态
        """
        self.current_state = initial_state
        self.previous_state = None
        self.transitions: Dict[State, list] = {}
        self.state_enter_callbacks: Dict[State, list] = {}
        self.state_exit_callbacks: Dict[State, list] = {}
        self.last_transition_time = time.time()

    def add_transition(self, transition: Transition):
        """
        添加状态转换
        :param transition: 转换规则
        """
        if transition.from_state not in self.transitions:
            self.transitions[transition.from_state] = []
        self.transitions[transition.from_state].append(transition)

    def add_state_callback(self, state: State, on_enter: Optional[Callable] = None,
                          on_exit: Optional[Callable] = None):
        """
        添加状态回调
        :param state: 状态
        :param on_enter: 进入状态时的回调
        :param on_exit: 退出状态时的回调
        """
        if on_enter:
            if state not in self.state_enter_callbacks:
                self.state_enter_callbacks[state] = []
            self.state_enter_callbacks[state].append(on_enter)

        if on_exit:
            if state not in self.state_exit_callbacks:
                self.state_exit_callbacks[state] = []
            self.state_exit_callbacks[state].append(on_exit)

    def update(self, context: Dict) -> bool:
        """
        更新状态机（检查转换条件）
        :param context: 上下文数据（世界状态等）
        :return: 是否发生了状态转换
        """
        if self.current_state not in self.transitions:
            return False

        # 检查所有可能的转换
        for transition in self.transitions[self.current_state]:
            if transition.condition(context):
                # 执行转换
                self._transition_to(transition.to_state)

                # 执行转换动作
                if transition.action:
                    transition.action(context)

                return True

        return False

    def _transition_to(self, new_state: State):
        """
        执行状态转换
        :param new_state: 新状态
        """
        if new_state == self.current_state:
            return

        # 执行退出回调
        if self.current_state in self.state_exit_callbacks:
            for callback in self.state_exit_callbacks[self.current_state]:
                callback()

        # 更新状态
        self.previous_state = self.current_state
        self.current_state = new_state
        self.last_transition_time = time.time()

        print(f"[FSM] State transition: {self.previous_state.value} -> {self.current_state.value}")

        # 执行进入回调
        if self.current_state in self.state_enter_callbacks:
            for callback in self.state_enter_callbacks[self.current_state]:
                callback()

    def force_state(self, new_state: State):
        """
        强制设置状态（不检查条件）
        :param new_state: 新状态
        """
        self._transition_to(new_state)

    def get_current_state(self) -> State:
        """获取当前状态"""
        return self.current_state

    def time_in_current_state(self) -> float:
        """返回在当前状态停留的时间（秒）"""
        return time.time() - self.last_transition_time


class GameFSM(FSM):
    """游戏状态机（预定义转换规则）"""

    def __init__(self):
        super().__init__(initial_state=State.UNKNOWN)
        self._setup_transitions()

    def _setup_transitions(self):
        """设置转换规则"""
        # UNKNOWN -> 其他状态（通过检测特征判断）
        self.add_transition(Transition(
            from_state=State.UNKNOWN,
            to_state=State.MAIN_MENU,
            condition=lambda ctx: self._is_main_menu(ctx)
        ))

        self.add_transition(Transition(
            from_state=State.UNKNOWN,
            to_state=State.FRIEND_LIST,
            condition=lambda ctx: self._is_friend_list(ctx)
        ))

        self.add_transition(Transition(
            from_state=State.UNKNOWN,
            to_state=State.FARM_VIEW,
            condition=lambda ctx: self._is_farm_view(ctx)
        ))

        # FARM_VIEW <-> FRIEND_LIST
        self.add_transition(Transition(
            from_state=State.FARM_VIEW,
            to_state=State.FRIEND_LIST,
            condition=lambda ctx: self._is_friend_list(ctx)
        ))

        self.add_transition(Transition(
            from_state=State.FRIEND_LIST,
            to_state=State.FARM_VIEW,
            condition=lambda ctx: self._is_farm_view(ctx)
        ))

        # 任何状态 -> LOADING
        for state in State:
            if state != State.LOADING:
                self.add_transition(Transition(
                    from_state=state,
                    to_state=State.LOADING,
                    condition=lambda ctx: self._is_loading(ctx)
                ))

    def _is_main_menu(self, context: Dict) -> bool:
        """判断是否在主菜单（根据世界状态）"""
        # TODO: 根据检测到的UI元素判断
        return False

    def _is_friend_list(self, context: Dict) -> bool:
        """判断是否在好友列表"""
        # TODO: 根据检测到的UI元素判断
        return False

    def _is_farm_view(self, context: Dict) -> bool:
        """判断是否在农场视图"""
        world = context.get('world')
        if not world:
            return False

        # 如果检测到成熟作物或变异作物，认为在农场视图
        mature_count = world.count_objects('mature')
        mutated_count = world.count_objects('mutated')

        return (mature_count + mutated_count) > 0

    def _is_loading(self, context: Dict) -> bool:
        """判断是否在加载"""
        # TODO: 检测加载图标
        return False


if __name__ == '__main__':
    # 测试状态机
    fsm = GameFSM()
    print(f"Initial state: {fsm.get_current_state()}")
