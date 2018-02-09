from telegram.ext import Updater
from telegram.ext import CommandHandler
from vent import Vent
from threading import Thread
import logging
import Adafruit_DHT
import time
import os


updater = Updater(token='452396346:AAEKPdIiwuFcrQbNxZTlUAkZOLWsxEQ_C5I')
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
'%(message)s', level=logging.INFO)
sensor = Adafruit_DHT.DHT22

### value limits
## temperature
minTemp = 18
maxTemp = 23
##humidity
minHum = 40
maxHum = 60

notificationLimit = 5*60
silent = False


class Flatmate:
    def __init__(self, name='', ip=[''], tID=0, sensorPin=0, ventPin=0, temperature=0, humidity=0, home='False'):
        self.name = name
        self.tID = tID
        self.sensorPin = sensorPin
        self.vent = Vent(ventPin)
        self.temperature = temperature
        self.humidity = humidity
        self.home = home
        self.ip = ip
        self.notified = False

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
        else: raise Exception("This mate wasn't found!")
        
    def setHome(self, name, home):
        if name.capitalize() in self.mates:
            self.mates[name.capitalize()].home = home
        else: raise Exception("This mate wasn't found!")        
    
    def getTemp(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].temperature
        else: raise Exception("This mate wasn't found!")
    
    def getHum(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].humidity
        else: raise Exception("This mate wasn't found!")
    
    def getID(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].tID
        else: raise Exception("This mate wasn't found!")
    
    def getPin(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].pin
        else: raise Exception("This mate wasn't found!")
    
    def getIP(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].ip
        else: raise Exception("This mate wasn't found!")
    
    def isHome(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()].home
        else: raise Exception("This mate wasn't found!")
        
    def getMate(self, name):
        if name.capitalize() in self.mates:
            return self.mates[name.capitalize()]
        else: raise Exception("This mate wasn't found!")
    
    def setNotified(self, name, on):
        if name.capitalize() in self.mates:
            self.mates[name.capitalize()].notified = True
        else: raise Exception("This mate wasn't found!")

##init flatmates
carl = Flatmate('Carl', ["e5823","DESKTOP-A18AGI2"], 10307260, 4, 14)
simon = Flatmate('Simon', ["android-18ef3254c89a664e","Simons-MBP"])
peter = Flatmate('Peter', ["android-9fcf94d7fe7938eb","Peters-MBP-2","192.168.178.60"])
stella = Flatmate('Stella', ["android-741115d63e5b6dcc","STELLA-LAPTOP"])

wg = Flat([carl, simon, peter, stella])

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please "
    "talk to me!")

def nighttime(bot, update):
    global silent
    silent = True

def daytime(bot, update):
    global silent
    silent = False

def whoshome(bot, update):
    out = "At the moment, "
    res = []
    for mate in wg.getAll():
        if mate.home:
            res.append(mate.name)
    if len(res) == 0:
        out += "nobody is "
    elif len(res) == 1:
        out += res[0] + " is "
    elif len(res) > 1:
        res.insert(len(res)-1,"and")
        res.append("are")
        
        for i in range(0,len(res)):
            out += (res[i] + " ")
    out += "home."
    
    bot.send_message(chat_id=update.message.chat_id, text=out)  
            

def getHumidity(bot, update, args):
    if len(args) == 0:
        bot.send_message(chat_id=update.message.chat_id, text="Please enter a "
        "name")
        return
    elif len(args) > 1:
        bot.send_message(chat_id=update.message.chat_id, text="Please enter on"
        "e name only")
        return
    else:
        try:
            bot.send_message(chat_id=update.message.chat_id, text="Humidity: "
                             + str(round(wg.getHum(args[0]),0)) + "%")
        except:
            bot.send_message(chat_id=update.message.chat_id, text="No user "
            "named " + args[0])

def id_echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.chat_id)    
    humidity, temperature = Adafruit_DHT.read_retry(sensor, 4)
    bot.send_message(chat_id=update.message.chat_id, text=str(humidity))

