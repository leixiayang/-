#! /usr/bin/python
# coding: utf-8

import time
import subprocess
import os
import sys
import logging
import threading
import platform
import subprocess
import traceback
import datetime
import xlsxwriter
import re
from performance.libs import BaseMonitor
from performance.libs import BaseReport
from performance.libs import BaseAnalysis
from performance.libs import BasePhoneMsg
from performance.libs import BaseCashEmnu as go


if __name__ == '__main__':
    project_dir = os.path.split(os.getcwd())
    project_dir = os.path.split(project_dir[0])
    sys.path.append(project_dir[0])
    os.chdir(project_dir[0])    # 将项目所在文件夹设置为 wkdir (目录下必须有 __init__.py 文件)

from performance.config.config import Config
from performance.libs.mail import SendMail
from performance.monkey.monkey_stop import stop_monkey

wkdir = os.getcwd()
adb = Config.adb
package_name = Config.package_name
monkey_seed = Config.monkey_seed
monkey_parameters = Config.monkey_parameters
mail_host = Config.mail_host
mail_user = Config.mail_user
mail_pass = Config.mail_pass
mail_to_list = Config.mail_to_list

#改动begin
def get_phome(device_id):
    bg = BasePhoneMsg.getPhone("log.txt",device_id).get_phone_Kernel(device_id)
    print("bg:", bg)
    app = {}
    app["phone_name"] = bg[0]["phone_name"] + "_" + bg[0]["phone_model"]
    app["pix"] = bg[3]
    app["rom"] = bg[1]
    app["kel"] = bg[2]
    return app

def get_line(log,num):
    cnt = 0
    if num == 0 :
        return ""
    with open(log, encoding="utf-8") as log_file:
        lines = log_file.readlines()
        for line in lines:
            cnt += 1
            if cnt == num:
                return line

def get_error(log, workbook, bo):
    crash = []
    num = 0
    with open(log, encoding="utf-8") as monkey_log:
        lines = monkey_log.readlines()
        for line in lines:
            num += 1
            if re.findall(go.ANR, line):
                previous_line = get_line(log, num - 2)
                latter_line = get_line(log, num + 2)
                str1 = "存在anr错误:"
                print(str1, previous_line, line, latter_line)
                crash.append(str1+'\n'+ previous_line+'\n'+ line+ latter_line)
            if re.findall(go.CRASH, line):
                previous_line = get_line(log, num - 2)
                latter_line = get_line(log, num + 2)
                str2 = "存在crash错误:"
                print( str2, previous_line, line, latter_line)
                crash.append(str2+'\n'+ previous_line+'\n'+ line+ latter_line)
            if re.findall(go.EXCEPTION, line):
                previous_line = get_line(log, num-2)
                latter_line = get_line(log, num+2)
                str3 = "存在exception错误:"
                print(str3, previous_line, line, latter_line)
                crash.append(str3+'\n'+ previous_line+'\n'+ line+ latter_line)
    if len(crash):
        worksheet2 = workbook.add_worksheet("异常日志")
        bo.crash(worksheet2, crash)

def report(app,sumTime, workbook, bo, device_id):

    header = get_phome(device_id)

    worksheet1 = workbook.add_worksheet("性能监控")
    app["maxMen"] = BaseAnalysis.maxMen(BaseMonitor.men)
    app["avgMen"] = BaseAnalysis.avgMen(men=BaseMonitor.men, total=header["rom"])
    app["maxCpu"] = BaseAnalysis.maxCpu(BaseMonitor.cpu)
    app["avgCpu"] = BaseAnalysis.avgCpu(BaseMonitor.cpu)
    app["maxFps"] = BaseAnalysis.avgFps(BaseMonitor.fps)
    app["avgFps"] = BaseAnalysis.avgFps(BaseMonitor.fps)
    app["afterBattery"] = BaseMonitor.get_battery(device_id)
    _maxFlow = BaseAnalysis.maxFlow(BaseMonitor.flow)
    _avgFLow = BaseAnalysis.avgFlow(BaseMonitor.flow)
    app["maxFlowUp"] = _maxFlow[0]
    app["maxFlowDown"] = _maxFlow[1]
    app["avgFlowUp"] = _avgFLow[0]
    app["avgFlowDown"] = _avgFLow[1]
    header["time"] = sumTime
    header["type"] = app["type"]
    bo.monitor(worksheet=worksheet1, header=header, data=app)
    print("---monkey_log------")
    print(app["monkey_log"])
    get_error(log=app["monkey_log"], workbook=workbook, bo=bo)

    worksheet3 = workbook.add_worksheet("详细信息")
    app = {}
    app["cpu"] = BaseMonitor.cpu
    app["men"] = BaseMonitor.men
    app["flow"] = BaseMonitor.flow
    app["battery"] = BaseMonitor.battery
    app["fps"] = BaseMonitor.fps
    bo.analysis(worksheet3, app)

