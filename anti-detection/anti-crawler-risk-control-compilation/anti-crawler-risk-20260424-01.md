# 验证码攻防（上）：从传统文本到图形识别，基础破解全攻略

> 来源: 微信公众号：反爬破解社
> 原始发布时间: 2026-04-24
> 归档日期: 2026-07-13
> 分类: anti-detection
>
> 在数字世界的入口处，一场持续20年的攻防战从未停歇。从简单的扭曲文字到复杂的AI验证，验证码技术已进化四代。今天，让我们深入战场最前线，揭秘验证码破解的核心技术。

>
> 在数字世界的入口处，一场持续20年的攻防战从未停歇。从简单的扭曲文字到复杂的AI验证，验证码技术已进化四代。今天，让我们深入战场最前线，揭秘验证码破解的核心技术。

##  一、验证码演进史：从简单验证到AI对抗

让我们先来看看验证码技术是如何一步步演进的：

###  1.1 四代验证码技术路线图

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    第一代：文本识别时代（2000-2010）   ├── 扭曲文本：字母数字变形   ├── 干扰线条：随机曲线干扰   └── 背景噪声：点状、网格噪声第二代：图形识别时代（2010-2018）   ├── 图片点选："点击包含红绿灯的图片"   ├── 图片旋转："旋转图片到正确角度"   └── 图片分类："选择所有包含桥梁的图片"第三代：行为分析时代（2018-2022）   ├── 滑块验证：缺口滑块匹配   ├── 轨迹验证：鼠标移动轨迹分析   └── 无感验证：静默行为分析第四代：AI对抗时代（2022-至今）   ├── 3D物体识别：三维空间验证   ├── 视频理解：动态内容理解   ├── 逻辑推理：简单数学/逻辑问题   └── 多模态验证：图片+文字+语音


###  1.2 2026年验证码市场份额分布

根据最新统计，当前市场上各类验证码的使用比例为：

  * ** 行为验证码  ** （滑块、轨迹）：35%

  * ** 无感验证码  ** ：25%

  * ** 图形验证码  ** （点选、旋转）：20%

  * ** AI验证码  ** ：15%

  * ** 传统文本验证码  ** ：5%

可以看到，  ** 传统的文本验证码虽然市场份额已降至5%，但仍然在一些老系统中存在  **
。更重要的是，理解基础验证码的破解原理，是我们学习更高级破解技术的基础。

##  二、第一代验证码：文本识别的破解艺术


###  2.1 传统文本验证码的技术原理

传统的文本验证码主要通过以下几种方式增加识别难度：

  1. ** 字符扭曲  ** ：将字符进行非线性变形

  2. ** 干扰线条  ** ：在字符上叠加随机曲线

  3. ** 背景噪声  ** ：添加点状、网格或彩色噪声

  4. ** 字符粘连  ** ：让字符之间部分重叠

  5. ** 颜色变化  ** ：使用多种颜色显示字符


###  2.2 完整的文本验证码破解器

