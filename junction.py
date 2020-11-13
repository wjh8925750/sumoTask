import datetime
import json
import time
import config
class Junction:
    def __init__(self, junctionid):
        self.junctionid = junctionid                     #仿真路口id
        self.deviceid = self.getDeviceID()               #信号机ID
        self.tlLogicid = junctionid                      #仿真信号灯id
        self.lanes = self.getLanes()                     #仿真路口包含车道（进入路口）
        self.channels = self.getChannels()               #通道与仿真链路的对应关系
        self.linknum = self.getLinknum()                 #路口仿真链路的数量
#        self.groupnum = self.getGroupnum()               #路口仿真的通道数量
        self.detectors = self.getDetectors()             #仿真路口检测器
        self.addr = self.getAddr()                       #信号机通信地址(IP.Port)


#     def __init__(self):
#         self.time = self.getLocalTime()

    def getDeviceID(self):
        deviceid = config.devices[self.junctionid]
        return deviceid

    def getChannels(self):
        channels = config.junction_channels[self.junctionid]
        return channels
    def getLanes(self):
        lanes = config.junction_lanes[self.junctionid]
        return lanes

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

    def getCreateTime(self, frameno):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        now = now[:-3]
        simTime = frameno * config.steplength * 1000  # 毫秒数
        s, ms = divmod(simTime, 1000)
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        h %= 24
        strSimTime = ("%02d:%02d:%02d.%03d" % (h, m, s, ms))
        now = now[:10] + ' ' + strSimTime
        return now


    def getfsoinfo(self, detList, laneList):
        """
            生成fso消息，
            detList:[{detectorid: num}...]
            laneList:[{laneId:{speed, waiting, occupancy}...]
        """
        fsoDict = {
            'sourcetype': 'simu',
            'infotype': 'status/fso',
            'agentid': '27',
            'createtime': 'xxxx-xx-xx xx:xx:xx.xxx',
            'location': '',
            'data':[]
        }
        dataList = []
        fsoDict['agentid'] = str(self.deviceid)
        fsoDict['createtime'] = self.getLocalTime()
        for i in range(len(self.detectors)):
            # print(self.detectors)
            # print(len(self.detectors))
            # print(self.lanes[i])
            dataDict = {'recordid':'', 'detectorid':0, 'flow':0, 'speed':0.0, 'occupancy':0.0}
            dataDict['recordid'] = str(self.deviceid) + '____' + self.getLocalTime() + '____' + str(i+1)
            dataDict['detectorid'] = i + 1
            dataDict['flow'] = detList[0][self.detectors[i]] + detList[1][self.detectors[i]]\
                               + detList[2][self.detectors[i]] + detList[3][self.detectors[i]] + detList[4][self.detectors[i]]
            dataDict['speed'] = (laneList[0][self.lanes[i]][0] + laneList[1][self.lanes[i]][0] +
                                 laneList[2][self.lanes[i]][0] + laneList[3][self.lanes[i]][0] + laneList[4][self.lanes[i]][0]) / 605
            dataDict['queue'] = max(laneList[0][self.lanes[i]][1], laneList[1][self.lanes[i]][1],
                                    laneList[2][self.lanes[i]][1], laneList[3][self.lanes[i]][1], laneList[4][self.lanes[i]][1])
            dataDict['occupancy'] = (laneList[0][self.lanes[i]][2]  + laneList[1][self.lanes[i]][2] +
                                     laneList[2][self.lanes[i]][2] + laneList[3][self.lanes[i]][2] + laneList[4][self.lanes[i]][2]) / 605
            dataList.append(dataDict)
        fsoDict['data'] = dataList
        json_fso = json.dumps(fsoDict)
        return json_fso




    # def getLocalTime(self):
    #     now = datetime.datetime.now().strftime('%Y-%m-%d %H:%H:%S.%f')
    #     print(now)
    #     now = now[:-3]
    #     now = now[:10] + ' ' + now[11:]
    #     return now
    def getLocalTime(self):
        #now = time.strftime('%Y-%m-%d %H:%H:%S',time.localtime(time.time()))
        now = datetime.datetime.now()
        now = str(now)[:-3]
        return now

if __name__ == "__main__":
    junction = Junction()
    junction.getTime()




