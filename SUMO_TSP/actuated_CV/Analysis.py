from xml.dom.minidom import parse
import xml.dom.minidom
import numpy as np


# open xml
domtree = xml.dom.minidom.parse('tripinfo.xml')

# obtain file element
collection = domtree.documentElement
tripinfos = collection.getElementsByTagName('tripinfo')
bdelay = []
bstp = []
cdelay = []
cstp = []
nwdelay = []
nsdelay = []
nedelay = []
ewdelay = []
esdelay = []
sedelay = []
sndelay = []
swdelay = []
wedelay = []
wndelay = []
bewdelay = []
bwedelay = []

for tripinfo in tripinfos:
    vtype = tripinfo.getAttribute('vType')
    # depart = tripinfo.getAttribute('departLane')[0:2]
    rou = tripinfo.getAttribute('id').split('.')[0]
    # print(rou)
    # print(depart)

    if vtype == 'bus':
        # print(tripinfo.getAttribute('timeLoss'))
        bdelay.append(tripinfo.getAttribute('timeLoss'))
        bstp.append(tripinfo.getAttribute('waitingTime'))
    else:
        cdelay.append(tripinfo.getAttribute('timeLoss'))
        cstp.append(tripinfo.getAttribute('waitingTime'))

    if rou == 'nw':
        nwdelay.append(tripinfo.getAttribute('timeLoss'))
    elif rou == 'NS':
        nsdelay.append(tripinfo.getAttribute('timeLoss'))
    elif rou == 'NE':
        nedelay.append(tripinfo.getAttribute('timeLoss'))
    elif rou == 'EW':
        ewdelay.append(tripinfo.getAttribute('timeLoss'))
    elif rou == 'ES':
        esdelay.append(tripinfo.getAttribute('timeLoss'))
    elif rou == 'SE':
        sedelay.append(tripinfo.getAttribute('timeLoss'))
    elif rou == 'SN':
        sndelay.append(tripinfo.getAttribute('timeLoss'))
    elif rou == 'SW':
        swdelay.append(tripinfo.getAttribute('timeLoss'))
    elif rou == 'WE':
        wedelay.append(tripinfo.getAttribute('timeLoss'))
    elif rou == 'WN':
        wndelay.append(tripinfo.getAttribute('timeLoss'))
    elif rou == 'BEW':
        bewdelay.append(tripinfo.getAttribute('timeLoss'))
    elif rou == 'BWE':
        bwedelay.append(tripinfo.getAttribute('timeLoss'))
    else:
        pass

# string to float
bdelay = [float(x) for x in bdelay]
bstp = [float(x) for x in bstp]

cdelay = [float(x) for x in cdelay]
cstp = [float(x) for x in cstp]

nwdelay = [float(x) for x in nwdelay]
nsdelay = [float(x) for x in nsdelay]
nedelay = [float(x) for x in nedelay]
ewdelay = [float(x) for x in ewdelay]
esdelay = [float(x) for x in esdelay]
sedelay = [float(x) for x in sedelay]
sndelay = [float(x) for x in sndelay]
swdelay = [float(x) for x in swdelay]
wedelay = [float(x) for x in wedelay]
wndelay = [float(x) for x in wndelay]
bewdelay = [float(x) for x in bewdelay]
bwedelay = [float(x) for x in bwedelay]

# list to array
# bdelay = np.array(bdelay)
# bstp = np.array(bstp)
#
# cdelay = np.array(cdelay)
# cstp = np.array(cstp)

# nwdelay = np.array(nwdelay)
# nsdelay = np.array(nsdelay)
# nedelay = np.array(nedelay)
# ewdelay = np.array(ewdelay)
# esdelay = np.array(esdelay)
# sedelay = np.array(sedelay)
# sndelay = np.array(sndelay)
# swdelay = np.array(swdelay)
# wedelay = np.array(wedelay)
# wndelay = np.array(wndelay)
# bewdelay = np.array(bewdelay)
# bwedelay = np.array(bwedelay)

# mean delay
bmean = np.mean(bdelay)
cmean = np.mean(cdelay)

# nwmean = np.mean(nwdelay)
nsmean = np.mean(nsdelay)
nemean = np.mean(nedelay)
ewmean = np.mean(ewdelay)
esmean = np.mean(esdelay)
# semean = np.mean(sedelay)
snmean = np.mean(sndelay)
swmean = np.mean(swdelay)
wemean = np.mean(wedelay)
wnmean = np.mean(wndelay)
bewmean = np.mean(bewdelay)
bwemean = np.mean(bwedelay)


print('delay per bus:', bmean)
print('delay per car:', cmean)

# print('delay per car(north right turn):', nwmean)
print('delay per car(north straight):', nsmean)
print('delay per car(north left turn):', nemean)
print('delay per car(east straight):', ewmean)
print('delay per car(east left turn):', esmean)
# print('delay per car(south right turn):', semean)
print('delay per car(south straight):', snmean)
print('delay per car(south left turn):', swmean)
print('delay per car(west straight):', wemean)
print('delay per car(west left turn):', wnmean)
print('delay per bus(east straight):', bewmean)
print('delay per bus(west straight):', bwemean)




