###### 쏘기 #####
## 라이다용 ####

from socket import *
from struct import pack, iter_unpack
import matplotlib.pyplot as plt
import numpy as np
import time
from pyrplidar import PyRPlidar

PortNum= '/dev/tty.usbserial-111440' ### Fix Me
MAX_DATA = 2000   # 2000마다 데이터 띄움
DIS_UP = 3000   # 1000mm
DIS_DOWN = 150
ANGLE_UP = 20
ANGLE_DOWN = -10
ROT = 82
RANGE = 10 #각도 범위
DIST = 1500 #거리
DIS_MIN = 150
count = 0

criteria = 65533
dis_detected = 65533

# LiDAR & Camera Fusion====================================================
def thetar2pix(rtheta):   # return pixel(u,v) and distance

    #Filtering Data-----------------------------------------------------------

    thetamin = 45; thetamax = 315  #FOV [Degrees]
    umax = 640; vmax = 480 #frame
    rmin = DIS_DOWN; rmax = DIS_UP  #Distance [mm] 

    for i in range(rtheta.shape[0]):
        if (rtheta[i,0] > thetamin) and (rtheta[i,0] < thetamax):
            rtheta[i,:] = rmax

    rtheta[:,0] = rtheta[:,0]*np.pi/180  #degree to radian

    for i in range(np.shape(rtheta)[0]):
        if (rtheta[i,1] < rmin) or (rtheta[i,1] >= rmax):
            rtheta[i,:] = rmax 


    #Polar -> Cartesian-------------------------------------------------------
    y_s = 0     #lidar height set to 0
    
    coor = np.zeros((rtheta.shape[0],3)) #(x*,y*,z*) [mm]
    for i in range(rtheta.shape[0]):
        if rtheta[i,0] == rmax:
            coor[i,:] = rmax
        else:
            coor[i,0] = -rtheta[i,1]*np.sin(rtheta[i,0])
            coor[i,1] = y_s
            coor[i,2] = rtheta[i,1]*np.cos(rtheta[i,0])
    
    trans_vec = [0,400,750]     #lidar to camera vector

    for i in range(3):
        coor[:,i] = coor[:,i] + trans_vec[i]    #to camera 3D space


    #Cartesian -> Pixel-------------------------------------------------------

    #1920x1080
    cam_mat1 = [[1.39697095e+03, 0.00000000e+00, 1.00983541e+03],
    [0.00000000e+00, 1.39632273e+03, 5.26933739e+02],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]]


    #640x480
    cam_mat2 = [[622.39801669,   0,         327.82995341],
    [  0,         617.28766013, 261.42463435],
    [  0,           0           , 1        ]]
    
    pix_coor = np.zeros((rtheta.shape[0],3))
    pix = np.zeros((rtheta.shape[0],2))    #pixel space

    for i in range(rtheta.shape[0]):   #(x,y,z) to (u,v)
        pix_coor[i,2] = coor[i,2]
        pix_coor[i,0] = cam_mat2[0][0]*coor[i,0] + cam_mat2[0][2]*coor[i,2]
        pix_coor[i,1] = cam_mat2[1][1]*coor[i,1] + cam_mat2[1][2]*coor[i,2]
        
        pix[i,0] = pix_coor[i,0]/pix_coor[i,2]
        pix[i,1] = pix_coor[i,1]/pix_coor[i,2]
    
    for i in range(rtheta.shape[0]):
        if pix[i,0] <= umax and pix[i,1] <= vmax and pix[i,0] >= 0 and pix[i,1] >= 0:
            pix[i,0] = round(pix[i,0],0)
            pix[i,1] = round(pix[i,1],0)
        else:
            pix [i,:] = np.nan
    
    return pix[:,0], pix[:,1], rtheta[:,1]


