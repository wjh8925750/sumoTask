from dettlssumo import SUMO

import config




class Main:
    def __init__(self):
        self.scenario_path = './scenario/'
        self.init_param()
        self.init_sumo()          #配置sumo启动文件


    def init_param(self):
        from configparser import ConfigParser
        cfg = ConfigParser()
        cfg.read(self.scenario_path + 'param.ini', encoding='utf-8')
        config.sumocfg = cfg.get('sumoconfig', 'sumocfg')
        config.radius = cfg.get('sumoconfig', 'radius')
        config.cinductionloopid = cfg.get('sumoconfig', 'cinductionloopid')
        print(config.sumocfg)

    def init_sumo(self):
        self.sumo = SUMO(config.sumocfg)   #sumoconfig中应传入将要打开的.sumocfg文件的路径
        #self.sumo.subInductionloop(config.cinductionloopid, config.radius)

    def start_sumo(self):
        self.sumo.simulation()

if __name__ == "__main__":
    main = Main()
    main.start_sumo()









