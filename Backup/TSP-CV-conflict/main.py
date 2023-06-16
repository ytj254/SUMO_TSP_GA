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
    nsthrough = 'gGGrgrrrrgGGrgrrrr'
    ewthrough = 'grrrgGGrrgrrrgGGrr'
    while traci.simulation.getMinExpectedNumber() > 0:
        vehlst = traci.vehicle.getIDList()  # get all the vehicle ID that currently running within the scenario
        # print(vehlst)
        buslst = []  # each time step, bus list set to empty
        for i in vehlst:
            vehcls = traci.vehicle.getVehicleClass(i)  # get vehicle class that currently running within scenario
            if vehcls == 'bus':
                buslst.append(i)  # create the bus id list in the time step

        programnow = traci.trafficlight.getProgram('J1')
        phasenow = traci.trafficlight.getRedYellowGreenState('J1')
        if programnow != 'online':
            for j in buslst:
                vehrou = j.split('.')[0]  # get characters in the vehicle id 'i' before the symbol '.'
                buspos = traci.vehicle.getNextTLS(j)
                if buspos:  # if bus approaching the intersection
                    buspos = buspos[0]  # get the distance between the bus and the upcoming traffic light
                    if 'NS' in vehrou or 'SN' in vehrou:
                        if buspos[2] < 100:  # distance control
                            traci.trafficlight.setRedYellowGreenState('J1', nsthrough)
                            break  # jump out of the search for bus list

                    elif 'EW' in vehrou or 'WE' in vehrou:
                        if buspos[2] < 75:  # distance control
                            traci.trafficlight.setRedYellowGreenState('J1', ewthrough)
                            break  # jump out of the search for bus list
        else:
            nscount = 0
            ewcount = 0
            for j in buslst:
                vehrou = j.split('.')[0]  # get characters in the vehicle id 'i' before the symbol '.'
                buspos = traci.vehicle.getNextTLS(j)
                if buspos:  # if bus approaching the intersection
                    buspos = buspos[0]  # get the distance between the bus and the upcoming traffic light
                    if 'NS' in vehrou or 'SN' in vehrou:
                        if buspos[2] < 100:  # distance control
                            nscount += 1
                    elif 'EW' in vehrou or 'WE' in vehrou:
                        if buspos[2] < 75:  # distance control
                            ewcount += 1
            if nscount == 0 and phasenow == nsthrough:
                traci.trafficlight.setProgram('J1', 'NEMA')
            elif ewcount == 0 and phasenow == ewthrough:
                traci.trafficlight.setProgram('J1', 'NEMA')

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