def getHome(bot, update, args):
    if len(args) == 0:
        bot.send_message(chat_id=update.message.chat_id, text="Please enter a "
        "name")
        return
    elif len(args) > 1:
        bot.send_message(chat_id=update.message.chat_id, text="Please enter on"
        "e name only")
        return
    else:
        try:
            bot.send_message(chat_id=update.message.chat_id, text=args[0].capitalize() + " is " + ("" if wg.isHome(args[0]) else "not ") + "home.")
        except:
            bot.send_message(chat_id=update.message.chat_id, text="No user "
            "named " + args[0])

def getTemperature(bot, update, args):
    if len(args) == 0:
        bot.send_message(chat_id=update.message.chat_id, text="Please enter a "
        "name")
        return
    elif len(args) > 1:
        bot.send_message(chat_id=update.message.chat_id, text="Please enter on"
        "e name only")
        return
    else:
        try: 
            bot.send_message(chat_id=update.message.chat_id, text="Temperature: "
                             + str(round(wg.getTemp(args[0]),1)) + "\xc2\xb0.")
        except:
            bot.send_message(chat_id=update.message.chat_id, text="No user "
            "named " + args[0])

def updateVars():
    while 1:
        for mate in wg.getAll():
            if mate.sensorPin != 0:
                humidity, temperature = Adafruit_DHT.read_retry(sensor, mate.sensorPin)
                wg.updateTH(mate.name, temperature, humidity)        
                
                msg = ""
                amount = 0
                    
                if humidity > maxHum:
                    msg += "The humidity in your room is " + str(round(humidity,0)) + "%. Open a window! "
                    amount = humidity - maxHum
                elif humidity < minHum:
                    msg += "The humidity in your room is " + str(round(humidity,0)) + "%. Do some sweatin' "
                    amount = minHum - humidity
            
                if temperature > maxTemp:
                    msg +=  "The temperature in your room is " + str(round(temperature,1)) + "\xc2\xb0. Turn down your Radiator!"
                    amount += temp_handler - maxTemp
                elif temperature < minTemp:
                    msg +=  "The temperature in your room is " + str(round(temperature,1)) + "\xc2\xb0. Turn on your Radiator!"
                    amount += minTemp - temperature
                
                if amount != 0:
                    if mate.home:
                        amount *= 2
                    else: amount *= 4

                    amount += 10 # minimum
                                        
                    if amount > 100:
                        amount = 100
                        
                    if not mate.notified:
                        wg.setNotified(mate.name, True)
                        dispatcher.bot.sendMessage(mate.tID, msg)
                    
                        muteThread = Thread(target=notifySleep, args=(mate.name,))
                        muteThread.daemon = True
                        muteThread.start()
                    
                if silent:
                    mate.vent.setVent(0)
                else:
                    mate.vent.setVent(amount)
                    
                print(mate.name + "'s fan is set to " + str(amount) + "%")
                
        time.sleep(10)

def pingService():
    while 1:
        for mate in wg.getAll():
            online = False
            for ip in mate.ip:
                
                online = online or (os.system("ping -c 1 -W 5 " + ip + " > /dev/null") == 0)
                print "pinging " + mate.name +":" + str(online)
            wg.setHome(mate.name, online)
        
        time.sleep(60)

def notifySleep(name):
    print "muting notifications for " + name + " for " + str(notificationLimit) + "s"
    time.sleep(notificationLimit)
    wg.setNotified(name, False)
    print "unmuted " + name
    

start_handler = CommandHandler('start', start)
hum_handler = CommandHandler('humidity', getHumidity, pass_args=True)
temp_handler = CommandHandler('temperature', getTemperature, pass_args=True)
id_handler = CommandHandler('id', id_echo)
home_handler = CommandHandler('home', getHome, pass_args=True)
allhome_handler = CommandHandler('whoshome', whoshome)
nighttime_handler = CommandHandler('nighttime', nighttime)
daytime_handler  = CommandHandler('daytime', daytime)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(hum_handler)
dispatcher.add_handler(temp_handler)
dispatcher.add_handler(id_handler)
dispatcher.add_handler(home_handler)
dispatcher.add_handler(allhome_handler)
dispatcher.add_handler(nighttime_handler)
dispatcher.add_handler(daytime_handler)

print('starting sensor')

updateThread = Thread(target=updateVars)
updateThread.daemon = True
updateThread.start()

print('starting ping thread')

pingThread = Thread(target=pingService)
pingThread.daemon = True
pingThread.start()

print('starting updater')

updater.start_polling()