if (__name__ == '__main__'):

    #========= Client Initialize ========
    serverIP = "127.0.0.1" #본인 무선 LAN IPv4도 가능
    port = 8080
    clientSock = socket(AF_INET, SOCK_STREAM)
    clientSock.connect((serverIP,port))

    ## 연결되면 자동으로 뜸 ###
    print("Connected to {}:{}".format(serverIP, port))

    ## 서버로 메세지 한번 쏴주기 ##
    msg= input("Message put : ")
    clientSock.send(msg.encode("utf-8"))



    #========== Lidar Initialize =========
    lidar = PyRPlidar()
    lidar.connect(port=PortNum, baudrate=115200, timeout=3) 
    lidar.set_motor_pwm(660)
    scan_generator = lidar.start_scan_express(3)

    #=== variables ===
    ang=np.array([0])
    dis=np.array([0])

    #=== plot =======
    plt.ion()
    fig = plt.figure(figsize=(5,5))
    ax = fig.add_subplot(projection='polar')
    plt.title('Graph Title', fontweight='bold', fontsize=20)
    plt.ylim(0,DIS_UP)
    c = ax.scatter(ang,dis, c='red', s=5)

    rtheta=np.zeros((MAX_DATA,2))

    # 송신 반복횟수 측정
    count = 1

    for scan in scan_generator():
        #=== 라이다 신호 받아오기
        scan = vars(scan)
        angle = np.array(scan["angle"])
        distance = np.array(scan["distance"])
        # print("Angle= " + str(angle) + ", Distance= " + str(distance))

        present_time=time.time()

        if len(ang) > MAX_DATA :
            #=== plot update ===
            obstacle = []

            fig.canvas.flush_events()
            ax.cla()
            c = ax.scatter((ang+ROT-180)*np.pi/180,dis, c='red', s=5)
            plt.ylim(0,DIS_UP)
            plt.title('Graph Title', fontweight='bold', fontsize=20)
            plt.title("Time : " + str(time.strftime('%M:%S', time.localtime(time.time()))), loc='right', pad=20)  ## +" / Count : " +str(count)
            ax.plot(np.array([ANGLE_UP,0])*np.pi/180, [DIS_UP,0], color='b', linewidth=2, linestyle='solid') ## range bar
            ax.plot(np.array([ANGLE_DOWN,0])*np.pi/180, [DIS_UP,0], color='b', linewidth=2, linestyle='solid') ## range bar
            fig.canvas.draw()
                    
            data=np.array([(ang+ROT-180),dis])
            rtheta = data.T
            
            #=== data masking ===
            for i in range(rtheta.shape[0]):
                if (ang[i]+ROT>=-RANGE+180) and (ang[i]+ROT<=RANGE+180) and (rtheta[i,1]<=DIST) and (rtheta[i,1]>=DIS_MIN):
                    obstacle.append(rtheta[i,1])
               

            #FOR PID Control=========================================================================
            if len(obstacle) <= 5:
                criteria = 65533 #NOTHING DETECTED (LAND CHANGE X)
                dis_detected = 65533
                print(criteria)     
            else:
                criteria = 65532 #SOMETHING DETECTED (LANE CHANGE O)
                dis_detected = int(np.min(obstacle)//0.4)
                print(criteria, ' (Distance: ', dis_detected, ')')
            #=========================================================================================



            #============= rtheta to pix, rtheta =====
            u, v, R = thetar2pix(rtheta)
            


            #=======서버 확인 끝=============본 통신 시작=======
            #1) Start 신호
            x = bytearray(pack('HHH', 65531, 250, 0))

            #2) u, v, R data
            u_pac = np.zeros(u.shape[0])
            v_pac = np.zeros(u.shape[0])
            R_pac = np.zeros(u.shape[0])

            if u[0]!=None:
                pass
            else:    
                for i in range(u.shape[0]):
                    u_pac[i] = int(u[i]//0.01)
                    v_pac[i] = int(v[i]//0.0075)
                    R_pac[i] = int(R[i]//0.4)
                    x += bytearray(pack('HHH', u_pac[i], v_pac[i], R_pac[i]))

            #3) Criteria data
            # 65533 : none / 65532: detected
            x += bytearray(pack('HHH', criteria, 0, dis_detected))
            
            #4) Finish
            x += bytearray(pack('HHH', 65535, 0, 0))
    

            ########## 전송 ###########
            clientSock.send(x)

            ###내 데이터 확인용###
            if criteria==65533 :
                print("{}th Criteria : Safe".format(count))
            else :
                print("{}th Criteria : Danger".format(count))

            j=0
            for y in iter_unpack('HHH', x):
                j+=1
            print("{}th 통신".format(count))
        
            count+=1

            ang=np.array([0])
            dis=np.array([0])

        else :
            ang = np.append(ang, angle)
            dis = np.append(dis, distance)

    print("asdfasdfasdfafasdf")

    ### 본 통신 끝 ####
    clientSock.send("Finish".encode("utf-8"))


        


