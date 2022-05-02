#!/usr/bin/env python

import os
import sys
import optparse

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
    options, args = opt_parser.parse_args()
    return options


#  contains TraCI control loop
def run():

    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        # print(traci.vehicle.getIDList())
        # print(step)
        # print(traci.inductionloop.getLastStepVehicleIDs("e0"))
        # print(traci.inductionloop.getVehicleData("e0"))
        detidlst = traci.inductionloop.getIDList()  # get the ID list of detector
        for i in detidlst:
            k = traci.inductionloop.getVehicleData(i)  # get vehicle data that through detector
            # print(k)
        # identifying buses that come across the detectors and changing the phase
            if k:
                k = k[0]
                # print(k[4])
                if k[4] == 'bus':
                    print('tsp is triggered')
                    traci.trafficlight.setPhase("J1", 3)
                else:
                    pass
            else:
                pass
            # print(traci.vehicle.getVehicleClass(k[0]))

        # print(traci.simulation.getMinExpectedNumber())
        step += 1

    traci.close()
    sys.stdout.flush()


# main entry point
if __name__ == "__main__":
    options = get_options()

    #  check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "data/tsp.sumocfg",
                 "--tripinfo-output", "tripinfo.xml", "--duration-log.statistics", "--log", "logfile.xml"])
    run()
