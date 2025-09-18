import cv2
import numpy as np
import os

def adjust_brightness(
        image,  # 改为接收BGR格式的图片对象
        gamma=0.8,  # gamma < 1 提高亮度，gamma > 1 降低亮度
        local_brightness=True,  # 是否启用局部亮度优化
        clip_limit=1.5  # 局部优化的对比度限制
):
    """
    调整老照片亮度，解决昏暗问题

    参数:
        image: 输入图片对象（BGR格式的numpy数组）
        gamma: 伽马校正系数，建议0.5-1.0（值越小亮度提升越明显）
        local_brightness: 是否启用局部亮度优化（适合明暗不均的照片）
        clip_limit: 局部亮度优化的对比度限制（值越小越柔和）
    
    返回:
        adjusted: 亮度调整后的图片对象（BGR格式的numpy数组）
    """
    # 保存原图用于后续处理（避免修改输入对象）
    original = image.copy()

    # 步骤1: 全局亮度调整（伽马校正）
    # 构建伽马校正查找表
    inv_gamma = 1.0 / gamma
    gamma_table = np.array([((i / 255.0) ** inv_gamma) * 255
                            for i in np.arange(0, 256)]).astype("uint8")
    # 应用伽马校正
    adjusted = cv2.LUT(original, gamma_table)

    # 步骤2: 可选的局部亮度优化（针对明暗不均的区域）
    if local_brightness:
        # 转换到YCrCb色彩空间，只处理亮度通道（避免色彩失真）
        ycrcb = cv2.cvtColor(adjusted, cv2.COLOR_BGR2YCrCb)
        y_channel, cr, cb = cv2.split(ycrcb)

        # 使用CLAHE进行局部亮度优化（平衡明暗区域）
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
        y_enhanced = clahe.apply(y_channel)

        # 合并通道并转回BGR格式
        adjusted = cv2.cvtColor(cv2.merge([y_enhanced, cr, cb]), cv2.COLOR_YCrCb2BGR)

    # 步骤3: 限制亮度上限，避免过曝（保留2%的高亮区域，更自然）
    b, g, r = cv2.split(adjusted)
    for channel in [b, g, r]:
        # 计算98%分位的亮度值作为上限（过滤极端高亮像素）
        limit = np.percentile(channel, 98)
        channel[channel > limit] = limit
    adjusted = cv2.merge([b, g, r])

    return adjusted


if __name__ == '__main__':
    # 1. 读取指定路径的图片
    image = cv2.imread("temp/image4.jpg")
    
    # 检查图片是否读取成功（避免路径错误/文件损坏导致后续报错）
    if image is None:
        print("错误：无法读取图片，请检查路径 'temp/image4.jpg' 是否正确，或文件是否完好")
    else:
        # 2. 调用亮度调整函数处理图片（传入图片对象，配置参数）
        processed_image = adjust_brightness(
            image,
            gamma=0.7,  # 严重昏暗用0.5-0.7，轻微昏暗用0.8-1.0
            local_brightness=True,  # 处理局部阴影（如人物面部阴影、角落昏暗）
            clip_limit=1.5  # 老照片建议1.0-2.0，值过大可能放大噪点
        )
        
        # 3. 保存处理后的图片到指定路径
        output_path = processed_image
        # 确保输出目录存在（若temp文件夹不存在则自动创建）
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存图片
        cv2.imwrite(output_path, processed_image)
        print(f"亮度调整完成！处理后的图片已保存至：{output_path}")