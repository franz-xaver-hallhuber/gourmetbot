import time
from vent import Vent


def l2c(msg):
    print("[" + time.strftime("%d/%m %H:%M:%S", time.gmtime()) + "] " + msg)


class UserNotRegisteredException(Exception):
    pass


class Flatmate:
    def __init__(self, name='', ip=None, t_id=0, int_id=0, sensor_pin=0, vent_pin=0, temperature=0, humidity=0, home=False, night=False):
        if ip is None:
            self.ip = ['']
        self.name = name
        self.tID = t_id
        self.sensorPin = sensor_pin
        self.vent = Vent(vent_pin)
        self.temperature = temperature
        self.humidity = humidity
        self.home = home
        self.night = night
        self.ip = ip
        self.notified = False
        self.intID = int_id


class Flat:
    mates = {}
    
    def __init__(self, list_of_mates):
        if len(list_of_mates) < 1:
            raise Exception('Give me a list of Inhabitants!')
        
        for mate in list_of_mates:
            self.mates[mate.name.capitalize()] = mate
    
    def get_all(self):
        return self.mates.values()
    
    def update_climate_data(self, name, temperature, humidity):
        if name.capitalize() in self.mates:
            self.mates[name.capitalize()].temperature = temperature
            self.mates[name.capitalize()].humidity = humidity
        else:
            raise UserNotRegisteredException("You're not registered!!")
        
    def update_remote_climate_data(self, internal_id, temperature, humidity):
        self.update_climate_data(self.get_name_from_internal_id(internal_id), temperature, humidity)

    def set_home(self, name, home):
        if name.capitalize() in self.mates:
            self.mates[name.capitalize()].home = home
        else:
            raise UserNotRegisteredException("You're not registered!!")
    
    def get_temp(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].temperature
        else:
            raise UserNotRegisteredException("You're not registered!!")
    
    def get_name_from_telegram_id(self, telegram_id):
        for mate in self.mates.values():
            if telegram_id == mate.tID:
                return mate.name
        raise UserNotRegisteredException("You're not registered!!")
    
    def get_name_from_internal_id(self, internal_id):
        for mate in self.mates.values():
            if internal_id == mate.intID:
                l2c("Got remote update for " + mate.name)
                return mate.name
        raise UserNotRegisteredException("You're not registered!!")
    
    def get_mate_from_telegram_id(self, telegram_id):
        for mate in self.mates.values():
            if telegram_id == mate.tID:
                return mate
        raise UserNotRegisteredException("You're not registered!!")
    
    def humidity(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].humidity
        else:
            raise UserNotRegisteredException("You're not registered!!")
    
    def set_night(self, name, night):
        if name.capitalize() in self.mates:
            self.mates[name.capitalize()].night = night
        else:
            raise UserNotRegisteredException("You're not registered!!")
    
    def get_id_from_name(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].tID
        else:
            raise UserNotRegisteredException("You're not registered!!")
    
    def get_dht_pin_nr(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].pin
        else:
            raise UserNotRegisteredException("You're not registered!!")
    
    def get_ip(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].ip
        else:
            raise UserNotRegisteredException("You're not registered!!")
    
    def home(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].home
        else:
            raise UserNotRegisteredException("You're not registered!!")
        
    def get_mate_from_name(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()]
        else:
            raise UserNotRegisteredException("You're not registered!!")
    
    def set_notified(self, name, on):
        if name.capitalize() in self.mates:
            self.mates[name.capitalize()].notified = True
        else:
            raise UserNotRegisteredException("You're not registered!!")
