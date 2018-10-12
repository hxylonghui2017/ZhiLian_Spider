# ZhiLian_Spider
本次使用开发环境python 3.6.5+Pycharm.
由于使用Firefox浏览器，所以需要下载其驱动：geckodriver.exe,并设置该exe文件在win系统环境变量下。
本次测试url：https://sou.zhaopin.com/?pageSize=60&jl=765&sf=10001&st=15000&kw=java&kt=3&=10001 
本次测试文件名：java岗位信息表。
# 详细信息：
My_csdn:https://blog.csdn.net/qq_34769196/article/details/82993985 
# 打包：
pyinstaller -F -i win.ico -w qt_ui_use.py -p img_list_rc.py -p main_zhilian.py -p qt.py
