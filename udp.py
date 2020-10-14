import socket



class UDP_Client:
    def __init__(self, ADDR_List, queue):
        self.ADDR_List = ADDR_List
        self.udpCliSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.queue = queue


    def send(self, sendinfo):
        self.udpCliSock.sendto(sendinfo, self.ADDR_List)

    def run(self):
        while True:
            if not self.queue.empty():
                sendinfo = self.queue.get()
                if isinstance(sendinfo, str):
                    self.send(str(sendinfo).encode())
                else:
                    self.send(sendinfo)










class UDP_Server:

    def __init__(self, port, queue):
        print("2、udp服务器初始化")
        self.port = port
        self.udpSerSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSerSock.bind(('', self.port))
        print("        2.1、udp服务器本地端口号：", self.port)
        self.queue = queue
        print("        2.2、初始化接收消息队列，当前queue.qsize：", self.queue.qsize())

    def run(self):
        print("        4.1、udp server run")
        BUFSIZE = 32 * 1024
        while True:
            data, addr = self.udpSerSock.recvfrom(BUFSIZE)
            print("Receive signal color from %s:%s" % addr)
            #print("Msg: ", data)
            self.queue.put(data)