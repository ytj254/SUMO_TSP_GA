import numpy as np
import traci


def enumeration():
    lstdelay = []
    acar = 1.0
    abus = 0.8
    cycle = 100
    vehlst = traci.vehicle.getIDList()  # get all the vehicle ID that currently running within the scenario

    for x in range(1, 80):
        for y in range(1, 80):
            for m in range(1, 80):
                for n in range(1, 80):
                    if x + y + m + n == 80:
                        g1 = x
                        g2 = y
                        g3 = m
                        g4 = n
                        # print(g1, g2, g3, g4)
                        p1 = g1 + 4
                        p2 = g1 + g2 + 9
                        p3 = g1 + g2 + g3 + 14
                        p4 = g1 + g2 + g3 + g4 + 19
                        totper = 0
                        veh = 0
                        veh1 = 0
                        veh2 = 0
                        veh3 = 0
                        veh4 = 0
                        # print(traci.vehicle.getIDCount())

                        for i in vehlst:
                            vehtls = traci.vehicle.getNextTLS(i)
                            vehsp = traci.vehicle.getSpeed(i)  # get the speed
                            vehtp = traci.vehicle.getTypeID(i)  # get the type
                            vehrou = traci.vehicle.getRoute(i)  # get the route
                            stptime = traci.vehicle.getAccumulatedWaitingTime(i)
                            # print(vehtls)

                            if vehtls:  # vehicles not crossing the intersection
                                veh2tls = vehtls[0]  # get the upcoming state related to the traffic lights
                                dist2stp = veh2tls[2]  # get the distance to the stop line
                                # print(dist2stp)

                                # calculate the travel time to stop line
                                if vehsp < 1:  # stopped vehicles
                                    if vehtp == "car":
                                        time2stp = pow(2*dist2stp/acar, 0.5)
                                    else:
                                        time2stp = pow(2*dist2stp/abus, 0.5)
                                else:
                                    time2stp = dist2stp / vehsp
                                # print(i, vehsp, time2stp, traci.vehicle.getWaitingTime(i), stptime)

                                # main street left turn, phase "g1"
                                if vehrou == ('E0', '-E3') or vehrou == ('E1', '-E2'):
                                    if time2stp <= p1:  # arrives at green and yellow time of phase 1
                                        delay = 0
                                    else:  # arrives at other phase
                                        delay = cycle - time2stp
                                        veh1 += 1

                                # main street straight, phase "g2"
                                elif vehrou == ('E0', '-E1') or vehrou == ('E1', '-E0'):

                                    if p2 >= time2stp >= (p1 + 1):  # arrives at green and yellow time of phase 2
                                        delay = 0
                                    elif time2stp < (p1 + 1):  # arrives at phase 1
                                        delay = (p1 + 1) - time2stp
                                        veh2 += 1

                                    else:  # arrives at phase 3 and 4
                                        delay = cycle + (p1 + 1) - time2stp
                                        veh2 += 1

                                # south, phase "g3"
                                elif vehrou == ('E2', '-E3') or vehrou == ('E2', '-E0'):

                                    if p3 >= time2stp >= (p2 + 1):  # arrives at green and yellow time of phase 3
                                        delay = 0
                                    elif time2stp < (p2 + 1):  # arrives at phase 1 and 2
                                        delay = (p2 + 1) - time2stp
                                        veh3 += 1

                                    else:  # arrives at phase 4
                                        delay = cycle + (p2 + 1) - time2stp
                                        veh3 += 1

                                # north, phase "g4"
                                elif vehrou == ('E3', '-E2') or vehrou == ('E3', '-E1'):

                                    if p4 >= time2stp >= (p3 + 1):  # arrives at green and yellow time of phase 4
                                        delay = 0
                                    elif time2stp < (p3 + 1):  # arrives other phase
                                        delay = (p3 + 1) - time2stp
                                        veh4 += 1

                                else:
                                    pass

                                # calculate the total person delay
                                # if vehtp == "car":
                                #     perdelay = (delay + stptime) * 2
                                # else:
                                #     perdelay = (delay + stptime) * 30
                                # totper += perdelay
                            else:
                                pass
                        veh = veh1 + veh2 + veh3 + veh4
                        # print(g1, g2, g3, g4)
                        # print(veh, veh1, veh2, veh3, veh4)
                        lstdelay.append(veh)  # add total person delay to list
    print(g1, g2, g3, g4)
    print(min(lstdelay))
                        # arrdelay = np.array(lstdelay)  # list to array
                        # arrdelay = arrdelay.reshape(-1, 1)  # reshape (20,) to (20, 1) for geatpy requirements
                        # print(arrdelay)
    return g1, g2, g3, g4
