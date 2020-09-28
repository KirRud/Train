import pytesseract
import cv2
import os
from PIL import Image
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'E:\\Program Files\\Anaconda3\\Lib\\site-packages\\Tesseract-OCR\\tesseract.exe'


class Preprocess:

    def __init__(self, img, preprocess="thresh"):
        self.image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        self.preprocess = preprocess

    # thresholding
    def thresholding(self):
        return cv2.threshold(self.image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # dilation
    def dilate(self):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.dilate(self.image, kernel, iterations=1)

    # erosion
    def erode(self):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.erode(self.image, kernel, iterations=1)

    # opening - erosion followed by dilation
    def opening(self):
        kernel = np.ones((5, 5), np.uint8)
        return cv2.morphologyEx(self.image, cv2.MORPH_OPEN, kernel)

    # canny edge detection
    def canny(self):
        return cv2.Canny(self.image, 100, 200)

    def blur(self):
        return cv2.medianBlur(self.image, 3)

    def choice_preprocess(self):
        if self.preprocess == "thresh":
            res_img = self.thresholding()

        elif self.preprocess == "dilate":
            res_img = self.dilate()

        elif self.preprocess == "erode":
            res_img = self.erode()

        elif self.preprocess == "opening":
            res_img = self.opening()

        elif self.preprocess == "canny":
            res_img = self.canny()

        elif self.preprocess == "blur":
            res_img = self.blur()

        else:
            res_img = self.blur()

        self.image = res_img
        return res_img

    def save_preprocessed(self):
        file_name = "{}.png".format(self.preprocess)
        cv2.imwrite(file_name, self.image)

    def open_preprocessed(self, file_name):
        self.image = Image.open(file_name)

image_name = "dip"
image_path = "img\\{}.png".format(image_name)
style_preprocess = "blur"
image = cv2.imread(image_path)

proc_func = Preprocess(image, style_preprocess)
processed_image = proc_func.choice_preprocess()

ocr_text = pytesseract.image_to_string(processed_image, lang="rus+eng")

with open("docs\\res_{}.docx".format(image_name), "w") as res_file:
    print(ocr_text, file=res_file)
