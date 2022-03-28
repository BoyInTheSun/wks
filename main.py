import re
import urllib.request
import json
import argparse
import os
import img2pdf  # pip install img2pdf
import shutil
import time
import gzip
import base64
from json2pdf import save_pdf  # local
from PyPDF2 import PdfFileMerger, PdfFileReader  # pip3 install PyPDF2

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='WKS v0.2 \nBaidu Wenku Spider BY BoyInTheSun\nDo NOT use it to download VIP documents or for commercial purpose! \nONLY FOR easy to view and exchange spider technical.'
)
parser.add_argument(
    'url',
    nargs='?',
    default=None,
    help='A url of baiduwenku, seem like "https://wenku.baidu.com/view/abcd.html"'
)
parser.add_argument(
    '-c', '--cookies', 
    help='Cookies of baiduwenku.'
)
parser.add_argument(
    '-C', '--cookies_filename', 
    help='Filename of the cookies.'
)
parser.add_argument(
    '-t', '--temp', 
    action='store_true',
    help='Save temporary files into folder'
)
parser.add_argument(
    '-o', '--output', 
    help='Output filename.'
)
parser.add_argument(
    '-u', '--useragent', 
    help='User-Agent when request.'
)
parser.add_argument(
    '-F', '--filename', 
    help='URLs in a file. One URL each line.'
)


args = parser.parse_args()

cookies = ''
if args.cookies:
    cookies = args.cookies
elif args.cookies_filename:
    with open(args.cookies_filename, 'r') as f:
        cookies = f.read()

useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
if args.useragent:
    useragent = args.useragent

if args.url:
    urls = [args.url]
elif args.filename:
    with open(args.filename) as f:
        urls = f.read().split('\n')
else:
    parser.parse_args(['-h'])


