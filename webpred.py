#----用于和flask项目联用进行在线预测----#
import time,sys,os
import cv2
import numpy as np
from PIL import Image

from frcnn import FRCNN


#----封装后用于服务器的调用

frcnn = FRCNN()

def webpred(orgpath,newpath,filename):
    image = Image.open(orgpath)
    reslut,clsResult = frcnn.detect_image(image)
    reslut.save(os.path.join(newpath, filename), quality=95, subsampling=0)
    return filename,clsResult

