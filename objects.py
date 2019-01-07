from datetime import time
from vent import Vent


def l2c(msg):
    print("[" + time.strftime("%d/%m %H:%M:%S", time.gmtime()) + "] " + msg)


class UserNotRegisteredException(Exception):
    pass


class Flatmate:
    def __init__(self, name='', ip=[''], tID=0, intID=0, sensorPin=0, ventPin=0, temperature=0, humidity=0, home=False, night=False):
        self.name = name
        self.tID = tID
        self.sensorPin = sensorPin
        self.vent = Vent(ventPin)
        self.temperature = temperature
        self.humidity = humidity
        self.home = home
        self.night = night
        self.ip = ip
        self.notified = False
        self.intID = intID


class Flat:
    mates = {}
    
    def __init__(self, listOfMates):
        if len(listOfMates) < 1:
            raise Exception('Give me a list of Inhabitants!')
        
        for mate in listOfMates:
            self.mates[mate.name.capitalize()] = mate
    
    def getAll(self):
        return self.mates.values()
    
    def updateTH(self, name, temp, hum):
        if name.capitalize() in self.mates:
            self.mates[name.capitalize()].temperature = temp
            self.mates[name.capitalize()].humidity = hum
        else: raise UserNotRegisteredException("You're not registered!!")
        
    def updateTHremote(self, intID, temp, hum):
        self.updateTH(self.getNameFromIntID(intID), temp, hum)

    def setHome(self, name, home):
        if name.capitalize() in self.mates:
            self.mates[name.capitalize()].home = home
        else: raise UserNotRegisteredException("You're not registered!!")        
    
    def getTemp(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].temperature
        else: raise UserNotRegisteredException("You're not registered!!")
    
    def getNameFromTID(self, tID):
        for mate in self.mates.values():
            if tID == mate.tID:
                return mate.name
        raise UserNotRegisteredException("You're not registered!!")
    
    def getNameFromIntID(self, intID):
        for mate in self.mates.values():
            if intID == mate.intID:
                l2c("Got remote update for " + mate.name)
                return mate.name
        raise UserNotRegisteredException("You're not registered!!")
    
    def getMateFromTID(self, tID):
        for mate in self.mates.values():
            if tID == mate.tID:
                return mate
        raise UserNotRegisteredException("You're not registered!!")
    
    def getHum(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].humidity
        else: raise UserNotRegisteredException("You're not registered!!")
    
    def setNight(self, name, night):
        if name.capitalize() in self.mates:
            self.mates[name.capitalize()].night = night
        else: raise UserNotRegisteredException("You're not registered!!")
    
    def getID(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].tID
        else: raise UserNotRegisteredException("You're not registered!!")
    
    def getPin(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].pin
        else: raise UserNotRegisteredException("You're not registered!!")
    
    def getIP(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].ip
        else: raise UserNotRegisteredException("You're not registered!!")
    
    def isHome(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].home
        else: raise UserNotRegisteredException("You're not registered!!")
        
    def getMate(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()]
        else: raise UserNotRegisteredException("You're not registered!!")
    
    def setNotified(self, name, on):
        if name.capitalize() in self.mates:
            self.mates[name.capitalize()].notified = True
        else: raise UserNotRegisteredException("You're not registered!!")