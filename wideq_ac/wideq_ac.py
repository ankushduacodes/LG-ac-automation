import wideq
import json
import sys
import time


state_file = "ac_state.json"


Feature has yet to be added to wideq release version
JET_ARG = {

    "OFF" : wideq.ACJetMode.OFF,
    "COOL_JET" : wideq.ACJetMode.COOL,
    "HEAT_JET" : wideq.ACJetMode.HEAT,
    "DRY_JET" : wideq.ACJetMode.DRY,
    "HIM_COOL" : wideq.ACJetMode.HIMALAYAS
}


SPEED_ARG = {

    'LOW' : wideq.ACFanSpeed.LOW,
    'LOW_MID' : wideq.ACFanSpeed.LOW_MID,
    'MID' : wideq.ACFanSpeed.MID,
    'MID_HIGH' : wideq.ACFanSpeed.MID_HIGH,
    'HIGH' : wideq.ACFanSpeed.HIGH,
    'NATURE' : wideq.ACFanSpeed.NATURE
}


VERT_SWING_ARG = {

    'OFF' : wideq.ACVSwingMode.OFF,
    'ONE' : wideq.ACVSwingMode.ONE,
    'TWO' : wideq.ACVSwingMode.TWO,
    'THREE' : wideq.ACVSwingMode.THREE,
    'FOUR' : wideq.ACVSwingMode.FOUR,
    'FIVE' : wideq.ACVSwingMode.FIVE,
    'SIX' : wideq.ACVSwingMode.SIX,
    'ALL' : wideq.ACVSwingMode.ALL
}


MODE_ARG = {

    'COOL' : wideq.ACMode.COOL,
    'DRY' : wideq.ACMode.DRY,
    'FAN' : wideq.ACMode.FAN,
    'AI' : wideq.ACMode.AI,
    'HEAT' : wideq.ACMode.HEAT,
    'AIRCLEAN' : wideq.ACMode.AIRCLEAN,
    'ACO' : wideq.ACMode.ACO,
    'AROMA' : wideq.ACMode.AROMA,
    'ENERGY_SAVING' : wideq.ACMode.ENERGY_SAVING
}


HORZ_SWING_ARG = {

    'OFF' : wideq.ACHSwingMode.OFF,
    'ONE' : wideq.ACHSwingMode.ONE,
    'TWO' : wideq.ACHSwingMode.TWO,
    'THREE' : wideq.ACHSwingMode.THREE,
    'FOUR' : wideq.ACHSwingMode.FOUR,
    'FIVE' : wideq.ACHSwingMode.FIVE,
    'LEFT_HALF' : wideq.ACHSwingMode.LEFT_HALF,
    'RIGHT_HALF' : wideq.ACHSwingMode.RIGHT_HALF,
    'ALL' : wideq.ACHSwingMode.ALL
}



class UserError(Exception):

    """A user-visible command-line error.
    """

    def __init__(self, msg):
        self.msg = msg



class WideqAuthentication:

    def __init__(self, gateway):
        self.gateway = gateway

    
    def authenticate(self):
        login_url = self.gateway.oauth_url()
        print('Log in here:')
        print(login_url)
        print('Then paste the URL where the browser is redirected:')
        callback_url = input()
        return wideq.Auth.from_url(self.gateway, callback_url)



