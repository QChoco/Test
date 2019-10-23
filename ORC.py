import os
import pytesseract
from PIL import Image
from collections import defaultdict

pytesseract.pytesseract.tesseract_cmd = 'D://Tesseract-OCR/tesseract.exe'


def get_threshold(image):
    pixel_dict = defaultdict(int)

    rows, cols = image.size
    for i in range(rows):
        for j in range(cols):
            pixel = image.getpixel((i, j))
            pixel_dict[pixel] += 1

    count_max = max(pixel_dict.values())  # 获取像素出现出多的次数
    pixel_dict_reverse = {v: k for k, v in pixel_dict.items()}
    threshold = pixel_dict_reverse[count_max]  # 获取出现次数最多的像素点

    return threshold


def get_bin_table(threshold):
    table = []
    for i in range(256):
        rate = 0.1  # 在threshold的适当范围内进行处理
        if threshold * (1 - rate) <= i <= threshold * (1 + rate):
            table.append(1)
        else:
            table.append(0)
    return table


def cut_noise(image):
    rows, cols = image.size  # 图片的宽度和高度
    change_pos = []  # 记录噪声点位置

    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            pixel_set = []
            for m in range(i - 1, i + 2):
                for n in range(j - 1, j + 2):
                    if image.getpixel((m, n)) != 1:  # 1为白色,0位黑色
                        pixel_set.append(image.getpixel((m, n)))

            if len(pixel_set) <= 4:
                change_pos.append((i, j))

    for pos in change_pos:
        image.putpixel(pos, 1)

    return image  # 返回修改后的图片


def OCR_lmj(img_path):
    image = Image.open(img_path)  # 打开图片文件
    imgry = image.convert('L')  # 转化为灰度图

    max_pixel = get_threshold(imgry)

    table = get_bin_table(threshold=max_pixel)
    out = imgry.point(table, '1')

    out = cut_noise(out)

    text = pytesseract.image_to_string(out)

    exclude_char_list = ' .:\\|\'\"?![],()~@#$%^&*_+-={};<>/¥'
    text = ''.join([x for x in text if x not in exclude_char_list])

    return text


def main():
    dir = 'E://figures'

    correct_count = 0  # 图片总数
    total_count = 0  # 识别正确的图片数量

    for file in os.listdir(dir):
        if file.endswith('.png') or file.endswith('.jpg'):
            image_path = '%s/%s' % (dir, file)  # 图片路径

            answer = file.split('.')[0]  # 图片名称，即图片中的正确文字
            recognizition = OCR_lmj(image_path)  # 图片识别的文字结果

            print((answer, recognizition))
            if recognizition == answer:  # 如果识别结果正确，则total_count加1
                correct_count += 1

            total_count += 1

    print('Total count: %d, correct: %d.' % (total_count, correct_count))



main()