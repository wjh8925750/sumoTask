import struct
import threading

from dettlssumo import SUMO
from junction import Junction
from udp import UDP_Server
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
        config.channelsList = {k : list(v.values()) for k, v in config.junction_channels.items()}

    def init_junctions(self):
        import xml.etree.ElementTree as ET
        tree = ET.parse(self.scenario_path + 'sumodata/shihuxilu.net.xml')
        root = tree.getroot()
        for item in root.findall('junction'):
            if item.attrib['type'] == 'traffic_light':
                junctionid = item.attrib['id']
                if junctionid in config.devices.keys():
                    config.junctions.append(junctionid)
                    config.junction_lanes[junctionid] = item.attrib['incLanes'].split()
                    print("        1.3、从net路网中读取的拥有信号灯及其链路配置信息config.junctions：",config.junctions)

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
    print("4、启动接收灯色数据的线程")
    process_tlsqueue_run = threading.Thread(target=main.tlsudpser.run)
    print("5、启动处理灯色数据的线程")
    process_tlsqueue_thread = threading.Thread(target = main.process_tlsqueue)
    threads.append(process_tlsqueue_run)
    threads.append(process_tlsqueue_thread)
    for thread in threads:
        thread.start()
    print("6、启动sumo仿真系统，开始进行sumo消息订阅及相关设置")
    main.start_sumo()









