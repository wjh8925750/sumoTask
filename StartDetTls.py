import struct
import threading

from dettlssumo import SUMO
from udp import UDP_Server
import queuedata


import config
class Main:
    def __init__(self):
        self.scenario_path = './scenario/'
        self.init_param()
        self.init_sumo()          #配置sumo启动文件
        self.init_tls_server()

    def init_param(self):
        from configparser import ConfigParser
        cfg = ConfigParser()
        cfg.read(self.scenario_path + 'param.ini', encoding='utf-8')
        config.steplength = cfg.getfloat('sumoconfig', 'steplength')
        config.sumocfg = cfg.get('sumoconfig', 'sumocfg')
        config.radius = cfg.getint('sumoconfig', 'radius')
        config.cinductionloopid = cfg.get('sumoconfig', 'cinductionloopid')
        config.tlsport = cfg.getint('sumoconfig', 'tlsport')
        print(config.sumocfg)
        print(type(config.radius))

    def init_sumo(self):
        self.sumo = SUMO(config.sumocfg)   #sumoconfig中应传入将要打开的.sumocfg文件的路径
        self.sumo.subInductionloop(config.cinductionloopid, config.radius)


    def init_tls_server(self):
        self.tlsudpser = UDP_Server(config.tlsport, queuedata.tls_queue)


    def start_sumo(self):
        self.sumo.simulation()


    def process_tlsqueue(self):
        while True:
            if not queuedata.tls_queue.empty():
                try:
                    tlsbin = queuedata.tls_queue.get()
                    tlsinfo = struct.unpack('>H' + 'B'*(len(tlsbin)-2), tlsbin)
                    #print(tlsinfo)

                except Exception as e:
                    print(e)
                #print("queuedata = ", tlsbin)



if __name__ == "__main__":
    main = Main()
    threads = []
    process_tlsqueue_thread = threading.Thread(target = main.process_tlsqueue)
    process_tlsqueue_run = threading.Thread(target = main.tlsudpser.run)
    threads.append(process_tlsqueue_thread)
    threads.append(process_tlsqueue_run)
    for thread in threads:
        thread.start()
    main.start_sumo()









