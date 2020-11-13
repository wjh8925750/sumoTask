import time


from queue import Queue
import traci
import traci.constants as tc
import config
import queuedata
import copy



class SUMO:
    junctions = dict()  # 这里存储的是所有关注路口的junction对象
    def __init__(self, sumoconfig):
        self.frameUpadte = 0;  # 循环更新步长
        self.frame = 0;  # 步长
        self.inductionloopid = '##'
        #traci.start(['sumo-gui', '--start', '-c', sumoconfig])
        traci.start(cmd=['sumo-gui', '--start', '-c', sumoconfig,
                         "--num-clients", "2"], port=8813, label="sim1")
        traci.setOrder(1)
        self.start = time.perf_counter()
        print("        3.2、启动sumo-gui,初始启动时间：", self.start)

    def subInductionloop(self, inductionloopid, laneid, radius):
        """
        订阅感应线圈数据（以检测器inductionloopid为中心，半径radius）
        """
        self.inductionloopid = inductionloopid
        self.laneid = laneid
        traci.lane.subscribeContext(
            laneid, tc.CMD_GET_INDUCTIONLOOP_VARIABLE, radius)


    def simulation(self):
        lastNumDict = {}  # 记录上一帧各个检测器的状态
        passedNumDict = {}  # 记录各个检测器累积的车辆数
        flowlist = []

        for k, v in config.junction_detectors.items():
            for det in v:
                passedNumDict[det] = 0

        while True:
            traci.simulationStep()  # 开始切帧
            self.frame += 1  # 步长+1
            self.frameUpadte += 1

            if not self.inductionloopid == '##':
                traciResult = traci.lane.getContextSubscriptionResults(self.laneid)
                #self.getVechileNum(traciResult, lastNumDict,passedNumDict)
                if self.frame > 1:
                    for k, v in traciResult.items():
                        currStatus = v[16]
                        preStatus = lastNumDict[k][16]
                        if currStatus - preStatus == 1:
                            passedNumDict[k] += 1

                if self.frame % int(60 / config.steplength) == 0:  ##时长达到1分钟，将数据推出去
                    flowlist.append(passedNumDict)
                    print("flowlist.size = ", len(flowlist) , flowlist)
                    if len(flowlist) == 3:
                        flowlist_push = copy.deepcopy(flowlist)
                        queuedata.flow_queue.put(flowlist_push)  ##将1分钟流量数据，推送到flow队列中，用别的线程进行处理
                        del flowlist[0]
                    for k, v in config.junction_detectors.items():
                        for det in v:
                            passedNumDict[det] = 0
                lastNumDict = traciResult



            logitTime = self.frame * config.steplength
            realTime = time.perf_counter() - self.start
            diff = logitTime - realTime
            if (diff > 0):
                time.sleep(diff)




    def getVechileNum(self, _traciResult, _lastNumDict, _passedNumDict):

        if self.frame > 1:
            for k, v in _traciResult.items():
                currStatus = v[16]
                preStatus = _lastNumDict[k][16]
                if currStatus - preStatus == 1:
                    _passedNumDict[k] += 1

        if self.frame % int(20 / config.steplength) == 0:  ##时长达到1分钟，将数据推出去
            print("-------------------------------", _traciResult)
            passedNumDictDup = copy.deepcopy(_passedNumDict)
            queuedata.flow_queue.put(passedNumDictDup)  ##将1分钟流量数据，推送到flow队列中，用别的线程进行处理
            for k, v in config.junction_detectors.items():
                for det in v:
                    _passedNumDict[det] = 0
        _lastNumDict = _traciResult






