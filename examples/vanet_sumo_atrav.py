#!/usr/bin/python

"""Sample file for SUMO

***Requirements***:

Kernel version: 5.8+ (due to the 802.11p support)
sumo 1.5.0 or higher
sumo-gui"""

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.sumo.runner import sumo
from mn_wifi.link import wmediumd, ITSLink
from mn_wifi.wmediumdConnector import interference


def topology():

    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating nodes\n")
    tram_id = [3,10,41,59,79,89,108,131,150,172,191,215,241,256,285,300,328,356,371,408,418,444,481,498]
    for id in range(0, 30):
        if id in tram_id:
            net.addCar('tram%s' % id, wlans=2, encrypt=['wpa2', ''])
        else:
            net.addCar('car%s' % id, wlans=2, encrypt=['wpa2', ''])

    kwargs = {'ssid': 'vanet-ssid', 'mode': 'n',
              'encrypt': 'wpa2', 'failMode': 'standalone', 'datapath': 'user'}
              #'scan_freq': '3500 700 2100 26000', 'freq_list': '3500 700 2100 26000', 'txpower': '45'}
    e1 = net.addAccessPoint('e1', mac='00:00:00:11:00:01', channel='1',
                            position='1000,1700,0', **kwargs)
    e2 = net.addAccessPoint('e2', mac='00:00:00:11:00:02', channel='6',
                            position='1900,1700,0', **kwargs)
    e3 = net.addAccessPoint('e3', mac='00:00:00:11:00:03', channel='11',
                            position='2800,1700,0', **kwargs)
    e4 = net.addAccessPoint('e4', mac='00:00:00:11:00:04', channel='1',
                            position='1000,800,0', **kwargs)
    e5 = net.addAccessPoint('e5', mac='00:00:00:11:00:05', channel='6',
                            position='1900,800,0', **kwargs)
    e6 = net.addAccessPoint('e6', mac='00:00:00:11:00:06', channel='11',
                            position='2800,800,0', **kwargs)


    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=2.8)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    net.addLink(e1, e2)
    net.addLink(e2, e3)
    net.addLink(e3, e4)
    net.addLink(e4, e5)
    net.addLink(e5, e6)
    for car in net.cars:
        net.addLink(car, intf=car.wintfs[1].name,
                    cls=ITSLink, band=20, channel=181)

    # exec_order: Tells TraCI to give the current
    # client the given position in the execution order.
    # We may have to change it from 0 to 1 if we want to
    # load/reload the current simulation from a 2nd client
    net.useExternalProgram(program=sumo, port=8813,
                           config_file='Grande_Map/osm.sumocfg',
                           extra_params=["--start --delay 200"],
                           clients=1, exec_order=0)

    info("*** Starting network\n")
    net.build()

    for enb in net.aps:
        enb.start([])

    for id, car in enumerate(net.cars):
        car.setIP('192.168.0.{}/24'.format(id+1),
                  intf='{}'.format(car.wintfs[0].name))
        car.setIP('192.168.1.{}/24'.format(id+1),
                  intf='{}'.format(car.wintfs[1].name))

    # Track the position of the nodes
    nodes =  net.cars + net.aps
    net.telemetry(nodes=nodes, data_type='position',
                  min_x=200, min_y=200,
                  max_x=3500, max_y=2300)

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
