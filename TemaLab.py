from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa


def generate_routefile():
    random.seed(42)  # make tests reproducible
    N = 3600  # number of time steps
    # demand per second from different directions
    pWE = 1. / 10
    pEW = 1. / 11
    pNS = 1. / 30
    with open("C:\SumoProjects/TemaLab.rou.xml", "w") as routes:
        print("""<routes>
        <vType id="typeWE" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" \
guiShape="passenger"/>
        <vType id="typeNS" accel="0.8" decel="4.5" sigma="0.5" length="7" minGap="3" maxSpeed="25" guiShape="bus"/>

        <route id="right" edges="51o 1i 2o 52i" />
        <route id="left" edges="52o 2i 1o 51i" />
        <route id="down" edges="54o 4i 3o 53i" />""", file=routes)
        vehNr = 0
        for i in range(N):
            if random.uniform(0, 1) < pWE:
                print('    <vehicle id="right_%i" type="typeWE" route="right" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pEW:
                print('    <vehicle id="left_%i" type="typeWE" route="left" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pNS:
                print('    <vehicle id="down_%i" type="typeNS" route="down" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1
        print("</routes>", file=routes)

def run():
    """execute the TraCI control loop"""
    step = 0
    traci.vehicle.setMaxSpeed("0", 3.0)
    traci.vehicle.setMaxSpeed("0", 11.0)

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        kocsi_edge = traci.vehicle.getRoadID("0")
        kocsik = traci.edge.getLastStepVehicleIDs(kocsi_edge)
        megtett_tav = traci.vehicle.getDistance("0")

        varakozasi_ido = traci.vehicle.getWaitingTime("4")
        if varakozasi_ido == 10:
            print("dugó van")

        car_4_jelenlegi_lane_index = traci.vehicle.getLaneIndex("4")
        car_4_elotti = traci.vehicle.getLeader("4", 0)


        if car_4_elotti is not None:
            if car_4_elotti[1] < 15:
                if car_4_jelenlegi_lane_index == 1:

                    traci.vehicle.changeLane("4",car_4_jelenlegi_lane_index-1,40)
                elif car_4_jelenlegi_lane_index == 0:

                    traci.vehicle.changeLane("4",car_4_jelenlegi_lane_index+1,40)

        if 900 < megtett_tav < 905:
            if traci.vehicle.getLaneID("0") == "E3" :
                traci.vehicle.setRouteID("0", "route_2")

        for i in range(len(kocsik)):
            if kocsik[i] == "0":
                if len(kocsik) > 1:
                    tavolsag = traci.vehicle.getLanePosition(kocsik[i]) - traci.vehicle.getLanePosition(kocsik[i - 1])
                    if tavolsag < 20:
                        traci.vehicle.setMaxSpeed("0", 15.0)
                    else:
                        traci.vehicle.setMaxSpeed("0", 3.0)

    step += 1
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    # generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "C:\SumoProjects/TemaLab.sumocfg"])
    run()