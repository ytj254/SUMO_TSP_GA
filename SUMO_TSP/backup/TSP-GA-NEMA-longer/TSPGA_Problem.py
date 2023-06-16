import numpy as np
import geatpy as ea
import traci

from sumolib import checkBinary  # noqa


class MyProblem(ea.Problem):
    def __init__(self):
        name = 'MyProblem'  # 初始化name（函数名称，可以随意设置）
        M = 1  # 初始化M（目标维数）
        maxormins = [1]  # 初始化maxormins（目标最小最大化标记列表，1：最小化该目标；-1：最大化该目标）
        Dim = 7  # 初始化Dim（决策变量维数）
        varTypes = [1] * Dim  # 初始化varTypes（决策变量的类型，元素为0表示对应的变量是连续的；1表示是离散的）
        lb = [54, 27, 10, 10, 10, 10, 0]  # 决策变量下边界
        ub = [155, 70, 25, 45, 25, 45, 15]  # 决策变量上边界
        lbin = [1] * Dim  # 决策变量下边界（0表示不包含该变量的下边界，1表示包含）
        ubin = [1] * Dim  # 决策变量上边界（0表示不包含该变量的上边界，1表示包含）
        # 调用父类构造方法完成实例化
        ea.Problem.__init__(self, name, M, maxormins, Dim, varTypes, lb, ub, lbin, ubin)

    def evalVars(self, Vars):  # Objective function
        f = totperdelay(Vars)
        x1 = Vars[:, [0]]
        x2 = Vars[:, [1]]
        x3 = Vars[:, [2]]
        x4 = Vars[:, [3]]
        x5 = Vars[:, [4]]
        x6 = Vars[:, [5]]
        CV = np.hstack(
            [x2 - x3 - 45,
             17 - x2 + x3,
             x2 - x5 - 45,
             17 - x2 + x5,
             x1 - x2 - x4 - 40,
             17 - x1 + x2 + x4,
             x1 - x2 - x6 - 40,
             17 - x1 + x2 + x6])
        return f, CV
        # print(f, Vars)


