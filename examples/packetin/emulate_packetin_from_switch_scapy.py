from scapy.all import *
from config import ServerConfig
import sys

eth_src="00:15:4d:13:61:49"
ip_src="10.0.0.1"

eth_dst="00:15:4d:13:61:07"
ip_dst="10.0.0.1"

vlan_id=1

dst_iface=ServerConfig.PACKETIN_IFACE

class Metadata(Packet):

	name = "MetadataPacket"
	fields_desc = [XByteField("metadata_id", 1),
                   XByteField("port", 1)]

metadata = Metadata(metadata_id=2, port=1)
eth = Ether(dst=eth_dst, src=eth_src)
vlan = Dot1Q(vlan=vlan_id)
ip = IP(src=ip_src, dst=ip_dst)
icmp = ICMP()

ServerConfig.print_debug("Preparing packet-in from {} ({}) => {} ({}) type IPv4/ICMP (vlan={}) over iface {}".
							format(eth_src, ip_src, eth_dst, ip_dst, vlan_id, dst_iface))
packet = metadata/eth/vlan/ip/icmp
sendp(packet, iface=dst_iface)

