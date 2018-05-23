import subprocess
import os
import re
from wsgiref.validate import validator


# from performance.libs.base import get_device_info


cpu = []
men = []
flow = [[], []]
fps = []
battery = []


# 修改如下
def get_cpu(device_id, pkg_name):
    cmd = "adb -s %s shell top -n 1| findstr %s" %(device_id, pkg_name)
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
    print("output:",output)
    if output[0].split()[-1].decode() == pkg_name:  # 只有包名相等
        cpu.append(float(output[0].split()[2].decode().split("%")[0]))
        print("----cpu-----")
        print(cpu)
        return cpu

def get_men(device_id, pkg_name):
    cmd = "adb -s %s shell  dumpsys  meminfo %s" % (device_id, pkg_name)
    print(cmd)
    men_s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
    for info in men_s:
        if len(info.split()) and info.split()[0].decode() == "TOTAL":
            men.append(int(info.split()[1].decode()))
            print("----men----")
            print(men)
            return men
# 得到fps
def get_fps(device_id, pkg_name):
    _adb = "adb -s %s shell dumpsys gfxinfo %s" % (device_id, pkg_name)
    print(_adb)
    results = os.popen(_adb).read().strip()
    frames = [x for x in results.split('\n') if validator(x)]
    frame_count = len(frames)
    jank_count = 0
    vsync_overtime = 0
    render_time = 0
    for frame in frames:
        time_block = re.split(r'\s+', frame.strip())
        if len(time_block) == 3:
            try:
                render_time = float(time_block[0]) + float(time_block[1]) + float(time_block[2])
            except Exception as e:
                render_time = 0

        '''
        当渲染时间大于16.67，按照垂直同步机制，该帧就已经渲染超时
        那么，如果它正好是16.67的整数倍，比如66.68，则它花费了4个垂直同步脉冲，减去本身需要一个，则超时3个
        如果它不是16.67的整数倍，比如67，那么它花费的垂直同步脉冲应向上取整，即5个，减去本身需要一个，即超时4个，可直接算向下取整

        最后的计算方法思路：
        执行一次命令，总共收集到了m帧（理想情况下m=128），但是这m帧里面有些帧渲染超过了16.67毫秒，算一次jank，一旦jank，
        需要用掉额外的垂直同步脉冲。其他的就算没有超过16.67，也按一个脉冲时间来算（理想情况下，一个脉冲就可以渲染完一帧）

        所以FPS的算法可以变为：
        m / （m + 额外的垂直同步脉冲） * 60
        '''
        if render_time > 16.67:
            jank_count += 1
            if render_time % 16.67 == 0:
                vsync_overtime += int(render_time / 16.67) - 1
            else:
                vsync_overtime += int(render_time / 16.67)

    _fps = int(frame_count * 60 / (frame_count + vsync_overtime))
    fps.append(_fps)
    print("-----fps------")
    print(fps)
    return fps


def get_battery(device_id):
    _batter = subprocess.Popen("adb -s " + device_id + " shell dumpsys battery" , shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE).stdout.readlines()
    for info in _batter:
        if len(info.split()) == 0:
            continue;
        if info.split()[0].decode() == "level:":
            battery.append(int(info.split()[1].decode()))
            print("-----battery------")
            print(battery)
            return int(info.split()[1].decode())


def get_pid(device_id, pkg_name):
    pid = subprocess.Popen("adb -s " + device_id + " shell ps | findstr " + pkg_name, shell=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE).stdout.readlines()
    for item in pid:
        if item.split()[-1].decode() == pkg_name:
            return item.split()[1].decode()


def get_flow(device_id, pkg_name, type):
    pid = get_pid(device_id, pkg_name)
    if pid is not None:
        _flow = subprocess.Popen("adb -s " + device_id + " shell cat /proc/" + pid + "/net/dev", shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE).stdout.readlines()
        for item in _flow:
            if type == "wifi" and item.split()[0].decode() == "wlan0:":  # wifi
                # 0 上传流量，1 下载流量
                flow[0].append(int(item.split()[1].decode()))
                flow[1].append(int(item.split()[9].decode()))
                print("------flow---------")
                print(flow)
                return flow
            if type == "gprs" and item.split()[0].decode() == "rmnet0:":  # gprs
                print("--------------")
                flow[0].append(int(item.split()[1].decode()))
                flow[1].append(int(item.split()[9].decode()))
                return flow
    else:
        flow[0].append(0)
        flow[1].append(0)
        return flow

if __name__ == '__main__':
    get_cpu("com.hhly.community.test")