下面是一个完整的传统文本验证码破解器实现，支持多种破解策略：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    import cv2import numpy as npimport pytesseractfrom PIL import Imagefrom collections import Counter# ===================== 重要配置 =====================# 必须指定你的 Tesseract 安装路径（Windows 必改，Linux/Mac 可注释）pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'# ====================================================class TraditionalCaptchaSolver:    """传统文本验证码破解器（优化版）"""
        def __init__(self):        # OCR引擎配置        self.tesseract_langs = {            'en': 'eng',            'zh': 'chi_sim',            'en+zh': 'eng+chi_sim'        }
        def preprocess_image(self, image, method='adaptive'):        """        图像预处理增强        参数:            image: 输入图片路径 / 字节流            method: 预处理方法        返回:            预处理后的二值图片        """        # 读取图片（兼容路径和字节流）        if isinstance(image, str):            img = cv2.imread(image)        else:            img = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
            if img is None:            raise ValueError("无法读取图片，请检查路径或图片数据")
            # 转为灰度图        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # 去噪（新增：大幅提升OCR效果）        gray = cv2.medianBlur(gray, 3)
            if method == 'adaptive':            # 自适应二值化            binary = cv2.adaptiveThreshold(                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,                cv2.THRESH_BINARY_INV, 11, 2            )        elif method == 'otsu':            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)        elif method == 'grayscale':            binary = gray
            return binary
        def remove_interference_lines(self, image):        """去除验证码干扰线"""        # 水平线        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))        horizontal = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel)
            # 垂直线        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))        vertical = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel)
            # 去除线条        result = cv2.subtract(image, horizontal)        result = cv2.subtract(result, vertical)        return result
        def recognize_tesseract(self, image, lang='en+zh'):        """Tesseract OCR 识别（优化版）"""        processed = self.preprocess_image(image, method='adaptive')        processed = self.remove_interference_lines(processed)
            # 最优OCR参数：单字识别、忽略空白        custom_config = f'--oem 3 --psm 8 -l {self.tesseract_langs[lang]} -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            # 转PIL格式（避免OpenCV格式兼容问题）        pil_img = Image.fromarray(processed)        text = pytesseract.image_to_string(pil_img, config=custom_config)
            # 清洗结果：只保留字母数字        clean_text = ''.join(filter(str.isalnum, text))        return clean_text.strip()
        def solve_captcha(self, image_path, method='ensemble'):        """综合识别验证码（投票机制）"""        results = []
            # 方法1：Tesseract 多策略识别        if method in ['tesseract', 'ensemble']:            try:                # 自适应阈值                res1 = self.recognize_tesseract(image_path, lang='en')                # OTSU阈值                res2 = self.recognize_tesseract(image_path, lang='en')                # 灰度模式                res3 = self.recognize_tesseract(image_path, lang='en')
                    for res in [res1, res2, res3]:                    if res and 4 <= len(res) <= 6:  # 通用验证码长度                        results.append(res)            except Exception as e:                print(f"识别失败: {str(e)}")
            # 投票选择最可信结果        if results:            counter = Counter(results)            final_text, votes = counter.most_common(1)[0]            print(f" 最终识别结果: {final_text} (置信度: {votes}/{len(results)})")            return final_text
            print(" 未能识别出有效验证码")        return ''# 使用示例if __name__ == "__main__":    solver = TraditionalCaptchaSolver()
        # 替换成你的验证码图片路径    captcha_path = "sample_captcha.png"    result = solver.solve_captcha(captcha_path)
        print(f"\n最终验证码：{result}")


###  2.3 实战：破解带干扰线的验证码

让我们看一个具体的实战案例，破解一个带有干扰线和背景噪声的验证码：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    def crack_complex_captcha(image_path):    """    破解复杂验证码的完整流程    步骤：    1. 颜色分离 - 去除彩色干扰    2. 噪声去除 - 移除背景噪声    3. 字符分割 - 分离单个字符    4. 字符识别 - 识别每个字符    """    # 1. 读取图片    img = cv2.imread(image_path)    # 2. 颜色分离：去除红色干扰线    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)    # 定义红色的HSV范围    lower_red1 = np.array([0, 50, 50])    upper_red1 = np.array([10, 255, 255])    lower_red2 = np.array([170, 50, 50])    upper_red2 = np.array([180, 255, 255])    # 创建红色掩码    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)    red_mask = cv2.bitwise_or(mask1, mask2)    # 反转掩码，去除红色    not_red_mask = cv2.bitwise_not(red_mask)    img_no_red = cv2.bitwise_and(img, img, mask=not_red_mask)    # 3. 转为灰度并二值化    gray = cv2.cvtColor(img_no_red, cv2.COLOR_BGR2GRAY)    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)    # 4. 去除小噪声点    kernel = np.ones((2, 2), np.uint8)    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)    # 5. 字符分割    contours, _ = cv2.findContours(        cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE    )    char_images = []    for contour in contours:        x, y, w, h = cv2.boundingRect(contour)        # 过滤太小的区域        if w * h < 50 or w < 5 or h < 5:            continue        # 提取字符区域        char_img = cleaned[y:y+h, x:x+w]        # 统一大小        char_img = cv2.resize(char_img, (32, 32))        char_images.append((char_img, (x, y, w, h)))    # 6. 按x坐标排序    char_images.sort(key=lambda c: c[1][0])    # 7. 识别每个字符    result_text = ""    for char_img, _ in char_images:        # 这里可以调用OCR识别单个字符        # 为简化示例，我们假设已经识别        pass    return result_text


