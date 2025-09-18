import cv2
import numpy as np
import random
import math

def new2old(image,yellow_intensity,fade_intensity,scratch_intensity,noise_intensity):
    image = fading(image, fade_intensity)
    image = yellowing(image, yellow_intensity)
    image = add_gaussian_noise(image, noise_intensity)
    image = add_scratches(image, scratch_intensity)

    return image


def yellowing(image, intensity):
    if intensity <= 0:
        return image.copy()

    intensity_factor = intensity / 100.0
    img_float = image.astype(np.float32) / 255.0

    # 1. 转换到Lab色彩空间（感知均匀）
    lab = cv2.cvtColor(img_float, cv2.COLOR_BGR2Lab)
    l, a, b = cv2.split(lab)

    # 2. 模拟胶片老化效果
    # 增加黄色调（增加b值）
    b_adjust = 8 + intensity_factor * 25  # 基础偏移+强度相关增量
    b = np.clip(b + b_adjust, 0, 100)

    # 模拟品红染料衰减（减少a值）
    a_reduction = intensity_factor * 10
    a = np.clip(a - a_reduction, -128, 127)

    # 轻微降低明度（模拟褪色）
    l_reduction = intensity_factor * 5
    l = np.clip(l - l_reduction, 0, 100)

    # 3. 转换回RGB
    adjusted_lab = cv2.merge([l, a, b])
    yellowed = cv2.cvtColor(adjusted_lab, cv2.COLOR_Lab2BGR)

    # 4. 非线性混合（保留原视觉权重）
    blend_factor = intensity_factor ** 0.7
    result = img_float * (1 - blend_factor) + yellowed * blend_factor

    # 5. 物理正确的边缘褪色
    if intensity > 20:
        h, w = img_float.shape[:2]

        # 基于平方反比定律的衰减模型
        center_y, center_x = h / 2, w / 2
        y, x = np.ogrid[:h, :w]

        # 计算到中心的距离（归一化）
        dist_x = (x - center_x) / (w / 2)
        dist_y = (y - center_y) / (h / 2)
        distance = np.sqrt(dist_x ** 2 + dist_y ** 2)

        # 平方反比衰减
        fade_factor = 1 / (1 + 4 * intensity_factor * distance ** 2)

        # 添加纸张纤维方向性（模拟纤维素排列）
        angle = np.arctan2(dist_y, dist_x)
        fiber_effect = 0.2 * np.sin(2 * angle + np.pi / 4)  # 双周期正弦波

        # 组合效果
        edge_mask = np.clip(fade_factor + fiber_effect, 0, 1)

        # 添加随机老化斑块
        if intensity_factor > 0.3:
            noise = np.random.normal(0, 0.1, (h, w))
            edge_mask = np.clip(edge_mask + noise, 0, 1)

        # 高斯模糊使过渡自然 - 修复这里
        # 错误：edge_mask = cv2.GaussianBlur(edge_mask, (0, 0), sigma=2)
        # 正确：使用 sigmaX 参数
        edge_mask = cv2.GaussianBlur(edge_mask, (0, 0), sigmaX=2)

        # 增强边缘效果强度
        edge_strength = intensity_factor * 0.7

        # 应用边缘效果 - 增强泛白效果
        result = result * (1 - edge_mask[:, :, np.newaxis] * edge_strength) + \
                 edge_mask[:, :, np.newaxis] * edge_strength * 0.8

    # 6. 轻微对比度降低
    contrast_factor = 1 - intensity_factor * 0.10
    result = contrast_factor * (result - 0.5) + 0.5

    result = np.clip(result, 0, 1)
    return (result * 255).astype(np.uint8)

def fading(image, intensity):
    intensity_val = intensity / 100.0

    #降低对比度 (非线性效果：低强度时变化小，高强度时变化大)
    contrast = 1.0 - intensity_val * 0.5  # 从0.7减少到0.5，最大降低50%对比度
    faded = cv2.convertScaleAbs(image, alpha=contrast, beta=0)

    #降低饱和度
    hsv = cv2.cvtColor(faded, cv2.COLOR_BGR2HSV)
    saturation_reduction = intensity_val * 0.6  # 从0.8减少到0.6，最大降低60%饱和度
    hsv[:, :, 1] = hsv[:, :, 1] * (1 - saturation_reduction)

    faded = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    if intensity > 30:
        blur_amount = int(1 + intensity_val * 0.1)
        faded = cv2.GaussianBlur(faded, (blur_amount, blur_amount), 0)
    return faded


