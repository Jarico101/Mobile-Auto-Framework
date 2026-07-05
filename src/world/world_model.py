"""
World State - 世界状态模型
维护游戏当前状态的数据结构
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time


class GameState(Enum):
    """游戏状态枚举"""
    UNKNOWN = "unknown"
    MAIN_MENU = "main_menu"
    FRIEND_LIST = "friend_list"
    FARM_VIEW = "farm_view"
    SHOP_VIEW = "shop_view"
    LOADING = "loading"


@dataclass
class GameObject:
    """游戏对象"""
    id: str
    type: str  # mature, mutated, price_tag等
    position: tuple  # (x, y)
    bbox: tuple  # (x1, y1, x2, y2)
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class WorldState:
    """世界状态"""
    current_state: GameState = GameState.UNKNOWN
    objects: List[GameObject] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_update: float = field(default_factory=time.time)

    def add_object(self, obj: GameObject):
        """添加游戏对象"""
        self.objects.append(obj)

    def clear_objects(self):
        """清空对象列表"""
        self.objects.clear()

    def find_objects_by_type(self, obj_type: str) -> List[GameObject]:
        """根据类型查找对象"""
        return [obj for obj in self.objects if obj.type == obj_type]

    def get_object_by_id(self, obj_id: str) -> Optional[GameObject]:
        """根据ID查找对象"""
        for obj in self.objects:
            if obj.id == obj_id:
                return obj
        return None

    def update(self):
        """更新时间戳"""
        self.last_update = time.time()

    def age(self) -> float:
        """返回状态年龄（秒）"""
        return time.time() - self.last_update


class WorldModel:
    """世界模型管理器"""

    def __init__(self):
        """初始化世界模型"""
        self.state = WorldState()
        self.history: List[WorldState] = []
        self.max_history = 10

    def update_from_perception(self, perception_result: Dict):
        """
        从感知结果更新世界状态
        :param perception_result: 感知引擎的输出
        """
        # 保存历史状态
        if len(self.history) >= self.max_history:
            self.history.pop(0)
        # 深拷贝当前状态保存
        import copy
        self.history.append(copy.deepcopy(self.state))

        # 清空当前对象
        self.state.clear_objects()

        # 从检测结果创建游戏对象
        detections = perception_result.get('detections', [])
        for idx, detection in enumerate(detections):
            obj = GameObject(
                id=f"{detection.label}_{idx}",
                type=detection.label,
                position=detection.center,
                bbox=detection.bbox,
                confidence=detection.confidence
            )
            self.state.add_object(obj)

        # 更新时间戳
        self.state.update()

    def get_state(self) -> WorldState:
        """获取当前状态"""
        return self.state

    def set_game_state(self, game_state: GameState):
        """设置游戏状态"""
        self.state.current_state = game_state
        print(f"[World] Game state changed to: {game_state.value}")

    def get_mature_crops(self) -> List[GameObject]:
        """获取所有成熟的作物"""
        return self.state.find_objects_by_type('mature')

    def get_mutated_crops(self) -> List[GameObject]:
        """获取所有变异作物"""
        return self.state.find_objects_by_type('mutated')

    def get_price_tags(self) -> List[GameObject]:
        """获取所有价格标签"""
        return self.state.find_objects_by_type('price_tag')

    def has_objects(self, obj_type: str) -> bool:
        """检查是否存在某类对象"""
        return len(self.state.find_objects_by_type(obj_type)) > 0

    def count_objects(self, obj_type: str) -> int:
        """统计某类对象的数量"""
        return len(self.state.find_objects_by_type(obj_type))


if __name__ == '__main__':
    # 测试世界模型
    world = WorldModel()
    world.set_game_state(GameState.FARM_VIEW)
    print(f"Current state: {world.get_state().current_state}")
