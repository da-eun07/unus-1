import matplotlib.pyplot as plt
import numpy as np
import time
from pyrplidar import PyRPlidar

PortNum="/dev/tty.usbserial-114430"   # Fix Me
MAX_DATA = 1500   # 2000마다 데이터 띄움
DIS_UP = 3000   # 1000mm
DIS_DOWN = 150
ANGLE_UP = 10
ANGLE_DOWN = -10
ROT = 82
RANGE = 10 #각도 범위
DIST = 2500 #거리
DIS_MIN = 150

#=== variables ===
ang=np.array([0])
dis=np.array([0])
#distance, angle은 라이다에서 오는 raw data

plt.ion()
fig = plt.figure(num="lidar", figsize=(5,5))
ax = fig.add_subplot(projection='polar')
plt.title('Graph Title', fontweight='bold', fontsize=20)
plt.ylim(0,DIS_UP)
c = ax.scatter(ang,dis, c='red', s=5)

#=== Lidar Initialize ===
lidar = PyRPlidar()
lidar.connect(port=PortNum, baudrate=115200, timeout=3) 
lidar.set_motor_pwm(660)
scan_generator = lidar.start_scan_express(3)

for scan in scan_generator():
    
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
        # print(rtheta)

        #=== data masking ===
        for i in range(rtheta.shape[0]):
            if (ang[i]+ROT>=-RANGE+180) and (ang[i]+ROT<=RANGE+180) and (rtheta[i,1]<=DIST) and (rtheta[i,1]>=DIS_MIN):
                obstacle.append(rtheta[i,:])

        # print(rtheta)   
        print(obstacle)

        if len(obstacle) <= 5:
            print("Nothing")        
        else:
            print("Detected")

        ang=np.array([0])
        dis=np.array([0])
        

    else :
        ang = np.append(ang, angle)
        dis = np.append(dis, distance)