#coding=utf-8
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import random

from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter
from reportlab.lib.pagesizes import A1
from reportlab.pdfgen import canvas

from invest.settings import APILOG_PATH
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm

# 随机颜色1:
def rndColor():
    return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))

# 随机颜色2:
def rndColor2():
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))


def rndColor3():
    colorset = [(247, 58, 97), (87, 96, 105), (173, 195, 192), (185, 227, 217)]
    return colorset[random.randint(0,3)]

#默认头像生成kk
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
    draw.text((textX0, textY0), name, font=font, fill=(255,255,255))
    from third.views.qiniufile import qiniuuploadfile
    image.save(APILOG_PATH['userAvatarPath'], 'jpeg')
    success, url, key = qiniuuploadfile(APILOG_PATH['userAvatarPath'], 'image')
    if success:
        return key
    else:
        return None

#水印增加（单文件）
def addWaterMark(pdfpath='water.pdf',watermarkcontent=None):
    if not isinstance(watermarkcontent, list):
        watermarkcontent = []
    while len(watermarkcontent) < 3:
        watermarkcontent.append(u'多维海拓')
    pdfmetrics.registerFont(TTFont('song', APILOG_PATH['pdfwaterfontPath']))
    watermarkpath = pdfpath.split('.')[0] + '-water' + '.pdf'
    out_path = pdfpath.split('.')[0] + '-out' + '.pdf'
    c = canvas.Canvas(watermarkpath, A1)
    c.rotate(45)
    fontsize = 20
    c.setFont("song", fontsize)
    c.translate(0, -A1[1] * 0.5)
    width0 = c.stringWidth(text=watermarkcontent[0], fontName='song', fontSize=fontsize)
    width1 = c.stringWidth(text=watermarkcontent[1], fontName='song', fontSize=fontsize)
    width2 = c.stringWidth(text=watermarkcontent[2], fontName='song', fontSize=fontsize)
    y = 0
    while y < A1[1]:
        x = 100
        while x < A1[0]:
            c.setFillAlpha(0.05)
            c.drawCentredString(x, y, watermarkcontent[0])
            x = x + width0 * 2
            c.drawCentredString(x, y, watermarkcontent[1])
            x = x + width1 * 2
            c.drawCentredString(x, y, watermarkcontent[2])
            x = x + width2 * 2
        y += 60
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

#水印增加（多文件）
def addWaterMarkToPdfFiles(pdfpaths, watermarkcontent=None):
    if len(pdfpaths) == 0:
        return 20071
    if not isinstance(watermarkcontent, list):
        watermarkcontent = []
    while len(watermarkcontent) < 3:
        watermarkcontent.append(u'多维海拓')
    pdfmetrics.registerFont(TTFont('song', APILOG_PATH['pdfwaterfontPath']))
    watermarkpath = pdfpaths[0].split('.')[0] + '-water' + '.pdf'
    c = canvas.Canvas(watermarkpath, A1)
    c.rotate(45)
    fontsize = 20
    c.setFont("song", fontsize)
    c.translate(0, -A1[1] * 0.5)
    width0 = c.stringWidth(text=watermarkcontent[0], fontName='song', fontSize=fontsize)
    width1 = c.stringWidth(text=watermarkcontent[1], fontName='song', fontSize=fontsize)
    width2 = c.stringWidth(text=watermarkcontent[2], fontName='song', fontSize=fontsize)
    y = 0
    while y < A1[1]:
        x = 100
        while x < A1[0]:
            c.setFillAlpha(0.05)
            c.drawCentredString(x, y, watermarkcontent[0])
            x = x + width0 * 2
            c.drawCentredString(x, y, watermarkcontent[1])
            x = x + width1 * 2
            c.drawCentredString(x, y, watermarkcontent[2])
            x = x + width2 * 2
        y += 60
    c.save()
    watermark = PdfFileReader(open(watermarkpath, "rb"))
    # Get our files ready
    for path in pdfpaths:
        out_path = path.split('.')[0] + '-out' + '.pdf'
        output_file = PdfFileWriter()
        input_file = PdfFileReader(open(path, "rb"))
        page_count = input_file.getNumPages()
        for page_number in range(page_count):
            input_page = input_file.getPage(page_number)
            input_page.mergePage(watermark.getPage(0))
            output_file.addPage(input_page)
        with open(out_path, "wb") as outputStream:
            output_file.write(outputStream)
        os.remove(path)
        os.rename(out_path, path)
    if os.path.exists(watermarkpath):
        os.remove(watermarkpath)
    return

#文件分片
def file_iterator(fn, chunk_size=512):
    while True:
        c = fn.read(chunk_size)
        if c:
            yield c
        else:
            break