#!/usr/bin/env python

import os
import sys
import optparse
import numpy as np
from Analysis import analysis

# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME")

from sumolib import checkBinary  # Check for the binary in environ vars
import traci


def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                          default=False, help="run the commandline version of sumo")
    arg = ['--nogui']
    # options, args = opt_parser.parse_args()
    options, args = opt_parser.parse_args(arg)  # 括号内有arg表示不启动gui
    return options


#  contains TraCI control loop
def run():
    detlist = traci.inductionloop.getIDList()
    triggertime = -20
    while traci.simulation.getMinExpectedNumber() > 0:
        # northdetector = {'N0', 'N1'}
        # southdetector = {'S0', 'S1'}
        # print(traci.trafficlight.getAllProgramLogics('J1'))
        for i in detlist:
            k = traci.inductionloop.getVehicleData(i)  # get vehicle data that through detector
            # identifying buses that come across the detectors and changing the phase
            if k:
                # print(k[0])
                buspos = traci.vehicle.getNextTLS(k[0][0])
                # print(buspos)
                triggertime = traci.simulation.getTime()
                # print(triggertime)
                if buspos[0][3] == 'r':
                    traci.trafficlight.setProgram('J1', 'TSP')
                    traci.trafficlight.setPhase('J1', 0)
                    # print('tsp is triggered')

        if traci.simulation.getTime() == triggertime + 20:
            traci.trafficlight.setProgram('J1', 'NEMA')

        # print(triggertime)
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


def iteration():
    options = get_options()
    totres = []
    n = 20
    for i in range(n):  # run n simulations
        #  check binary
        print(i)
        if options.nogui:
            sumoBinary = checkBinary('sumo')
        else:
            sumoBinary = checkBinary('sumo-gui')

        # traci starts sumo as a subprocess and then this script connects and runs
        # "--step-length", "0.1",
        traci.start([sumoBinary, "-c", "data/Eastway-Central.sumocfg", "--seed", "%d" % i,
                     "--tripinfo-output", "tripinfo.xml", "--duration-log.statistics", "--log", "logfile.xml"])
        run()
        res = analysis()
        totres.append(res)

    # ares = np.concatenate(totres, axis=0)
    ares = np.reshape(totres, (n, 16))  # change list to array and reshape
    np.savetxt('totalresult.csv', ares, delimiter=',')  # save to files
    # print(ares)


# main entry point
if __name__ == "__main__":
    iteration()
