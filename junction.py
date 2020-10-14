

import config
class Junction:
    def __init__(self, junctionid):
        self.junctionid = junctionid                     #仿真路口id
        self.tlLogicid = junctionid                      #仿真信号灯id
        self.channels = self.getChannels()               #通道与仿真链路的对应关系
        self.linknum = self.getLinknum()                 #路口仿真链路的数量
        self.groupnum = self.getGroupnum()               #路口仿真的通道数量
        self.detectors = self.getDetectors()             #仿真路口检测器
        self.addr = self.getAddr()                       #信号机通信地址(IP.Port)


    def getChannels(self):
        channels = config.junction_channels[self.junctionid]
        return channels

    def getLinknum(self):
        linknum = config.junction_linknum[self.junctionid]
        return linknum

    def getAddr(self):
        addr = config.addrs[self.junctionid]
        return addr

    def getGroupnum(self):
        return config.junction_groupnum[self.junctionid]

    def getDetectors(self):
        detectors = config.junction_detectors[self.junctionid]
        return detectors