class WideqAC:

    def __init__(self, country = wideq.DEFAULT_COUNTRY, language = wideq.DEFAULT_LANGUAGE):

        try:
            with open(state_file) as jsonfile:
                self.state = json.load(jsonfile)
        except IOError:
            self.state = {}
        
        self.client = wideq.Client.load(self.state)
        
        self.client._country = country
        self.client._language = language

        if not self.client._auth:
            wideq_auth = WideqAuthentication(self.client.gateway)
            self.client._auth = wideq_auth.authenticate()

        self.state = self.client.dump()
        with open(state_file, mode= 'w+') as f:
            json.dump(self.state, f)


    def _force_device(self, device_id):

        device = self.client.get_device(device_id)

        if not device:
            raise UserError('device "{}" not found'.format(device_id))

        return device


    def ls(self):

        retry_count = 5
        while retry_count:
            try:
                ac_device_list = []
                for device in self.client.devices:
                    if (device.type.name == 'AC'):
                        ac_device_list.append(device.id)

                return ac_device_list

            except wideq.NotLoggedInError:
                time.sleep(10)
                retry_count -= 1
                self.client.refresh()

        else:
            print("Session could not be extablished") 
            sys.exit(0)


    def turn(self, device_id, on_off):

        ac = wideq.ACDevice(self.client, self._force_device(device_id))
        
        retry_count = 5
        while retry_count:
            try:
                ac.monitor_start()
                state = ac.poll()
                if (state):
                    if (not state.is_on and on_off == 'on'):
                        ac.set_on(True)
                    elif(state.is_on and on_off == 'off'):
                        ac.set_on(False)
                    break

                time.sleep(10)

            except wideq.NotLoggedInError:
                time.sleep(10)
                retry_count -= 1
                self.client.refresh()
            
        else:
            print("Session could not be extablished") 
            sys.exit(0)


    def set_temp(self, device_id, temp):

        ac = wideq.ACDevice(self.client, self._force_device(device_id))

        retry_count = 5
        while retry_count:
            try:
                ac.set_celsius(int(temp))
                break

            except wideq.NotLoggedInError:
                time.sleep(10)
                retry_count -= 1
                self.client.refresh()

        else:
            print("Session could not be extablished") 
            sys.exit(0)


    def fan_speed(self, device_id, speed):

        ac = wideq.ACDevice(self.client, self._force_device(device_id))

        retry_count = 5
        while retry_count:
            try:
                selected_speed = SPEED_ARG.get(speed.upper(), 'N/A')

                if (selected_speed == 'N/A'):
                    print('INVALID SPEED!...')
                    print('Please select one of ' + ', '.join(SPEED_ARG))
                    return False

                ac.set_fan_speed(selected_speed)
                break
            
            except wideq.NotLoggedInError:
                time.sleep(10)
                retry_count -= 1
                self.client.refresh()

        else:
            print("Session could not be extablished") 
            sys.exit(0)


    def set_ac_mode(self, device_id, mode):

        ac = wideq.ACDevice(self.client, self._force_device(device_id))

        retry_count = 5
        while retry_count:
            try:
                selected_mode = MODE_ARG.get(mode.upper(), 'N/A')

                if (selected_mode == 'N/A'):
                    print('INVALID MODE!...')
                    print('Please select one of ' + ', '.join(MODE_ARG))
                    return False

                ac.set_mode(selected_mode)
                break

            except wideq.NotLoggedInError:
                time.sleep(10)
                retry_count -= 1
                self.client.refresh()

        else:
            print("Session could not be extablished") 
            sys.exit(0)


    def set_vert_swing(self, device_id, swing_mode):

        ac = wideq.ACDevice(self.client, self._force_device(device_id))

        retry_count = 5
        while retry_count:
            try:
                selected_swing_mode = VERT_SWING_ARG.get(swing_mode.upper(), 'N/A')

                if (selected_swing_mode == 'N/A'):
                    print('INVALID MODE!...')
                    print('Please select one of ' + ', '.join(VERT_SWING_ARG))
                    return False
                
                ac.set_vert_swing(selected_swing_mode)
                break

            except wideq.NotLoggedInError:
                time.sleep(10)
                retry_count -= 1
                self.client.refresh()

        else:
            print("Session could not be extablished") 
            sys.exit(0)


    def set_horz_swing(self, device_id, swing_mode):

        ac = wideq.ACDevice(self.client, self._force_device(device_id))

        retry_count = 5
        while retry_count:
            try:
                selected_swing_mode = HORZ_SWING_ARG.get(swing_mode.upper(), 'N/A')

                if (selected_swing_mode == 'N/A'):
                    print('INVALID MODE!...')
                    print('Please select one of ' + ', '.join(HORZ_SWING_ARG))
                    return False
                
                ac.set_horz_swing(selected_swing_mode)
                break

            except wideq.NotLoggedInError:
                time.sleep(10)
                retry_count -= 1
                self.client.refresh()

        else:
            print("Session could not be extablished") 
            sys.exit(0)



    def turn_jet_mode(self, device_id, jet_opt):

        ac = wideq.ACDevice(self.client, self._force_device(device_id))

        retry_count = 5
        while retry_count:
            try:
                selected_jet_mode = JET_ARG.get(jet_opt.upper(), 'N/A')

                if (selected_jet_mode == 'N/A'):
                    print('INVALID MODE!...')
                    print('Please select one of ' + ', '.join(JET_ARG))
                    return False

                ac.set_jet_mode(selected_jet_mode)
                break

            except wideq.NotLoggedInError:
                time.sleep(10)
                retry_count -= 1
                self.client.refresh()

        else:
            print("Session could not be extablished") 
            sys.exit(0)


    def return_ac_info(self, device_id):

        ac = wideq.ACDevice(self.client, self._force_device(device_id))

        retry_count = 10
        while retry_count:
            try:
                ac.monitor_start()
                state = ac.poll()
                if state:
                    return [state.temp_cur_c, state.temp_cfg_c, state.fan_speed.name]

                time.sleep(10)

            except wideq.NotLoggedInError:
                time.sleep(10)
                retry_count -= 1
                self.client.refresh()

        else:
            print("Session could not be extablished") 
            sys.exit(0)
