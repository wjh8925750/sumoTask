import struct
import threading

from dettlssumo import SUMO
from junction import Junction
from udp import UDP_Server, UDP_Client
import queuedata


import config
class Main:
    def __init__(self):
        self.scenario_path = './scenario/'
        self.init_param()
        self.init_device()
        self.init_junctions()     #得到配置文件中的路口
        self.init_tls_server()
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
                    config.junction_groupnum[row[0]] = int(row[6])                                          #路口id对应的通道数量，与信号机发送的灯色个数一致

        config.channelsList = {k : list(v.values()) for k, v in config.junction_channels.items()}

    def init_junctions(self):
        import xml.etree.ElementTree as ET
        tree = ET.parse(self.scenario_path + 'sumodata/shihuxilu_add.net.xml')
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
        tree2 = ET.parse(self.scenario_path + 'sumodata/detector_add.add.xml')
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


    def init_tls_server(self):
        self.tlsudpser = UDP_Server(config.tlsport, queuedata.tls_queue)

    def init_sumo(self):
        print("3、初始化sumo仿真对象")
        SUMO.junctions = dict()
        for jid in config.junctions:
            SUMO.junctions[jid] = Junction(jid)
            print("        3.1、初始化SUMO.junctions成员变量：", Junction(jid))
        self.sumo = SUMO(config.sumocfg)   #sumoconfig中应传入将要打开的.sumocfg文件的路径
        self.sumo.subInductionloop(config.cinductionloopid, config.radius)

    def start_sumo(self):
        self.sumo.simulation()





    def process_detqueue(self):
        """
            封装检测器数据消息并发送到对应设备
            暂设所有检测器均无故障
        """
        while True:
            if not queuedata.det_queue.empty():
                detdata = queuedata.det_queue.get()
                for junctionid in config.junctions:
                    J = Junction(junctionid)
                    # detdata = {'J1_1': {16: 1}, 'J1_10': {16: 0}, 'J1_11': {16: 0}, 'J1_12': {16: 0}, 'J1_2': {16: 0},
                    #  'J1_3': {16: 0}, 'J1_4': {16: 0}, 'J1_5': {16: 0}, 'J1_6': {16: 0}, 'J1_7': {16: 0},
                    #  'J1_8': {16: 0}, 'J1_9': {16: 0}}
                    detstatus = ''.join(['1' if detdata[d][16] else '0' for d in J.detectors])
                    if len(detstatus) < 17:    #暂设检测器都没有故障，故障位全为0
                        tmp = detstatus + '0'*(64 - len(detstatus))
                    else:
                        tmp = detstatus[:16] + '0' * 16 + detstatus[16:] + '0' * (48 - len(detstatus))
                    print(tmp)
                    try:
                        bindet = struct.pack('>Q', int(tmp, 2))

                    except Exception as e:
                        print("========================")
                        print(e)
                    udpcli = UDP_Client(J.addr, 0)
                    udpcli.send(bindet)




    def process_tlsqueue_grouped(self):
        """
        处理接收灯色数据，基于分组
        """

        mask = 0b00001111  ##通过与运算先解码后四位(半个字节)，然后通过移位运算解码前四位
        bit2ryg = {0: '0', 1: 'r', 2: 'y', 3: 'g', 4: 'g', 5: 'o'}
        while True:
            if not queuedata.tls_queue.empty():
                print("        6.1、当前消息队列中信号灯色的数量：", queuedata.tls_queue.qsize())
                try:
                    tlsbin = queuedata.tls_queue.get()
                    tlsinfo = struct.unpack('>H' + 'B' * (len(tlsbin) - 2),
                                            tlsbin)  # '>H'表示大端序解析两个字节 'B'*(len(tlsbin)-2)表示剩余的字节，每一个字节解析一次
                    cstatus = []
                    for b in tlsinfo[1:]:
                        cstatus.append(b & mask)  # 首先解析后四位
                        cstatus.append(b >> 4)    # 然后解析前四位，移位运算并不影响list表中的值
                    print("cstatus = ", cstatus)
                    print("        6.2、当前接收到的信号灯信息所属的路口id：= ", tlsinfo[0])
                    if str(tlsinfo[0]) in config.junctions:  # 仅处理关注的路口
                        junctionid = config.devices2junction[tlsinfo[0]]
                        tlsid = SUMO.junctions[junctionid].tlLogicid      # 信号id
                        groupNum = SUMO.junctions[junctionid].groupnum  # 路口对应的通道数量
                        ryg = [bit2ryg[cstatus[i]] for i in range(groupNum)]
                        rygstr = ''.join(ryg)
                        print("        6.3、经过处理后，发往设置消息队列(ryg_queue)的灯色信息：", (tlsid, rygstr))
                        queuedata.ryg_queue.put((tlsid, rygstr))

                except Exception as e:
                    print(e)



    def process_tlsqueue(self):
        """
        处理接收的灯色数据
        """
        mask = 0b00001111     ##通过与运算先解码后四位(半个字节)，然后通过移位运算解码前四位
        bit2ryg = {0:'0', 1:'r', 2:'y', 3:'g', 4:'g', 5:'o'}
        while True:
            if not queuedata.tls_queue.empty():
                print("        6.1、当前消息队列中信号灯色的数量：", queuedata.tls_queue.qsize())
                try:
                    tlsbin = queuedata.tls_queue.get()
                    tlsinfo = struct.unpack('>H' + 'B'*(len(tlsbin)-2), tlsbin) #'>H'表示大端序解析两个字节 'B'*(len(tlsbin)-2)表示剩余的字节，每一个字节解析一次
                    cstatus = []
                    for b in tlsinfo[1:]:
                        cstatus.append(b & mask)  #首先解析后四位
                        cstatus.append(b >> 4)    #然后解析前四位，移位运算并不影响list表中的值
                    print("cstatus = ", cstatus)
                    print("        6.2、当前接收到的信号灯信息所属的路口id：= ", tlsinfo[0])
                    if str(tlsinfo[0]) in config.junctions:        #仅处理关注的路口
                        junctionid = config.devices2junction[tlsinfo[0]]
                        tlsid = SUMO.junctions[junctionid].tlLogicid      #信号id
                        channels = SUMO.junctions[junctionid].channels     #通道与链路对应的字典
                        ryg = ['g'] * SUMO.junctions[junctionid].linknum   #初始化所有链路的等色
                        for c, l in channels.items():
                            for link in l:
                                ryg[link] = bit2ryg[cstatus[c-1]]
                        rygstr = ''.join(ryg)
                        print("        6.3、经过处理后，发往设置消息队列(ryg_queue)的灯色信息：",(tlsid,rygstr))
                        queuedata.ryg_queue.put((tlsid,rygstr))

                except Exception as e:
                    print(e)
                #print("queuedata = ", tlsbin)



if __name__ == "__main__":
    main = Main()
    threads = []
    process_detqueue_thread = threading.Thread(target=main.process_detqueue)
    print("4、启动接收灯色数据的线程")
    process_tlsqueue_run = threading.Thread(target=main.tlsudpser.run)
    print("5、启动处理灯色数据的线程")
    #process_tlsqueue_thread = threading.Thread(target = main.process_tlsqueue)
    process_tlsqueue_thread = threading.Thread(target= main.process_tlsqueue_grouped)
    threads.append(process_detqueue_thread)
    threads.append(process_tlsqueue_run)
    threads.append(process_tlsqueue_thread)
    for thread in threads:
        thread.start()
    print("6、启动sumo仿真系统，开始进行sumo消息订阅及相关设置")
    main.start_sumo()









