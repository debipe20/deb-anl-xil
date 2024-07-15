import socket


def main():
    
hostIp = "192.168.26.150"
port = 60001
hostAddress = (hostIp, port)

testSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
testSocket.bind(hostAddress)


while True:
    
    data, address = testSocket.recvfrom(2048)
    
    print(data)

if __name__ == "__main__":
    main()
