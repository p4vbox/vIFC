import EventType

class PacketEvent():
    
    def __init__(self, src, dst, packet_hash):
        self.type = EventType.PACKET_EVENT
        self.src = src
        self.dst = dst
        self.packetOut = packet_hash
