import wideq
from wideq_ac import *
import time
import datetime


def main():
    
    ac = WideqAC()
    device_list = ac.ls()
    device_id = device_list[0]
    print(device_id)
    while True:
        try:
            ac.turn(device_id, 'on')

        except wideq.core.NotConnectedError:
            time.sleep(900)
            continue

        ac.set_vert_swing(device_id, 'ONE')

        ac_info = ac.return_ac_info(device_id)

        first_time_start = True
        day_time = datetime.datetime.now()
        # different settings for day and night

        # for day 
        if (day_time.hour >= 7 and day_time.hour <= 22):
            
            if (ac_info[1] < 24 and first_time_start):
                ac.set_temp(device_id, '24')
                ac.fan_speed(device_id, 'NATURE')
                ac_info[1] = '24'
                first_time_start = False
        
            temp_diff = int(float(ac_info[0])) - int(ac_info[1])

            if temp_diff >= 4:
                ac.turn_jet_mode(device_id, 'HIM_COOL')
                time.sleep(900)

                ac.set_temp(device_id, '24')
                ac.set_vert_swing(device_id, 'ONE')
                ac.fan_speed(device_id, 'HIGH')

            elif temp_diff == 3:
                if ac_info[2] != 'HIGH':
                    ac.fan_speed(device_id, 'HIGH')
                    time.sleep(1800)
                else:
                    ac.set_temp(device_id, int(ac_info[1]) - 1)
                    ac.fan_speed(device_id, 'MID')
                    time.sleep(3600)

            elif temp_diff == 2:
                ac.fan_speed(device_id, 'NATURE')
                time.sleep(3600)

            elif temp_diff == 1:
                ac.fan_speed(device_id, 'LOW')
                time.sleep(3600)
            elif temp_diff < 1:
                ac.set_temp(device_id, int(ac_info[1]) + 1)
                ac.fan_speed(device_id, 'LOW')
                time.sleep(3600)


        # for night
        else:
            if (ac_info[1] < 24 and first_time_start):
                ac.set_temp(device_id, '24')
                ac.fan_speed(device_id, 'NATURE')
                ac_info[1] = '24'
                first_time_start = False

            #temperature difference between room temp and configured temp
            temp_diff = int(float(ac_info[0])) - int(ac_info[1])

            if temp_diff >= 4:
                ac.turn_jet_mode(device_id, 'HIM_COOL')
                time.sleep(600)
                ac.set_temp(device_id, '24')
                ac.fan_speed(device_id, 'NATURE')
                ac.set_vert_swing(device_id, 'ONE')

            elif temp_diff == 3:
                if ac_info[2] != 'HIGH':
                    ac.fan_speed(device_id, 'HIGH')
                    time.sleep(1800)
                else:
                    ac.set_temp(device_id, int(ac_info[1]) - 1)
                    ac.fan_speed(device_id, 'NATURE')
                    time.sleep(3600)

            elif temp_diff == 2:
                ac.fan_speed(device_id, 'NATURE')
                time.sleep(1800)
                    
            elif temp_diff < 2:
                ac.fan_speed(device_id, 'LOW_MID')
                time.sleep(1800)
        

if __name__ == "__main__":
    main()