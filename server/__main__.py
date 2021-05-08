from server.network import Network

print("Started server...")
try:
    Network()
except KeyboardInterrupt:
    print("Interrupt signal received... Closing server")
    exit()
