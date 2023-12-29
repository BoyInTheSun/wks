# wks

百度文库爬虫  Baidu Wenku Spider

仅支持python3

## 郑重声明

请勿将该脚本用于下载付费文档或商业用途，否则后果自负！

本项目仅为方便查看在线文档和交流爬虫技术。

## 使用教程

目前该项目支持所有格式文档下载。

ppt仅能保存图片格式的pdf，建议下载后通过Acrobot等光学识别软件拷贝文字；

doc、pdf文件仅能保存为pdf，且可能看起来会有一些不同；

xls文件仅能保存为pdf，未来可能会支持保存为xls；

txt可保存为原始格式。

如果需要提取图片或查看原始数据，可以带参数`-t`不删除临时文件。

原理为下载网页中显示的内容，而并非原始文档，只能尽力还原格式。

目前来看，部分情况无需会员账号cookies即可下载完整文档，即使非会员账号在网页尽可查看部分文档。

### 安装wks

#### 方法一：使用源码（推荐）

要求Python3.5+，如有必要，请使用pip3和python3。

下载源码并安装依赖

```powershell
git clone https://github.com/BoyInTheSun/wks.git
cd wks
pip install -r requirements.txt
python main.py --help
```

#### 方法二：使用可执行程序(非最新版)

请下载对应系统版本的可执行程序。

[点击跳转](https://github.com/BoyInTheSun/wks/releases)

在windows系统中，选择你喜欢的地方，将`wks.exe`放到其中，按住shift右键，选择`在此处打开powershell窗口`，输入`.\wks.exe --help`查看帮助。

不要直接双击`wks.exe`！！！

### 获取cookies

这是必要的步骤，如果仅能下载文档前几页，可以尝试该方法。由于接口更新，目前可能即使提供了非VIP账号的cookie也无法获取完整文档。如果使用vip账号的cookie仍无法下载，请提issue。

首先登陆[百度文库](https://wenku.baidu.com/)，按`F12`打开开发者工具，找到`网络`栏，`F5`刷新，找到`Request URL`和地址栏相同的一项，复制`Request Headers`的`Cookie`的值，形如`kunlunFlag=1; PSTM=1638106870; __yjs_duid=1_9d69de0379cb51aa4b48e663f9e1e6591638110590672;...`。将其保存至文件如`Cookies.txt`或在下文命令行中使用字符串形式。

### 下载

获取到cookies后，可以通过命令行传参或者传文件两种形式。

`python main.py "https://wenku.baidu.com/view/abcd.html" -c "kunlunFlag=1; PSTM=1638106870;..."`

`python main.py "https://wenku.baidu.com/view/abcd.html" -C "Cookies.txt"`

如果你使用了可执行文件`wks.exe`，请替换上述命令中的`python main.py`。

### 进阶用法

#### -h, --help

显示帮助信息并退出。

#### -c COOKIES, --cookies COOKIES

传入cookie格式字符串，使请求带cookie。

#### -C COOKIES_FILENAME, --cookies_filename COOKIES_FILENAME

传入cookie文件，使请求带cookie。优先级低于前者。

#### -t, --temp

将临时文件保存到文件夹。

#### -o OUTPUT, --output OUTPUT

指定文件名（后缀名自动生成）

#### -p PAGENUMS, --pagenums PAGENUMS

指定下载和保存的页数，例如"2,6-8,10"代表下载页码"2,6,7,8,10"，从"1"开始。

#### -u USERAGENT, --useragent USERAGENT

指定请求时User-Agent。

#### -F FILENAME, --filename FILENAME

批量下载。传入文件名，文件中一行一个链接。
