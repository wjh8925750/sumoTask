
import threading

from flow_sumo import SUMO
from junction import Junction

import queuedata


import config
class Main:
    def __init__(self):
        self.scenario_path = './scenario/'
        self.init_param()
        self.init_device()
        self.init_junctions()     #得到配置文件中的路口
        #self.init_tls_server()
        self.init_sumo()  # 配置sumo启动文件

    def init_param(self):
        print("1、读取配置文件信息")
        from configparser import ConfigParser
        cfg = ConfigParser()
        cfg.read(self.scenario_path + 'param.ini', encoding='utf-8')
        config.steplength = cfg.getfloat('sumoconfig', 'steplength')
        config.sumocfg = cfg.get('sumoconfig', 'sumocfg')
        config.radius = cfg.getint('sumoconfig', 'radius')
        config.cinductionloopid = cfg.get('sumoconfig', 'cinductionloopid')
        config.clane = cfg.get('sumoconfig', 'clane')
        config.tlsport = cfg.getint('sumoconfig', 'tlsport')
        print("        1.1、udp服务器端口号：",config.tlsport)

    def init_device(self):
        import csv
        with open(self.scenario_path+'devices.csv','r') as fp:
            reader = csv.reader(fp)
            next(reader)     #跳过标题
            for row in reader:
                if '' not in row:
                    config.devices[row[0]] = int(row[1])                                                    #路口id对应的设备id
                    config.devices2junction[int(row[1])] = row[0]                                           #设备id对应的路口id
                    config.addrs[row[0]] = (row[2], int(row[3]))                                            #路口id对用的信号机ip地址
                    config.junction_channels[row[0]] = eval(row[5])                                         #向eval()函数中传入字典字符串，则生成一个字典
                    print("        1.2、设备配置文件中的信号灯id:通道:[链路索引]：", config.junction_channels)
                    config.junction_linknum[row[0]] = int(row[4])                                           #路口id对应的链路数量
                   # config.junction_groupnum[row[0]] = int(row[6])                                          #路口id对应的通道数量，与信号机发送的灯色个数一致

        config.channelsList = {k : list(v.values()) for k, v in config.junction_channels.items()}

    def init_junctions(self):
        import xml.etree.ElementTree as ET
        tree = ET.parse(self.scenario_path + 'sumodata/pudong100.net.xml')
        root = tree.getroot()
        for item in root.findall('junction'):
            if item.attrib['type'] == 'traffic_light':
                junctionid = item.attrib['id']
                if junctionid in config.devices.keys():
                    config.junctions.append(junctionid)
                    config.junction_lanes[junctionid] = item.attrib['incLanes'].split()
                    print("        1.3、从net路网中读取的拥有信号灯及其链路配置信息config.junctions：",config.junctions)
                    print("        1.4、从net路网中读取的拥有信号灯及其链路配置信息的config.junction_lanes: ", config.junction_lanes)

        # 注意修改为实际使用场景的检测器det文件名
        #tree2 = ET.parse(self.scenario_path + 'sumodata/detector_add.add.xml')
        tree2 = ET.parse(self.scenario_path + 'sumodata/detectorPudong.add.xml')
        root2 = tree2.getroot()
        for k, v in config.junction_lanes.items():
            config.junction_detectors[k] = list()
            for det in root2.findall('e1Detector'):
                if det.attrib['lane'] in v:
                    config.junction_detectors[k].append(det.attrib['id'])
        print("        1.5、从net路网中读取的拥有信号灯及其链路配置的路口道路检测器config.junction_detectors: ", config.junction_detectors)
        ##需要对检测器的顺序重新排序： {'30001': ['J1_1', 'J1_10', 'J1_11', 'J1_12', 'J1_2', 'J1_3', 'J1_4', 'J1_5', 'J1_6', 'J1_7', 'J1_8', 'J1_9']}
        #下述排序仅在路口对应的检测器数小于100时有效
        # for k,v in config.junction_detectors.items():
        #     tempDectors = []
        #     i = 0
        #     while i < len(v):
        #         if int(v[i].split('_')[-1]) > 9:
        #             tempDectors.append(v[i])
        #             v.remove(v[i])
        #             i-=1
        #         i+=1
        #     config.junction_detectors[k] += tempDectors
        for k, v in config.junction_detectors.items():
            v.sort(key = lambda e: int(e.split('_')[-1]))
        print("        1.5.1、经过排序后的路口检测器config.junction_detectors: ", config.junction_detectors)




    def init_sumo(self):
        print("3、初始化sumo仿真对象")
        SUMO.junctions = dict()
        for jid in config.junctions:
            SUMO.junctions[jid] = Junction(jid)
            print("        3.1、初始化SUMO.junctions成员变量：", Junction(jid))
        self.sumo = SUMO(config.sumocfg)   #sumoconfig中应传入将要打开的.sumocfg文件的路径
        self.sumo.subInductionloop(config.cinductionloopid, config.clane, config.radius)

    def start_sumo(self):
        self.sumo.simulation()


    # #处理检测器流量线程
    # def process_flowQueue(self):
    #     while True:
    #         if not queuedata.flow_queue.empty():
    #             tmp = queuedata.flow_queue.get()
    #             print("接收流量线程 flowDict =", tmp)




if __name__ == "__main__":
    main = Main()
    #threads = []


    print("5、启动处理灯色数据的线程")
    #process_tlsqueue_thread = threading.Thread(target = main.process_tlsqueue)
    #process_flowqueue_thread = threading.Thread(target= main.process_flowQueue)
    # threads.append(process_flowqueue_thread)
    # for thread in threads:
    #     thread.start()
    print("6、启动sumo仿真系统，开始进行sumo消息订阅及相关设置")
    main.start_sumo()









