#!/usr/bin/env python

import os
import sys
import optparse
from sumolib import checkBinary  # Check for the binary in environ vars
import traci
import geatpy as ea
from TSPGA_main import ga
import numpy as np
from Analysis import analysis

# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME")


def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                          default=False, help="run the commandline version of sumo")
    arg = ['--nogui']
    options, args = opt_parser.parse_args(arg)  # 括号内有arg表示不启动gui
    return options


#  contains TraCI control loop
def run():
    buslst = []
    while traci.simulation.getMinExpectedNumber() > 0:
        vehlst = traci.vehicle.getIDList()  # get all the vehicle ID that currently running within the scenario

        # set the tau
        # for i in vehlst:
        #     leader = traci.vehicle.getLeader(i)
        #     vtype = traci.vehicle.getTypeID(i)
        #
        #     if leader:
        #         ltype = traci.vehicle.getTypeID(leader[0])
        #
        #         if ltype == 'car' and vtype == 'cav':
        #             traci.vehicle.setType(i, 'av')
        simtime = traci.simulation.getTime()
        currentbuslst = []

        for i in vehlst:
            vehclass = traci.vehicle.getVehicleClass(i)
            if vehclass == 'bus':
                currentbuslst.append(i)
                if i not in buslst:
                    buslst.append(i)
                    # print(buslst, currentbuslst)

                    # call GA
                    res = ga()
                    bestres = res.get('Vars')
                    cycle = bestres[0, 0]
                    mainphase = bestres[0, 1]
                    p1 = bestres[0, 2]
                    p3 = bestres[0, 3]
                    p5 = bestres[0, 4]
                    p7 = bestres[0, 5]
                    sequence = '{:04b}'.format(bestres[0, 6])  # get the sequence and change to binary with four digits
                    # traci.trafficlight.setLinkState('J1', 7, 'r')
                    # print(triggertime, cyclestart)
                    cyclestart = simtime
                    cycleend = cyclestart + cycle
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
        # for j in currentbuslst:
        #     buspos = traci.vehicle.getNextTLS(j)
        #     print('control')
        #     if buspos:
        #         print('controlling', simtime - cyclestart)
        try:
            if cyclestart <= simtime <= cycleend:
                # print('control')
                # control phase 4, north to south
                if gsns <= simtime - cyclestart <= gens:
                    traci.trafficlight.setLinkState('J1', 1, 'G')
                    traci.trafficlight.setLinkState('J1', 2, 'G')
                elif gens <= simtime - cyclestart <= gens + 3:
                    traci.trafficlight.setLinkState('J1', 1, 'y')
                    traci.trafficlight.setLinkState('J1', 2, 'y')
                else:
                    traci.trafficlight.setLinkState('J1', 1, 'r')
                    traci.trafficlight.setLinkState('J1', 2, 'r')
                # control phase 7, north to east
                if gsne <= simtime - cyclestart <= gene:
                    traci.trafficlight.setLinkState('J1', 3, 'G')
                elif gene <= simtime - cyclestart <= gene + 3:
                    traci.trafficlight.setLinkState('J1', 3, 'y')
                else:
                    traci.trafficlight.setLinkState('J1', 3, 'r')
                # control phase 2, east to west
                if gsew <= simtime - cyclestart <= geew:
                    traci.trafficlight.setLinkState('J1', 5, 'G')
                    traci.trafficlight.setLinkState('J1', 6, 'G')
                elif geew <= simtime - cyclestart <= geew + 3:
                    traci.trafficlight.setLinkState('J1', 5, 'y')
                    traci.trafficlight.setLinkState('J1', 6, 'y')
                else:
                    traci.trafficlight.setLinkState('J1', 5, 'r')
                    traci.trafficlight.setLinkState('J1', 6, 'r')
                # control phase 5, east to south
                if gses <= simtime - cyclestart <= gees:
                    traci.trafficlight.setLinkState('J1', 7, 'G')
                    traci.trafficlight.setLinkState('J1', 8, 'G')
                elif gees <= simtime - cyclestart <= gees + 3:
                    traci.trafficlight.setLinkState('J1', 7, 'y')
                    traci.trafficlight.setLinkState('J1', 8, 'y')
                else:
                    traci.trafficlight.setLinkState('J1', 7, 'r')
                    traci.trafficlight.setLinkState('J1', 8, 'r')
                # control phase 8, south to north
                if gssn <= simtime - cyclestart <= gesn:
                    traci.trafficlight.setLinkState('J1', 10, 'G')
                    traci.trafficlight.setLinkState('J1', 11, 'G')
                elif gesn <= simtime - cyclestart <= gesn + 3:
                    traci.trafficlight.setLinkState('J1', 10, 'y')
                    traci.trafficlight.setLinkState('J1', 11, 'y')
                else:
                    traci.trafficlight.setLinkState('J1', 10, 'r')
                    traci.trafficlight.setLinkState('J1', 11, 'r')
                # control phase 3, south to west
                if gssw <= simtime - cyclestart <= gesw:
                    traci.trafficlight.setLinkState('J1', 12, 'G')
                elif gesw <= simtime - cyclestart <= gesw + 3:
                    traci.trafficlight.setLinkState('J1', 12, 'y')
                else:
                    traci.trafficlight.setLinkState('J1', 12, 'r')
                # control phase 6, west to east
                if gswe <= simtime - cyclestart <= gewe:
                    traci.trafficlight.setLinkState('J1', 14, 'G')
                    traci.trafficlight.setLinkState('J1', 15, 'G')
                elif gewe <= simtime - cyclestart <= gewe + 3:
                    traci.trafficlight.setLinkState('J1', 14, 'y')
                    traci.trafficlight.setLinkState('J1', 15, 'y')
                else:
                    traci.trafficlight.setLinkState('J1', 14, 'r')
                    traci.trafficlight.setLinkState('J1', 15, 'r')
                # control phase 1, west to north
                if gswn <= simtime - cyclestart <= gewn:
                    traci.trafficlight.setLinkState('J1', 16, 'G')
                    traci.trafficlight.setLinkState('J1', 17, 'G')
                elif gewn <= simtime - cyclestart <= gewn + 3:
                    traci.trafficlight.setLinkState('J1', 16, 'y')
                    traci.trafficlight.setLinkState('J1', 17, 'y')
                else:
                    traci.trafficlight.setLinkState('J1', 16, 'r')
                    traci.trafficlight.setLinkState('J1', 17, 'r')
            else:
                if traci.trafficlight.getProgram('J1') != 'NEMA':
                    traci.trafficlight.setProgram('J1', 'NEMA')
        except:
            pass

        traci.simulationStep()
    traci.close()
    sys.stdout.flush()


def test():
    options = get_options()
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # traci starts sumo as a subprocess and then this script connects and runs
    # "--step-length", "0.1",
    traci.start([sumoBinary, "-c", "data/Eastway-Central.sumocfg",
                 "--tripinfo-output", "tripinfo.xml", "--duration-log.statistics", "--log", "logfile.xml"])
    run()


def interation():
    options = get_options()
    totres = []
    n = 10
    for i in range(n):  # run n simulations
        #  check binary
        print(i)
        if options.nogui:
            sumoBinary = checkBinary('sumo')
        else:
            sumoBinary = checkBinary('sumo-gui')

        # traci starts sumo as a subprocess and then this script connects and runs
        # "--step-length", "0.1",
        traci.start([sumoBinary, "-c", "data/Eastway-Central.sumocfg",
                     "--tripinfo-output", "tripinfo.xml", "--duration-log.statistics", "--log", "logfile.xml"])
        run()
        res = analysis()
        totres.append(res)

    # ares = np.concatenate(totres, axis=0)
    ares = np.reshape(totres, (n, 14))  # change list to array and reshape
    np.savetxt('totalresult.csv', ares, delimiter=',')  # save to files
    # print(ares)


# main entry point
if __name__ == "__main__":
    test()
