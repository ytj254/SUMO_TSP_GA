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
        lb = [6, 12, 6, 12]  # 决策变量下边界
        ub = [30, 35, 20, 35]  # 决策变量上边界
        lbin = [1] * Dim  # 决策变量下边界（0表示不包含该变量的下边界，1表示包含）
        ubin = [1] * Dim  # 决策变量上边界（0表示不包含该变量的上边界，1表示包含）
        # 调用父类构造方法完成实例化
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)

    def evalVars(self, Vars):  # Objective function

        f = totperdelay(Vars)

        return f
        # print(f, Vars)


# calculate the total person delay
def totperdelay(Vars):
    lstdelay = []
    cavlst = []
    vehlst = traci.vehicle.getIDList()  # get all the vehicle ID that currently running within the scenario
    for k in vehlst:
        vehtype = traci.vehicle.getTypeID(k)
        if 'cav' in vehtype or 'bus' in vehtype:
            cavlst.append(k)
    # print(cavlst)
    ns_freespd = 20.12
    ew_freespd = 15.65
    caroccupancy = 1.5
    busoccupancy = 30
    lowspd = 5

    # assign the vector values to the corresponding green time variables
    for j in range(Vars.shape[0]):  # the range function checks the variable passed into it and returns a series of
        # numbers starting from 0 and stopping right before the specified number.
        g1 = Vars[j, 0]
        g2 = Vars[j, 1]
        g3 = Vars[j, 2]
        g4 = Vars[j, 3]
        cycle = g1 + g2 + g3 + g4 + 20
        # cycle = 120
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

        totstopper = 0
        totrunningper = 0
        g1nequeuedelay = [0]
        g2nsqueuedelay = [0]
        g3esqueuedelay = [0]
        g4ewqueuedelay = [0]
        g1swqueuedelay = [0]
        g2snqueuedelay = [0]
        g3wnqueuedelay = [0]
        g4wequeuedelay = [0]

        for i in cavlst:
            vehtls = traci.vehicle.getNextTLS(i)

            if vehtls:  # vehicles not crossing the intersection
                vehsp = traci.vehicle.getSpeed(i)  # get the speed

                # calculate the delay of stopped vehicle (Zeng et al., 2015)
                if vehsp < lowspd:  # stopped vehicles
                    veh2tls = vehtls[0]  # get the upcoming state related to the traffic lights
                    dist2stp = veh2tls[2]  # get the distance to the stop line
                    vehclass = traci.vehicle.getVehicleClass(i)  # get the type
                    stptime = traci.vehicle.getAccumulatedWaitingTime(i)
                    vehrou = i.split('.')[0]  # get characters in the vehicle id 'i' before the symbol '.'

                    # distance-to-stop * saturation flow rate / average distance between stopped vehicles
                    time2stp = int(dist2stp / 7.5) * 2.5  # in fact, saturation flow rates differ for different turns

                    # north & south left turn, phase "g1"
                    if 'NE' in vehrou:
                        if time2stp <= ge1 - gs1:  # can leave at current phase
                            delay = max(0, stptime + gs1 + time2stp - dist2stp / ns_freespd)
                        else:  # cannot leave at current phase
                            delay = stptime + gs1 + cycle + time2stp - g1 - dist2stp / ns_freespd
                        g1nequeuedelay.append(time2stp)

                    elif 'SW' in vehrou:
                        if time2stp <= ge1 - gs1:  # can leave at current phase
                            delay = max(0, stptime + gs1 + time2stp - dist2stp / ns_freespd)
                        else:  # cannot leave at current phase
                            delay = stptime + gs1 + cycle + time2stp - g1 - dist2stp / ns_freespd
                        g1swqueuedelay.append(time2stp)

                    # north & south through, phase "g2"
                    elif 'NS' in vehrou:
                        if time2stp <= ge2 - gs2:  # can leave at current phase
                            delay = max(0, stptime + gs2 + time2stp - dist2stp / ns_freespd)
                        else:  # cannot leave at current phase
                            delay = stptime + gs2 + cycle + time2stp - g2 - dist2stp / ns_freespd
                        g2nsqueuedelay.append(time2stp)
                    elif 'SN' in vehrou:
                        if time2stp <= ge2 - gs2:  # can leave at current phase
                            delay = max(0, stptime + gs2 + time2stp - dist2stp / ns_freespd)
                        else:  # cannot leave at current phase
                            delay = stptime + gs2 + cycle + time2stp - g2 - dist2stp / ns_freespd
                        g2snqueuedelay.append(time2stp)

                    # east & west left turn, phase "g3"
                    elif 'ES' in vehrou:
                        if time2stp <= ge3 - gs3:  # can leave at current phase
                            delay = max(0, stptime + gs3 + time2stp - dist2stp / ew_freespd)
                        else:  # cannot leave at current phase
                            delay = stptime + gs3 + cycle + time2stp - g3 - dist2stp / ew_freespd
                        g3esqueuedelay.append(time2stp)
                    elif 'WN' in vehrou:
                        if time2stp <= ge3 - gs3:  # can leave at current phase
                            delay = max(0, stptime + gs3 + time2stp - dist2stp / ew_freespd)
                        else:  # cannot leave at current phase
                            delay = stptime + gs3 + cycle + time2stp - g3 - dist2stp / ew_freespd
                        g3wnqueuedelay.append(time2stp)

                    # east & west through, phase "g4"
                    elif 'EW' in vehrou:
                        if time2stp <= ge4 - gs4:  # can leave at current phase
                            delay = max(0, stptime + gs4 + time2stp - dist2stp / ew_freespd)
                        else:  # cannot leave at current phase
                            delay = stptime + gs4 + cycle + time2stp - g4 - dist2stp / ew_freespd
                        g4ewqueuedelay.append(time2stp)
                    elif 'WE' in vehrou:
                        if time2stp <= ge4 - gs4:  # can leave at current phase
                            delay = max(0, stptime + gs4 + time2stp - dist2stp / ew_freespd)
                        else:  # cannot leave at current phase
                            delay = stptime + gs4 + cycle + time2stp - g4 - dist2stp / ew_freespd
                        g4wequeuedelay.append(time2stp)

                    else:
                        delay = stptime  # assigning delay to right turn vehicles

                    if vehclass == 'passenger':
                        perdelay = delay * caroccupancy
                        # print('carstop', perdelay)
                    else:
                        perdelay = delay * busoccupancy
                        # print('busstop', perdelay)
                    totstopper += perdelay
                    # print('totstop', totstopper)

        g1nemaxqueuedelay = max(g1nequeuedelay)
        g2nsmaxqueuedelay = max(g2nsqueuedelay)
        g3esmaxqueuedelay = max(g3esqueuedelay)
        g4ewmaxqueuedelay = max(g4ewqueuedelay)
        g1swmaxqueuedelay = max(g1swqueuedelay)
        g2snmaxqueuedelay = max(g2snqueuedelay)
        g3wnmaxqueuedelay = max(g3wnqueuedelay)
        g4wemaxqueuedelay = max(g4wequeuedelay)
        # print(g1maxqueuedelay)
        # print(g2maxqueuedelay)
        # print(g3maxqueuedelay)
        # print(g4maxqueuedelay)

        for i in cavlst:
            vehtls = traci.vehicle.getNextTLS(i)

            if vehtls:  # vehicles not crossing the intersection
                vehsp = traci.vehicle.getSpeed(i)  # get the speed

                # calculate the delay of stopped vehicle (Zeng et al., 2015)
                if vehsp >= lowspd:  # stopped vehicles
                    veh2tls = vehtls[0]  # get the upcoming state related to the traffic lights
                    dist2stp = veh2tls[2]  # get the distance to the stop line
                    vehclass = traci.vehicle.getVehicleClass(i)  # get the type
                    stptime = traci.vehicle.getAccumulatedWaitingTime(i)
                    vehrou = i.split('.')[0]  # get characters in the vehicle id 'i' before the symbol '.'

                # calculate the delay of running vehicle
                    time2stp = dist2stp / vehsp

                    # north & south left turn, phase "g1"
                    if 'NE' in vehrou:
                        if gs1 + g1nemaxqueuedelay < ge1:  # can clear the queue
                            if time2stp < gs1 + g1nemaxqueuedelay:
                                delay = gs1 + g1nemaxqueuedelay - time2stp
                            elif gs1 + g1nemaxqueuedelay <= time2stp <= ge1:  # arrives at green time of phase 1
                                delay = 0
                            else:  # arrives at other phase
                                delay = cycle + gs1 - time2stp
                            # print(i, delay, g1maxqueuedelay, time2stp, ge1, sep='||')
                        else:  # can not clear the queue
                            delay = cycle + gs1 - time2stp
                    elif 'SW' in vehrou:
                        if gs1 + g1swmaxqueuedelay < ge1:  # can clear the queue
                            if time2stp < gs1 + g1swmaxqueuedelay:
                                delay = gs1 + g1swmaxqueuedelay - time2stp
                            elif gs1 + g1swmaxqueuedelay <= time2stp <= ge1:  # arrives at green time of phase 1
                                delay = 0
                            else:  # arrives at other phase
                                delay = cycle + gs1 - time2stp
                            # print(i, delay, g1maxqueuedelay, time2stp, ge1, sep='||')
                        else:  # can not clear the queue
                            delay = cycle + gs1 - time2stp

                    # north & south through, phase "g2"
                    elif 'NS' in vehrou:
                        if gs2 + g2nsmaxqueuedelay < ge2:  # can clear the queue
                            if time2stp < gs2 + g2nsmaxqueuedelay:  # arrives before phase 2
                                delay = gs2 + g2nsmaxqueuedelay - time2stp
                            elif gs2 + g2nsmaxqueuedelay <= time2stp <= ge2:  # arrives at green time of phase 2
                                delay = 0
                            else:  # arrives after phase 2
                                delay = cycle + gs2 - time2stp
                        else:
                            delay = cycle + gs2 - time2stp
                    elif 'SN' in vehrou:
                        if gs2 + g2snmaxqueuedelay < ge2:  # can clear the queue
                            if time2stp < gs2 + g2snmaxqueuedelay:  # arrives before phase 2
                                delay = gs2 + g2snmaxqueuedelay - time2stp
                            elif gs2 + g2snmaxqueuedelay <= time2stp <= ge2:  # arrives at green time of phase 2
                                delay = 0
                            else:  # arrives after phase 2
                                delay = cycle + gs2 - time2stp
                        else:
                            delay = cycle + gs2 - time2stp

                    # east & west left turn, phase "g3"
                    elif 'ES' in vehrou:
                        if gs3 + g3esmaxqueuedelay < ge3:  # can clear the queue
                            if time2stp < gs3 + g3esmaxqueuedelay:  # arrives before phase 3
                                delay = gs3 + g3esmaxqueuedelay - time2stp
                            elif gs3 + g3esmaxqueuedelay <= time2stp <= ge3:  # arrives at green time of phase 3
                                delay = 0
                            else:  # arrives after phase 3
                                delay = cycle + gs3 - time2stp
                        else:
                            delay = cycle + gs3 - time2stp
                    elif 'WN' in vehrou:
                        if gs3 + g3wnmaxqueuedelay < ge3:  # can clear the queue
                            if time2stp < gs3 + g3wnmaxqueuedelay:  # arrives before phase 3
                                delay = gs3 + g3wnmaxqueuedelay - time2stp
                            elif gs3 + g3wnmaxqueuedelay <= time2stp <= ge3:  # arrives at green time of phase 3
                                delay = 0
                            else:  # arrives after phase 3
                                delay = cycle + gs3 - time2stp
                        else:
                            delay = cycle + gs3 - time2stp

                    # east & west through, phase "g4"
                    elif 'EW' in vehrou:
                        if gs4 + g4ewmaxqueuedelay < ge4:  # can clear the queue
                            if time2stp < gs4 + g4ewmaxqueuedelay:  # arrives before phase 4
                                delay = gs4 + g4ewmaxqueuedelay - time2stp
                            elif gs4 + g4ewmaxqueuedelay <= time2stp <= ge4:  # arrives at green time of phase 4
                                delay = 0
                            else:  # arrives after phase 4
                                delay = cycle + gs4 - time2stp
                        else:
                            delay = cycle + gs4 - time2stp
                    elif 'WE' in vehrou:
                        if gs4 + g4wemaxqueuedelay < ge4:  # can clear the queue
                            if time2stp < gs4 + g4wemaxqueuedelay:  # arrives before phase 4
                                delay = gs4 + g4wemaxqueuedelay - time2stp
                            elif gs4 + g4wemaxqueuedelay <= time2stp <= ge4:  # arrives at green time of phase 4
                                delay = 0
                            else:  # arrives after phase 4
                                delay = cycle + gs4 - time2stp
                        else:
                            delay = cycle + gs4 - time2stp

                    else:
                        delay = stptime  # assigning delay to right turn vehicles

                    if vehclass == 'passenger':
                        perdelay = delay * caroccupancy
                        # print('carrun', perdelay)
                    else:
                        perdelay = delay * busoccupancy
                        # print('busrun', perdelay)
                    totrunningper += perdelay
                    # print('totrun', totrunningper)

        totper = totstopper + totrunningper

        # print(veh1, veh2, veh3, veh4)
        # print(totper)
        lstdelay.append(totper)  # add total person delay to list
        arrdelay = np.array(lstdelay)  # list to array
        arrdelay = arrdelay.reshape(-1, 1)  # reshape (20,) to (20, 1) for geatpy requirements
        # print(arrdelay)
    return arrdelay
