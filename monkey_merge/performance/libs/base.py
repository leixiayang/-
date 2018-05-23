#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import platform
import subprocess
import sys
import time
import logging
import subprocess
import traceback
import imp

if __name__ == '__main__':
    project_dir = os.path.split(os.getcwd())
    project_dir = os.path.split(project_dir[0])
    sys.path.append(project_dir[0])
    os.chdir(project_dir[0])    # 将项目所在文件夹设置为 wkdir (目录下必须有 __init__.py 文件)

from performance.config.config import Config

imp.reload(sys) #重新加载sys模块
# sys.setdefaultencoding('utf-8') #设置默认编码格式为utf-8

config = Config() #实例化config.py下的Config()
adb = config.adb


#调用系统cmd执行adb devices命令，通过条件判断是windows系统还是其它系统，调用对应的方法。因为不同系统执行adb devices命令的方法不一样
def start_adb():
    cmd = "%s devices" % Config.adb
    if platform.system() == 'Windows':
        subprocess.check_output(cmd, shell=True)
    else:
        subprocess.getstatusoutput(cmd)
    time.sleep(2)

#这个方法可以从mac电脑获取设备id和型号
def get_info_from_mac():
    '''返回 device id 和 device model'''
    device_dict = {}
    '''
    从adb devices的的结果中进行二次查询获取到设备名称，|grep 就是进行二次查询
    '''
    get_device_id_cmd = "%s devices | grep '\tdevice'" % adb
    '''这里我们要处理getstatusoutput方法返回的结果output,不用管status是什么
        
    '''
    (status, output) = subprocess.getstatusoutput(get_device_id_cmd)
    output = output.decode()

    # logging.info(output)
    if output == '':
        #为空表示没有设备连接到电脑，或者说连接到电脑了，电脑没有识别出来
        logging.info('All device lost')
    else:
        output = output.split("\n")
        # logging.info(output)
        device_id_list = []
        #得到所有插入电脑的设备id列表
        for device_id in output:
            device_id = device_id.replace("\tdevice", "")
            device_id_list.append(device_id)
        # logging.info(device_id_list)

        for device_id in device_id_list:
            device_model = ""
            #adb -s GMT879VO7H9PKRQS shell getprop ro.product.model，得到手机型号，GMT879VO7H9PKRQS就是设备id

            get_device_model_cmd = "%s -s %s shell getprop ro.product.model" % (adb, device_id)
            # logging.info(get_device_model_cmd)

            #这里也一样只用处理output
            (status, output) = subprocess.getstatusoutput(get_device_model_cmd)
            output = output.decode()
            # logging.info("'%s'" %output)
            output = output.strip("\r") # 去除行尾的换行光标
            output = output.split(" ")
            for i in output:
                device_model += i
            # logging.info("'%s'" %device_model)
            device_dict.update({device_model: device_id})
        logging.debug("get the device info: %s" % device_dict)
    return device_dict

def get_info_from_win():
    '''返回 device model 和 device id'''
    device_dict = {}
    #这里是windows上的adb命令，跟mac有所不同，其它都一样
    get_device_id_cmd = "%s devices | findstr /e device" % adb   # /e 对一行的结尾进行匹配
    try:
        output = subprocess.check_output(get_device_id_cmd, shell=True)
        output = output.decode()
        logging.debug('connected devices:\r%s' % output)
    except Exception:
        # traceback.print_exc()
        logging.info("All device lost")
        output = None
    if output is not None:
        output = output.split("\n")
        logging.debug('split connect devices id: %s' % output)
        device_id_list = []
        for device_id in output:
            if 'device' in device_id:
                logging.debug('get device: %s' % device_id)
                device_id = device_id.replace("\tdevice\r", "")
                device_id_list.append(device_id)
        logging.debug('got devices id: %s' % device_id_list)

        for device_id in device_id_list:
            device_model = ""
            get_device_model_cmd = "%s -s %s shell getprop ro.product.model" % (adb, device_id)
            # logging.info(get_device_model_cmd)
            try:
                output_model = subprocess.check_output(get_device_model_cmd, shell=True)
                output_model = output_model.decode()
                logging.debug("'%s'" % output_model)
            except Exception:
                logging.error('get device model error')
                traceback.print_exc()
                output_model = None
            if output_model is not None:
                output_model = output_model.strip("\r\r\n") # 去除行尾的换行光标
                logging.debug(output_model)
                output_model = output_model.split(' ')
            for i in output_model:
                device_model += i
            # logging.info("'%s'" %device_model)
            device_dict.update({device_model: device_id})
        logging.debug("get the device info: %s" % device_dict)
    return device_dict


#后续的模块只需要调用这个方法，不论是mac还是windows都不影响代码执行
def get_device_info():
    if platform.system() == "Darwin":
        return get_info_from_mac()
    elif platform.system() == "Windows":
        return get_info_from_win()

if __name__ == '__main__':
    get_device_info()
    pass

