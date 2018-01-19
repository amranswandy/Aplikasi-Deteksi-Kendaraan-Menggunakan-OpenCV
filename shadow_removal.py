import cv2
import numpy as np

def hsvPassShadowRemoval(src, shadowThreshold):
    blurLevel = 3
    height, width = src.shape[:2]
    imgHSV = cv2.cvtColor(src, cv2.COLOR_RGB2HSV)
    gaussianBlur = cv2.GaussianBlur(imgHSV, (blurLevel, blurLevel), 0)
    hueImg, satImg, valImg = cv2.split(gaussianBlur)

    NSVDI = np.zeros((height, width, 1), np.uint8)
    count = height * width
    with np.errstate(divide='ignore'):

        NSVDI = (satImg + valImg) / ((satImg - valImg) * 1)
    thresh = np.sum(NSVDI)
    avg = thresh / (count * 1.0)
    if shadowThreshold is None:
        avg = avg
    else:
        avg = shadowThreshold

    np.where(NSVDI > avg, 255, 0)
    _, threshold = cv2.threshold(NSVDI, avg, 255, cv2.THRESH_BINARY_INV)

    output = threshold
    return output

def yuvPassShadowRemoval(src, shadowThreshold):
    height, width = src.shape[:2]
    imgYUV = cv2.cvtColor(src, cv2.COLOR_RGB2YUV)
    yImg, uImg, vImg = cv2.split(imgYUV)
    yImg = np.zeros((height, width, 1), np.uint8)
    imgYUV = cv2.merge([yImg, uImg, vImg])

    rgbImg = cv2.cvtColor(imgYUV, cv2.COLOR_YUV2RGB)
    rImg, gImg, bImg = cv2.split(rgbImg)

    count = width * height
    avg = np.sum(bImg)
    avg /= count * 1.0

    if shadowThreshold is None:
        avg = avg
    else:
        avg = shadowThreshold

    np.where(bImg > avg, 255, 0)
    _, threshold = cv2.threshold(bImg, avg, 255, cv2.THRESH_BINARY)

    output = threshold
    return output