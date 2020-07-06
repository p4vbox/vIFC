import hashlib

from server.connections import *
from server.connections.ConnectionArray import *

class Hash():
	@staticmethod
	def pktin_toHash():
		user_name = "admin"
		pkt_in = ConnectionArray.getPacketInFromBuffer(user_name)
		if str(pkt_in) != "False":
			print "Getting packet-in from buffer and generating hash"
           		hash = hashlib.sha256(str(pkt_in)).hexdigest()
            		dict = {}
            		dict.update({str(pkt_in):hash})
            		print(dict)
