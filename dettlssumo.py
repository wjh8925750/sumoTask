import time

import traci
import traci.constants as tc
import config
import queuedata


class SUMO:
    def __init__(self, sumoconfig):
        self.frame = 0;             #初始步长为0
        self.inductionloopid = '##'
        traci.start(['sumo-gui', '--start', '-c', sumoconfig])
        self.start = time.perf_counter()
        print("初始时间 = " , self.start)

    def subInductionloop(self, inductionloopid, radius):
        """
        订阅感应线圈数据（以检测器inductionloopid为中心，半径radius）
        """
        self.inductionloopid = inductionloopid
        # traci.inductionloop.subscribeContext(
        #     inductionloopid, tc.CMD_GET_INDUCTIONLOOP_VARIABLE, radius)
        traci.simulation.subscribe((tc.VAR_DEPARTED_VEHICLES_IDS,tc.VAR_LOADED_VEHICLES_IDS))
        # traci.inductionloop.subscribe(inductionloopid,tc.CMD_GET_INDUCTIONLOOP_VARIABLE,radius)

    def simulation(self):

        while True:
            for vec_id in traci.vehicle.getIDList():
                traci.vehicle.subscribe(str(vec_id),
                                        (tc.VAR_POSITION, tc.VAR_ANGLE, tc.VAR_TYPE, tc.VAR_COLOR, tc.VAR_SPEED))
            traci.simulationStep()                 #开始切帧

            self.frame +=1                             #步长+1
            if not self.inductionloopid == '##':
                temp = traci.inductionloop.getContextSubscriptionResults(self.inductionloopid)
                #print(temp)
                for vec_id in traci.vehicle.getIDList():
                    dic = traci.vehicle.getSubscriptionResults(vec_id)
                    print(dic)
                    if dic:
                        #print(dic[66])
                        x,y = dic[66]
                        lon, lat = traci.simulation.convertGeo(x,y)
                        #print(lon,lat)
                queuedata.det_queue.put(temp)
            time.sleep(0.1)
            logitTime = self.frame * config.steplength
            realTime = time.perf_counter() - self.start
            diff = logitTime - realTime
            if(diff > 0):
                time.sleep(diff)


