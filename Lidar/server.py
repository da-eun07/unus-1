###### 받기 #####
## YOLO용 ####

# import Lidar.yolo_ds.detect as yolo
from socket import *
from struct import iter_unpack
import numpy as np

if (__name__ == '__main__'):

    ##### initialize #####
    serverSock = socket(AF_INET, SOCK_STREAM)
    serverSock.bind(('127.0.0.1',8080)) #본인 무선 LAN IPv4도 가능
    serverSock.listen(1)
    connectionSock, addr = serverSock.accept()
    print("접속 IP: {}".format(str(addr)))

    ## 클라이언트로부터 메세지 한번 받기 ##
    data = connectionSock.recv(1024)
    print("IP{}의 message: {}".format(str(addr), data))

    uvR=np.array([])
    dis_detected=0
    buffer=np.array([])  # 버퍼 역할

    #=======서버 확인 끝=============본 통신 시작============
    # 수신 반복횟수 측정
    count = 0
    while True:
        #데이터 수신
        data = connectionSock.recv(3000) #Fix me

        #데이터 확인
        for y in iter_unpack('HHH', data):  # get u, v, r

            if y[0] == 65531 :    # 1) start
                count+=1
                j=0
            elif y[0] == 65532 :     # 3-1) criteria - Detected
                print("{}th Criteria : Detected".format(count))
                dis_detected = round(y[2]*0.4)

            elif y[0] == 65533 :     # 3-2) criteria - none
                print("{}th Criteria : Nothing".format(count))
                dis_detected = 0
            
            elif y[0] == 65534 :    # 4) finish
                uvR = buffer
                buffer = np.array([])
                print("mean value / u = {}, v = {}, R = {}".format(np.nanmean(uvR[:][0]), np.nanmean(uvR[:][1]), np.nanmean(uvR[:][2])))
                print("통신, 데이터 개수 {}개!".format(count,uvR.size//2))
                

            else :  #2) u, v, R data
                u_converted = round(y[0]*0.01)
                v_converted = round(y[1]*0.0075)
                R_converted = round(y[2]*0.4)
                buffer = np.append(buffer,np.array([u_converted, v_converted, R_converted]))
            
        
    

    ### 본 통신 끝 ####
    data = connectionSock.recv(1024)
    print(data.decode("utf-8"))
    print("Complete sending message")
    





    # data = connectionSock.recv(1024)
    # if data == "Start" :
    #     array=np.array([])
    #     print("Hello from server")
    # elif data :
    #     array = np.append(array, data)
    # elif data == "Finish" :
    #     store = array.reshape(2,-1)
    #     store[0] = store*4 #distance
    #     store[1] = store*0.36 #angle
    #     print("IP{}의 len(r): {}".format(str(addr), len(store[0])))
    
    # opt_yolo = yolo.parse_opt()
    # for pix in yolo.shoot(opt_yolo):
    #     print(pix)


