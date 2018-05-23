# /usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import time
import logging
import random

project_name = "performance"
wkdir = os.getcwd()
#设置日志级别 时间格式 日志文件名格式 filemode设置文件是读还是写
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s | %(message)s--[%(filename)-5s:%(lineno)d]',
                    datefmt='%y%m%d %H:%M:%S',
                    filename='%s%s%s%slog%s%s.log' % (
                        wkdir, os.sep, project_name, os.sep, os.sep, time.strftime("%Y%m%d %H-%M-%S")),
                    filemode='w')

#设置控制台日志输出格式
if True:
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s | %(message)s--[%(filename)-5s:%(lineno)d]')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

"""
    Config是一个配置类，主要作用是把工程所需的参数定义好，方便后面的模块调用
    有些参数的值为空是因为它会变化，或者说需要从其它地方获取
    不为空的参数一般是固定下来了

"""
class Config:

    # 配置 package_name, adb_location, mail_host, mail_user, mail_pass
    package_name = ""
    adb_location = ''
    type = ''
    adb = ''
    mail_host = ""  # 设置邮箱服务器
    mail_user = ""  # 邮箱用户名
    mail_pass = ""  # 邮箱密码
    mail_to_list = [''] # 发送给收件人

    device_dict = {}
    thread_instances = []
    thread_instances_monkey = []
    table_list = [] #表格列表
    taken_time = "1.5"
    mail_pre_title = "Automation-Monkey " #邮件标题
    result_table_name = "Result" #测试结果表名
    str_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    data_num = 1000 #数据量1000条
    monkey_seed = str(random.randrange(1, 1000)) #随机生成Monkey的seed值。这里随机生成，所以每一次跑的事件顺序都会不一样
    """
    设置monkey的一些参数
    --throttle 300 表示monkey事件之间执行的时间间隔为300毫秒
    --pct-syskeys 0 表示设置系统按键事件的比例为0%
    --pct-nav 0 表示设置基本导航事件的比例为0%
    --pct-trackball 0 设置轨迹球事件的比例为0%
    --pct-anyevent 0 表示设置任意事件的比例为0%
    
    """
    monkey_parameters = "--throttle 300 --pct-syskeys 0 --pct-nav 0 --pct-trackball 0 --pct-anyevent 0"


    def __init__(self):
        pass

if __name__ == '__main__':

    pass
