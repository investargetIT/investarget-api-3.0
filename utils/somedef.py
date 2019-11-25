#coding=utf-8
import os

import datetime
import traceback

import jpype
from PIL import Image, ImageDraw, ImageFont
import random

from reportlab.lib.pagesizes import A1
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

from invest.settings import APILOG_PATH
from reportlab.pdfbase.ttfonts import TTFont
from pdfrw import PdfReader, PdfWriter, PageMerge

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
def addWaterMark(pdfpath, watermarkcontent=None):
    try:
        now = datetime.datetime.now()

        watermarkpath = pdfpath.split('.')[0] + '-water' + '.pdf'
        out_path = pdfpath.split('.')[0] + '-out' + '.pdf'
        watermark = create_watermark(watermarkpath, watermarkcontent)

        # Get our files ready
        input_file = PdfReader(pdfpath)
        for page in input_file.pages:
            PageMerge(page).add(watermark, prepend=False).render()
        PdfWriter(out_path, trailer=input_file).write()
        os.remove(pdfpath)
        os.rename(out_path, pdfpath)
        os.remove(watermarkpath)
        print('覆盖水印pdf--%s--源文件%s' % (now, out_path))
    except Exception:
        print('覆盖水印pdf出错--%s--源文件%s' % (now, out_path))
        filepath = APILOG_PATH['excptionlogpath'] + '/' + now.strftime('%Y-%m-%d')
        f = open(filepath, 'a')
        f.writelines(now.strftime('%H:%M:%S') + '\n' + traceback.format_exc() + '\n\n')
        f.close()
    return pdfpath


def create_watermark(waterpath, watermarkcontent):
    """创建PDF水印模板
    """
    # 使用reportlab来创建一个PDF文件来作为一个水印文件
    pdfmetrics.registerFont(TTFont('song', APILOG_PATH['pdfwaterfontPath']))
    if not isinstance(watermarkcontent, list):
        watermarkcontent = []
    while len(watermarkcontent) < 3:
        watermarkcontent.append(u'多维海拓')
    c = canvas.Canvas(waterpath, A1)
    c.rotate(45)
    fontsize = 20     # 水印字体大小
    fontAlpha = 0.05  # 水印字体透明度
    space = 80        # 水印间距
    c.setFont("song", fontsize)
    c.translate(0, -A1[1] * 0.5)
    width0 = c.stringWidth(text=watermarkcontent[0], fontName='song', fontSize=fontsize)
    width1 = c.stringWidth(text=watermarkcontent[1], fontName='song', fontSize=fontsize)
    width2 = c.stringWidth(text=watermarkcontent[2], fontName='song', fontSize=fontsize)
    y = 0
    while y < A1[1]:
        x = 100
        while x < A1[0]:
            c.setFillAlpha(fontAlpha)
            c.drawString(x, y, watermarkcontent[0])
            x = x + width0 + space
            c.drawString(x, y, watermarkcontent[1])
            x = x + width1 + space
            c.drawString(x, y, watermarkcontent[2])
            x = x + width2 + space
        y += 60
    c.save()
    pdf_watermark = PageMerge().add(PdfReader(waterpath).pages[0])[0]
    return pdf_watermark


#水印增加（多文件）
def addWaterMarkToPdfFiles(pdfpaths, watermarkcontent=None):
    try:
        if len(pdfpaths) == 0:
            return
        watermarkpath = pdfpaths[0].split('.')[0] + '-water' + '.pdf'
        watermark = create_watermark(watermarkpath, watermarkcontent)
    except Exception:
        now = datetime.datetime.now()
        print('制作水印pdf--%s'%now)
        filepath = APILOG_PATH['excptionlogpath'] + '/' + now.strftime('%Y-%m-%d')
        f = open(filepath, 'a')
        f.writelines(now.strftime('%H:%M:%S') + '\n' + traceback.format_exc() + '\n\n')
        f.close()
        return
    # Get our files ready
    for path in pdfpaths:
        now = datetime.datetime.now()
        try:
            print('覆盖水印pdf--%s--源文件%s' % (now, path))
            out_path = path.split('.')[0] + '-out' + '.pdf'
            input_file = PdfReader(path)
            for page in input_file.pages:
                PageMerge(page).add(watermark, prepend=False).render()
            PdfWriter(out_path, trailer=input_file).write()
            os.remove(path)
            os.rename(out_path, path)
        except Exception as err:
            print('覆盖水印pdf失败--%s--源文件%s' % (now, path))
            filepath = APILOG_PATH['excptionlogpath'] + '/' + now.strftime('%Y-%m-%d')
            f = open(filepath, 'a')
            f.writelines(now.strftime('%H:%M:%S') + '\n' + traceback.format_exc() + '\n\n')
            f.close()
    if os.path.exists(watermarkpath):
        os.remove(watermarkpath)
    return

def encryptPdfFilesWithPassword(filepaths, password):
    if password and len(filepaths) > 0:
        jarPath = "my-app-1.0-SNAPSHOT-jar-with-dependencies.jar"
        jpype.startJVM(jpype.getDefaultJVMPath(), "-ea", "-Djava.class.path=" + jarPath)
        JDClass = jpype.JClass("com.mycompany.app.App")
        jd = JDClass()

        for input_filepath in filepaths:
            now = datetime.datetime.now()
            try:
                print('加密pdf--%s--源文件%s' % (now, input_filepath))
                (filepath, tempfilename) = os.path.split(input_filepath)
                (filename, filetype) = os.path.splitext(tempfilename)
                out_path = os.path.join(filepath, filename + '-encryout.pdf')
                jd.addPassword(input_filepath, password, out_path)
                os.remove(input_filepath)
                os.rename(out_path, input_filepath)
            except Exception as err:
                print('加密pdf--%s--源文件%s' % (now, input_filepath))
                filepath = APILOG_PATH['excptionlogpath'] + '/' + now.strftime('%Y-%m-%d')
                f = open(filepath, 'a')
                f.writelines(now.strftime('%H:%M:%S')+ '加密pdf失败（文件路径%s）'% input_filepath  + '\n' + traceback.format_exc() + '\n\n')
                f.close()
        jpype.shutdownJVM()

#文件分片
def file_iterator(fn, chunk_size=512):
    while True:
        c = fn.read(chunk_size)
        if c:
            yield c
        else:
            break