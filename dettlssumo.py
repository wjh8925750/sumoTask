
import traci

import traci.constants as tc
class SUMO:
    def __init__(self, sumoconfig):
        self.inductionloopid = '##'
        traci.start(['sumo-gui', '--start', '-c', sumoconfig])
        #self.start = time.per_counter()

    def subInductionloop(self, inductionloopid, radius):
        """
        订阅感应线圈数据（以检测器inductionloopid为中心，半径radius）
        """
        self.inductionloopid = inductionloopid
        traci.inductionloop.subscribeContext(
            inductionloopid, tc.CMD_GET_INDUCTIONLOOP_VARIABLE, radius)

    def simulation(self):
        while True:
            traci.simulationStep()
            if not self.inductionloopid == '##':
                print(traci.inductionloop.getContextSubscriptionResults(self.inductionloopid))
