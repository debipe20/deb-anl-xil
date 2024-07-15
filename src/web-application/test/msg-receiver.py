import socket
import struct

    
hostIp = "192.168.26.101"
port = 1022
hostAddress = (hostIp, port)

testSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
testSocket.bind(hostAddress)


while True:
    
    data, address = testSocket.recvfrom(80)

    Dyno_Ctrl_Grade_Cmd, VUT_Ctrl_ACC_AxlTrq_Cmd, VUT_Ctrl_ACC_BrkDecel_Cmd, VUT_Ctrl_ACC_Accel_Cmd,  VUT_Ctrl_ACC_Accel_Actv,  VUT_Ctrl_Trns_Gear_Actv,  VUT_Ctrl_ACC_AxlTrq_Actv, VUT_Ctrl_LongCtrl_Method, VUT_Ctrl_ACC_BrkDecel_Actv, VUT_Ctrl_Trns_TrqCnvCl_Cmd = struct.unpack("dddddddddd", data)
    

    print(f"Decoded data of the following fields are ': {Dyno_Ctrl_Grade_Cmd, VUT_Ctrl_ACC_Accel_Cmd, VUT_Ctrl_Trns_TrqCnvCl_Cmd}")   

    print(Dyno_Ctrl_Grade_Cmd)

testSocket.close()

