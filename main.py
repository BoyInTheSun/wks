import re
import urllib.request
import json
import argparse
import os
import img2pdf
import shutil
import traceback
import sys

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='''WKS v0.1 \nBaidu Wenku Spider BY BoyInTheSun\nDo NOT use it to download VIP documents or for commercial purpose! \nONLY FOR Easy to view and communicate spider technical.'''
)
parser.add_argument(
    'url',
    nargs='?',
    default=None,
    help='A url of baiduwenku, seem like "https://wenku.baidu.com/view/abcd.html"'
)
parser.add_argument(
    '-c', '--cookies', 
    help='cookies of baiduwenku.'
)
parser.add_argument(
    '-C', '--cookies_filename', 
    help='filename of the cookies.'
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


    print('Success. \nParse HTML...', end='')
    page_data = re.search( r'var pageData = (.*);', html)
    title = re.search( r'<title>(.*) - 百度文库</title>', html).group(1)
    data = json.loads(page_data.group(1))
 

    print('Success. ')
    print('title: ', title)
    if isinstance(data['readerInfo']['htmlUrls'], list):
        print('Found PPT file, prepare for downloading...', end='')
        temp_dir = url.split('?')[0].split('/')[-1][:-5]
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.mkdir(temp_dir)
        
        print('Success.\nstart downloading images...', end='')
        imgs = data['readerInfo']['htmlUrls']
        if len(imgs) == 3:
            print("It seems that you provided incorrect cookies, only be able to download a part (3 page) of the file.")
        for i in range(len(imgs)):
            # TODO: theading
            percentage = (i + 1) / len(imgs) * 100
            print('\r|{}| {} / {} ({:.2f}%)'.format('=' * int(percentage // 2 - 1) + '>' + '-' * int((100 - percentage) // 2), i + 1, len(imgs), percentage), end='')
            request = urllib.request.Request(url=imgs[i], headers=headers)
            page = urllib.request.urlopen(request)
            with open(os.path.join(temp_dir, str(i) + '.jpg'), 'wb') as f:
                f.write(page.read())

        print('\nmerge images to a PDF...', end='')
        imgs = [os.path.join(temp_dir, img) for img in os.listdir(temp_dir)]
        if args.output:
            output = args.output
        else:
            output = title
        with open(output + '.pdf', 'wb') as f:
            f.write(img2pdf.convert(imgs))
        shutil.rmtree(temp_dir)
        
        print('Success.')
        print('Saved to ' + title + '.pdf')

    else:
        print('Do NOT support this document now.')

