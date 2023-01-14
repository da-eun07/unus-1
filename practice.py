import Lidar.li_util_func as li_util

if (__name__ == '__main__'):

    env = li_util.libLIDAR('COM7') ### FIX ME
    env.init()

    env.getState()

    count = 0

    for scan in env.scanning():
        count += 1
        print('%d: Got %d measurements' %(count,  len(scan)))

        if count == 10:
            env.stop()
            break