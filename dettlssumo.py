import time
from queue import Queue

import traci
import traci.constants as tc
import config
import queuedata
import copy
import os


class SUMO:
    junctions = dict()  # 这里存储的是所有关注路口的junction对象
    cross_dict = {}

    def __init__(self, sumoconfig):
        self.frameUpadte = 0;  # 循环更新步长
        self.frame = 0;  # 步长
        self.inductionloopid = '##'
        #traci.start(['sumo-gui', '--start', '-c', sumoconfig])
        traci.init(8813)
        traci.setOrder(2)
        self.start = time.perf_counter()
        print("        3.2、启动sumo-gui,初始启动时间：", self.start)

    # def subInductionloop(self, inductionloopid, lane, radius):
    #     """
    #     订阅感应线圈数据（以检测器inductionloopid为中心，半径radius）
    #     """
    #     self.inductionloopid = inductionloopid
    #     self.lane = lane
    #     # traci.inductionloop.subscribeContext(
    #     #     inductionloopid, tc.CMD_GET_INDUCTIONLOOP_VARIABLE, radius)
    #     # traci.lane.subscribeContext(
    #     #     lane, tc.CMD_GET_LANE_VARIABLE, radius)
    #
    #     # traci.simulation.subscribe((tc.VAR_DEPARTED_VEHICLES_IDS,tc.VAR_LOADED_VEHICLES_IDS))
    def subInductionloop(self, inductionloopid, laneid, radius):
        """
        订阅感应线圈数据（以检测器inductionloopid为中心，半径radius）
        """
        self.inductionloopid = inductionloopid
        self.laneid = laneid
        self.radius = radius
        traci.lane.subscribeContext(
            laneid, tc.CMD_GET_INDUCTIONLOOP_VARIABLE, radius)

    # def simulation(self):
    #
    #     laneDataDict = {}  # {"lane" : [sumSpeed, maxQueue, sumOccupancy], ...., { }}
    #     laneDatas = []  # 记录五条数据
    #     lastNumDict = {}  # 记录上一帧各个检测器的状态
    #     passedNumDict = {}  # 记录各个检测器累积的车辆数
    #     flowlist = []
    #     count_meanSpeed = 0
    #
    #
    #     #=====================================
    #     # for v in config.junction_detectors.values():
    #     #     for det in v:
    #     #         traci.inductionloop.subscribeContext(
    #     #             det,
    #     #             tc.CMD_GET_LANE_VARIABLE,
    #     #             0,
    #     #             [tc.LAST_STEP_MEAN_SPEED, tc.LAST_STEP_VEHICLE_HALTING_NUMBER, tc.LAST_STEP_OCCUPANCY])
    #             #17                               20                                 19
    #     #=====================================
    #
    #
    #     # traci.lane.subscribeContext(
    #     #     self.laneid, tc.CMD_GET_INDUCTIONLOOP_VARIABLE, self.radius)
    #     while True:
    #
    #         traci.simulationStep()  # 开始切帧
    #         self.frame += 1  # 步长+1
    #         self.frameUpadte += 1
    #
    #         if not self.inductionloopid == '##':
    #             traciResult = traci.lane.getContextSubscriptionResults(self.laneid)
    #             # self.getVechileNum(traciResult, lastNumDict,passedNumDict)
    #             if self.frame > 1:
    #                 for k, v in traciResult.items():
    #                     currStatus = v[16]
    #                     preStatus = lastNumDict[k][16]
    #                     if currStatus - preStatus == 1:
    #                         passedNumDict[k] += 1
    #
    #             if self.frame % int(60 / config.steplength) == 0:  ##时长达到1分钟，将数据推出去
    #                 flowlist.append(passedNumDict)
    #                 print("flowlist.size = ", len(flowlist), flowlist)
    #                 if len(flowlist) == 3:
    #                     flowlist_push = copy.deepcopy(flowlist)
    #                     queuedata.flow_queue.put(flowlist_push)  ##将1分钟流量数据，推送到flow队列中，用别的线程进行处理
    #                     del flowlist[0]
    #                 for k, v in config.junction_detectors.items():
    #                     for det in v:
    #                         passedNumDict[det] = 0
    #             lastNumDict = traciResult
    #
    #
    #         # if self.frameUpadte % 5 == 0 or self.frameUpadte == 1:  # 每5帧计算一次
    #         #     self.getLaneDataDict(laneDataDict, count_meanSpeed, laneDatas)
    #         logitTime = self.frame * config.steplength
    #         realTime = time.perf_counter() - self.start
    #         diff = logitTime - realTime
    #         if (diff > 0):
    #             time.sleep(diff)

    def simulation(self):
        laneDataDict = {}  # {"lane" : [sumSpeed, maxQueue, sumOccupancy], ...., { }}
        laneDatas = []  # 记录五条数据
        lastNumDict = {}  # 记录上一帧各个检测器的状态
        passedNumDict = {}  # 记录各个检测器累积的车辆数
        flowlist = []
        count_meanSpeed = 0

        for k, v in config.junction_detectors.items():
            for det in v:
                passedNumDict[det] = 0
        for v in config.junction_detectors.values():
            for det in v:
                traci.inductionloop.subscribeContext(
                    det,
                    tc.CMD_GET_LANE_VARIABLE,
                    0,
                    [tc.LAST_STEP_MEAN_SPEED, tc.LAST_STEP_VEHICLE_HALTING_NUMBER, tc.LAST_STEP_OCCUPANCY])
                    #17                               20                                 19

        # traci.inductionloop.subscribeContext(
        #             #'e1Detector_499430068_1_17',
        #             'e1Detector_10689621#1_3_203',
        #             tc.CMD_GET_LANE_VARIABLE,
        #             0,
        #             [tc.LAST_STEP_MEAN_SPEED, tc.LAST_STEP_VEHICLE_HALTING_NUMBER, tc.LAST_STEP_OCCUPANCY])
        while True:
            traci.simulationStep()  # 开始切帧
            self.frame += 1  # 步长+1
            self.frameUpadte += 1

            if not self.inductionloopid == '##':
                traciResult = traci.lane.getContextSubscriptionResults(self.laneid)
                # self.getVechileNum(traciResult, lastNumDict,passedNumDict)
                if self.frame > 1:
                    for k, v in traciResult.items():
                        currStatus = v[16]
                        preStatus = lastNumDict[k][16]
                        if currStatus - preStatus == 1:
                            passedNumDict[k] += 1

                if self.frame % int(60 / config.steplength) == 0:  ##时长达到1分钟，将数据推出去
                    flowlist.append(passedNumDict)
                    #print("flowlist.size = ", len(flowlist), flowlist)
                    if len(flowlist) == 5:
                        flowlist_push = copy.deepcopy(flowlist)
                        queuedata.flow_queue.put(flowlist_push)  ##将1分钟流量数据，推送到flow队列中，用别的线程进行处理
                        del flowlist[0]
                    for k, v in config.junction_detectors.items():
                        for det in v:
                            passedNumDict[det] = 0
                lastNumDict = traciResult

            # dict_sub = traci.inductionloop.getContextSubscriptionResults('e1Detector_10689621#1_3_203')
            # print(dict_sub)
            if self.frameUpadte % 5 == 0 or self.frameUpadte == 1:  # 每5帧计算一次
                self.getLaneDataDict(laneDataDict, count_meanSpeed, laneDatas)

            logitTime = self.frame * config.steplength
            realTime = time.perf_counter() - self.start
            diff = logitTime - realTime
            if (diff > 0):
                time.sleep(diff)

    def getLaneDataDict(self, _laneDataDict, _count_Meanspeed, _laneDatas):
        for v in config.junction_detectors.values():
            for det in v:
                dict_sub = traci.inductionloop.getContextSubscriptionResults(det)
                if dict_sub != None:
                    if self.frameUpadte == 1:  # frame == 1时，初始化laneDataDict
                        dataList = []  # 初始化三个变量
                        for k, v in dict_sub.items():
                            for d in v:
                                dataList.append(v[d])
                            _laneDataDict[k] = dataList
                    else:
                        for k, v in dict_sub.items():
                            _laneDataDict[k][0] += v[17]
                            if v[20] > _laneDataDict[k][2]:
                                _laneDataDict[k][1] = v[20]
                            _laneDataDict[k][2] += v[19]
                            _count_Meanspeed += 1

        # 每分钟向laneDatas中存储一个当前dict，存储5个
        if self.frame % int(60 / config.steplength) == 0:  ##每分钟推一次前5分钟的数据
            lanDatasDeepCopy = copy.deepcopy(_laneDataDict)
            #print(lanDatasDeepCopy)
            _laneDatas.append(lanDatasDeepCopy)
            #print("laneDatas.qsize() = ", len(_laneDatas))
            if (len(_laneDatas) == 5):
                laneDatas_push = copy.deepcopy(_laneDatas)  # 将列表中元素进行深复制，并放入一个列表中
                queuedata.laneData_queue.put(laneDatas_push)
                del _laneDatas[0]         ##删除首元素
                ##然后计算当前队列中五分钟数据的均值，并推出去
            self.frameUpadte = 0