##  三、第二代验证码：图形点选与目标检测


###  3.1 图片点选验证码的技术原理


图片点选验证码是目前最常见的一种图形验证码，其基本原理是：

  1. ** 目标检测  ** ：让用户识别并点击图片中的特定物体

  2. ** 自然语言理解  ** ：通过文字描述指定要点击的目标

  3. ** 行为验证  ** ：分析点击位置、时间间隔等行为特征


###  3.2 基于YOLO的目标检测破解


YOLO（You Only Look Once）是目前最流行的实时目标检测算法之一。下面我们使用YOLOv5来破解图片点选验证码：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    import torchfrom PIL import Imageimport cv2import numpy as npclass ImageClickCaptchaSolver:    """图片点选验证码破解器"""    def __init__(self):        # 加载YOLOv5模型        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)        # COCO数据集类别名称        self.class_names = [            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train',            'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',            'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep',            'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella',            'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard',            'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard',            'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork',            'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair',            'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv',            'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',            'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',            'scissors', 'teddy bear', 'hair drier', 'toothbrush'        ]    def detect_objects(self, image):        """        检测图片中的所有物体        返回: 包含物体类别、位置和置信度的列表        """        if isinstance(image, str):            img = Image.open(image)        else:            img = Image.fromarray(image)        # 使用YOLO进行目标检测        results = self.model(img)        detections = []        for *xyxy, conf, cls in results.xyxy[0]:            if conf > 0.5:  # 置信度阈值设为0.5                x1, y1, x2, y2 = map(int, xyxy)                label = self.class_names[int(cls)]                detections.append({                    'label': label,                    'confidence': float(conf),                    'bbox': (x1, y1, x2, y2),                    'center': ((x1 + x2) // 2, (y1 + y2) // 2)                })        return detections    def match_prompt(self, prompt, detections):        """        根据提示文字匹配物体        例如：提示"点击所有包含自行车的图片"        会匹配所有标签为'bicycle'的物体        """        prompt = prompt.lower()        matched_objects = []        # 常见提示词到类别标签的映射        keyword_mapping = {            '自行车': ['bicycle', 'bike'],            '汽车': ['car', 'automobile'],            '公交车': ['bus'],            '火车': ['train'],            '摩托车': ['motorcycle'],            '船': ['boat', 'ship'],            '飞机': ['airplane'],            '红绿灯': ['traffic light'],            '交通标志': ['stop sign'],            '动物': ['bird', 'cat', 'dog', 'horse', 'sheep', 'cow'],            '人': ['person'],        }        # 查找匹配的关键词        target_labels = []        for chinese, english_labels in keyword_mapping.items():            if chinese in prompt:                target_labels.extend(english_labels)        # 如果没找到中文匹配，尝试英文直接匹配        if not target_labels:            for label in self.class_names:                if label in prompt:                    target_labels.append(label)        # 过滤匹配的检测结果        for detection in detections:            detection_label = detection['label'].lower()            if any(target in detection_label for target in target_labels):                matched_objects.append(detection)        return matched_objects    def solve_click_captcha(self, image_path, prompt):        """        解决图片点选验证码        参数:            image_path: 图片路径            prompt: 提示文字，如"点击所有自行车"        返回:            click_positions: 需要点击的位置列表        """        # 1. 检测图片中的物体        detections = self.detect_objects(image_path)        if not detections:            print("未检测到任何物体")            return []        # 2. 根据提示匹配物体        matched = self.match_prompt(prompt, detections)        if not matched:            print(f"提示'{prompt}'未匹配到任何物体")            return []        # 3. 计算点击位置（点击每个匹配物体的中心点）        click_positions = [obj['center'] for obj in matched]        print(f"检测到{len(detections)}个物体，匹配到{len(matched)}个目标")        print(f"点击位置: {click_positions}")        return click_positions# 使用示例if __name__ == "__main__":    solver = ImageClickCaptchaSolver()    # 示例：破解包含自行车的验证码    image_path = "captcha_with_bikes.jpg"    prompt = "点击所有自行车"    click_positions = solver.solve_click_captcha(image_path, prompt)    # 模拟点击    for i, (x, y) in enumerate(click_positions):        print(f"点击位置 {i+1}: ({x}, {y})")


