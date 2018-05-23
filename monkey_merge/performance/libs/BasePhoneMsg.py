#! /usr/bin/python
# coding: utf-8
import os
import re
import subprocess
import math
class getPhone():
    def __init__(self, cmd_log, device_id) :
        self.cmd_log = cmd_log
        self.decive_id = device_id
    def getModel(self, device_id):
        os.system('adb -s %s shell cat /system/build.prop >' %device_id +self.cmd_log)
        l_list = {}
        with open(self.cmd_log, "r",encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                line = line.split('=')
                #Android 系统，如anroid 4.0
                if (line[0] == 'ro.build.version.release'):
                    l_list["release"] = line[1].replace("\n", " ")
                    #手机名字
                if (line[0]=='ro.product.model') or (line[0]=='ro.product.model.bbk'):
                    l_list["phone_name"] = line[1].replace("\n", " ")
                    #手机品牌
                if (line[0]=='ro.product.brand'):
                     l_list["phone_model"] = line[1].replace("\n", " ")

        # 删除本地存储的手机信息文件
        if os.path.exists(self.cmd_log):
            os.remove(self.cmd_log)
        return l_list

    def get_men_total(self, device_id):
        os.system("adb -s %s shell cat /proc/meminfo >" %device_id + self.cmd_log)
        men_total = ""
        with open(self.cmd_log, "r") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.split('=')
                    if line[0]:
                        men_total = re.findall(r"\d+", line[0])[0]
                        break
        if os.path.exists(self.cmd_log):
            os.remove(self.cmd_log)
        return int(men_total)
    # 得到几核cpu
    def get_cpu_kel(self, device_id):
        os.system("adb -s %s shell cat /proc/cpuinfo >" % device_id + self.cmd_log)
        cpu_kel = 0
        with open(self.cmd_log, "r") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.split(':')
                    if line[0].find("processor") >= 0:
                       cpu_kel += 1
        if os.path.exists(self.cmd_log):
            os.remove(self.cmd_log)
        return str(cpu_kel) + "核"

    # 得到手机分辨率
    def get_app_pix(self, device_id):
        # result = os.popen("adb -s s% shell wm size" % device_id, "r")
        result = subprocess.Popen("adb -s %s shell wm size" % device_id,  shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE).stdout.readlines()
        print("result:",result[0])
        return result[0].decode().split()[-1]
        print(result[0].decode().split()[-1])
        # print(result.readline().split("Physical size:")[1])

    # 获取内核
    def get_phone_Kernel(self, device_id):
        pix = self.get_app_pix(device_id)
        men_total = self.get_men_total(device_id)
        phone_msg = self.getModel(device_id)
        cpu_sum = self.get_cpu_kel(device_id)
        return phone_msg, men_total, cpu_sum, pix

