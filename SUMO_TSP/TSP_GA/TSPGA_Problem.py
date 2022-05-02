import numpy as np
import geatpy as ea
import traci

from sumolib import checkBinary  # noqa


class MyProblem(ea.Problem):
    def __init__(self):
        name = 'MyProblem'  # 初始化name（函数名称，可以随意设置）
        M = 1  # 初始化M（目标维数）
        maxormins = [1]  # 初始化maxormins（目标最小最大化标记列表，1：最小化该目标；-1：最大化该目标）
        Dim = 4  # 初始化Dim（决策变量维数）
        varTypes = [1] * Dim  # 初始化varTypes（决策变量的类型，元素为0表示对应的变量是连续的；1表示是离散的）
        lb = [10, 10, 10, 10]  # 决策变量下边界
        ub = [30, 40, 30, 30]  # 决策变量上边界
        lbin = [1] * Dim  # 决策变量下边界（0表示不包含该变量的下边界，1表示包含）
        ubin = [1] * Dim  # 决策变量上边界（0表示不包含该变量的上边界，1表示包含）
        # 调用父类构造方法完成实例化
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)

    def evalVars(self, Vars):  # Objective function
        # print(totperdelay(Vars))
        # res = totperdelay(Vars)
        # totdelay = res[0]
        # veh1 = res[1]
        # veh2 = res[2]
        # veh3 = res[3]
        # veh4 = res[4]
        # g1 = Vars[:, [0]]
        # g2 = Vars[:, [1]]
        # g3 = Vars[:, [2]]
        # g4 = Vars[:, [3]]
        # print(veh1, veh2, veh3, veh4)
        # print(veh1, veh2, veh3, veh4)

        f = totperdelay(Vars)
        # CV = np.hstack([veh2 * 2 - g2,
        #                 veh3 * 2 - g3,
        #                 veh4 * 2 - g4])

        return f
        # print(f, Vars)


