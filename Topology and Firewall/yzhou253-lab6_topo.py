#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController

class MyTopology(Topo):
  def __init__(self):
    Topo.__init__(self)
   
    # laptop1 = self.addHost('Laptop1', ip='200.20.2.8/24',defaultRoute="Laptop1-eth1")

    # switch1 = self.addSwitch('s1')

    # self.addLink(laptop1, switch1, port1=1, port2=2)


    #------------------------------------------------------------------------------------------------------#
    # s2-5 are all connected to s1(coreSwitch)
    coreSwitch = self.addSwitch('s1')

    # Faculty LAN:
    # ‘facultyWS’ - 10.0.1.2/24d
    # ‘facultyPC’ - 10.0.1.3/24 
    # ‘printer’ - 10.0.1.4/24 
    # all connected to ‘s2’ (facultySwitch)
    facultySwitch = self.addSwitch('s2')
    self.addLink(facultySwitch, coreSwitch, port1=1, port2=1)
    facultyWS = self.addHost('facultyWS', ip='10.0.1.2/24', defaultRoute="facultyWS-eth1")
    self.addLink(facultyWS, facultySwitch, port1=1, port2=2)#all host on 1, connect to swtich
    facultyPC = self.addHost('facultyPC', ip='10.0.1.3/24', defaultRoute="facultyPC-eth1")
    self.addLink(facultyPC, facultySwitch, port1=1, port2=3)
    printer = self.addHost('printer', ip='10.0.1.4/24', defaultRoute="printer-eth1")
    self.addLink(printer, facultySwitch, port1=1, port2=4)
    
    
    # Student Housing LAN:
    # ‘labWS’ - 10.0.2.3/24 
    # ‘studentPC1’ - 10.0.2.2/24 (also has an arrow to labWS)
    # ‘studentPC2’ - 10.0.2.40 
    # all connected to ‘s3’ (studentSwitch)
    studentSwitch = self.addSwitch('s3')
    self.addLink(studentSwitch, coreSwitch, port1=1, port2=4)
    labWS = self.addHost('labWS', ip='10.0.2.3/24', defaultRoute="labWS-eth1")
    self.addLink(labWS, studentSwitch, port1=1, port2=3)
    studentPC1 = self.addHost('studentPC1', ip='10.0.2.2/24', defaultRoute="studentPC1-eth1")
    self.addLink(studentPC1, studentSwitch, port1=1, port2=2)
    #do we connect this to labWS?
    studentPC2 = self.addHost('studentPC2', ip='10.0.2.40/24', defaultRoute="studentPC2-eth1")
    self.addLink(studentPC2, studentSwitch, port1=1, port2=4)

    
    # IT Department LAN: 
    # ‘itWS’ - 10.40.3.30 
    # ‘itPC’ - 10.40.3.254 
    # all connected to ‘s4’ (itSwitch)
    itSwitch = self.addSwitch('s4')
    self.addLink(itSwitch, coreSwitch, port1=1, port2=3)
    itWS = self.addHost('itWS', ip='10.40.3.30/24', defaultRoute="itWS-eth1")
    self.addLink(itWS, itSwitch, port1=1, port2=2)
    itPC = self.addHost('itPC', ip='10.40.3.254/24', defaultRoute="itPC-eth1")
    self.addLink(itPC, itSwitch, port1=1, port2=3)


    # University Data Center: 
    # ‘examServer’ - 10.100.100.2/24
    # ‘webServer’ - 10.100.100.20
    # ‘dnsServer’  - 10.100.100.56
    # all connected to ‘s5’ (dataCenterSwitch)
    dataCenterSwitch = self.addSwitch('s5')
    self.addLink(dataCenterSwitch, coreSwitch, port1=1, port2=2)
    examServer = self.addHost('examServer', ip='10.100.100.2/24', defaultRoute="examServer-eth1")
    self.addLink(examServer, dataCenterSwitch, port1=1, port2=2)
    webServer = self.addHost('webServer', ip='10.100.100.20/24', defaultRoute="webServer-eth1")
    self.addLink(webServer, dataCenterSwitch, port1=1, port2=3)
    dnsServer = self.addHost('dnsServer', ip='10.100.100.56/24', defaultRoute="dnsServer-eth1")
    self.addLink(dnsServer, dataCenterSwitch, port1=1, port2=4)
        

    # Internet: 
    # ‘trustedPC’ - 10.0.203.6/32
    # ‘guest1’ - 10.0.198.6/32
    # ‘guest2’ - 10.0.198.10/32 
    guest1 = self.addHost('guest1', ip='10.0.198.6/32', defaultRoute="guest1-eth1")
    self.addLink(guest1, coreSwitch, port1=1, port2=5)
    guest2 = self.addHost('guest2', ip='10.0.198.10/32', defaultRoute="guest2-eth1")
    self.addLink(guest2, coreSwitch, port1=1, port2=6)
    trustedPC = self.addHost('trustedPC', ip='10.0.203.6/32', defaultRoute="trustedPC-eth1") #are these diff
    self.addLink(trustedPC, coreSwitch, port1=1, port2=7)
    #extra credit
    dServer = self.addHost('dServer', ip='10.0.203.10/32', defaultRoute="dServer-eth1") #are these diff
    self.addLink(dServer, coreSwitch, port1=1, port2=8)

    
        
        

if __name__ == '__main__':
  #This part of the script is run when the script is executed
  topo = MyTopology() #Creates a topology
  c0 = RemoteController(name='c0', controller=RemoteController, ip='127.0.0.1', port=6633) #Creates a remote controller
  net = Mininet(topo=topo, controller=c0) #Loads the topology
  #net = Mininet(topo=topo)
  net.start() #Starts mininet
  CLI(net) #Opens a command line to run commands on the simulated topology
  net.stop() #Stops mininet