import cv2
import numpy as np
from noise_processing import noise_process

def old2new(image):
    image = noise_process(image)
    return image