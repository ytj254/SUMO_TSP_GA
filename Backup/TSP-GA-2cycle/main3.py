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
import time

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
    while traci.simulation.getMinExpectedNumber() > 0:
        # vehlst = traci.vehicle.getIDList()  # get all the vehicle ID that currently running within the scenario
        # # print(vehlst)
        # # set the tau
        # for i in vehlst:
        #     leader = traci.vehicle.getLeader(i)
        #     vtype = traci.vehicle.getTypeID(i)
        #     if leader:
        #         ltype = traci.vehicle.getTypeID(leader[0])
        #         if 'car' in ltype and 'cav' in vtype:
        #             tau = traci.vehicle.getTau(i)
        #             if tau != 0.9:
        #                 traci.vehicle.setTau(i, 0.9)
        #         elif 'cav' in vtype:
        #             tau = traci.vehicle.getTau(i)
        #             if tau != 0.6:
        #                 traci.vehicle.setTau(i, 0.6)

        phase = traci.trafficlight.getPhase('J1')
        # print(phase)
        nextswitch = traci.trafficlight.getNextSwitch('J1')
        simtime = traci.simulation.getTime()
        # calltime = simtime + 0.1
        # print(nextswitch, simtime, calltime)

        # control loop
        if phase == 12:  # equals to the last phase index "11"
            # print(simtime, nextswitch, calltime)
            if simtime == nextswitch:  # cycle ends
                # print(simtime)

                res = ga()
                bestres = res.get('Vars')
                # print(bestres)
                g1 = bestres[0, 0]
                g2 = bestres[0, 1]
                g3 = bestres[0, 2]
                g4 = bestres[0, 3]
                # print(g1, g2, g3, g4)

                # set up phase program logic
                phases = [traci.trafficlight.Phase(1,  "grrrgrrrrgrrrgrrrr", 0, 0),
                          traci.trafficlight.Phase(g1, "grrGgrrrrgrrGgrrrr", 0, 0),
                          traci.trafficlight.Phase(3,  "grrygrrrrgrrygrrrr", 0, 0),
                          traci.trafficlight.Phase(2,  "grrrgrrrrgrrrgrrrr", 0, 0),
                          traci.trafficlight.Phase(g2, "gGGrgrrrrgGGrgrrrr", 0, 0),
                          traci.trafficlight.Phase(3,  "gyyrgrrrrgyyrgrrrr", 0, 0),
                          traci.trafficlight.Phase(2,  "grrrgrrrrgrrrgrrrr", 0, 0),
                          traci.trafficlight.Phase(g3, "grrrgrrGGgrrrgrrGG", 0, 0),
                          traci.trafficlight.Phase(3,  "grrrgrryygrrrgrryy", 0, 0),
                          traci.trafficlight.Phase(2,  "grrrgrrrrgrrrgrrrr", 0, 0),
                          traci.trafficlight.Phase(g4, "grrrgGGrrgrrrgGGrr", 0, 0),
                          traci.trafficlight.Phase(3,  "grrrgyyrrgrrrgyyrr", 0, 0),
                          traci.trafficlight.Phase(2,  "grrrgrrrrgrrrgrrrr", 0, 0)]
                logic = traci.trafficlight.Logic("custom", 0, 0, phases)
                traci.trafficlight.setProgramLogic('J1', logic)  # set customized program logic to J1

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
    local = time.strftime('%Y-%m-%d-%H-%M-%S')
    n = 5
    for i in range(n):  # run n times of simulations
        #  check binary
        print(i)
        if options.nogui:
            sumoBinary = checkBinary('sumo')
        else:
            sumoBinary = checkBinary('sumo-gui')

        # traci starts sumo as a subprocess and then this script connects and runs
        # "--step-length", "0.1",
        traci.start([sumoBinary, "-c", "data/Eastway-Central.sumocfg", "--seed", "%d" % (i + 20),
                     "--tripinfo-output", "result/" + str(local) + "tripinfo.xml",
                     "--duration-log.statistics", "--log", "result/" + str(local) + "logfile.xml"])
        run()
        res = analysis("result/" + str(local) + "tripinfo.xml")
        totres.append(res)

    # ares = np.concatenate(totres, axis=0)
    ares = np.reshape(totres, (n, 16))  # change list to array and reshape
    np.savetxt(str(local) + 'totalresult.csv', ares, delimiter=',')  # save to files
    # print(ares)


# main entry point
if __name__ == "__main__":
    iteration()
