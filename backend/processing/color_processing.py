import cv2
import numpy as np
from PIL import Image
import os
import matplotlib.pyplot as plt

# 确保中文显示正常
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]


def enhance_color(
        image_path,
        output_path=None,
        saturation_gain=1.5,  # 饱和度增强系数（核心参数）
        hue_correction=0,  # 色相修正（-10~10，解决偏色）
        protect_skin=True,  # 是否保护肤色避免过度增强
        local_boost=True  # 对低饱和区域额外增强
):
    """
    恢复并增强老照片的色彩饱和度，解决褪色问题

    参数:
        image_path: 输入图片路径（WebP格式）
        output_path: 增强后图片保存路径
        saturation_gain: 饱和度增强系数（建议1.2~2.0，老照片常用1.5）
        hue_correction: 色相修正值（如泛黄照片可设-3~-5）
        protect_skin: 保护肤色，避免人像肤色过度饱和
        local_boost: 对低饱和度区域进行额外增强，平衡整体色彩
    """
    # 读取WebP图片（只读不修改原图）
    try:
        with Image.open(image_path).convert('RGB') as pil_img:
            img = cv2.cvtColor(np.array(pil_img.copy()), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"读取图片失败: {e}")
        return None

    # 保存原图用于对比
    original = img.copy()

    # 转换到HSV色彩空间（便于单独处理饱和度）
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    # 色相修正（解决老照片常见的偏黄、偏红问题）
    if hue_correction != 0:
        # 修复：先转换为int16避免负数溢出，计算后再转回uint8
        h = h.astype(np.int16)  # 转换为有符号整数
        h = (h + hue_correction) % 180  # H通道范围是0-179
        h = h.astype(np.uint8)  # 转换回uint8

    # 复制原始饱和度用于后续处理
    s_original = s.copy().astype(np.float32)

    # 局部增强：对低饱和度区域进行额外增强
    if local_boost:
        # 计算局部饱和度均值
        s_blur = cv2.GaussianBlur(s_original, (21, 21), 0)
        # 低饱和度区域（<50）增强系数提高，高饱和度区域（>100）降低
        gain_factor = np.where(
            s_blur < 50, saturation_gain * 1.3,
            np.where(s_blur > 100, saturation_gain * 0.7, saturation_gain)
        )
    else:
        gain_factor = saturation_gain

    # 应用饱和度增强
    s_enhanced = s_original * gain_factor
    s_enhanced = np.clip(s_enhanced, 0, 255).astype(np.uint8)

    # 保护肤色（避免人像肤色过度饱和）
    if protect_skin:
        # 定义肤色的HSV范围
        lower_skin = np.array([0, 20, 40])
        upper_skin = np.array([20, 255, 255])
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)

        # 对肤色区域降低饱和度增强效果
        skin_mask = cv2.GaussianBlur(skin_mask, (15, 15), 0) / 255
        s_enhanced = (s_enhanced * (1 - skin_mask * 0.5) + s_original * (skin_mask * 0.5)).astype(np.uint8)

    # 合并通道并转换回BGR色彩空间
    enhanced_hsv = cv2.merge([h, s_enhanced, v])
    enhanced = cv2.cvtColor(enhanced_hsv, cv2.COLOR_HSV2BGR)

    # 轻微锐化，增强细节（可选）
    enhanced = cv2.GaussianBlur(enhanced, (0, 0), 1.5)
    enhanced = cv2.addWeighted(enhanced, 1.5, img, -0.5, 0)

    # 显示原图和增强后的效果对比
    plt.figure(figsize=(12, 6))

    plt.subplot(121)
    plt.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    plt.title('原图')
    plt.axis('off')

    plt.subplot(122)
    plt.imshow(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))
    plt.title('色彩增强后')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

    # 保存增强后的图片
    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        cv2.imwrite(output_path, enhanced)
        print(f"色彩增强后的图片已保存至: {output_path}")
        print(f"原图 {image_path} 未被修改")

    return enhanced


if __name__ == "__main__":
    # 获取当前目录下的所有WebP图片
    webp_files = [f for f in os.listdir('.') if f.lower().endswith('.webp')]

    if not webp_files:
        print("当前目录下没有找到WebP格式的图片")
    else:
        print(f"找到WebP图片: {webp_files}")
        input_image = webp_files[0]
        output_image = f"color_enhanced_{input_image.replace('.webp', '.jpg')}"

        print(f"正在增强图片色彩: {input_image}")
        print(f"增强结果将保存为: {output_image}")

        # 根据照片褪色程度调整参数
        enhance_color(
            input_image,
            output_image,
            saturation_gain=1.5,  # 严重褪色用1.8-2.0，轻微褪色用1.2-1.4
            hue_correction=-3,  # 泛黄照片建议-3~-5，正常照片用0
            protect_skin=True,  # 有人像时建议开启
            local_boost=True  # 建议开启，平衡不同区域饱和度
        )
