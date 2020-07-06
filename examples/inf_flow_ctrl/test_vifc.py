import inf_flow_ctrl.vIFC as vIFC

from inf_flow_ctrl.events.PacketEvent import PacketEvent

import hashlib

def main():

    maliciousPacket = hashlib.sha256(str("MaliciousPacket")).hexdigest()

    if vIFC.verifyEvent(PacketEvent("App1", "Switch1", maliciousPacket)) == False:
        print "Information flow violation detected"
    else:
        print "Event ok."
    
    if vIFC.verifyEvent(PacketEvent("Switch2", "App2", maliciousPacket)) == False:
        print "Information flow violation detected"
    else:
        print "Event ok."

if __name__ == "__main__":
    main()
