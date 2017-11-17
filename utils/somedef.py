#coding=utf-8
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import random

from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter
from reportlab.pdfgen import canvas

from invest.settings import APILOG_PATH

# 随机颜色1:
def rndColor():
    return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))

# 随机颜色2:
def rndColor2():
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))


def rndColor3():
    colorset = [(247, 58, 97), (87, 96, 105), (173, 195, 192), (243, 244, 246), (185, 227, 217)]
    return colorset[random.randint(0,4)]


def makeAvatar(name):
    width = 100
    height = 100
    font = ImageFont.truetype(APILOG_PATH['fontPath'], size=50)
    backcolor = rndColor3()
    image = Image.new('RGB', (width, height), backcolor)
    (letterWidth, letterHeight) = font.getsize(name)
    textY0 = (width - letterHeight - 14) / 2
    textY0 = int(textY0)
    textX0 = int((height - letterWidth) / 2)
    # 创建Draw对象:
    draw = ImageDraw.Draw(image)
    # 填充每个像素:
    # for x in range(width):
    #     for y in range(height):
    #         draw.point((x, y), fill=backcolor)
    # 输出文字:
    draw.text((textX0, textY0), name, font=font, fill=(255,255,255))
    from third.views.qiniufile import qiniuuploadfile
    image.save(APILOG_PATH['userAvatarPath'], 'jpeg')
    success, url, key = qiniuuploadfile(APILOG_PATH['userAvatarPath'], 'image')
    if success:
        return key
    else:
        return None

def addWaterMark(pdfpath='water.pdf',watermarkcontent='多维海拓'):
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import cm
    pdfmetrics.registerFont(TTFont('song', APILOG_PATH['pdfwaterfontPath']))
    watermarkpath = pdfpath.split('.')[0] + '-water' + '.pdf'
    out_path = pdfpath.split('.')[0] + '-out' + '.pdf'
    c = canvas.Canvas(watermarkpath)
    x = 16
    y = 1
    # 设置字体
    c.setFont("song", 40)
    # 旋转45度，坐标系被旋转
    # 旋转45度，坐标系被旋转
    c.rotate(45)
    # 设置透明度，1为不透明
    c.setFillAlpha(0.1)
    c.drawCentredString((x - 3) * cm, (y - 3) * cm, watermarkcontent)
    c.setFillAlpha(0.1)
    c.drawCentredString(x * cm, y * cm, watermarkcontent)
    c.setFillAlpha(0.1)
    c.drawCentredString((x + 3) * cm, (y + 3) * cm, watermarkcontent)
    c.save()
    watermark = PdfFileReader(open(watermarkpath, "rb"))

    # Get our files ready
    output_file = PdfFileWriter()
    input_file = PdfFileReader(open(pdfpath, "rb"))
    page_count = input_file.getNumPages()
    for page_number in range(page_count):
        input_page = input_file.getPage(page_number)
        input_page.mergePage(watermark.getPage(0))
        output_file.addPage(input_page)
    with open(out_path, "wb") as outputStream:
        output_file.write(outputStream)
    os.remove(pdfpath)
    os.remove(watermarkpath)
    return out_path

def file_iterator(fn, chunk_size=512):
    while True:
        c = fn.read(chunk_size)
        if c:
            yield c
        else:
            break