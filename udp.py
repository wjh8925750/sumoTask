import socket


class UDP_Server:
    def __init__(self, port, queue):
        self.port = port
        self.udpSerSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSerSock.bind(('', self.port))
        self.queue = queue

    def run(self):
        BUFSIZE = 32 * 1024
        while True:
            data, addr = self.udpSerSock.recvfrom(BUFSIZE)
            #print("Receive from %s:%s" % addr)
            #print("Msg: ", data)
            self.queue.put(data)