# calculate the total person delay
def totperdelay(Vars):
    lstdelay = []
    vehlst = traci.vehicle.getIDList()  # get all the vehicle ID that currently running within the scenario
    ns_freespd = 20.12
    ew_freespd = 15.65
    caroccupancy = 1.5
    busoccupancy = 30
    lowspd = 5

    # assign the vector values to the corresponding green time variables
    for j in range(Vars.shape[0]):  # the range function checks the variable passed into it and returns a series of
        # numbers starting from 0 and stopping right before the specified number.
        cycle = Vars[j, 0]
        mainphase = Vars[j, 1]
        p1 = Vars[j, 2]
        p3 = Vars[j, 3]
        p5 = Vars[j, 4]
        p7 = Vars[j, 5]
        sequence = '{:04b}'.format(Vars[j, 6])  # get the sequence and change to binary with four digits

        # based on phase sequence, assigning green start and end time for each turning movement
        if sequence[0] == '0':  # sequence is 3 4
            gssw = 0
            gsns = p1
            gesw = p1 - 5
            gens = mainphase - 5
        else:  # sequence is 2 1
            gssw = p1
            gsns = 0
            gesw = mainphase - 5
            gens = p1 - 5

        if sequence[1] == '0':  # sequence is 1 2
            gswn = mainphase
            gsew = mainphase + p3
            gewn = mainphase + p3 - 5
            geew = cycle - 5
        else:  # sequence is 4 3
            gswn = mainphase + p3
            gsew = mainphase
            gewn = cycle - 5
            geew = mainphase + p3 - 5

        if sequence[2] == '0':  # sequence is 7 8
            gsne = 0
            gssn = p5
            gene = p5 - 5
            gesn = mainphase - 5
        else:  # sequence is 6 5
            gsne = p5
            gssn = 0
            gene = mainphase - 5
            gesn = p5 - 5

        if sequence[3] == '0':  # sequence is 5 6
            gses = mainphase
            gswe = mainphase + p7
            gees = mainphase + p7 - 5
            gewe = cycle - 5
        else:  # sequence is 8 7
            gses = mainphase + p7
            gswe = mainphase
            gees = cycle - 5
            gewe = mainphase + p7 - 5

        totstopper = 0
        totrunningper = 0
        wnqueuedelay = [0]
        ewqueuedelay = [0]
        swqueuedelay = [0]
        nsqueuedelay = [0]
        esqueuedelay = [0]
        wequeuedelay = [0]
        nequeuedelay = [0]
        snqueuedelay = [0]

        for i in vehlst:
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
                    # phase 1
                    if 'WN' in vehrou:
                        if time2stp <= gewn - gswn:  # can leave during green time
                            delay = max(0, stptime + gswn + time2stp - dist2stp / ew_freespd)
                        else:  # cannot leave during green time
                            delay = stptime + gswn + cycle + time2stp - (gewn - gswn) - dist2stp / ew_freespd
                        wnqueuedelay.append(time2stp)
                    # phase 2
                    elif 'EW' in vehrou:
                        if time2stp <= geew - gsew:  # can leave during green time
                            delay = max(0, stptime + gsew + time2stp - dist2stp / ew_freespd)
                        else:  # cannot leave during green time
                            delay = stptime + gsew + cycle + time2stp - (geew - gsew) - dist2stp / ew_freespd
                        ewqueuedelay.append(time2stp)
                    # phase 3
                    elif 'SW' in vehrou:
                        if time2stp <= gesw - gssw:  # can leave during green time
                            delay = max(0, stptime + gssw + time2stp - dist2stp / ns_freespd)
                        else:  # cannot leave during green time
                            delay = stptime + gssw + cycle + time2stp- (gesw - gssw) - dist2stp / ns_freespd
                        swqueuedelay.append(time2stp)
                    # phase 4
                    elif 'NS' in vehrou:
                        if time2stp <= gens - gsns:  # can leave during green time
                            delay = max(0, stptime + gsns + time2stp - dist2stp / ns_freespd)
                        else:  # cannot leave during green time
                            delay = stptime + gsns + cycle + time2stp - (gens - gsns) - dist2stp / ns_freespd
                        # print('NS stop vehicle delay ', delay, i, time2stp, dist2stp, stptime, gsns)
                        nsqueuedelay.append(time2stp)
                    # phase 5
                    elif 'ES' in vehrou:
                        if time2stp <= gees - gses:  # can leave during green time
                            delay = max(0, stptime + gses + time2stp - dist2stp / ew_freespd)
                        else:  # cannot leave during green time
                            delay = stptime + gses + cycle + time2stp- (gees - gses) - dist2stp / ew_freespd
                        esqueuedelay.append(time2stp)
                    # phase 6
                    elif 'WE' in vehrou:
                        if time2stp <= gewe - gswe:  # can leave during green time
                            delay = max(0, stptime + gswe + time2stp - dist2stp / ew_freespd)
                        else:  # cannot leave during green time
                            delay = stptime + gswe + cycle + time2stp - (gewe - gswe) - dist2stp / ew_freespd
                        wequeuedelay.append(time2stp)
                    # phase 7
                    elif 'NE' in vehrou:
                        if time2stp <= gene - gsne:  # can leave during green time
                            delay = max(0, stptime + gsne + time2stp - dist2stp / ns_freespd)
                        else:  # cannot leave during green time
                            delay = stptime + gsne + cycle + time2stp - (gene - gsne) - dist2stp / ns_freespd
                        nequeuedelay.append(time2stp)
                    # phase 8
                    elif 'SN' in vehrou:
                        if time2stp <= gesn - gssn:  # can leave during green time
                            delay = max(0, stptime + gssn + time2stp - dist2stp / ns_freespd)
                        else:  # cannot leave during green time
                            delay = stptime + gssn + cycle + time2stp - (gesn - gssn) - dist2stp / ns_freespd
                        snqueuedelay.append(time2stp)
                        # print('SN stop vehicle delay ', delay, i)

                    else:
                        delay = stptime  # assigning delay to right turn vehicles

                    if vehclass == 'passenger':
                        perdelay = delay * caroccupancy
                    else:
                        perdelay = delay * busoccupancy
                    totstopper += perdelay
        # print('stop', totstopper)
        # print(nsqueuedelay)
        wnmaxqueuedelay = max(wnqueuedelay)
        ewmaxqueuedelay = max(ewqueuedelay)
        swmaxqueuedelay = max(swqueuedelay)
        nsmaxqueuedelay = max(nsqueuedelay)
        esmaxqueuedelay = max(esqueuedelay)
        wemaxqueuedelay = max(wequeuedelay)
        nemaxqueuedelay = max(nequeuedelay)
        snmaxqueuedelay = max(snqueuedelay)
        # print(nsmaxqueuedelay)

        for i in vehlst:
            vehtls = traci.vehicle.getNextTLS(i)

            if vehtls:  # vehicles not crossing the intersection
                vehsp = traci.vehicle.getSpeed(i)  # get the speed

                # calculate the delay of running vehicle
                if vehsp >= lowspd:  # running vehicles
                    veh2tls = vehtls[0]  # get the upcoming state related to the traffic lights
                    dist2stp = veh2tls[2]  # get the distance to the stop line
                    vehclass = traci.vehicle.getVehicleClass(i)  # get the type
                    stptime = traci.vehicle.getAccumulatedWaitingTime(i)
                    vehrou = i.split('.')[0]  # get characters in the vehicle id 'i' before the symbol '.'

                    time2stp = dist2stp / vehsp

                    # phase 1
                    if 'WN' in vehrou:
                        if gswn +wnmaxqueuedelay < gewn:  # can clear the queue
                            if time2stp < gswn + wnmaxqueuedelay:
                                delay = gswn + wnmaxqueuedelay - time2stp
                            elif gswn + wnmaxqueuedelay <= time2stp <= gewn:  # arrives at green time
                                delay = 0
                            else:  # arrives after green time
                                delay = cycle + gswn - time2stp
                        else:
                            delay = cycle + gswn - time2stp
                    # phase 2
                    elif 'EW' in vehrou:
                        if gsew +ewmaxqueuedelay < geew:  # can clear the queue
                            if time2stp < gsew + ewmaxqueuedelay:
                                delay = gsew + ewmaxqueuedelay - time2stp
                            elif gsew + ewmaxqueuedelay <= time2stp <= geew:  # arrives at green time
                                delay = 0
                            else:  # arrives after green time
                                delay = cycle + gsew - time2stp
                        else:
                            delay = cycle + gsew - time2stp
                    # phase 3
                    elif 'SW' in vehrou:
                        if gssw + swmaxqueuedelay < gesw:  # can clear the queue
                            if time2stp < gssw + swmaxqueuedelay:
                                delay = gssw + swmaxqueuedelay - time2stp
                            elif gssw + swmaxqueuedelay <= time2stp <= gesw:  # arrives at green time
                                delay = 0
                            else:  # arrives after green time
                                delay = cycle + gssw - time2stp
                        else:
                            delay = cycle + gssw - time2stp
                    # phase 4
                    elif 'NS' in vehrou:
                        if gsns + nsmaxqueuedelay < gens:  # can clear the queue
                            if time2stp < gsns + nsmaxqueuedelay:
                                delay = gsns + nsmaxqueuedelay - time2stp
                            elif gsns + nsmaxqueuedelay <= time2stp <= gens:  # arrives at green time
                                delay = 0
                            else:  # arrives after green time
                                delay = cycle + gsns - time2stp
                        else:
                            delay = cycle + gsns - time2stp
                    # phase 5
                    elif 'ES' in vehrou:
                        if gses + esmaxqueuedelay < gees:  # can clear the queue
                            if time2stp < gses + esmaxqueuedelay:
                                delay = gses + esmaxqueuedelay - time2stp
                            elif gses + esmaxqueuedelay <= time2stp <= gees:  # arrives at green time
                                delay = 0
                            else:  # arrives after green time
                                delay = cycle + gses - time2stp
                        else:
                            delay = cycle + gses - time2stp
                    # phase 6
                    elif 'WE' in vehrou:
                        if gswe + wemaxqueuedelay < gewe:  # can clear the queue
                            if time2stp < gswe + wemaxqueuedelay:
                                delay = gswe + wemaxqueuedelay - time2stp
                            elif gswe + wemaxqueuedelay <= time2stp <= gewe:  # arrives at green time
                                delay = 0
                            else:  # arrives after green time
                                delay = cycle + gswe - time2stp
                        else:
                            delay = cycle + gswe - time2stp
                    # phase 7
                    elif 'NE' in vehrou:
                        if gsne + nemaxqueuedelay < gene:  # can clear the queue
                            if time2stp < gsne + nemaxqueuedelay:
                                delay = gsne + nemaxqueuedelay - time2stp
                            elif gsne + nemaxqueuedelay <= time2stp <= gene:  # arrives at green time
                                delay = 0
                            else:  # arrives after green time
                                delay = cycle + gsne - time2stp
                        else:
                            delay = cycle + gsne - time2stp
                    # phase 8
                    elif 'SN' in vehrou:
                        if gssn + snmaxqueuedelay < gesn:  # can clear the queue
                            if time2stp < gssn + snmaxqueuedelay:
                                delay = gssn + snmaxqueuedelay - time2stp
                            elif gssn + snmaxqueuedelay <= time2stp <= gesn:  # arrives at green time
                                delay = 0
                            else:  # arrives after green time
                                delay = cycle + gssn - time2stp
                        else:
                            delay = cycle + gssn - time2stp
                    else:
                        delay = stptime  # assigning delay to right turn vehicles
                # print(i, vehtls, delay)
                # totper += delay
                # print(totper)
                # calculate the total person delay
                    if vehclass == 'passenger':
                        perdelay = delay * caroccupancy
                    else:
                        perdelay = delay * busoccupancy
                    totrunningper += perdelay
        # print('run', totrunningper)
        totper = totstopper + totrunningper

        # print(veh1, veh2, veh3, veh4)
        # print('total', totper)
        lstdelay.append(totper)  # add total person delay to list
        arrdelay = np.array(lstdelay)  # list to array
        arrdelay = arrdelay.reshape(-1, 1)  # reshape (20,) to (20, 1) for geatpy requirements
        # print(arrdelay)
    return arrdelay
