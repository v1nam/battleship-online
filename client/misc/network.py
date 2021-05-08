import json
import socket


class Network:
    server = ""
    port = 1234
    address = server, port

    def __init__(
        self,
        sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM),
    ):
        self.client = sock
        self.client.connect(self.address)

    def receive(self):
        buff = b""
        n = int.from_bytes(self.client.recv(4)[:4], "big")
        while n > 0:
            b = self.client.recv(n)
            buff += b
            n -= len(b)
        return json.loads(buff.decode())

    def send(self, *data):
        if len(data) == 1:
            data = data[0]
        final_data = b""
        data = json.dumps(data)
        final_data += len(data).to_bytes(4, "big")
        final_data += data.encode()
        try:
            self.client.send(final_data)
        except:
            pass

    def close(self):
        self.client.close()
