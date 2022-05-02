import os
import sys
import optparse
from sumolib import checkBinary  # Check for the binary in environ vars
import traci
import geatpy as ea
from TSPGA_main import ga
from enumeration import enumeration

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
    options, args = opt_parser.parse_args()
    return options


#  contains TraCI control loop
def run():
    step = 0

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        # print(traci.vehicle.getIDList())
        # print(step)

        # set the tau
        vehlst = traci.vehicle.getIDList()
        for i in vehlst:
            leader = traci.vehicle.getLeader(i)
            vtype = traci.vehicle.getTypeID(i)

            if leader:
                ltype = traci.vehicle.getTypeID(leader[0])

                if ltype == 'car' and vtype == 'cav':
                    traci.vehicle.setTau(i, 1.1)
                else:
                    pass

        phase = traci.trafficlight.getPhase('J1')
        nextswitch = traci.trafficlight.getNextSwitch('J1')
        simtime = traci.simulation.getTime()
        # print(nextswitch, simtime, calltime)

        # control loop
        if phase == 11:  # equals to the last phase index "11"
            if simtime == nextswitch:  # cycle ends

                res = ga()
                bestres = res.get('Vars')
                # print(bestres)
                g1 = bestres[0, 0]
                g2 = bestres[0, 1]
                g3 = bestres[0, 2]
                g4 = bestres[0, 3]
                # print(g1, g2, g3, g4)

                # set up phase program logic
                phases = []
                phases.append(traci.trafficlight.Phase(1, "grrrrrgrrrrr", 0, 0))
                phases.append(traci.trafficlight.Phase(g1, "grrrrGgrrrrG", 0, 0))
                phases.append(traci.trafficlight.Phase(4, "grrrrygrrrry", 0, 0))
                phases.append(traci.trafficlight.Phase(1, "grrrrrgrrrrr", 0, 0))
                phases.append(traci.trafficlight.Phase(g2, "grrGGrgrrGGr", 0, 0))
                phases.append(traci.trafficlight.Phase(4, "grryyrgrryyr", 0, 0))
                phases.append(traci.trafficlight.Phase(1, "grrrrrgrrrrr", 0, 0))
                phases.append(traci.trafficlight.Phase(g3, "grrrrrGGgrrr", 0, 0))
                phases.append(traci.trafficlight.Phase(4, "grrrrrgyyrrr", 0, 0))
                phases.append(traci.trafficlight.Phase(1, "grrrrrgrrrrr", 0, 0))
                phases.append(traci.trafficlight.Phase(g4, "gggrrrGrrrrr", 0, 0))
                phases.append(traci.trafficlight.Phase(4, "gyyrrrgrrrrr", 0, 0))
                phases.append(traci.trafficlight.Phase(1, "grrrrrgrrrrr", 0, 0))
                logic = traci.trafficlight.Logic("custom", 0, 0, phases)
                traci.trafficlight.setProgramLogic('J1', logic)  # set customized program logic to J1

            else:
                pass
        else:
            pass

        step += 1
    traci.close()
    sys.stdout.flush()


def sumorun():
    options = get_options()
    #  check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "data/tsp.sumocfg", "--step-length", "0.1",
                 "--tripinfo-output", "tripinfo.xml", "--duration-log.statistics", "--log", "logfile.xml"])
    run()


# main entry point
if __name__ == "__main__":
    sumorun()
