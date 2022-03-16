# wks

百度文库爬虫  Baidu Wenku Spider

## 郑重声明

请勿将该脚本用于下载付费文档或商业用途，否则后果自负！
本项目仅为方便查看在线文档和交流爬虫技术。

## 使用教程

目前该项目仅支持ppt格式文档下载，且仅能下载图片格式。建议下载后通过Acrobot等光学识别软件拷贝文字。

### 获取cookies

这是必要的步骤。首先登陆[百度文库](https://wenku.baidu.com/)，按`F12`打开开发者工具，找到`网络`栏，`F5`刷新，找到`Request URL`和地址栏相同的一项，复制`Request Headers`的`Cookie`的值，形如`kunlunFlag=1; PSTM=1638106870; __yjs_duid=1_9d69de0379cb51aa4b48e663f9e1e6591638110590672;...`

## 下载

获取到cookies后，可以通过命令行传参或者传文件两种形式。
`python3 main.py https://wenku.baidu.com/view/abcd.html -c "kunlunFlag=1; PSTM=1638106870;..."`
`python3 main.py https://wenku.baidu.com/view/abcd.html -C Cookies.txt`

## 进阶用法

有空再写，可以`-h`查看。
