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
    description='''WKS v0.1 \nBaidu Wenku Spider BY BoyInTheSun\nDo NOT use it to download VIP documents or for commercial purpose! \nONLY FOR Easy to view and exchange spider technical.'''
)
parser.add_argument(
    'url', 
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
    '-u', '--useragent', 
    help='User-Agent when request.'
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
url = args.url
print('Download from', url)

print('Download HTML...', end='')
try:
    headers = {
        'User-Agent': useragent,
        'Cookie': cookies,
        'Referer': url
    }
    request = urllib.request.Request(url=url, headers=headers)
    page = urllib.request.urlopen(request)
    html = page.read().decode("utf-8")
except Exception as e:
    print('Error!')
    print(traceback.print_exc())
    sys.exit() 

print('Success. \nParse HTML...', end='')
try:
    page_data = re.search( r'var pageData = (.*);', html)
    title = re.search( r'<title>(.*) - 百度文库</title>', html).group(1)
    data = json.loads(page_data.group(1))
except Exception as e:
    print('Error!')
    print(traceback.print_exc())
    sys.exit() 

print('Success. ')
print('title: ', title)
if isinstance(data['readerInfo']['htmlUrls'], list):
    print('Found PPT file, prepare for downloading...', end='')
    try:
        temp_dir = url.split('/')[-1][:-5]
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.mkdir(temp_dir)
    except Exception as e:
        print('Error!')
        print(traceback.print_exc())
        sys.exit() 
    
    print('Success.\nstart downloading images...', end='')
    try:
        imgs = data['readerInfo']['htmlUrls']
        if len(imgs) == 3:
            print("It seems that you provided incorrect cookies, only be able to download a part (3 page) of the file.")
        for i in range(len(imgs)):
            # TODO: theading
            percentage = (i + 1) / len(imgs) * 100
            print('\r|{}| {} / {} ({:.2f}%)'.format('=' * int(percentage // 2 - 1) + '>' + '-' * int((100 - percentage) // 2), i + 1, len(imgs), percentage), end='')
            request = urllib.request.Request(url=imgs[i], headers=headers)
            page = urllib.request.urlopen(request)
            with open(os.path.join(url.split('/')[-1][:-5], str(i) + '.jpg'), 'wb') as f:
                f.write(page.read())
    except Exception as e:
        print('Error!')
        print(traceback.print_exc())
        sys.exit() 

    print('merge images to a PDF...', end='')
    try:
        imgs = [os.path.join(temp_dir, img) for img in os.listdir(temp_dir)]
        with open(title + '.pdf', 'wb') as f:
            f.write(img2pdf.convert(imgs))
        shutil.rmtree(temp_dir)
    except Exception as e:
        print('Error!')
        print(traceback.print_exc())
        sys.exit() 
    
    print('Success.')
    print('Saved to ' + title + '.pdf')

else:
    print('Do NOT suppose this document now.')

