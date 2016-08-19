# Gossip-based-Failure-Detector

This is a fun project to implement gossip-based failture detector where its node information
in the network is put in a configuration file. The underlying communication is udp. For an interval
a node will send its membership table including id, heartbeat to other node in the network. If it does not
hear it back for maximum amout of time (configurable), it will move that node to suspected state. If it happens again,
it will mark this node as dead node. The basic implementation is two threads that shared access to the table through
a mutex (lock). One thread is responsible for listening to any udp coming and another thread is responsible for sending
its table to other node. If there is a new table coming, it simply updates its own table. The table is constructed using
json.

## Future features (Maybe if I have time)
- set duration to mark a node as failure node
- set the number of nodes to send its table, not all of them

## Language

- python 3.5 (threading, json, sys)
