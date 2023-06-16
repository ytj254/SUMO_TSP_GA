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
    options, args = opt_parser.parse_args(arg)  # 括号内有arg表示不启动gui
    return options


#  contains TraCI control loop
def run():
    while traci.simulation.getMinExpectedNumber() > 0:
        vehlst = traci.vehicle.getIDList()  # get all the vehicle ID that currently running within the scenario
        # print(vehlst)
        buslst = []  # each time step, bus list set to empty
        busposlst = []

        for i in vehlst:
            vehcls = traci.vehicle.getVehicleClass(i)  # get vehicle class that currently running within scenario
            if vehcls == 'bus':
                buslst.append(i)  # create the bus id list in the time step

        # print(buslst)
        for j in buslst:
            buspos = traci.vehicle.getNextTLS(j)
            if buspos:
                buspos = buspos[0]  # get the distance between the bus and the upcoming traffic light
                busposlst.append(buspos)
        # print(busposlst)
        if any(pos[2] < 100 for pos in busposlst):
            # print(111)
            for k in busposlst:
                if k:
                    if k[2] < 100:
                        if k[3] == 'r':
                            if traci.trafficlight.getProgram('J1') == 'NEMA':
                                traci.trafficlight.setProgram('J1', 'TSP')
                                traci.trafficlight.setPhase('J1', 0)
                                # print(traci.trafficlight.getProgram('J1'))
                                print('TSP is triggered')
        else:
            if traci.trafficlight.getProgram('J1') != 'NEMA':
                traci.trafficlight.setProgram('J1', 'NEMA')
                # print(traci.trafficlight.getProgram('J1'))
                # print(triggertime, traci.simulation.getTime())
                print('NEMA is used')

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
