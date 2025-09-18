import cv2
import torch
import numpy as np
from gfpgan import GFPGANer

def restore_face(image_path, output_path):
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
    
    # 读取图像
    input_img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    
    # 进行修复
    _, _, restored_img = restorer.enhance(
        input_img,
        has_aligned=False,
        only_center_face=False,
        paste_back=True
    )
    
    # 保存结果 - 使用OpenCV的imwrite替代basicsr的imwrite
    cv2.imwrite(output_path, restored_img)

if __name__ == '__main__':
    input_image = 'restored_photo.jpg'  # 输入图像路径
    output_image = 'restored_photo.jpg'  # 输出图像路径
    restore_face(input_image, output_image)