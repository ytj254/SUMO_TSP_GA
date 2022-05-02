import random


def generate_routefile():
    random.seed(42)  # make tests reproducible
    N = 3600  # number of time steps
    # demand per second from different directions
    nw = 1. / 10  # right flow 360
    ns = 1. / 30  # straight flow 120
    ne = 1. / 15  # left flow 240
    ew = 1. / 3   # straight flow 1200
    es = 1. / 15  # left flow 240
    se = 1. / 10  # right flow 360
    sn = 1. / 30  # straight flow 120
    sw = 1. / 15  # left flow 240
    we = 1. / 3   # straight flow 1200
    wn = 1. / 15  # left flow 240
    bew = 1. / 300  # bus flow 5min interval
    bwe = 1. / 300  # bus flow 5min interval

    with open("data/tsp.rou.xml", "w") as routes:
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