def add_scratches(image, intensity):
    if intensity == 0:
        return image

    intensity_val = intensity / 100.0
    intensity_val = max(0.0, min(intensity_val, 1.0))

    h, w = image.shape[:2]
    scratch_layer = np.zeros((h, w), dtype=np.float32)

    # 优化参数计算
    num_clusters = int(3 + intensity_val * 9)
    max_scratches_per_cluster = int(60 + intensity_val * 180)

    # 预计算常用值
    cos = math.cos
    sin = math.sin
    randint = random.randint
    uniform = random.uniform
    pi = math.pi

    # 优化主折痕簇生成
    for _ in range(num_clusters):
        # 确定起点
        if uniform(0, 1) > 0.5:
            start_x = random.choice([0, w - 1])
            start_y = randint(0, h - 1)
        else:
            start_x = randint(0, w - 1)
            start_y = random.choice([0, h - 1])

        # 初始角度
        if start_x == 0:
            angle = uniform(-0.4, 0.4)
        elif start_x == w - 1:
            angle = uniform(pi - 0.4, pi + 0.4)
        elif start_y == 0:
            angle = uniform(pi / 2 - 0.4, pi / 2 + 0.4)
        else:
            angle = uniform(3 * pi / 2 - 0.4, 3 * pi / 2 + 0.4)

        # 簇参数
        cluster_length = randint(int(w * 0.4), int(w * 0.9))
        cluster_width = randint(3, 10)
        segments = randint(4, 8)

        # 创建主路径
        main_path = []
        current_x, current_y = start_x, start_y

        # 预计算每段长度因子
        segment_lengths = [cluster_length * (1.0 - i * 0.1) / segments for i in range(segments)]

        for i in range(segments):
            angle += uniform(-0.5, 0.5)
            seg_len = segment_lengths[i]

            next_x = current_x + seg_len * cos(angle)
            next_y = current_y + seg_len * sin(angle)

            next_x = max(0, min(int(next_x), w - 1))
            next_y = max(0, min(int(next_y), h - 1))

            main_path.append((current_x, current_y, angle))
            current_x, current_y = next_x, next_y

        # 绘制主折痕路径 - 使用LINE_8确保锐利边缘
        for i in range(len(main_path) - 1):
            x1, y1, _ = main_path[i]
            x2, y2, _ = main_path[i + 1]

            cv2.line(scratch_layer,
                     (int(x1), int(y1)),
                     (int(x2), int(y2)),
                     0.85,  # 提高亮度
                     2,
                     lineType=cv2.LINE_8)  # 改为LINE_8消除抗锯齿

        # 优化微小划痕生成
        scratches = []
        dots = []

        # 计算每段微小划痕数量
        scratches_per_segment = randint(max_scratches_per_cluster // (segments * 2),
                                        max_scratches_per_cluster // segments)

        for segment in main_path:
            seg_x, seg_y, seg_angle = segment

            for _ in range(scratches_per_segment):
                # 随机偏移
                offset_along = uniform(-cluster_length / (segments * 4), cluster_length / (segments * 4))
                offset_across = uniform(-cluster_width / 2, cluster_width / 2)

                # 计算位置
                x = seg_x + offset_along * cos(seg_angle) + offset_across * sin(seg_angle)
                y = seg_y + offset_along * sin(seg_angle) - offset_across * cos(seg_angle)

                x = max(0, min(int(x), w - 1))
                y = max(0, min(int(y), h - 1))

                # 划痕参数
                scratch_length = randint(3, 12)
                scratch_angle = seg_angle + uniform(-0.3, 0.3)

                # 终点
                end_x = x + scratch_length * cos(scratch_angle)
                end_y = y + scratch_length * sin(scratch_angle)

                end_x = max(0, min(int(end_x), w - 1))
                end_y = max(0, min(int(end_y), h - 1))

                # 提高微小划痕亮度
                opacity = uniform(0.6, 0.95)

                # 收集划痕数据
                scratches.append(((int(x), int(y)), (int(end_x), int(end_y)), opacity))

                # 添加散点
                if uniform(0, 1) < 0.4:
                    for _ in range(randint(1, 4)):
                        dot_x = x + uniform(-2, 2)
                        dot_y = y + uniform(-2, 2)
                        dot_x = max(0, min(int(dot_x), w - 1))
                        dot_y = max(0, min(int(dot_y), h - 1))
                        dot_opacity = opacity * uniform(0.7, 1.0)
                        dots.append((int(dot_x), int(dot_y), dot_opacity))

        # 批量绘制微小划痕 - 使用LINE_8确保锐利边缘
        for (start, end, opacity) in scratches:
            cv2.line(scratch_layer, start, end, opacity, 1, lineType=cv2.LINE_8)

        # 批量绘制散点
        for (x, y, opacity) in dots:
            cv2.circle(scratch_layer, (x, y), 1, opacity, -1)

    # 优化独立划痕生成
    num_independent = int(15 + intensity_val * 40)
    independent_scratches = []

    for _ in range(num_independent):
        x = randint(0, w - 1)
        y = randint(0, h - 1)
        length = randint(5, 25)
        angle = uniform(0, 2 * pi)
        opacity = uniform(0.7, 0.95)  # 提高亮度
        num_segments = randint(2, 4)

        points = [(x, y)]

        for i in range(num_segments):
            seg_length = length / (i + 1)
            angle += uniform(-0.4, 0.4)

            next_x = points[-1][0] + seg_length * cos(angle)
            next_y = points[-1][1] + seg_length * sin(angle)

            next_x = max(0, min(int(next_x), w - 1))
            next_y = max(0, min(int(next_y), h - 1))

            points.append((next_x, next_y))

        # 收集独立划痕数据
        for i in range(len(points) - 1):
            start = (int(points[i][0]), int(points[i][1]))
            end = (int(points[i + 1][0]), int(points[i + 1][1]))
            independent_scratches.append((start, end, opacity))

    # 批量绘制独立划痕 - 使用LINE_8确保锐利边缘
    for (start, end, opacity) in independent_scratches:
        cv2.line(scratch_layer, start, end, opacity, 1, lineType=cv2.LINE_8)

    # 提高整体亮度并移除亮度压制
    scratch_layer = np.clip(scratch_layer, 0, 0.95)  # 仅做安全裁剪

    # 转换为三通道
    if len(image.shape) == 3:
        scratch_layer = cv2.merge([scratch_layer, scratch_layer, scratch_layer])

    # 将折痕应用到原图 - 使用更直接的混合方式
    result = image.copy().astype(np.float32)

    # 创建划痕蒙版 - 值大于0.1的区域视为有效划痕
    scratch_mask = scratch_layer > 0.1

    # 在划痕区域直接应用高亮白色
    result[scratch_mask] = np.maximum(result[scratch_mask], 255 * scratch_layer[scratch_mask])

    result = np.clip(result, 0, 255).astype(np.uint8)
    return result

def add_gaussian_noise(image, intensity):
    if intensity <= 0:
        return image.copy()

    intensity_factor = intensity / 100.0
    img_float = image.astype(np.float32) / 255.0

    # 1. 增强整体模糊效果 - 模拟老照片焦点损失
    blur_amount = intensity_factor * 1.5
    blurred = cv2.GaussianBlur(img_float, (0, 0), blur_amount)

    # 2. 改进的噪声模型 - 使用韦伯分布模拟胶片颗粒
    yuv = cv2.cvtColor(blurred, cv2.COLOR_BGR2YUV)

    # 韦伯分布噪声模型 (模拟胶片颗粒)
    def weibull_noise(shape, scale=0.5, shape_param=1.5):
        uniform = np.random.uniform(0, 1, shape)
        return scale * (-np.log(1 - uniform)) ** (1 / shape_param)

    # 应用韦伯噪声到亮度通道
    weibull_scale = 0.01 + intensity_factor * 0.04
    weibull_noise_val = weibull_noise(yuv.shape[:2], scale=weibull_scale)

    # 添加高斯噪声作为补充
    gauss_sigma = intensity_factor * 0.02
    gauss_noise = np.random.normal(0, gauss_sigma, yuv.shape[:2])

    # 组合噪声
    combined_noise = weibull_noise_val + gauss_noise

    # 应用噪声到亮度通道
    yuv[:, :, 0] = np.clip(yuv[:, :, 0] + combined_noise, 0, 1)

    # 转换回BGR
    noisy = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

    # 3. 改进的污渍效果
    if intensity > 40:
        h, w = noisy.shape[:2]
        stain_mask = np.zeros((h, w), dtype=np.float32)

        # 污渍数量与强度相关
        num_stains = int(2 + intensity_factor * 5)

        # 创建边缘权重图 - 增加边缘区域污渍概率
        edge_weight = np.zeros((h, w), dtype=np.float32)
        border_size = min(h, w) // 10
        edge_weight[:border_size, :] = 1.0
        edge_weight[-border_size:, :] = 1.0
        edge_weight[:, :border_size] = 1.0
        edge_weight[:, -border_size:] = 1.0

        # 中心区域减少权重
        center_y, center_x = h // 2, w // 2
        center_size = min(h, w) // 4
        edge_weight[center_y - center_size:center_y + center_size, center_x - center_size:center_x + center_size] = 0.3

        # 模糊权重图使过渡自然
        edge_weight = cv2.GaussianBlur(edge_weight, (0, 0), sigmaX=min(h, w) * 0.05)

        for _ in range(num_stains):
            # 使用边缘权重图选择位置 - 边缘区域更高概率
            while True:
                # 随机位置
                center_x = random.randint(0, w - 1)
                center_y = random.randint(0, h - 1)

                # 根据权重图决定是否接受此位置
                if random.random() < edge_weight[center_y, center_x]:
                    break

            # 污渍大小与强度相关
            max_radius = int(min(h, w) * (0.010 + intensity_factor * 0.06))

            # 创建更自然的污渍形状 - 使用分形噪声方法
            stain_shape = np.zeros((max_radius * 2 + 1, max_radius * 2 + 1), dtype=np.float32)

            # 生成基础圆形
            y, x = np.ogrid[-max_radius:max_radius + 1, -max_radius:max_radius + 1]
            mask = x * x + y * y <= max_radius * max_radius
            stain_shape[mask] = 1.0

            # 添加不规则边缘
            for i in range(3):  # 迭代次数控制不规则程度
                # 随机偏移
                offset_x = random.randint(-max_radius // 4, max_radius // 4)
                offset_y = random.randint(-max_radius // 4, max_radius // 4)

                # 创建扰动形状
                perturb_shape = stain_shape.copy()
                perturb_shape = cv2.GaussianBlur(perturb_shape, (0, 0), sigmaX=max_radius * 0.2)

                # 应用扰动
                stain_shape = np.clip(stain_shape + perturb_shape * 0.3, 0, 1)

            # 添加内部纹理
            texture = np.random.normal(0, 0.2, stain_shape.shape)
            texture = cv2.GaussianBlur(texture, (0, 0), sigmaX=max_radius * 0.1)
            stain_shape = np.clip(stain_shape + texture * 0.2, 0, 1)

            # 创建径向渐变透明度 - 中心更暗，边缘更淡
            dist_from_center = np.sqrt(x * x + y * y) / max_radius
            radial_gradient = 1 - dist_from_center ** 0.5
            stain_shape *= radial_gradient

            # 模糊污渍形状使边缘自然
            stain_shape = cv2.GaussianBlur(stain_shape, (0, 0), sigmaX=max_radius * 0.2)

            # 将污渍添加到整个图像的遮罩
            y_start = max(0, center_y - max_radius)
            y_end = min(h, center_y + max_radius + 1)
            x_start = max(0, center_x - max_radius)
            x_end = min(w, center_x + max_radius + 1)

            # 计算污渍在图像中的位置
            stain_y_start = max_radius - (center_y - y_start)
            stain_y_end = max_radius + (y_end - center_y)
            stain_x_start = max_radius - (center_x - x_start)
            stain_x_end = max_radius + (x_end - center_x)

            # 添加到污渍遮罩
            stain_mask[y_start:y_end, x_start:x_end] = np.maximum(
                stain_mask[y_start:y_end, x_start:x_end],
                stain_shape[stain_y_start:stain_y_end, stain_x_start:stain_x_end]
            )

        # 模糊污渍遮罩使过渡更自然
        stain_mask = cv2.GaussianBlur(stain_mask, (0, 0), sigmaX=max_radius * 0.3)

        # 污渍效果 - 使用黄褐色调 (BGR: 60, 90, 150)
        stain_color = np.array([60 / 255, 90 / 255, 150 / 255])  # 黄褐色

        # 应用污渍效果 - 混合黄褐色
        for c in range(3):
            # 原始图像通道
            orig_channel = noisy[:, :, c]

            # 污渍颜色通道
            stain_channel = stain_color[c]

            # 混合: 污渍区域使用污渍颜色和原始颜色的加权混合
            noisy[:, :, c] = orig_channel * (1 - stain_mask) + stain_mask * (
                    stain_channel * 0.7 + orig_channel * 0.3
            )

    # 5. 添加轻微色偏 - 模拟老照片化学变化
    if intensity > 30:
        # 随机色偏 - 偏向黄褐色
        color_shift = np.array([
            random.uniform(-0.03, 0.02),  # B (减少蓝色)
            random.uniform(-0.02, 0.03),  # G
            random.uniform(0.03, 0.10)  # R (增加红色/黄色)
        ]) * intensity_factor

        # 应用色偏
        noisy += color_shift
    # 确保值在0-1范围内
    noisy = np.clip(noisy, 0, 1)
    return (noisy * 255).astype(np.uint8)