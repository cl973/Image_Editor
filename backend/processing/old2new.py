import cv2
import numpy as np
from .noise_processing import noise_process
from .color_processing import enhance_color
from .contrast_processing import enhance_contrast
#from .face_processing import restore_face
from .brightness_processing import adjust_brightness

def old2new(image):
    image = enhance_color(image)
    image = enhance_contrast(image)
    image = adjust_brightness(image)
    image = noise_process(image)
    # image = restore_face(image)
    return image