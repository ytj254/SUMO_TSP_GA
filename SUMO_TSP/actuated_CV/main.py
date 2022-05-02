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
        vehlst = traci.vehicle.getIDList()  # get all the vehicle ID that currently running within the scenario
        for i in vehlst:
            k = traci.vehicle.getVehicleClass(i)  # get vehicle class that currently running within scenario
            # if bus, then get the state of upcoming traffic light
            if k == 'bus':
                # print(traci.vehicle.getNextTLS(i))
                buspos = traci.vehicle.getNextTLS(i)
                if buspos:
                    buspos = buspos[0]  # get the distance between the bus and the upcoming traffic light
                    # print(buspos[2])
                    if buspos[2] < 60 and buspos[3] == 'r':  # distance < 45m (3*15.28m/s) and link state is red
                        # set the phase to yellow
                        #     if traci.trafficlight.getPhase('J1') % 3 == 0:  # not yellow phase
                        #         # switch to next yellow phase
                        #         traci.trafficlight.setPhase('J1', traci.trafficlight.getPhase('J1') + 1)
                        #         print('triggered')
                        #
                        #         # if traci.simulation.getTime() == traci.trafficlight.getNextSwitch('J1'):
                        #         #     traci.trafficlight.setPhase('J1', 3)  # switch to phase 0
                        #         #     print('triggered')
                        #     # when yellow time is over, switch to phase 0
                        #     else:  # is yellow phase
                        #         # yellow time is over
                        #         if traci.simulation.getTime() == traci.trafficlight.getNextSwitch('J1'):
                        #             traci.trafficlight.setPhase('J1', 3)  # switch to phase 0
                        #         else:
                        #             pass
                        # elif buspos[2] < 60 and buspos[3] == 'y':
                        traci.trafficlight.setPhase('J1', 3)

                    else:
                        pass
                else:
                    pass
            else:
                pass
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
