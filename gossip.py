from MemberPackage import *
import socket
import time
from threading import Thread, Lock
import sys
from copy import deepcopy
import random
import json

class NodeConfig(object):

    def __init__(self, id, aliveTime):
        self.id = id
        self.aliveTime = aliveTime # how long we want to check for alive status

    @staticmethod
    def getConfig(filename):
        memberInfoList = {}
        with open(filename, "r") as ins:
            for line in ins:
                line = line.strip()
                line = line.split()
                memberInfoList[int(line[0])] = MemberInfo(
                    int(line[0]),
                    line[1],
                    int(line[2])
                )
        return memberInfoList


class UDPSender(Thread):

    def __init__(self, socket):
        # it will be another thread
        Thread.__init__(self)
        self.socket = socket
        self.memberListAccess = None
        self.memberList = None
        self.config = None

    def run(self):
        while True:
            myMemberList = None
            myId = self.config.id

            # lock to access the memberlist
            with self.memberListAccess:
                # check if any member is not alive now
                curTime = time.time()
                aliveTime = self.config.aliveTime

                for id in self.memberList:
                    if id != myId:
                        member = self.memberList[id]
                        elapse = curTime - member.timestamp
                        if elapse > aliveTime:
                            member.updateStatus()

                myMember = self.memberList.getMember(myId)
                myMember.increaseHeartbeat()

                # deep copy here
                myMemberList = deepcopy(self.memberList)

            # choose a member to send, not itself
            dataToSend = myMemberList.toJson()

            potentialMemberInfos = [myMemberList[key].memberInfo for key in myMemberList]

            numSent = 0
            requiredSent = 2

            while True:
                mychoice = random.choice(potentialMemberInfos)
                # dont want to send itself
                if mychoice.id != myId:
                    self.send(mychoice, dataToSend)
                    numSent += 1
                    if numSent == requiredSent:
                        break

            time.sleep(self.config.aliveTime)

    def send(self, memberInfo, message):
        # send data to (ip, port) with message
        self.socket.sendto(message, (memberInfo.ip, memberInfo.port))
        print("Sent gossip-based membership to node %d" % memberInfo.id)

class UDPListener(Thread):
    """

    """
    def __init__(self, threadID, threadName, socket, mtu = 512):
        # set the socket for the node that it will use
        Thread.__init__(self)
        self.threadID = threadID
        self.threadName = threadName
        self.socket = socket
        self.mtu = mtu
        self.memberListAccess = None
        self.memberList = None

    def updateMemberList(self, data):
        # get current time stamp
        timestamp = time.time()
        with self.memberListAccess:
            for myMess in data:
                newHeartBeat = myMess["heartbeat"]
                newId = myMess["id"]
                memberEntry = self.memberList.getMember(newId)
                memberEntry.update(newHeartBeat, timestamp)

    def run(self):
        print("Thread %d with name '%s' is listening." %
            (self.threadID, self.threadName))
        while True:
            mess, addr = self.socket.recvfrom(self.mtu)
            data = json.loads(mess)
            self.updateMemberList(data)

class NodeRunner(object):

    def __init__(self, memberInfo):
        self.memberInfo = memberInfo
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((memberInfo.ip, memberInfo.port))
        self.listener = UDPListener(1, "Listener Thread", self.socket) #listen the new udp packge
        self.sender = UDPSender(self.socket) # responsible for sending data
        self.config = None # Configuration of this node
        self.memberList = MemberList() # All Member Info in this node
        self.memberListAccess = None
        self.setup()

    def setup(self):
        """
            - setup the lock for listener and sender
            - both listener and sender can share access to memberList
        """
        self.memberListAccess = Lock()
        self.listener.memberListAccess = self.memberListAccess
        self.sender.memberListAccess = self.memberListAccess

        self.listener.memberList = self.memberList
        self.sender.memberList = self.memberList


    def setupConfig(self, nodeConfig):
        self.config = nodeConfig # set the config for this node
        self.sender.config = nodeConfig # give sender acces to the config

    def setupMemberList(self, memberListInfo):
        """
            We assume memberListInfo is a dict
            id -> MemberInfo
            We add the potential memberList to this list
        """
        timestamp = time.time()
        for id, memberInfo in memberListInfo.items():
            self.memberList.addMember(memberInfo, timestamp)

    def run(self):
        try:
            print("Node %d is running." % (self.memberInfo.id))
            self.listener.start()
            self.sender.start()

            self.listener.join()
            self.sender.start()
        except:
            print("Could not start the new thread")

if __name__ == '__main__':
    myId = int(sys.argv[1])
    configFileName = sys.argv[2]
    myConfig = NodeConfig(myId, int(sys.argv[3]))
    myMemberInfoList = NodeConfig.getConfig(configFileName)
    myMemberInfo = myMemberInfoList[myId]
    myNode = NodeRunner(myMemberInfo)
    myNode.setupConfig(myConfig)
    myNode.setupMemberList(myMemberInfoList)
    myNode.run()
