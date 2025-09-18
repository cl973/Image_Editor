import cv2
import torch
import numpy as np
from gfpgan import GFPGANer

def restore_face(image):
    """
    修复人脸图像
    
    参数:
        image: 输入的图像对象，应是BGR格式的numpy数组（OpenCV默认格式）
    
    返回:
        restored_img: 修复后的图像对象，BGR格式的numpy数组
    """
    # 设置设备
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # 初始化修复器
    restorer = GFPGANer(
        model_path='https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth',
        upscale=1,  # 不需要放大
        arch='clean',
        channel_multiplier=2,
        device=device
    )
    
    # 进行修复
    _, _, restored_img = restorer.enhance(
        image,
        has_aligned=False,
        only_center_face=False,
        paste_back=True
    )
    
    return restored_img

# 使用示例
if __name__ == '__main__':
    # 从文件读取图像作为输入
    input_image = cv2.imread('input_photo.jpg', cv2.IMREAD_COLOR)
    
    # 调用修复函数
    processed_image = restore_face(input_image)
    
    # 保存修复后的图像
    cv2.imwrite('restored_photo.jpg', processed_image)
