# Lab 5 controller skeleton 
#
# Based on of_tutorial by James McCauley



from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class Firewall (object):
  """
  A Firewall object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

  def do_firewall (self, packet, packet_in):
    # The code in here will be executed for every packet

    def accept():
      # Write code for an accept function
      #important to include:
      #msg.actions.append(of.ofp_action_output(port=of.OFPP_NORMAL))
      msg = of.ofp_flow_mod()

      #self.match = ofp_match()
      #msg.match = of.ofp_match()
      msg.match = of.ofp_match.from_packet(packet)


      #idle_timeout of 45 seconds and a hard_timeout of 10 minutes?
      msg.idle_timeout = 45 #in seconds
      msg.hard_timeout = 600
      
      msg.actions.append(of.ofp_action_output(port=of.OFPP_NORMAL))
  
      self.connection.send(msg)
      
      print("Packet Accepted - Flow Table Installed on Switches")

    def drop():
      # Write code for a drop function
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet)
      msg.idle_timeout = 45 #in seconds
      msg.hard_timeout = 600

      msg.buffer_id = packet_in.buffer_id

      self.connection.send(msg)
      print("Packet Dropped - Flow Table Installed on Switches")

    # Write firewall code 
    #print("Example Code")

    # ip_header = packet.find('ipv4')
    ip_header = packet.find('ipv4')
    tcp_header = packet.find('tcp')
    udp_header = packet.find('udp')
    arp_header = packet.find('arp')
    icmp_header = packet.find('icmp')

    
    # if ip_header.srcip == "1.1.1.1":
    #   print "Packet is from 1.1.1.1"

    #server 10.1.1.1
    #laptop 10.1.1.2
    #Lights 10.1.2.1
    #Fridge 10.1.2.2

    # rule 1 Src IP : any, Dst IP: any, Protocol: ARP, action: accept
    if arp_header:
        self.accept(packet, packet_in)

    # rule 2 Src IP : any, Dst IP: any, Protocol: ICMP, action: accept
    if icmp_header:
       self.accept(packet, packet_in)

    # rule 3 Src Host: laptop, Dst Host : server, Protocol: TCP, action: accept
    if ip_header and tcp_header:
       if ip_header.srcip == "10.1.1.2" and ip_header.dstip == "10.1.1.1":
           self.accept(packet, packet_in)
  
    # rule 4 Src Host: server, Dst Host : laptop, Protocol: TCP, action: accept
    if ip_header and tcp_header:
       if ip_header.srcip == "10.1.1.1" and ip_header.dstip == "10.1.1.2":
           self.accept(packet, packet_in)

    # rule 5 Src Host: laptop, Dst Host : Lights, Protocol: TCP, action: accept
    if ip_header and tcp_header:
       if ip_header.srcip == "10.1.1.2" and ip_header.dstip == "10.1.2.1":
           self.accept(packet, packet_in)

    # rule 6 Src Host: Lights, Dst Host : laptop, Protocol: TCP, action: accept
    if ip_header and tcp_header:
       if ip_header.srcip == "10.1.2.1" and ip_header.dstip == "10.1.1.2":
           self.accept(packet, packet_in)

    # rule 7 Src Host: laptop, Dst Host : Fridge, Protocol: UDP, action: accept
    if ip_header and udp_header:
       if ip_header.srcip == "10.1.1.2" and ip_header.dstip == "10.1.2.2":
          self.accept(packet, packet_in)

    # rule 8 Src Host: laptop, Dst Host : server, Protocol: UDP, action: accept
    if ip_header and udp_header:
       if ip_header.srcip == "10.1.1.2" and ip_header.dstip == "10.1.2.2":
          self.accept(packet, packet_in)

    # rule 9 Src IP : any, Dst IP: any, Protocol: ANY,, action: drop
    #basically drop all other packets
    self.drop(packet, packet_in)

    # Hints:
    #
    # To check the source and destination of an IP packet, you can use
    # the header information... For example:
    #
    # ip_header = packet.find('ipv4')
    #
    # if ip_header.srcip == "1.1.1.1":
    #   print "Packet is from 1.1.1.1"
    #
    # Important Note: the "is" comparison DOES NOT work for IP address
    # comparisons in this way. You must use ==.
    #
    # To drop packets, simply omit the action .

  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    self.do_firewall(packet, packet_in)

def launch ():
  """
  Starts the components
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Firewall(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)