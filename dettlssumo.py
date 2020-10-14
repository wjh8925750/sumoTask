import time

import traci
import traci.constants as tc
import config
import queuedata


class SUMO:
    junctions = dict()    #这里存储的是所有关注路口的junction对象
    def __init__(self, sumoconfig):
        self.frame = 0;             #初始步长为0
        self.inductionloopid = '##'
        traci.start(['sumo-gui', '--start', '-c', sumoconfig])
        self.start = time.perf_counter()
        print("        3.2、启动sumo-gui,初始启动时间：", self.start)

    def subInductionloop(self, inductionloopid, radius):
        """
        订阅感应线圈数据（以检测器inductionloopid为中心，半径radius）
        """
        self.inductionloopid = inductionloopid
        traci.inductionloop.subscribeContext(
            inductionloopid, tc.CMD_GET_INDUCTIONLOOP_VARIABLE, radius)
        traci.simulation.subscribe((tc.VAR_DEPARTED_VEHICLES_IDS,tc.VAR_LOADED_VEHICLES_IDS))
        # traci.inductionloop.subscribe(inductionloopid,tc.CMD_GET_INDUCTIONLOOP_VARIABLE,radius)

    def simulation(self):
        while True:
            # for vec_id in traci.vehicle.getIDList():
            #
            #     #订阅车辆信息：坐标，角度，车辆类型，颜色，速度
            #     traci.vehicle.subscribe(str(vec_id),
            #                             (tc.VAR_POSITION, tc.VAR_ANGLE, tc.VAR_TYPE, tc.VAR_COLOR, tc.VAR_SPEED))

            traci.simulationStep()                 #开始切帧
            # loopdata = traci.inductionloop.getInductionLoopStat()
            # lanedata = traci.lane.getLaneStat()
            # cross_data = [loopdata, lanedata]
            # print(cross_data)

            self.frame+=1                             #步长+1
            if not self.inductionloopid == '##':
                temp = traci.inductionloop.getContextSubscriptionResults(self.inductionloopid)
                print("当来车时：", temp)
                queuedata.det_queue.put(temp)
                #print(temp)             ##此处打印检测器是否检测到车辆的信息

                # for vec_id in traci.vehicle.getIDList():
                #     dic = traci.vehicle.getSubscriptionResults(vec_id)
                #     print(dic)           ##这里打印的是之前车辆订阅的信息：坐标，角度，车辆类型，颜色，速度
                #     if dic:
                #         #print(dic[66])
                #         x,y = dic[66]
                #         lon, lat = traci.simulation.convertGeo(x,y)
                        #print(lon,lat)


            q_size = queuedata.ryg_queue.qsize()
            while q_size > 0:
                print("        5.4、当前ryg_queue.qsize：", q_size)
                tlsID, newryg = queuedata.ryg_queue.get()
                traci.trafficlight.setRedYellowGreenState(tlsID, newryg)
                traci.trafficlight.setPhaseDuration(tlsID,999)
                print("        5.5、向sumo仿真系统中设置灯色信息及其持续时间：", (tlsID, newryg))
                q_size -= 1
            logitTime = self.frame * config.steplength
            realTime = time.perf_counter() - self.start
            diff = logitTime - realTime
            if(diff > 0):
                time.sleep(diff)






