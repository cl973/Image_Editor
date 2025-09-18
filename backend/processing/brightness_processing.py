import cv2
import numpy as np
from PIL import Image
import os
import matplotlib.pyplot as plt

# 确保中文显示正常
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]


def adjust_brightness(
        image_path,
        output_path=None,
        gamma=0.8,  # gamma < 1 提高亮度，gamma > 1 降低亮度
        local_brightness=True,  # 是否启用局部亮度优化
        clip_limit=1.5  # 局部优化的对比度限制
):
    """
    调整老照片亮度，解决昏暗问题

    参数:
        image_path: 输入图片路径（WebP格式）
        output_path: 调整后图片保存路径
        gamma: 伽马校正系数，建议0.5-1.0（值越小亮度提升越明显）
        local_brightness: 是否启用局部亮度优化（适合明暗不均的照片）
        clip_limit: 局部亮度优化的对比度限制（值越小越柔和）
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

    # 步骤1: 全局亮度调整（伽马校正）
    # 构建伽马校正查找表
    inv_gamma = 1.0 / gamma
    gamma_table = np.array([((i / 255.0) ** inv_gamma) * 255
                            for i in np.arange(0, 256)]).astype("uint8")
    # 应用伽马校正
    adjusted = cv2.LUT(img, gamma_table)

    # 步骤2: 可选的局部亮度优化（针对明暗不均的区域）
    if local_brightness:
        # 转换到YCrCb色彩空间，只处理亮度通道
        ycrcb = cv2.cvtColor(adjusted, cv2.COLOR_BGR2YCrCb)
        y_channel, cr, cb = cv2.split(ycrcb)

        # 使用CLAHE进行局部亮度优化
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        y_enhanced = clahe.apply(y_channel)

        # 合并通道
        adjusted = cv2.cvtColor(cv2.merge([y_enhanced, cr, cb]), cv2.COLOR_YCrCb2BGR)

    # 限制亮度上限，避免过曝（保留2%的高亮区域）
    b, g, r = cv2.split(adjusted)
    for channel in [b, g, r]:
        # 计算98%分位的亮度值作为上限
        limit = np.percentile(channel, 98)
        channel[channel > limit] = limit
    adjusted = cv2.merge([b, g, r])

    # 显示原图和调整后的效果对比
    plt.figure(figsize=(12, 6))

    plt.subplot(121)
    plt.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    plt.title('原图')
    plt.axis('off')

    plt.subplot(122)
    plt.imshow(cv2.cvtColor(adjusted, cv2.COLOR_BGR2RGB))
    plt.title('亮度调整后')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

    # 保存调整后的图片
    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        cv2.imwrite(output_path, adjusted)
        print(f"亮度调整后的图片已保存至: {output_path}")
        print(f"原图 {image_path} 未被修改")

    return adjusted


if __name__ == "__main__":
    # 获取当前目录下的所有WebP图片
    webp_files = [f for f in os.listdir('.') if f.lower().endswith('.webp')]

    if not webp_files:
        print("当前目录下没有找到WebP格式的图片")
    else:
        print(f"找到WebP图片: {webp_files}")
        input_image = webp_files[0]
        output_image = f"brightness_adjusted_{input_image.replace('.webp', '.jpg')}"

        print(f"正在调整图片亮度: {input_image}")
        print(f"调整结果将保存为: {output_image}")

        # 根据照片昏暗程度调整参数
        adjust_brightness(
            input_image,
            output_image,
            gamma=0.7,  # 严重昏暗用0.5-0.7，轻微昏暗用0.8-1.0
            local_brightness=True,  # 建议开启，处理局部阴影
            clip_limit=1.5  # 老照片建议1.0-2.0，避免噪点放大
        )

        print("\n参数调整建议:")
        print("1. 若照片严重昏暗：降低gamma值（如0.5）")
        print("2. 若调整后过亮：增大gamma值（如0.9）")
        print("3. 若局部仍有阴影：保持local_brightness=True，可适当提高clip_limit至2.0")
        print("4. 若照片噪点较多：关闭local_brightness（设为False），使用较大的gamma值")
