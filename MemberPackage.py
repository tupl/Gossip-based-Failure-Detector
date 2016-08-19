from enum import Enum
import json

class MemberStatus(Enum):
	Alive = 0
	Suspected = 1
	Died = 2

class MemberInfo(object):

	def __init__(self, id, ip, port):
		self.id = id
		self.ip = ip
		self.port = port

	def __repr__(self):
		return str(self)

	def __str__(self):
		return "(MemberInfo %s - %s - %s)" % (str(self.id), self.ip, str(self.port))

	def __eq__(self, other):
		if isinstance(other, MemberInfo):
			return self.id == other.id and \
				self.ip == other.ip and \
				self.port == other.port
		return NotImplemented

class MemberListEntry(object):

	def __init__(self, memberInfo, status = MemberStatus.Alive,
		heartbeat = 0, timestamp = 0):
		self.memberInfo = memberInfo
		self.heartbeat = heartbeat
		self.timestamp = timestamp
		self.status = status

	def increaseHeartbeat(self):
		self.heartbeat += 1

	def updateStatus(self):
		if self.status == MemberStatus.Alive:
			self.status = MemberStatus.Suspected
			print("Node %d is suspected now." % self.memberInfo.id)
		elif self.status == MemberStatus.Suspected:
			self.status = MemberStatus.Died
			print("Node %d is dead now." % self.memberInfo.id)

	def update(self, heartbeat, timestamp):
		# if the heartbeat is higher, we update  with new timestamp
		if heartbeat > self.heartbeat:
			self.heartbeat = heartbeat
			self.timestamp = timestamp
			if self.status != MemberStatus.Alive:
				print("Node %d is alive now." % self.memberInfo.id)

			self.status = MemberStatus.Alive

	def __repr__(self):
		return str(self)

	def __str__(self):
		return str(self.memberInfo) + " _ " + str(self.status) + " _ " + \
			str(self.heartbeat) + " _ " + str(self.timestamp)

	def __eq__(self, other):
		# equal if same member
		if isinstance(other, MemberListEntry):
			return self.node == other.node
		return NotImplemented

class MemberList(object):

	def __init__(self):
		self.tables = {}

	def __iter__(self):
		return self.tables.__iter__()

	def __getitem__(self, key):
		return self.tables[key]

	def __len__(self):
		return len(self.tables)

	def __str__(self):
		tmp = ""
		for key in self.tables:
			member = self.tables[key]
			tmp += str(member) + "\n"
		return tmp

	def __repr__(self):
		return str(self)

	def toJson(self, K = -1):
		# K = -1 mean all of member
		grp = []
		if K == -1:
			for id in self.tables:
				grp.append({
						"id": id,
						"heartbeat": self.tables[id].heartbeat
					})
			return json.dumps(grp)
		return None

	def getMember(self, id):
		if id in self.tables:
			return self.tables[id]
		return None

	def addMember(self, memberInfo, timestamp):
		# add new member, set the time we add
		if memberInfo.id not in self.tables:
			self.tables[memberInfo.id] = MemberListEntry(memberInfo,
				timestamp = timestamp)

if __name__ == '__main__':
	memberInfo1 = MemberInfo(0, "localhost", 50)
	memberInfo2 = MemberInfo(1, "localhost", 100)
	memberInfo3 = MemberInfo(2, "localhost", 150)

	memberList = MemberList()
	memberList.addMember(memberInfo1, 0)
	memberList.addMember(memberInfo2, 0)
	memberList.addMember(memberInfo3, 0)

	print(memberList.toJson())
