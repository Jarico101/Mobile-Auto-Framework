"""
Rule Engine - 规则引擎
基于当前状态做出决策
"""
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
import random


@dataclass
class Rule:
    """规则定义"""
    name: str
    condition: Callable[[Dict], bool]  # 条件函数
    action: str  # 动作名称
    priority: int = 0  # 优先级（数字越大越优先）
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class Decision:
    """决策结果"""
    def __init__(self, action: str, params: Dict[str, Any] = None, reason: str = ""):
        """
        :param action: 动作名称
        :param params: 动作参数
        :param reason: 决策理由
        """
        self.action = action
        self.params = params if params else {}
        self.reason = reason

    def __repr__(self):
        return f"Decision(action={self.action}, params={self.params}, reason={self.reason})"


class RuleEngine:
    """规则引擎"""

    def __init__(self):
        """初始化规则引擎"""
        self.rules: List[Rule] = []

    def add_rule(self, rule: Rule):
        """
        添加规则
        :param rule: 规则对象
        """
        self.rules.append(rule)
        # 按优先级排序（高优先级在前）
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def decide(self, context: Dict) -> Optional[Decision]:
        """
        根据当前上下文做出决策
        :param context: 上下文（包含world, fsm等）
        :return: 决策结果或None
        """
        # 按优先级遍历规则
        for rule in self.rules:
            try:
                if rule.condition(context):
                    decision = Decision(
                        action=rule.action,
                        params=rule.metadata,
                        reason=f"Rule: {rule.name}"
                    )
                    print(f"[Rule] Matched: {rule.name} -> {rule.action}")
                    return decision
            except Exception as e:
                print(f"[Rule] Error evaluating rule '{rule.name}': {e}")
                continue

        return None


class GameRuleEngine(RuleEngine):
    """游戏规则引擎（预定义规则）"""

    def __init__(self):
        super().__init__()
        self._setup_rules()

    def _setup_rules(self):
        """设置游戏规则"""

        # 规则1: 发现成熟作物 -> 收获（优先级高）
        self.add_rule(Rule(
            name="harvest_mature_crop",
            condition=lambda ctx: self._has_mature_crops(ctx),
            action="harvest",
            priority=100
        ))

        # 规则2: 发现变异作物 -> 优先收获（优先级最高）
        self.add_rule(Rule(
            name="harvest_mutated_crop",
            condition=lambda ctx: self._has_mutated_crops(ctx),
            action="harvest_mutated",
            priority=200
        ))

        # 规则3: 没有可收获作物 -> 访问下一个好友
        self.add_rule(Rule(
            name="visit_next_friend",
            condition=lambda ctx: self._no_harvestable_crops(ctx),
            action="next_friend",
            priority=50
        ))

        # 规则4: 检测到价格标签 -> 读取价格
        self.add_rule(Rule(
            name="check_price",
            condition=lambda ctx: self._has_price_tags(ctx),
            action="read_price",
            priority=150
        ))

        # 规则5: 在加载状态 -> 等待
        self.add_rule(Rule(
            name="wait_loading",
            condition=lambda ctx: self._is_loading(ctx),
            action="wait",
            priority=300,
            metadata={'duration': 2}
        ))

        # 规则6: 状态未知 -> 探索
        self.add_rule(Rule(
            name="explore",
            condition=lambda ctx: self._is_unknown_state(ctx),
            action="explore",
            priority=10
        ))

    def _has_mature_crops(self, context: Dict) -> bool:
        """是否有成熟作物"""
        world = context.get('world')
        if not world:
            return False
        return world.count_objects('mature') > 0

    def _has_mutated_crops(self, context: Dict) -> bool:
        """是否有变异作物"""
        world = context.get('world')
        if not world:
            return False
        return world.count_objects('mutated') > 0

    def _no_harvestable_crops(self, context: Dict) -> bool:
        """没有可收获作物"""
        world = context.get('world')
        if not world:
            return False
        mature = world.count_objects('mature')
        mutated = world.count_objects('mutated')
        return (mature + mutated) == 0

    def _has_price_tags(self, context: Dict) -> bool:
        """是否有价格标签"""
        world = context.get('world')
        if not world:
            return False
        return world.count_objects('price_tag') > 0

    def _is_loading(self, context: Dict) -> bool:
        """是否在加载"""
        from src.fsm.game_fsm import State
        fsm = context.get('fsm')
        if not fsm:
            return False
        return fsm.get_current_state() == State.LOADING

    def _is_unknown_state(self, context: Dict) -> bool:
        """状态是否未知"""
        from src.fsm.game_fsm import State
        fsm = context.get('fsm')
        if not fsm:
            return True
        return fsm.get_current_state() == State.UNKNOWN


class StrategySelector:
    """策略选择器（高级决策）"""

    def __init__(self):
        """初始化策略选择器"""
        self.strategies = {}
        self.current_strategy = None

    def register_strategy(self, name: str, rule_engine: RuleEngine):
        """
        注册策略
        :param name: 策略名称
        :param rule_engine: 规则引擎实例
        """
        self.strategies[name] = rule_engine
        print(f"[Strategy] Registered: {name}")

    def select_strategy(self, name: str) -> bool:
        """
        选择策略
        :param name: 策略名称
        :return: 是否成功
        """
        if name in self.strategies:
            self.current_strategy = self.strategies[name]
            print(f"[Strategy] Selected: {name}")
            return True
        return False

    def decide(self, context: Dict) -> Optional[Decision]:
        """
        使用当前策略做决策
        :param context: 上下文
        :return: 决策结果
        """
        if self.current_strategy is None:
            print("[Strategy] No strategy selected")
            return None

        return self.current_strategy.decide(context)


if __name__ == '__main__':
    # 测试规则引擎
    engine = GameRuleEngine()
    print(f"[Rule] Loaded {len(engine.rules)} rules")
