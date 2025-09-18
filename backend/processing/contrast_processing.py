import cv2
import numpy as np
from PIL import Image
import os
import matplotlib.pyplot as plt

# 确保中文显示正常
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]


def enhance_contrast(
        image_path,
        output_path=None,
        clip_limit=2.0,
        grid_size=(8, 8),
        use_color_enhance=True
):
    """
    增强老照片的对比度，使细节更清晰

    参数:
        image_path: 输入图片路径（WebP格式）
        output_path: 增强后图片保存路径
        clip_limit: 对比度限制阈值，值越大增强效果越强（建议1.0-3.0）
        grid_size: 自适应直方图均衡化的网格大小
        use_color_enhance: 是否同时增强色彩饱和度
    """
    # 读取WebP图片（只读不修改原图）
    try:
        with Image.open(image_path).convert('RGB') as pil_img:
            # 转换为OpenCV格式 (BGR)
            img = cv2.cvtColor(np.array(pil_img.copy()), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"读取图片失败: {e}")
        return None

    # 保存原图用于对比
    original = img.copy()

    # 转换为YCrCb色彩空间，分离亮度通道和色度通道
    # 这样可以只增强亮度通道的对比度，避免色彩失真
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y_channel, cr, cb = cv2.split(ycrcb)

    # 创建CLAHE对象（对比度受限的自适应直方图均衡化）
    # 相比全局直方图均衡化，CLAHE能更好地保留细节，避免过度增强
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
    enhanced_y = clahe.apply(y_channel)

    # 合并增强后的亮度通道和原始色度通道
    enhanced_ycrcb = cv2.merge([enhanced_y, cr, cb])
    enhanced = cv2.cvtColor(enhanced_ycrcb, cv2.COLOR_YCrCb2BGR)

    # 可选：适度增强色彩饱和度
    if use_color_enhance:
        hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV)
        # 适度提高饱和度（乘以1.1-1.3系数）
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.2, 0, 255)
        enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # 显示原图和增强后的效果对比
    plt.figure(figsize=(12, 6))

    plt.subplot(121)
    plt.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    plt.title('原图')
    plt.axis('off')

    plt.subplot(122)
    plt.imshow(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))
    plt.title('对比度增强后')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

    # 保存增强后的图片
    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        cv2.imwrite(output_path, enhanced)
        print(f"增强后的图片已保存至: {output_path}")
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
        output_image = f"contrast_enhanced_{input_image.replace('.webp', '.jpg')}"

        print(f"正在增强图片对比度: {input_image}")
        print(f"增强结果将保存为: {output_image}")

        # 增强参数可根据照片情况调整
        enhance_contrast(
            input_image,
            output_image,
            clip_limit=2.0,  # 对比度强度：老照片建议1.5-2.5
            grid_size=(8, 8),  # 网格大小：值越小细节保留越好
            use_color_enhance=True  # 同时增强色彩饱和度
        )
