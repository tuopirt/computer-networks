# Lab5 Skeleton

from pox.core import core

import pox.openflow.libopenflow_01 as of

import ipaddress

#from netaddr import IPNetwork, IPAddress

log = core.getLogger()

class Routing (object):
    
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

  def do_routing (self, packet, packet_in, port_on_switch, switch_id):
    # port_on_swtich - the port on which this packet was received
    # switch_id - the switch which received this packet
    
    # Your code here
    #accept packets
    def accept(end_port):
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet)
      msg.idle_timeout = 45 #in seconds
      msg.hard_timeout = 600
      msg.data = packet_in
      msg.actions.append(of.ofp_action_output(port=end_port))
      self.connection.send(msg)
      print("Packet accepted - Flow Table Installed on Switches")


    #drop packets
    def drop():
      msg = of.ofp_flow_mod()
      msg.match = of.ofp_match.from_packet(packet)
      msg.idle_timeout = 45 #in seconds
      msg.hard_timeout = 600
      msg.buffer_id = packet_in.buffer_id
      self.connection.send(msg)
      print("Packet Dropped - Flow Table Installed on Switches")


    #ip headers
    ip_header = packet.find('ipv4')
    tcp_header = packet.find('tcp')
    udp_header = packet.find('udp')
    icmp_header = packet.find('icmp')
    arp_header = packet.find('arp')


    #subnets
    faculty_Lan = ipaddress.ip_network('10.0.1.0/24')
    student_Lan = ipaddress.ip_network("10.0.2.0/24")
    it_Lan = ipaddress.ip_network("10.40.3.0/24")
    data_Lan = ipaddress.ip_network("10.100.100.0/24")
    #special ips
    trusted_pc = ("10.0.203.6")
    exam_server = ("10.100.100.2")
    guest_1 = ('10.0.198.6')
    guest_2 = ('10.0.198.10')
    #extra credit
    discord = ('10.0.203.10')


    #port number hash
    ports = {
        '1': { '2': 1, '3': 4, '4': 3, '5': 2, '10.0.198.6': 5, '10.0.198.10': 6, '10.0.203.6': 7, '10.0.203.10': 8 },
        '2': { '10.0.1.2': 2, '10.0.1.3': 3, '10.0.1.4': 4},              # Faculty LAN
        '3': { '10.0.2.3': 3, '10.0.2.2': 2, '10.0.2.40': 4},             # Student Housing LAN
        '4': { '10.40.3.30': 2, '10.40.3.254': 3},                        # IT Department LAN
        '5': { '10.100.100.2': 2, '10.100.100.20': 3, '10.100.100.56': 4} # University Data Center
    }
    

    # #finds where destination subnet is
    def find_dst_subnet():
      dst = None
      if guest_1 == str(ip_header.dstip):
         dst = "10.0.198.6"
      elif guest_2 == str(ip_header.dstip):
         dst = "10.0.198.10"
      elif trusted_pc == str(ip_header.dstip):
         dst = "10.0.203.6"
      elif discord == str(ip_header.dstip):
         dst = "10.0.203.10"
      elif ipaddress.ip_address(ip_header.dstip) in faculty_Lan:
        dst = "2"
      elif ipaddress.ip_address(ip_header.dstip) in student_Lan:
        dst = "3"
      elif ipaddress.ip_address(ip_header.dstip) in it_Lan:
        dst = "4"
      elif ipaddress.ip_address(ip_header.dstip) in data_Lan:
        dst = "5"
      return dst
    

    #routes within subnet
    def route_within(switch_id):
      if str(switch_id) == find_dst_subnet():
          end_port = ports[str(switch_id)].get(str(ip_header.dstip))
          accept(end_port)
          return
      else:
        end_port = 1
        accept(end_port)
        return


    if arp_header:
       accept(of.OFPP_NORMAL)
    #not core switch
    elif switch_id != 1:
       route_within(switch_id)
    #core switch
    elif switch_id == 1:
      #Rule 1: ICMP traffic is forwarded only between the Student Housing LAN, Faculty LAN and IT Department subnets or between devices that are on the same subnet.
      if ip_header and icmp_header:
          dst = find_dst_subnet()
              #student_Lan and faculty_Lan
          if ((port_on_switch == 4 and dst == "2") or 
              (port_on_switch == 1 and dst == "3") or 
              #faculty_Lan and it_Lan
              (port_on_switch == 1 and dst == "4") or 
              (port_on_switch == 3 and dst == "2") or 
              #student_Lan and it_Lan
              (port_on_switch == 4 and dst == "4") or 
              (port_on_switch == 3 and dst == "3") or
              #extra credit
              (port_on_switch == 4 and ip_header.dstip == discord) or 
              (port_on_switch == 8 and dst == "3")):

              end_port = ports[str(switch_id)].get(dst)
              accept(end_port)
              return


      #Rule 2:TCP traffic is forwarded only between the University Data Center, IT Department, Faculty LAN, Student Housing LAN, trustedPC, or between devices that are on the same subnet; however, only the Faculty LAN may access the exam server.
      if ip_header and tcp_header:
          dst = find_dst_subnet()
              #data and it
          if ((port_on_switch == 2 and dst == "4") or
              (port_on_switch == 3 and dst == "5" and ip_header.dstip != exam_server) or # only the Faculty LAN may access the exam server. ??????????????????????????
              #data and fac
              (port_on_switch == 2 and dst == "2") or
              (port_on_switch == 1 and dst == "5") or
              #data and student
              (port_on_switch == 2 and dst == "3") or
              (port_on_switch == 4 and dst == "5" and ip_header.dstip != exam_server) or
              #trusted pc
              (port_on_switch == 2 and ip_header.dstip == trusted_pc) or
              (ip_header.srcip == trusted_pc and dst == "5" and ip_header.dstip != exam_server) or

              #it and fac
              (port_on_switch == 3 and dst == "2") or
              (port_on_switch == 1 and dst == "4") or
              #it and student
              (port_on_switch == 3 and dst == "3") or
              (port_on_switch == 4 and dst == "4") or
              #trusted pc
              (port_on_switch == 3 and ip_header.dstip == trusted_pc) or
              (ip_header.srcip == trusted_pc and dst == "4") or

              #faculty and student
              (port_on_switch == 1 and dst == "3") or
              (port_on_switch == 4 and dst == "2") or
              #pc
              (port_on_switch == 1 and ip_header.dstip == trusted_pc) or
              (ip_header.srcip == trusted_pc and dst == "2") or

              #student housing and pc
              (port_on_switch == 4 and ip_header.dstip == trusted_pc) or
              (ip_header.srcip == trusted_pc and dst == "3") or

              #extra credit
              (port_on_switch == 4 and ip_header.dstip == discord) or 
              (port_on_switch == 8 and dst == "3")):
              
              end_port = ports[str(switch_id)].get(dst)
              accept(end_port)
              return


      #Rule 3: UDP traffic is forwarded only between the University Data Center, IT Department, Faculty LAN, Student Housing LAN, or between devices that are on the same subnet
      if ip_header and udp_header:
          dst = find_dst_subnet()
              #data and it
          if ((port_on_switch == 2 and dst == "4") or
              (port_on_switch == 3 and dst == "5") or
              #data and fac
              (port_on_switch == 2 and dst == "2") or
              (port_on_switch == 1 and dst == "5") or
              #data and student
              (port_on_switch == 2 and dst == "3") or
              (port_on_switch == 4 and dst == "5") or

              #it and fac
              (port_on_switch == 3 and dst == "2") or
              (port_on_switch == 1 and dst == "4") or
              #it and student
              (port_on_switch == 3 and dst == "3") or
              (port_on_switch == 4 and dst == "4") or

              #faculty and student
              (port_on_switch == 1 and dst == "3") or
              (port_on_switch == 4 and dst == "2") or
              
              #extra credit
              (port_on_switch == 4 and ip_header.dstip == discord) or 
              (port_on_switch == 8 and dst == "3")):
              
              end_port = ports[str(switch_id)].get(dst)
              accept(end_port)
              return

      #Rule 4: All other traffic should be dropped.
      drop()


  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    self.do_routing(packet, packet_in, event.port, event.dpid)

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Routing(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)