for url in urls:
    print('Download from', url)

    print('Download HTML...', end='')
    headers = {
        'User-Agent': useragent,
        'Cookie': cookies,
        'Referer': url
    }
    request = urllib.request.Request(url=url, headers=headers)
    page = urllib.request.urlopen(request)
    html = page.read().decode("utf-8")

    temp_dir = url.split('?')[0].split('/')[-1][:-5]
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)

    print('Success. \nParse HTML...', end='')
    page_data = re.search( r'var pageData = (.*);', html)
    try:
        data = json.loads(page_data.group(1))
        with open(os.path.join(temp_dir, 'pagedata.json'), 'w') as f:
            json.dump(data, f)
        title = re.search( r'<title>(.*) - 百度文库</title>', html).group(1)
        # filetype = re.search(r'<div class="file-type-icon (.*)"></div>').group(1)
        filetype = data['viewBiz']['docInfo']['fileType']
        if args.output:
            output = args.output
        else:
            output = title
    except:
        print('Error! It is not a Baidu Wenku document.')
        continue
 

    print('Success. ')
    print('title: ', title)


    # PPT
    if data['readerInfo']['tplKey'] == 'new_view' and filetype == 'ppt':
        print('Found ppt file, prepare for download...', end='')
        
        print('Success.\nstart downloading jpg(s)...')
        imgs = data['readerInfo']['htmlUrls']
        if data['readerInfo']['page'] > len(imgs):
            print("It seems that you provided incorrect or Non-VIP cookies, only be able to download a part of the file ({} page), not the whole file ({} page).".format(len(imgs), data['readerInfo']['page']))
        for i in range(len(imgs)):
            # TODO: theading
            percentage = (i + 1) / len(imgs) * 100
            print('\r|{}| {} / {} ({:.2f}%)'.format('=' * int(percentage // 2 - 1) + '>' + '-' * int((100 - percentage) // 2), i + 1, len(imgs), percentage), end='')
            request = urllib.request.Request(url=imgs[i], headers=headers)
            page = urllib.request.urlopen(request)
            with open(os.path.join(temp_dir, str(i) + '.jpg'), 'wb') as f:
                f.write(page.read())

        print('\nMerge images to a PDF...', end='')
        # imgs = [os.path.join(temp_dir, img) for img in os.listdir(temp_dir) if img[-4:] == '.jpg']
        file_imgs = [os.path.join(temp_dir, str(i) + '.jpg') for i in range(len(imgs))]
        
        with open(output + '.pdf', 'wb') as f:
            f.write(img2pdf.convert(file_imgs))
        if not args.temp:
            shutil.rmtree(temp_dir)
        
        print('Success.')
        print('Saved to ' + output + '.pdf')

    # PDF WORD (EXCEL)
    elif data['readerInfo']['tplKey'] == 'html_view' and filetype in ['word', 'pdf', 'excel']:
        print('Found {} file, prepare for download...'.format(filetype), end='')
        jsons = {x['pageIndex']: x['pageLoadUrl'] for x in data['readerInfo']['htmlUrls']['json']}
        pngs = {x['pageIndex']: x['pageLoadUrl'] for x in data['readerInfo']['htmlUrls']['png']}
        fonts_csss = {x['pageIndex']: "https://wkretype.bdimg.com/retype/pipe/" + temp_dir + "?pn=" + str(x['pageIndex']) + "&t=ttf&rn=1&v=6" + x['param'] for x in data['readerInfo']['htmlUrls']['ttf']}  # temp_dir is doc ID in wenku.baidu.com
        print('Success.')

        if data['readerInfo']['page'] > len(jsons):
            print("It seems that you provided incorrect or Non-VIP cookies, only be able to download a part of the file ({} page), not the whole file ({} page).".format(len(jsons), data['readerInfo']['page']))
        
        print('Start downloading font(s)...')
        for i in fonts_csss:
            percentage = i / len(fonts_csss) * 100
            print('\r|{}| {} / {} ({:.2f}%)'.format('=' * int(percentage // 2 - 1) + '>' + '-' * int(50 - percentage // 2), i, len(fonts_csss), percentage), end='')
            request = urllib.request.Request(url=fonts_csss[i], headers=headers)
            page = urllib.request.urlopen(request)
            raw = gzip.decompress(page.read()).decode('utf-8')
            temp = re.findall( r'@font-face {src: url\(data:font/opentype;base64,(.*?)\)format\(\'truetype\'\);font-family: \'(.*?)\';', raw)
            for each in temp:
                with open(os.path.join(temp_dir, str(each[1]) + '.ttf'), 'wb') as f:
                    f.write(base64.b64decode(each[0]))

        print()
        print('Start downloading json(s)...')
        for i in jsons:
            # TODO: theading
            percentage = i / len(jsons) * 100
            print('\r|{}| {} / {} ({:.2f}%)'.format('=' * int(percentage // 2 - 1) + '>' + '-' * int(50 - percentage // 2), i, len(jsons), percentage), end='')
            request = urllib.request.Request(url=jsons[i], headers=headers)
            page = urllib.request.urlopen(request)
            with open(os.path.join(temp_dir, str(i) + '.json'), 'w') as f:
                temp = re.search( r'wenku_[0-9]+\((.*)\)', page.read().decode('utf-8', 'ignore')).group(1)
                f.write(temp)

        print()
        print('Start downloading png(s)...')
        for i in pngs:
            # TODO: theading
            percentage = i / len(pngs) * 100
            print('\r|{}| {} / {} ({:.2f}%)'.format('=' * int(percentage // 2 - 1) + '>' + '-' * int(50 - percentage // 2), i, len(pngs), percentage), end='')
            request = urllib.request.Request(url=pngs[i], headers=headers)
            page = urllib.request.urlopen(request)
            with open(os.path.join(temp_dir, str(i) + '.png'), 'wb') as f:
                f.write(page.read())

        print()
        print('Start generating pdf...')
        # jsons is right!
        for i in jsons:
            # TODO: theading
            percentage = i / len(jsons) * 100
            print('\r|{}| {} / {} ({:.2f}%)'.format('=' * int(percentage // 2 - 1) + '>' + '-' * int(50 - percentage // 2), i, len(jsons), percentage), end='')
            save_pdf(temp_dir, i)

        print()
        print('Start merging pdf...', end='')
        pdfs = {x[:-4]: os.path.join(temp_dir, x) for x in os.listdir(temp_dir) if x[-4:] == '.pdf'}
        file_merger = PdfFileMerger()
        for i in range(len(pdfs)):
            with open(pdfs[str(i + 1)], 'rb') as f_pdf:
                file_merger.append(PdfFileReader(f_pdf))
        file_merger.write(output + '.pdf')

        print('Success.')
        print('Saved to ' + output + '.pdf')

        if not args.temp:
            shutil.rmtree(temp_dir)

    # TXT
    elif data['readerInfo']['tplKey'] == 'txt_view' and filetype == 'txt':
        print('Found txt file, parse text from HTML...', end='')
        lines = re.findall(r'<p class="p-txt">(.*)</p>', html)

        print('Success.\nDownload other(s) text...', end='')
        temp_dir = url.split('?')[0].split('/')[-1][:-5]
        request = urllib.request.Request(
            url='https://wkretype.bdimg.com/retype/text/' + temp_dir + data['readerInfo']['md5sum'] + "&pn=2&rn=" + str(int(data['viewBiz']['docInfo']['page']) - 1) + '&type=txt&rsign=' + data['readerInfo']['rsign'] + '&callback=cb&_=' + str(int(time.time())), 
            headers=headers
        )
        page = urllib.request.urlopen(request)
        lines_others_json = json.loads(gzip.decompress(page.read())[3: -1])
        lines_others = [x['parags'][0]['c'][:-2] for x in lines_others_json]
        lines = [line for line in lines if line]
        lines[-1] = lines[-1][:-1]
        lines = lines + lines_others
        print('Success.')
        with open(output + '.txt', 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line.replace('\r\n', '\r'))
        print('Saved to ' + output + '.txt')

        if not args.temp:
            shutil.rmtree(temp_dir)
        
    else:
        print('Do NOT support this document. File type:', filetype)