#改动end


def main(device_id, device_model):
    try:
        stop_monkey(device_id, device_model)

        log_file_name = generate_log_file_name(device_model)
        log_file_name_with_location = generate_log_file_name_with_location(device_model)

        ## 改动begin
        monkey_duration = start_monkey(adb, device_id, device_model, monkey_seed, monkey_parameters, package_name)
        time.sleep(1)

        #写入报告
        workbook = xlsxwriter.Workbook(device_model + '_' + device_id + '_' + time.strftime("%Y-%m-%d~%H-%M-%S") + '_' + 'report.xlsx')
        bo = BaseReport.OperateReport(workbook)
        time.sleep(1)

        # 检查日志
        monkey_log = "%s.txt" % (log_file_name_with_location)
        starttime = datetime.datetime.now()
        time.sleep(1)
        while True:
            with open(monkey_log, encoding='utf-8') as monkeylog:
                print("collect infos and check log ...")
                BaseMonitor.get_cpu(device_id, package_name)
                BaseMonitor.get_men(device_id, package_name)
                BaseMonitor.get_fps(device_id, package_name)
                BaseMonitor.get_battery(device_id)
                BaseMonitor.get_flow(device_id, package_name, type = 'wifi')
                time.sleep(1) # 每1秒采集检查一次
                if monkeylog.read().count('Monkey finished') > 0:
                    endtime = datetime.datetime.now()
                    print("测试完成")
                    # app = {"beforeBattery": BaseMonitor.get_battery(), "net": mc["net"], "monkey_log": mc["monkey_log"]}
                    app = {"beforeBattery": BaseMonitor.get_battery(device_id), "type": "wifi", "monkey_log": monkey_log}
                    report(app, str((endtime - starttime).seconds) + "秒",workbook, bo, device_id)
                    print('Sumtime:', str((endtime - starttime).seconds)+ "秒")
                    bo.close()
                    break
        ## 改动end

        time.sleep(1)
        capture_screen(device_id, log_file_name, log_file_name_with_location, monkey_duration)
        time.sleep(1)
        reboot_device(device_id, device_model)
    except Exception:
        traceback.print_exc()

#获取apk名字的方法，只要把apk放在工程目录下就可以找到，这个方法会遍历工程下所有目录
def get_apk_name():
    abspath = os.path.abspath(__file__)
    current_location = os.path.split(abspath)[0]
    files_in_current_location = os.listdir(current_location)

    for i in files_in_current_location:
        if 'apk' in i:
            apk_name = i
    return apk_name



def generate_log_file_name(device_model):
    # 生成 crash log 名字
    current_time = time.strftime("%m-%d~%H-%M-%S")
    log_file_name = device_model + '_' + current_time
    return log_file_name


def generate_log_file_name_with_location(device_model):
    # 生成当前 Log 存储路径
    location_log = os.path.join(wkdir, 'performance', 'monkey', 'monkeylog')
    current_date = time.strftime("%Y-%m-%d")
    current_date = os.path.join(location_log, current_date)
    if os.path.exists(current_date) is False:
        os.mkdir(current_date)
    log_file_name = generate_log_file_name(device_model)
    log_file_name_with_location = os.path.join(current_date, log_file_name)
    return log_file_name_with_location

