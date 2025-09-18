import cv2
import numpy as np

def enhance_contrast(
        image,
        clip_limit=2.0,
        grid_size=(8, 8),
        use_color_enhance=True
):
    """
    增强老照片的对比度，使细节更清晰

    参数:
        image: 输入图片对象（BGR格式的numpy数组）
        clip_limit: 对比度限制阈值，值越大增强效果越强（建议1.0-3.0）
        grid_size: 自适应直方图均衡化的网格大小
        use_color_enhance: 是否同时增强色彩饱和度
    
    返回:
        enhanced: 增强后的图片对象（BGR格式的numpy数组）
    """
    # 保存原图用于处理
    original = image.copy()

    # 转换为YCrCb色彩空间，分离亮度通道和色度通道
    ycrcb = cv2.cvtColor(original, cv2.COLOR_BGR2YCrCb)
    y_channel, cr, cb = cv2.split(ycrcb)

    # 创建CLAHE对象
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=grid_size)
    enhanced_y = clahe.apply(y_channel)

    # 合并通道
    enhanced_ycrcb = cv2.merge([enhanced_y, cr, cb])
    enhanced = cv2.cvtColor(enhanced_ycrcb, cv2.COLOR_YCrCb2BGR)

    # 增强色彩饱和度
    if use_color_enhance:
        hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.2, 0, 255)
        enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return enhanced


if __name__ == '__main__':
    # 读取图片
    image = cv2.imread("temp/image4.jpg")
    
    # 检查图片是否读取成功
    if image is None:
        print("无法读取图片，请检查路径是否正确")
    else:
        # 处理图片（使用增强对比度函数替代noise_process）
        processed_image = enhance_contrast(image)
        
        # 保存处理后的图片
        cv2.imwrite("temp/processed_image4.jpg", processed_image)
        print("图片处理完成并已保存")