# calculate the total person delay
def totperdelay(Vars):
    lstdelay = []
    acar = 1.0
    abus = 0.8
    vehlst = traci.vehicle.getIDList()  # get all the vehicle ID that currently running within the scenario

    # assign the vector values to the corresponding green time variables
    for j in range(Vars.shape[0]):  # the range function checks the variable passed into it and returns a series of
        # numbers starting from 0 and stopping right before the specified number.
        g1 = Vars[j, 0]
        g2 = Vars[j, 1]
        g3 = Vars[j, 2]
        g4 = Vars[j, 3]
        cycle = g1 + g2 + g3 + g4 + 20
        # green starts time
        gs1 = 0
        gs2 = g1 + 5
        gs3 = g1 + g2 + 10
        gs4 = g1 + g2 + g3 + 15
        # green ends time
        ge1 = g1
        ge2 = g1 + g2 + 5
        ge3 = g1 + g2 + g3 + 10
        ge4 = g1 + g2 + g3 + g4 + 15
        totper = 0
        veh = 0
        veh1 = 0
        veh2 = 0
        veh3 = 0
        veh4 = 0
        vq1 = 0
        vq2 = 0
        vq3 = 0
        vq4 = 0
        freespd = 13.89

        for i in vehlst:
            vehtls = traci.vehicle.getNextTLS(i)
            vehsp = traci.vehicle.getSpeed(i)  # get the speed
            vehtp = traci.vehicle.getTypeID(i)  # get the type
            vehrou = traci.vehicle.getRoute(i)  # get the route
            stptime = traci.vehicle.getAccumulatedWaitingTime(i)

            if vehtls:  # vehicles not crossing the intersection
                veh2tls = vehtls[0]  # get the upcoming state related to the traffic lights
                dist2stp = veh2tls[2]  # get the distance to the stop line

                # calculate the delay of stopped vehicle
                if vehsp < 1:  # stopped vehicles
                    time2stp = dist2stp * 2.5 / 7.75

                    # main street left turn, phase "g1"
                    if vehrou == ('E0', '-E3') or vehrou == ('E1', '-E2'):
                        if time2stp <= g1:  # can leave at current phase
                            delay = stptime + time2stp - dist2stp / freespd
                        else:  # cannot leave at current phase
                            delay = stptime + cycle + time2stp - dist2stp / freespd
                            vq1 += 1

                    # main street straight, phase "g2"
                    elif vehrou == ('E0', '-E1') or vehrou == ('E1', '-E0'):
                        if time2stp <= g2:  # can leave at current phase
                            delay = stptime + gs2 + time2stp - dist2stp / freespd
                        else:  # cannot leave at current phase
                            delay = stptime + cycle + gs2 + time2stp - dist2stp / freespd
                            vq2 += 1

                    # south, phase "g3"
                    elif vehrou == ('E2', '-E3') or vehrou == ('E2', '-E0'):
                        if time2stp <= g3:  # can leave at current phase
                            delay = stptime + gs3 + time2stp - dist2stp / freespd
                        else:  # cannot leave at current phase
                            delay = stptime + cycle + gs3 + time2stp - dist2stp / freespd
                            vq3 += 1

                    # north, phase "g4"
                    elif vehrou == ('E3', '-E2') or vehrou == ('E3', '-E1'):
                        if time2stp <= g4:  # can leave at current phase
                            delay = stptime + gs4 + time2stp - dist2stp / freespd
                        else:  # cannot leave at current phase
                            delay = stptime + cycle + gs4 + time2stp - dist2stp / freespd
                            vq4 += 1

                    else:
                        pass

                # calculate the delay of running vehicle
                else:  # running vehicles
                    time2stp = dist2stp / vehsp

                    # main street left turn, phase "g1"
                    if vehrou == ('E0', '-E3') or vehrou == ('E1', '-E2'):
                        if ge1 >= time2stp >= gs1:  # arrives at green time of phase 1
                            delay = 0
                        else:  # arrives at other phase
                            delay = cycle - time2stp
                            # veh1 += 1

                    # main street straight, phase "g2"
                    elif vehrou == ('E0', '-E1') or vehrou == ('E1', '-E0'):
                        if ge2 >= time2stp >= gs2:  # arrives at green time of phase 2
                            delay = 0
                            veh2 += 1
                        elif time2stp < gs2:  # arrives at phase 1
                            delay = gs2 - time2stp  # not considering the acceleration time and queuing distance
                            veh2 += 1  # used for constrains to clear the vehicles arrive before green time in the cycle
                        else:  # arrives at phase 3 and 4
                            delay = cycle + gs2 - time2stp
                            # veh2 += 1

                    # south, phase "g3"
                    elif vehrou == ('E2', '-E3') or vehrou == ('E2', '-E0'):
                        if ge3 >= time2stp >= gs3:  # arrives at green time of phase 3
                            delay = 0
                            veh3 += 1
                        elif time2stp < gs3:  # arrives at phase 1 and 2
                            delay = gs3 - time2stp
                            veh3 += 1
                        else:  # arrives at phase 4
                            delay = cycle + gs3 - time2stp
                            # veh3 += 1

                    # north, phase "g4"
                    elif vehrou == ('E3', '-E2') or vehrou == ('E3', '-E1'):
                        if ge4 >= time2stp >= gs4:  # arrives at green time of phase 4
                            delay = 0
                            veh4 += 1
                        elif time2stp < gs4:  # arrives other phase
                            delay = gs4 - time2stp
                            veh4 += 1

                    else:
                        pass

                # calculate the total person delay
                if vehtp == 'car' or vehtp == 'cav':
                    perdelay = delay * 2
                else:
                    perdelay = delay * 30
                totper += perdelay
            else:
                pass
        # print(veh1, veh2, veh3, veh4)
        # print(totper)
        lstdelay.append(totper)  # add total person delay to list
        arrdelay = np.array(lstdelay)  # list to array
        arrdelay = arrdelay.reshape(-1, 1)  # reshape (20,) to (20, 1) for geatpy requirements
    return arrdelay