###  3.3 实战：处理复杂场景的图片点选


在实际应用中，图片点选验证码可能会更复杂。下面是一个处理复杂场景的增强版破解器：

  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    import torchimport torchvisionfrom torchvision import transformsfrom PIL import Imageimport cv2import numpy as npimport warningswarnings.filterwarnings("ignore")# 基础类（你之前的）class ImageClickCaptchaSolver:    """图片点选验证码破解器"""
        def __init__(self):        print("正在加载 YOLOv5 模型...")        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, trust_repo=True)        self.model.conf = 0.45        self.model.iou = 0.45        self.class_names = self.model.names    def detect_objects(self, image):        if isinstance(image, str):            img = cv2.imread(image)            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)        elif isinstance(image, np.ndarray):            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)        else:            img_rgb = np.array(image)        results = self.model(img_rgb)        detections = []
            for *xyxy, conf, cls in results.xyxy[0]:            x1, y1, x2, y2 = map(int, xyxy)            label = self.class_names[int(cls)]            center = ((x1 + x2) // 2, (y1 + y2) // 2)            detections.append({                'label': label,                'confidence': round(float(conf), 2),                'bbox': (x1, y1, x2, y2),                'center': center            })        return detections    def match_prompt(self, prompt, detections):        prompt = prompt.lower()        target_labels = []        keyword_map = {            "自行车": ["bicycle"], "摩托": ["motorcycle"], "汽车": ["car"],            "公交车": ["bus"], "火车": ["train"], "飞机": ["airplane"], "船": ["boat"],            "人": ["person"], "猫": ["cat"], "狗": ["dog"], "鸟": ["bird"],            "红绿灯": ["traffic light"], "杯子": ["cup"], "瓶子": ["bottle"],            "手机": ["cell phone"], "键盘": ["keyboard"], "书": ["book"], "时钟": ["clock"]        }        for cn_key, en_labels in keyword_map.items():            if cn_key in prompt:                target_labels = en_labels                break        if not target_labels:            for cls_name in self.class_names.values():                if cls_name in prompt:                    target_labels.append(cls_name)        return [obj for obj in detections if obj["label"] in target_labels]    def draw_result(self, image_path, detections, matched_objects):        img = cv2.imread(image_path)        for obj in detections:            x1, y1, x2, y2 = obj["bbox"]            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)        for obj in matched_objects:            x1, y1, x2, y2 = obj["bbox"]            cx, cy = obj["center"]            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)            cv2.circle(img, (cx, cy), 5, (0, 0, 255), -1)        cv2.imshow("Result", img)        cv2.waitKey(0)        cv2.destroyAllWindows()    def solve_click_captcha(self, image_path, prompt, draw=True):        detections = self.detect_objects(image_path)        if not detections:            print("未检测到物体")            return []        matched = self.match_prompt(prompt, detections)        if not matched:            print("未匹配到目标")            return []        positions = [obj["center"] for obj in matched]        if draw:            self.draw_result(image_path, detections, matched)        return positions# ===================== 你要的 增强多模型集成版 =====================class EnhancedImageClickSolver(ImageClickCaptchaSolver):    """增强版：YOLOv5 + Faster R-CNN 双模型集成，准确率更高"""
        def __init__(self):        super().__init__()        print("正在加载 Faster R-CNN 模型...")        self.models = {            'yolov5': self.model,            'faster_rcnn': self.load_faster_rcnn()        }        self.transform = transforms.Compose([transforms.ToTensor()])    def load_faster_rcnn(self):        try:            model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)            model.eval()            return model        except Exception as e:            print("Faster R-CNN 加载失败", e)            return None    def detect_with_frcnn(self, image):        if self.models['faster_rcnn'] is None:            return []        if isinstance(image, str):            image = Image.open(image).convert("RGB")        elif isinstance(image, np.ndarray):            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))        img_tensor = self.transform(image).unsqueeze(0)        with torch.no_grad():            pred = self.models['faster_rcnn'](img_tensor)[0]        detections = []        for box, score, label in zip(pred["boxes"], pred["scores"], pred["labels"]):            if score < 0.5:                continue            x1, y1, x2, y2 = map(int, box)            label_name = self.class_names[label.item() - 1]            detections.append({                "label": label_name,                "confidence": round(float(score), 2),                "bbox": (x1, y1, x2, y2),                "center": ((x1 + x2) // 2, (y1 + y2) // 2)            })        return detections    def fuse_detections(self, all_detections):        if not all_detections:            return []        boxes = []        scores = []        labels = []        centers = []        for model_name, d in all_detections:            boxes.append(d["bbox"])            scores.append(d["confidence"])            labels.append(d["label"])            centers.append(d["center"])        if len(boxes) == 0:            return []        indices = cv2.dnn.NMSBoxes(boxes, scores, score_threshold=0.5, nms_threshold=0.4)        if len(indices) == 0:            return []        final = []        for i in indices.flatten():            final.append({                "label": labels[i],                "confidence": scores[i],                "bbox": boxes[i],                "center": centers[i]            })        return final    def ensemble_detection(self, image):        all_dets = []        yolo = self.detect_objects(image)        all_dets += [("yolo", d) for d in yolo]        if self.models["faster_rcnn"]:            frcnn = self.detect_with_frcnn(image)            all_dets += [("frcnn", d) for d in frcnn]        return self.fuse_detections(all_dets)    # 重写破解函数 → 使用多模型集成结果    def solve_click_captcha(self, image_path, prompt, draw=True):        detections = self.ensemble_detection(image_path)        if not detections:            print(" 多模型未检测到任何物体")            return []        matched = self.match_prompt(prompt, detections)        if not matched:            print(f" 未匹配：{prompt}")            return []        positions = [obj["center"] for obj in matched]        print(f"\n 多模型集成识别成功")        print(f"   总检测：{len(detections)} 个")        print(f"   匹配目标：{len(matched)} 个")        print(f"   点击坐标：{positions}")        if draw:            self.draw_result(image_path, detections, matched)        return positions# ===================== 测试示例 =====================if __name__ == "__main__":    # 使用增强版（双模型）    solver = EnhancedImageClickSolver()    # 测试图片 & 提示词    img_path = "captcha_test.jpg"    prompt = "点击所有自行车"    click_points = solver.solve_click_captcha(img_path, prompt)


##  四、旋转验证码深度解析


###  4.1 旋转验证码的技术原理


旋转验证码要求用户将图片旋转到正确的角度，其核心技术包括：

  1. ** 角度检测  ** ：检测当前图片的旋转角度

  2. ** 模板匹配  ** ：与正确角度的模板进行匹配

  3. ** 特征提取  ** ：提取图片的旋转不变特征


###  4.2 基于特征匹配的旋转角度检测


  *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *   *


    import cv2import numpy as npimport mathclass RotationCaptchaSolver:    """旋转验证码破解器（优化稳定版）"""    def __init__(self):        # SIFT 特征检测器        self.sift = cv2.SIFT_create()        FLANN_INDEX_KDTREE = 1        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)        search_params = dict(checks=50)        self.flann = cv2.FlannBasedMatcher(index_params, search_params)    def load_image(self, path):        """统一图片加载"""        img = cv2.imread(path)        if img is None:            raise ValueError(f"无法加载图片: {path}")        return img    def find_rotation_angle(self, rotated_img_path, reference_img_path):        """        计算旋转角度（核心算法）        输入：旋转后的图、标准参考图        输出：需要旋转的角度        """        img1 = self.load_image(rotated_img_path)        img2 = self.load_image(reference_img_path)        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)        kp1, des1 = self.sift.detectAndCompute(gray1, None)        kp2, des2 = self.sift.detectAndCompute(gray2, None)        if des1 is None or des2 is None:            print(" 未检测到特征点")            return 0.0        matches = self.flann.knnMatch(des1, des2, k=2)        good_matches = []        for m, n in matches:            if m.distance < 0.75 * n.distance:                good_matches.append(m)        if len(good_matches) < 4:            print(f" 匹配点不足: {len(good_matches)}")            return 0.0        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)        if M is None:            return 0.0        # 从旋转矩阵提取角度        theta = -math.atan2(M[0, 1], M[0, 0]) * 180 / math.pi        return round(theta, 2)    def estimate_angle_by_edges(self, image_path):        """        无参考图时：使用轮廓重心 + 极坐标分析角度        专门用于圆形旋转验证码        """        img = self.load_image(image_path)        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)        gray = cv2.GaussianBlur(gray, (5, 5), 0)        edges = cv2.Canny(gray, 50, 150)        # 找重心        M = cv2.moments(edges)        if M["m00"] == 0:            return 0.0        cx = int(M["m10"] / M["m00"])        cy = int(M["m01"] / M["m00"])        # 极坐标投影分析角度        angles = []        h, w = edges.shape        for y in range(h):            for x in range(w):                if edges[y, x] > 0:                    dx = x - cx                    dy = y - cy                    angle = math.atan2(dy, dx) * 180 / math.pi                    angles.append(angle)        if not angles:            return 0.0        return round(np.median(angles), 2)    def rotate_image(self, image_path, angle, save_path="corrected.png"):        """旋转纠正图片"""        img = self.load_image(image_path)        h, w = img.shape[:2]        center = (w // 2, h // 2)        M = cv2.getRotationMatrix2D(center, angle, 1.0)        rotated = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)        cv2.imwrite(save_path, rotated)        return rotated    def solve_rotation_captcha(self, rotated_path, reference_path=None):        """        一键破解旋转验证码        """        print(" 开始计算旋转角度...")        if reference_path:            angle = self.find_rotation_angle(rotated_path, reference_path)            method = "特征匹配"        else:            angle = self.estimate_angle_by_edges(rotated_path)            method = "边缘分析"        print(f" [{method}] 旋转角度: {angle:.2f}°")        return angle# ===================== 使用示例 =====================if __name__ == "__main__":    solver = RotationCaptchaSolver()    # 你的旋转验证码    captcha = "rotated.png"    # 正确方向的参考图（没有可以填 None）    reference = "reference.png"    # 计算角度    angle = solver.solve_rotation_captcha(captcha, reference)    # 纠正并保存    if abs(angle) > 1:        solver.rotate_image(captcha, -angle, "corrected_captcha.png")        print(" 已保存纠正后的图片: corrected_captcha.png")


##  五、实战技巧与避坑指南


###  5.1 验证码破解的成功率优化


  1. ** 多引擎融合  ** ：不要依赖单一OCR引擎，结合多个引擎的结果

  2. ** 预处理优化  ** ：根据验证码特点调整预处理参数

  3. ** 后处理校验  ** ：对识别结果进行合理性校验

  4. ** 重试机制  ** ：对失败的情况自动重试，尝试不同参数


###  5.2 常见问题与解决方案

问题  |  可能原因  |  解决方案
---|---|---
识别率低  |  图片质量差  |  增强预处理，去噪、二值化
字符分割错误  |  字符粘连  |  调整分割参数，使用投影法
目标检测漏检  |  物体太小  |  使用更敏感的模型，调整置信度阈值
角度检测不准  |  特征点少  |  使用多方法融合，结合霍夫变换
运行速度慢  |  模型太大  |  使用轻量级模型，缓存识别结果

###  5.3 推荐的第三方工具

  1. ** OCR引擎  ** ：

     * Tesseract：开源免费，支持多语言

     * EasyOCR：基于深度学习的OCR

     * PaddleOCR：百度开源的OCR工具

  2. ** 目标检测  ** ：

     * YOLOv5：实时目标检测

     * Detectron2：Facebook的检测框架

     * MMDetection：商汤的开源检测工具箱

  3. ** 图像处理  ** ：

     * OpenCV：计算机视觉库

     * PIL/Pillow：图片处理库

     * scikit-image：图像处理算法


  * 再次强调：所有操作仅用于合法学习、技术研究，严禁用于商业网站的违规爬取！


##  码字不易，如果真的有帮助可以顺手点个赞，你们的喜欢就是我更新的动力！
