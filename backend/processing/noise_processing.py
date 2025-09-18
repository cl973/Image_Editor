import os
import cv2
import numpy as np
import dlib
from imutils import face_utils

# 处理亮暗噪声与裂纹
def noise_process(
        image,
        # 双边滤波预处理参数
        crack_bilateral_d=7,         # 双边滤波中计算的邻域直径
        crack_bilateral_sigma=35,    # 颜色/空间标准差
        crack_median_ksize=3,
        # 缺陷检测参数
        morph_kernel_size_small=3,   # 用于检测小噪声的核
        morph_kernel_size_large=5,   # 用于检测大裂纹的核
        adaptive_block_size=11,
        adaptive_c_bright=-1,
        adaptive_c_dark=-6,
        # 缺陷分离参数
        crack_area_threshold=150,    # 面积大于此值的认为是主要裂纹
        min_noise_area=3,
        # 最终修复和人脸保护相关参数
        inpaint_radius=3,
        dilate_iterations=1,
        face_protection_on=True,
        inpaint_iterations=3,        # 修复运行轮数
        predictor_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models/shape_predictor_68_face_landmarks.dat')
):
    if len(image.shape) == 3:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = image.copy()

    # 双边滤波 + 中值滤波
    smoothed_gray = cv2.bilateralFilter(gray_image, crack_bilateral_d, crack_bilateral_sigma, crack_bilateral_sigma)
    if crack_median_ksize > 1 and crack_median_ksize % 2 == 1:
        smoothed_gray = cv2.medianBlur(smoothed_gray, crack_median_ksize)
    else:
        smoothed_gray = smoothed_gray

    # 定义一个通用的核
    kernel_detect = cv2.getStructuringElement(cv2.MORPH_RECT, (morph_kernel_size_small, morph_kernel_size_small))

    # 白帽变换检测亮噪点
    tophat = cv2.morphologyEx(smoothed_gray, cv2.MORPH_TOPHAT, kernel_detect)
    # 自适应阈值
    bright_noise_mask = cv2.adaptiveThreshold(tophat, 255,
                                              cv2.ADAPTIVE_THRESH_MEAN_C,
                                              cv2.THRESH_BINARY,
                                              adaptive_block_size,
                                              adaptive_c_bright)

    # 黑帽变换检测暗噪点
    blackhat = cv2.morphologyEx(smoothed_gray, cv2.MORPH_BLACKHAT, kernel_detect)
    dark_noise_mask = cv2.adaptiveThreshold(blackhat, 255,
                                            cv2.ADAPTIVE_THRESH_MEAN_C,
                                            cv2.THRESH_BINARY,
                                            adaptive_block_size,
                                            adaptive_c_dark)

    # 合并所有噪点
    combined_noise_mask = cv2.bitwise_or(bright_noise_mask, dark_noise_mask)

    # 方形核
    pre_close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    # 应用闭运算
    combined_noise_mask = cv2.morphologyEx(combined_noise_mask, cv2.MORPH_CLOSE, pre_close_kernel, iterations=1)

    # 分离大小噪声
    contours, _ = cv2.findContours(combined_noise_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    crack_mask = np.zeros_like(gray_image)
    noise_mask = np.zeros_like(gray_image)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > crack_area_threshold:
            # 这是一个大裂纹
            cv2.drawContours(crack_mask, [cnt], -1, 255, -1)
        elif area > min_noise_area:
            # 这是一个小噪声点
            cv2.drawContours(noise_mask, [cnt], -1, 255, -1)

    # 对大裂纹：使用闭运算连接断点
    close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (morph_kernel_size_large, morph_kernel_size_large))
    crack_mask = cv2.morphologyEx(crack_mask, cv2.MORPH_CLOSE, close_kernel, iterations=3)

    # 对小噪声：进行轻微膨胀
    dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (morph_kernel_size_small, morph_kernel_size_small))
    noise_mask = cv2.dilate(noise_mask, dilate_kernel, iterations=dilate_iterations)

    # 合并处理后的蒙版
    final_mask_before_protection = cv2.bitwise_or(crack_mask, noise_mask)

    # 使用dlib保护人脸部分不被破坏
    protection_mask = np.zeros_like(gray_image)
    if face_protection_on:
        try:
            detector = dlib.get_frontal_face_detector()
            predictor = dlib.shape_predictor(predictor_path)
            faces = detector(smoothed_gray, 1)

            for face in faces:
                shape = predictor(smoothed_gray, face)
                shape = face_utils.shape_to_np(shape)
                # 绘制眼睛、鼻子、嘴巴等关键区域的代码
                left_eye = shape[
                    face_utils.FACIAL_LANDMARKS_IDXS["left_eye"][0]:face_utils.FACIAL_LANDMARKS_IDXS["left_eye"][1]]
                right_eye = shape[
                    face_utils.FACIAL_LANDMARKS_IDXS["right_eye"][0]:face_utils.FACIAL_LANDMARKS_IDXS["right_eye"][1]]
                nose = shape[
                    face_utils.FACIAL_LANDMARKS_IDXS["nose"][0]:face_utils.FACIAL_LANDMARKS_IDXS["nose"][1]]
                mouth = shape[
                    face_utils.FACIAL_LANDMARKS_IDXS["mouth"][0]:face_utils.FACIAL_LANDMARKS_IDXS["mouth"][1]]
                left_eyebrow = shape[face_utils.FACIAL_LANDMARKS_IDXS["left_eyebrow"][0]:
                                     face_utils.FACIAL_LANDMARKS_IDXS["left_eyebrow"][1]]
                right_eyebrow = shape[face_utils.FACIAL_LANDMARKS_IDXS["right_eyebrow"][0]:
                                      face_utils.FACIAL_LANDMARKS_IDXS["right_eyebrow"][1]]
                cv2.fillConvexPoly(protection_mask, left_eye, 255)
                cv2.fillConvexPoly(protection_mask, right_eye, 255)
                cv2.fillConvexPoly(protection_mask, nose, 255)
                cv2.fillConvexPoly(protection_mask, mouth, 255)
                cv2.fillConvexPoly(protection_mask, left_eyebrow, 255)
                cv2.fillConvexPoly(protection_mask, right_eyebrow, 255)
            # 对保护区域进行轻微膨胀，创建一个安全边界
            protection_mask = cv2.dilate(protection_mask, np.ones((5, 5), np.uint8), iterations=3)

        except Exception as e:
            print(f"人脸特征检测失败: {e}")

    # 应用保护并进行最终修复
    final_mask = cv2.bitwise_and(final_mask_before_protection, cv2.bitwise_not(protection_mask))

    # 净化边缘
    pre_blur_image = cv2.GaussianBlur(image, (5, 5), 0)
    # 定义一个边界混合区
    boundary_kernel = np.ones((5, 5), np.uint8)
    boundary_mask = cv2.dilate(final_mask, boundary_kernel, iterations=2)
    boundary_mask = cv2.subtract(boundary_mask, final_mask)
    inpainting_source_image = image.copy()
    # 在裂纹边缘用模糊像素替换
    boundary_mask_3ch = np.stack([boundary_mask] * 3, axis=-1) > 0
    np.copyto(inpainting_source_image, pre_blur_image, where=boundary_mask_3ch)

    repaired_image = inpainting_source_image.copy()
    for _ in range(inpaint_iterations):
        repaired_image = cv2.inpaint(repaired_image, final_mask, inpaint_radius, cv2.INPAINT_NS)

    return repaired_image


if __name__ == '__main__':
    image = cv2.imread("temp/image4.jpg")
    processed_image = noise_process(image)
    cv2.imwrite("temp/processed_image4.jpg", processed_image)