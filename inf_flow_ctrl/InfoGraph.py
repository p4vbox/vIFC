from events import EventType

from events.PacketEvent import PacketEvent

from InfoNode import InfoNode

class InfoGraph():

    def __init__(self):
        self.nodes = []
        self.edges = set()

    def add_node(self, node_name):
        for n in self.nodes:
            if n.name == node_name:
                return False

        new_node = InfoNode(node_name)
        self.nodes.append(new_node)
        return True

    def __add_edge(self, src_node_name, dst_node_name):
        edge = (src_node_name, dst_node_name)
        self.edges.add(edge)
        return True

    def add_event(self, event):
        src_node = False
        dst_node = False
        for n in self.nodes:
            if n.name == event.src:
                src_node = n
            if n.name == event.dst:
                dst_node = n

        if src_node == False or dst_node == False:
            return False

        if event.type == EventType.PACKET_EVENT:
            for n in self.nodes:
                if n is not src_node and event.packetOut in n.packetOutArrivedList:
                    self.__add_edge(n.name, src_node.name)
                    src_node.packetOutArrivedList.add(event.packetOut)

            self.__add_edge(src_node.name, dst_node.name)
            dst_node.packetOutArrivedList.add(event.packetOut)

    def existInfoFlow(self, src_node_name, dst_node_name):
        src_node = False
        dst_node = False
        for n in self.nodes:
            if n.name == src_node_name:
                src_node = n
            if n.name == dst_node_name:
                dst_node = n

        if src_node == False or dst_node == False:
            return False

        open = [src_node.name]
        closed = set()
        while len(open) > 0:
            node = open[0]
            open.pop(0)
            closed.add(node)

            for src, dst in self.edges:
                if(src == node and dst not in closed):
                    if dst == dst_node.name:
                        return True
                    open.append(dst)

        return False

    #----------------------------- Debug Methods -----------------------------#
    def print_nodes(self):
        for n in self.nodes:
            print n.name + ":"
            print n.packetOutArrivedList
            print "\n"

    def print_edges(self):
        for e in self.edges:
            print e
