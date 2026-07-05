"""
Perception Layer - 感知层
负责图像识别：YOLO目标检测 + OCR文字识别
"""
from typing import List, Dict, Optional, Tuple
import numpy as np


class Detection:
    """检测结果"""
    def __init__(self, label: str, confidence: float, bbox: Tuple[int, int, int, int]):
        """
        :param label: 类别标签
        :param confidence: 置信度
        :param bbox: 边界框 (x1, y1, x2, y2)
        """
        self.label = label
        self.confidence = confidence
        self.bbox = bbox  # (x1, y1, x2, y2)

    @property
    def center(self) -> Tuple[int, int]:
        """返回中心点坐标"""
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    @property
    def area(self) -> int:
        """返回面积"""
        x1, y1, x2, y2 = self.bbox
        return (x2 - x1) * (y2 - y1)

    def __repr__(self):
        return f"Detection(label={self.label}, conf={self.confidence:.2f}, bbox={self.bbox})"


class YOLODetector:
    """YOLO目标检测器"""

    def __init__(self, model_path: str = "data/models/best.pt", conf_threshold: float = 0.5):
        """
        初始化YOLO检测器
        :param model_path: 模型路径
        :param conf_threshold: 置信度阈值
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.model = None
        self.initialized = False

    def initialize(self) -> bool:
        """
        初始化模型（延迟加载）
        :return: 是否成功
        """
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            self.initialized = True
            print(f"[YOLO] Model loaded from {self.model_path}")
            return True
        except ImportError:
            print("[YOLO] ultralytics not installed. Run: pip install ultralytics")
            return False
        except Exception as e:
            print(f"[YOLO] Model load failed: {e}")
            return False

    def detect(self, image: np.ndarray) -> List[Detection]:
        """
        检测图像中的目标
        :param image: numpy数组图像 (H, W, 3) BGR格式
        :return: 检测结果列表
        """
        if not self.initialized:
            if not self.initialize():
                return []

        try:
            # YOLO推理
            results = self.model(image, conf=self.conf_threshold, verbose=False)

            detections = []
            for result in results:
                boxes = result.boxes
                for i in range(len(boxes)):
                    # 提取信息
                    bbox = boxes.xyxy[i].cpu().numpy().astype(int)  # (x1, y1, x2, y2)
                    conf = float(boxes.conf[i].cpu().numpy())
                    cls_id = int(boxes.cls[i].cpu().numpy())
                    label = result.names[cls_id]

                    detection = Detection(
                        label=label,
                        confidence=conf,
                        bbox=tuple(bbox)
                    )
                    detections.append(detection)

            return detections

        except Exception as e:
            print(f"[YOLO] Detection error: {e}")
            return []

    def detect_by_label(self, image: np.ndarray, label: str) -> List[Detection]:
        """
        检测指定类别的目标
        :param image: 图像
        :param label: 类别标签
        :return: 该类别的检测结果
        """
        all_detections = self.detect(image)
        return [d for d in all_detections if d.label == label]


class OCRReader:
    """OCR文字识别器"""

    def __init__(self):
        """初始化OCR"""
        self.ocr = None
        self.initialized = False

    def initialize(self) -> bool:
        """
        初始化PaddleOCR（延迟加载）
        :return: 是否成功
        """
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)
            self.initialized = True
            print("[OCR] PaddleOCR initialized")
            return True
        except ImportError:
            print("[OCR] paddleocr not installed. Run: pip install paddleocr")
            return False
        except Exception as e:
            print(f"[OCR] Initialization failed: {e}")
            return False

    def read_text(self, image: np.ndarray) -> List[Dict]:
        """
        识别图像中的文字
        :param image: numpy数组图像
        :return: 识别结果列表 [{'text': str, 'confidence': float, 'bbox': [...]}]
        """
        if not self.initialized:
            if not self.initialize():
                return []

        try:
            result = self.ocr.ocr(image, cls=True)

            texts = []
            if result and result[0]:
                for line in result[0]:
                    bbox = line[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    text_info = line[1]  # (text, confidence)

                    texts.append({
                        'text': text_info[0],
                        'confidence': text_info[1],
                        'bbox': bbox
                    })

            return texts

        except Exception as e:
            print(f"[OCR] Read error: {e}")
            return []

    def read_numbers(self, image: np.ndarray) -> List[int]:
        """
        识别图像中的数字（专用于价格识别）
        :param image: numpy数组图像
        :return: 识别到的数字列表
        """
        texts = self.read_text(image)
        numbers = []

        for item in texts:
            text = item['text']
            # 提取数字
            import re
            nums = re.findall(r'\d+', text)
            for num_str in nums:
                try:
                    numbers.append(int(num_str))
                except ValueError:
                    continue

        return numbers


class PerceptionEngine:
    """感知引擎 - 整合YOLO和OCR"""

    def __init__(self, yolo_model_path: str = "data/models/best.pt"):
        """
        初始化感知引擎
        :param yolo_model_path: YOLO模型路径
        """
        self.yolo = YOLODetector(model_path=yolo_model_path)
        self.ocr = OCRReader()

    def perceive(self, image: np.ndarray) -> Dict:
        """
        完整感知流程：目标检测 + 文字识别
        :param image: 输入图像
        :return: 感知结果字典
        """
        # YOLO检测
        detections = self.yolo.detect(image)

        # OCR识别（可选，按需调用）
        # texts = self.ocr.read_text(image)

        result = {
            'detections': detections,
            'image_shape': image.shape
        }

        return result

    def find_target(self, image: np.ndarray, label: str) -> Optional[Detection]:
        """
        查找指定类别的目标（返回置信度最高的）
        :param image: 图像
        :param label: 目标类别
        :return: 检测结果或None
        """
        detections = self.yolo.detect_by_label(image, label)
        if not detections:
            return None

        # 返回置信度最高的
        return max(detections, key=lambda d: d.confidence)

    def read_price(self, image: np.ndarray, price_bbox: Tuple[int, int, int, int]) -> Optional[int]:
        """
        读取价格区域的数字
        :param image: 完整图像
        :param price_bbox: 价格区域边界框 (x1, y1, x2, y2)
        :return: 识别到的价格或None
        """
        # 裁剪价格区域
        x1, y1, x2, y2 = price_bbox
        price_region = image[y1:y2, x1:x2]

        # OCR识别数字
        numbers = self.ocr.read_numbers(price_region)

        if numbers:
            return numbers[0]  # 返回第一个识别到的数字
        return None


if __name__ == '__main__':
    # 测试感知引擎
    engine = PerceptionEngine()
    print("[Perception] Engine initialized")
