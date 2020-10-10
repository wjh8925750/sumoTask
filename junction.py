

import config
class Junction:
    def __init__(self, junctionid):
        self.junctionid = junctionid                     #仿真路口id
        self.tlLogicid = junctionid                      #仿真信号灯id
        self.channels = self.getChannels()               #通道与仿真链路的对应关系
        self.linknum = self.getLinknum()                 #路口仿真链路的数量

    def getChannels(self):
        channels = config.junction_channels[self.junctionid]
        return channels

    def getLinknum(self):
        linknum = config.junction_linknum[self.junctionid]
        return linknum