'''
开始执行monkey脚本
'''
def start_monkey(adb, device_id, device_model, monkey_seed, monkey_parameters, package_name):
    logging.info("start monkey with %s" % device_model)
    log_file_name_with_location = generate_log_file_name_with_location(device_model)
    monkey_start_time = time.time()
    cmd_monkey = "%s -s %s shell monkey -s %s -p %s %s > %s.txt" % (
        adb, device_id, monkey_seed, package_name, monkey_parameters, log_file_name_with_location)

    if platform.system() == "Darwin":
        #Darwin就是mac系统的名称
        logging.info("Monkey cmd: %s" % cmd_monkey)
        status, output = subprocess.getstatusoutput(cmd_monkey)
    elif platform.system() == "Windows":
        logging.info("Monkey cmd: %s" % cmd_monkey)
        #output = subprocess.check_output(cmd_monkey, shell=True)
        subprocess.Popen(cmd_monkey, shell=True)
    logging.info("monkey end with %s" % device_model)
    monkey_end_time = time.time()
    monkey_duration = round((monkey_end_time - monkey_start_time) / 3600, 2)
    return str(monkey_duration)

#截屏的方法
def capture_screen(device_id, log_file_name, log_file_name_with_location, monkey_duration):
    logging.info("capture screen")
    cmd_capture = "%s -s %s shell screencap -p /sdcard/%s.png" % (adb, device_id, log_file_name)
    status, output = subprocess.getstatusoutput(cmd_capture)
    if output == "":
        cmd_pull_screenshot = "%s -s %s pull /sdcard/%s.png %s.png" % (
            adb, device_id, log_file_name, log_file_name_with_location)
        status, output = subprocess.getstatusoutput(cmd_pull_screenshot)
        logging.info(output)
    # rename log file
    if output == "":
        log_file_name_location_final = log_file_name_with_location + '_' + monkey_duration
        os.rename(log_file_name_with_location + '.png', log_file_name_location_final + '.png')

#处理无响应和崩溃相关的日志，生成邮件的一些内容
def deal_with_log(log_file_name_with_location, monkey_duration):
    # analyze with log:
    logging.info("deal_with_log")
    f_full_log = open(log_file_name_with_location + '.txt', 'r')
    full_log = f_full_log.readlines()
    f_full_log.close()
    full_log_lines_number = len(full_log)
    anr = '// NOT RESPONDING: ' + package_name + ' '
    crash = '// CRASH: ' + package_name + ' '
    exception = '// EXCEPTION: ' + package_name + ' '
    mail_content = ''
    for i in range(full_log_lines_number):
        if (exception in full_log[i]) | (anr in full_log[i]) | (crash in full_log[i]):
            f_crash_log = open(log_file_name_with_location + '.txt', 'r')
            f_crash_log.close()
            for j in range(i, full_log_lines_number):
                mail_content = mail_content + full_log[j] + '\r'
                # f_crash_log = open(log_file_name_with_location + '.txt', 'a+')
                # f_crash_log.writelines(full_log[j])
                # f_crash_log.close()
            break
    if mail_content == "":
        return mail_content
    else:
        # rename log file
        log_file_name_location_final = log_file_name_with_location + ' ' + monkey_duration + "hour"
        tmp = log_file_name_with_location.split('/')
        # logging.info(tmp)
        log_file_name = tmp[-1]
        mail_content = log_file_name + '_' + monkey_duration + "hour" + '\r\r' + mail_content
        os.rename(log_file_name_with_location + '.txt', log_file_name_location_final + '.txt')
        return mail_content

#重启设备的方法
def reboot_device(device_id, device_model):
    if platform.system() == "Darwin":
        logging.info("Reboot %s" % device_model)
        status, output = subprocess.getstatusoutput(adb + ' -s ' + device_id + ' reboot')
    elif platform.system() == "Windows":
        subprocess.check_output("%s -s %s reboot" % (adb, device_id), shell=True)

#monkey线程类
class MonkeyThread(threading.Thread):
    def __init__(self, device_id, device_model):
        threading.Thread.__init__(self)
        self.thread_stop = False
        self.device_id = device_id
        self.device_model = device_model

    def run(self):
        time.sleep(6)
        main(self.device_id, self.device_model)

#给每一台设备创建一个线程跑monkey
def create_threads_monkey(device_dict):
    thread_instances = []
    if device_dict != {}:
        logging.info('changed device: %s' % device_dict)
        for model_device, id_device in device_dict.items():
            device_model = model_device
            device_id = id_device
            instance = MonkeyThread(device_id, device_model)
            thread_instances.append(instance)
        for instance in thread_instances:
            instance.start()

if __name__ == '__main__':
    pass

