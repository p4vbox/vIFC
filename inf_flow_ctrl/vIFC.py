from events import EventType

from InfoGraph import InfoGraph

infoGraph = InfoGraph()

# from lower to higher priority
appPrioRank = ["App1", "App2"]

def verifyEvent(event):
    global infoGraph
    # add event
    if event.type == EventType.PACKET_EVENT:
        infoGraph.add_node(event.src)
        infoGraph.add_node(event.dst)
        infoGraph.add_event(event)
   
    # for debug purposes
    infoGraph.print_nodes()
    infoGraph.print_edges()

    # check for violations
    for low_prio in range(0, len(appPrioRank)):
        for high_prio in range(low_prio + 1, len(appPrioRank)):
            if infoGraph.existInfoFlow(appPrioRank[low_prio], appPrioRank[high_prio]):
                return False
    
    return True
