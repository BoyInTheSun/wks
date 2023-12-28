from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
# from reportlab.lib.utils import ImageReader
import json
import os
from PIL import Image
from imp import reload

def save_pdf(tempdir, pagenum, font_replace=dict()):

    with open(os.path.join(tempdir, str(pagenum) + ".json")) as f:
        data = json.load(f)
    c = canvas.Canvas(
        os.path.join(tempdir, str(pagenum) + ".pdf"),
        pagesize=(data['page']['pw'], data['page']['ph']),
    )

    styles = dict()
    for style in data['style']:
        for style_c in style['c']:
            if not styles.get(style_c):
                styles[style_c] = dict()
            for each in style['s']:
                styles[style_c][each] = style['s'][each]

    ttfs = [x for x in os.listdir(tempdir) if x[-4:] == '.ttf' and int(x[-8: -4], 16) == pagenum]
    # ttf2font = data['font']
    reload(pdfmetrics)  # TODO: a issue here, if no reload(), font only work in page 1.
    for ttf in ttfs:
        # pdfmetrics.registerFont(TTFont(ttf2font.get(ttf[:-4]), os.path.join(tempdir, ttf)))
        pdfmetrics.registerFont(TTFont(ttf[:-4], os.path.join(tempdir, ttf)))
    
    try:
        img = Image.open(os.path.join(tempdir, str(pagenum) +  '.png'))
    except:
        pass

    try:
        os.mkdir(os.path.join(tempdir, str(pagenum)))
    except:
        pass

    data_body = data['body']
    data_body = sorted(data_body, key=lambda each: each['p']['z'])
    for item in data_body:
        if item['t'] == 'word':
            style = dict()
            if item.get('r'):
                for item_r in item['r']:
                    style.update(styles[item_r])
            if item.get('s'):
                style.update(item['s'])
            
            text = item['c']
            # TODO: bold do not work
            '''
            if style.get('bold'):
                text = '<b>' + text + '</b>'
            '''
            textobject = c.beginText()
            textobject.setTextOrigin(
                item['p']['x'],
                data['page']['ph'] - item['p']['y'] - 14  # TODO: why is 14?
            )
            if style.get('font-family'):
                if style['font-family'] + '.ttf' in ttfs:
                    font_family = style['font-family']
                elif style['font-family'] in font_replace:
                    font_family = font_replace[style['font-family']]
                else:
                    if len(ttfs) == 1:
                        font_replace[style['font-family']] = ttfs[0][:-4]
                        font_family = font_replace[style['font-family']]
                        print('Font "{}" missing, will be repalce by "{}" ({}.ttf)'.format(style.get('font-family'), data['font'].get(font_family), font_family))

                    else:
                        print('Font "{}" missing, will be repalce by one of other fonts'.format(style.get('font-family')))
                        i = 1
                        for each in data['font']:
                            print('[{}] {} ({})'.format(i, data['font'][each], each + '.ttf'))
                            i += 1
                        num_font = input('please input the number:')
                        try:
                            font_new = list(data['font'].keys())[int(num_font) - 1]
                        except:
                            font_new = ttfs[0][:-4]
                        font_replace[style['font-family']] = font_new
                        font_family = font_replace[style['font-family']]
                        print('Font "{}" missing, will be repalce by "{}" ({}.ttf)'.format(style.get('font-family'), data['font'].get(font_family), font_family))
                textobject.setFont(
                    psfontname=font_family, 
                    size=float(style['font-size']) if style.get('font-size') else 16
                )
            if style.get('letter-spacing'):
                textobject.setCharSpace(float(style['letter-spacing']))
            if style.get('color'):
                textobject.setFillColorRGB(
                    int(style['color'][1: 3], 16) / 255,
                    int(style['color'][3: 5], 16) / 255,
                    int(style['color'][5: 7], 16) / 255
                )
            textobject.textLine(text)
            c.drawText(textobject)
        elif item['t'] == 'pic':
            # TODO: is that work?
            # if item['ps'] and item['ps'].get('_drop') and item['ps'].get('_drop') == 1:
            #     continue

            # follow code do not work.
            # https://groups.google.com/g/reportlab-users/c/SmIzKYdCodo
            # new_image = Image.new('RGBA', (int(item['c']['iw']), int(item['c']['ih'])))
            # new_image.paste(img, (int(item['c']['ix']), int(item['c']['iy'])))
            new_image = img.crop((
                int(item['c']['ix']), 
                int(item['c']['iy']),
                int(item['c']['iw'] + item['c']['ix']), 
                int(item['c']['ih'] + item['c']['iy'])
            ))
            img_width = None
            img_height = None
            if int(item['c']['iw']) != int(item['p']['w']) or int(item['c']['ih']) != int(item['p']['h']):
                img_width = item['p']['w']
                img_height = item['c']['ih'] / item['c']['iw'] * item['p']['w']
            else:
                img_height = int(item['c']['ih'])
            pic_name = item['s'].get('pic_file').replace('/', '+') if item['s'] and item['s'].get('pic_file') else '{}-{}.png'.format(item['p']['x'], item['p']['y'])
            if pic_name[-4:] != '.png':
                pic_name = '.'.join(pic_name.split('.')[:-1]) + '.png'
            new_image.save(os.path.join(tempdir, str(pagenum), pic_name))
            # c.drawImage(ImageReader(new_image), int(item['p']['x']), data['page']['ph'] - int(item['p']['y']) - int(item['c']['ih']), mask='auto') 
            c.drawImage(
                os.path.join(
                    tempdir, 
                    str(pagenum), 
                    pic_name
                ), 
                int(item['p']['x']), 
                data['page']['ph'] - int(item['p']['y']) - img_height, 
                width=img_width,
                height=img_height,
                mask='auto'
            ) 

    c.showPage()
    c.save()
    return font_replace
