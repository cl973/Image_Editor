import cv2
import numpy as np
import os

def enhance_color(
        image,  # 改为接收BGR格式的图片对象
        saturation_gain=1.5,  # 饱和度增强系数（核心参数）
        hue_correction=0,  # 色相修正（-10~10，解决偏色）
        protect_skin=True,  # 是否保护肤色避免过度增强
        local_boost=True  # 对低饱和区域额外增强
):
    """
    恢复并增强老照片的色彩饱和度，解决褪色问题

    参数:
        image: 输入图片对象（BGR格式的numpy数组）
        saturation_gain: 饱和度增强系数（建议1.2~2.0，老照片常用1.5）
        hue_correction: 色相修正值（如泛黄照片可设-3~-5）
        protect_skin: 保护肤色，避免人像肤色过度饱和
        local_boost: 对低饱和度区域进行额外增强，平衡整体色彩
    
    返回:
        enhanced: 色彩增强后的图片对象（BGR格式的numpy数组）
    """
    # 保存原图用于对比和后续处理
    original = image.copy()

    # 转换到HSV色彩空间（便于单独处理饱和度）
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
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
    enhanced = cv2.addWeighted(enhanced, 1.5, image, -0.5, 0)
    
    return enhanced

if __name__ == '__main__':
    # 读取图片
    image = cv2.imread("temp/image4.jpg")
    
    # 检查图片是否读取成功
    if image is None:
        print("无法读取图片，请检查路径是否正确")
    else:
        # 处理图片（使用色彩增强函数）
        processed_image = enhance_color(
            image, 
            saturation_gain=1.8, 
            hue_correction=-4,
            protect_skin=True,
            local_boost=True
        )
        
        # 保存处理后的图片
        cv2.imwrite("temp/processed_image4.jpg", processed_image)
        print("图片处理完成并已保存")
