# -*- coding: utf-8 -*-
import os, inspect, sys, sched, time
from datetime import datetime, timedelta
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,currentdir)

from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, Filters, MessageHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from threading import Thread
import logging
import Adafruit_DHT
import time
import json

import socket

from objects import *

#sys.stdout = open(currentdir + "/log/" + time.strftime("%d.%m_%H:%M:%S", time.gmtime()) + "_gourmetbot_info.log", 'w+')
#sys.stderr = open(currentdir + "/log/" + time.strftime("%d.%m_%H:%M:%S", time.gmtime()) + "_gourmetbot_err.log", 'w+')



# init flatmates
carl = Flatmate('Carl', ["DESKTOP-A18AGI2", "android-4e1dfd4a1148ac05"], 10307260, 12)
simon = Flatmate('Simon', ["android-e5cf63a05ae4ea6c", "android-18ef3254c89a664e", "Simons-MBP"], 215807065, 11)
# peter = Flatmate('Peter', ["android-9fcf94d7fe7938eb","Peters-MBP-2","192.168.178.60"], 52115553, 12)
stella = Flatmate('Stella', ["Galaxy-J7", "LAPTOP-SJSQ8ATP"], 200929247,
                  13)
# andra = Flatmate('Andra', ["Andras-Air","iPhone"])

wg = Flat([carl, simon, stella])

# command list for main menu
commands = ["Check Temperature", "Check Humidity", "Check who's home", "Set Daytime Mode", "Set Silent Mode",
            "/Shopping"]
mainKeyboard = [[KeyboardButton(commands[0], callback_data='1'),
                 KeyboardButton(commands[1], callback_data='2')],
                [KeyboardButton(commands[2], callback_data='3'),
                 KeyboardButton(commands[5], callback_data='6')],
                [KeyboardButton(commands[3], callback_data='4'),
                 KeyboardButton(commands[4], callback_data='5')]]

# shopping commands
shopcommands = ["Back to main menu", "Back"]

# shopping list
groceryList = []


def start(bot, update):
    reply_markup = ReplyKeyboardMarkup(mainKeyboard)
    update.message.reply_text('Please select', reply_markup=reply_markup)
    return DEFAULT


def readGroceryList():
    global groceryList
    groceryFile = open("groceries.list", "r")
    content = groceryFile.read()

    if content != "":
        groceryList = json.loads(content)

    groceryFile.close()


def broadcast_message(msg):
    for mate in wg.get_all():
        if mate.tID != 0 and msg != "":
            dispatcher.bot.sendMessage(mate.tID, msg)
            l2c("Sent reboot message to " + mate.name)


def updateGroceryList():
    global groceryFile, groceryList
    groceryFile = open("groceries.list", "w")
    json.dump(groceryList, groceryFile)
    groceryFile.close()


def nighttime(bot, update):
    global silent
    silent = True


def daytime(bot, update):
    global silent
    silent = False


def whoshomestring():
    out = "At the moment, "
    res = []
    for mate in wg.get_all():
        if mate.home:
            res.append(mate.name)
    if len(res) == 0:
        out += "nobody is "
    elif len(res) == 1:
        out += res[0] + " is "
    elif len(res) > 1:
        res.insert(len(res) - 1, "and")
        res.append("are")

        for i in range(0, len(res)):
            out += (res[i] + " ")
    out += "home."

    return out


def whoshome(bot, update):
    out = "At the moment, "
    res = []
    for mate in wg.get_all():
        if mate.home:
            res.append(mate.name)
    if len(res) == 0:
        out += "nobody is "
    elif len(res) == 1:
        out += res[0] + " is "
    elif len(res) > 1:
        res.insert(len(res) - 1, "and")
        res.append("are")

        for i in range(0, len(res)):
            out += (res[i] + " ")
    out += "home."

    bot.send_message(chat_id=update.message.chat_id, text=out)


def button(bot, update):
    # print '----default'
    # query = update.callback_query
    l2c("user " + str(update.message.from_user.id) + " sent request " + update.message.text)
    # bot.edit_message_text(text="Selected option: {}".format(query.data), chat_id=query.message.chat_id, message_id=query.message.message_id)
    if update.message.text in commands:
        command_id = commands.index(update.message.text)
        name = wg.get_name_from_telegram_id(update.message.from_user.id)
        try:
            if command_id == 0:
                bot.send_message(chat_id=update.message.from_user.id, text="Temperature: "
                                                                           + str(
                    round(wg.get_temp(name), 1)) + "\xb0.")
            if command_id == 1:
                bot.send_message(chat_id=update.message.from_user.id, text="Humidity: "
                                                                           + str(round(wg.humidity(name), 0)) + "%")

            if command_id == 2:
                bot.send_message(chat_id=update.message.from_user.id, text=whoshomestring())

            if command_id == 4:
                wg.set_night(name, True)
                bot.send_message(chat_id=update.message.from_user.id, text="Silent mode on")

            if command_id == 3:
                wg.set_night(name, False)
                bot.send_message(chat_id=update.message.from_user.id, text="Silent mode off")

        except UserNotRegisteredException as e:
            # bot.send_message(chat_id=update.message.from_user.id, text=Exception.args[0])
            l2c("#####ERROR: " + str(e))

    else:
        bot.send_message(chat_id=update.message.from_user.id, text="I don't get that")


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
                                                                  + str(round(wg.humidity(args[0]), 0)) + "%")
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
            bot.send_message(chat_id=update.message.chat_id,
                             text=args[0].capitalize() + " is " + ("" if wg.home(args[0]) else "not ") + "home.")
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
                                                                  + str(round(wg.get_temp(args[0]), 1)) + "\x00\xb0.")
        except:
            bot.send_message(chat_id=update.message.chat_id, text="No user "
                                                                  "named " + args[0])


def setFanMan(bot, update, args):
    if len(args) == 0:
        bot.send_message(chat_id=update.message.chat_id, text="Please enter a "
                                                              "value 0-100")
        return
    elif len(args) > 1:
        bot.send_message(chat_id=update.message.chat_id, text="Please enter on"
                                                              "e value only")
        return
    else:
        l2c("set fan to " + args[0])
        try:
            m = wg.get_mate_from_telegram_id(update.message.chat_id)
            l2c(m.name + " set the fan to " + args[0])
            global manual
            manual = True
            if args[0] == "auto":
                manual = False
                return
            m.vent.setVent(float(args[0]))
        except:
            bot.send_message(chat_id=update.message.chat_id, text="Command failed")


def updateVars():
    while 1:
        time.sleep(10)
        #try:
        for mate in wg.get_all():
            humidity = 0
            temperature = 0

            # fetch data
            # from sensor (if hard wired)
            if mate.sensorPin != 0:
                print("wired")
                humidity, temperature = Adafruit_DHT.read_retry(sensor, mate.sensorPin)
                wg.update_climate_data(mate.name, temperature, humidity)

            # from data (if remote)
            else:
                humidity = mate.humidity
                temperature = mate.temperature

            l2c(mate.name + ": T:" + str(temperature) + " H:" + str(humidity))

            if temperature != 0 and humidity != 0:
                msg = ""
                amount = 0

                # create notification message
                if humidity > maxHum:
                    msg += "The humidity in your room is " + str(round(humidity, 0)) + "%. Open a window! "
                    amount = humidity - maxHum
                elif humidity < minHum:
                    msg += "The humidity in your room is " + str(round(humidity, 0)) + "%. Do some sweatin' "
                    amount = minHum - humidity

                if temperature > maxTemp:
                    msg += "The temperature in your room is " + str(
                        round(temperature, 1)) + "\xb0. Turn down your Radiator!"
                    amount += temp_handler - maxTemp
                elif temperature < minTemp:
                    msg += "The temperature in your room is " + str(
                        round(temperature, 1)) + "\xb0. Turn on your Radiator!"
                    amount += minTemp - temperature

                # fan setting
                if amount != 0:
                    if mate.home:
                        amount *= 2
                    else:
                        amount *= 4

                    amount += 10  # minimum

                    if amount > 100:
                        amount = 100

                # notify mate
                if not mate.notified and msg != "":
                    # l2c(mate.name + ":" + msg)
                    wg.set_notified(mate.name, True)
                    dispatcher.bot.sendMessage(mate.tID, msg)

                    muteThread = Thread(target=notifySleep, args=(mate.name,))
                    muteThread.daemon = True
                    muteThread.start()

                if mate.night:
                    mate.vent.setVent(0)
                elif not manual:
                    mate.vent.setVent(amount)
                l2c(mate.name + "'s fan is set to " + str(amount) + "%")
        #except:
        #    startServices()

def pingService():
    while 1:
        #try:
        for mate in wg.get_all():
            online = False
            for ip in mate.ip:
                online = online or (os.system("ping -c 1 -W 5 " + ip + " > /dev/null") == 0)
                l2c("Pinging " + mate.name + ":" + str(online))
            wg.set_home(mate.name, online)

        time.sleep(60)
        #except:
        #    startServices()


def error_callback(bot, update, error):
    l2c("##########ERROR: " + str(error))


def notifySleep(name):
    l2c("Muting notifications for " + name + " for " + str(notificationLimit) + "s")
    time.sleep(notificationLimit)
    wg.set_notified(name, False)
    l2c("Unmuting notifications for " + name)


def addShoppingItem(bot, update):
    # print '----addhandler'
    if update.message.text == shopcommands[1]:
        groceryKeyboard = [[KeyboardButton(shopcommands[1])]]
        groceryKeyboard.extend(createKeyboardFromList())
        update.message.reply_text('Please tap items to remove', reply_markup=ReplyKeyboardMarkup(groceryKeyboard))
        return REMOVEGROCERIES
    else:
        l2c('Add shopping item' + update.message.text)
        groceryList.append(update.message.text)
        groceryKeyboard = [[KeyboardButton(shopcommands[1])]]
        groceryKeyboard.extend(createKeyboardFromList())
        update.message.reply_text('Please send items to add', reply_markup=ReplyKeyboardMarkup(groceryKeyboard))


def removeShoppingItem(bot, update):
    # print '----removehandler: ' + update.message.text
    if update.message.text == shopcommands[0]:
        reply_markup = ReplyKeyboardMarkup(mainKeyboard)
        update.message.reply_text('Please select', reply_markup=reply_markup)
        return DEFAULT
    elif update.message.text in groceryList:
        groceryList.remove(update.message.text)
        update.message.reply_text(update.message.text + " removed")
        updateGroceryList()
    else:
        groceryList.append(update.message.text)
        update.message.reply_text(update.message.text + " added")
        updateGroceryList()

    groceryKeyboard = [[KeyboardButton(shopcommands[0])]]
    groceryKeyboard.extend(createKeyboardFromList())
    update.message.reply_text('Please tap items to remove. Send message to add items.',
                              reply_markup=ReplyKeyboardMarkup(groceryKeyboard))
    # if message==add return 'add'
    # if message==done return 'default'


def shopping_entry(bot, update):
    # print "----shoppingentry"
    groceryKeyboard = [[KeyboardButton(shopcommands[0])]]
    groceryKeyboard.extend(createKeyboardFromList())
    # print str(groceryKeyboard)

    update.message.reply_text('Please tap items to remove. Send message to add items.',
                              reply_markup=ReplyKeyboardMarkup(groceryKeyboard))
    return REMOVEGROCERIES


def createKeyboardFromList():
    ret = []
    itemsPerRow = 3
    retCol = []

    for item in groceryList:
        retCol.append(KeyboardButton(item))
        if len(retCol) >= itemsPerRow:
            ret.append(retCol)
            retCol = []

    if len(retCol) != 0:
        ret.append(retCol)

    return ret


def udpRcvService():
    while 1:
        # try:
        data, addr = s.recvfrom(1024)
        recv = json.loads(data.decode("utf-8"))
        print(recv)
        if len(recv) == 3:
            wg.update_remote_climate_data(int(recv[0]), float(recv[1]), float(recv[2]))
        #except:
         #   startServices()


def send_shopping_message():
    broadcast_message("You have %s on the shopping list." %
                      ", ".join(groceryList))


def shopReminder():
    s = sched.scheduler(time.time, time.sleep)
    while 1:
        s.enter(shop_reminder_time_secs(), 1, send_shopping_message)
        l2c("Shopping reminder set: %s" % s.queue)
        s.run()


def shop_reminder_time_secs():
    # schedule shopping reminder
    # time now
    now = datetime.now()
    # time today at 6pm
    inc = 0
    if now.hour <= 18:
        # add one day
        inc = 1
    remind_time = datetime(now.year, now.month, now.day, 18)
    remind_time += timedelta(inc)
    # start scheduler with time difference
    return (remind_time - now).seconds


# threads
updateThread = Thread(target=updateVars)
pingThread = Thread(target=pingService)
udpThread = Thread(target=udpRcvService)
shoppingReminderThread = Thread(target=shopReminder)


def startServices():
    l2c('starting sensor')
    global updateThread
    global pingThread
    global udpThread
    global shoppingReminderThread

    if updateThread.isAlive():
        l2c("UpdateThread still alive")
    else:
        updateThread = Thread(target=updateVars)
        updateThread.daemon = True
        updateThread.start()

    l2c('starting ping thread')
    if pingThread.isAlive():
        l2c("PintThread still alive")
    else:
        pingThread = Thread(target=pingService)
        pingThread.daemon = True
        pingThread.start()

    l2c('starting network thread')
    if udpThread.isAlive():
        l2c("NetworkThread still alive")
    else:
        udpThread = Thread(target=udpRcvService)
        udpThread.daemon = True
        udpThread.start()

    l2c('starting shopping reminder thread')
    if shoppingReminderThread.isAlive():
        l2c("Shopping Reminder still active")
    else:
        shoppingReminderThread = Thread(target=shopReminder)
        shoppingReminderThread.daemon = True
        shoppingReminderThread.start()


updater = Updater(token='452396346:AAEKPdIiwuFcrQbNxZTlUAkZOLWsxEQ_C5I')
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                           '%(message)s', level=logging.INFO)
sensor = Adafruit_DHT.DHT22

# threads
# global updateThread, pingThread, udpThread

# stati
DEFAULT, ADDGROCERIES, REMOVEGROCERIES = range(3)

## network config
PORT = 5000
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", PORT))

### value limits
## temperature
minTemp = 16
maxTemp = 24
##humidity
minHum = 40
maxHum = 65

notificationLimit = 5 * 60
silent = False
manual = False

add_item_handler = MessageHandler(Filters.text, addShoppingItem)
remove_item_handler = MessageHandler(Filters.text, removeShoppingItem)

start_handler = CommandHandler('start', start)
hum_handler = CommandHandler('humidity', getHumidity, pass_args=True)
temp_handler = CommandHandler('temperature', getTemperature, pass_args=True)
id_handler = CommandHandler('id', id_echo)
home_handler = CommandHandler('home', getHome, pass_args=True)
allhome_handler = CommandHandler('whoshome', whoshome)
nighttime_handler = CommandHandler('nighttime', nighttime)
daytime_handler = CommandHandler('daytime', daytime)
shopping_init = CommandHandler('Shopping', shopping_entry)
fan_manual = CommandHandler('setfan', setFanMan, pass_args=True)

main_handler = MessageHandler(Filters.text, button)

allstates = {REMOVEGROCERIES: [remove_item_handler],
             ADDGROCERIES: [add_item_handler],
             DEFAULT: [main_handler, shopping_init]}

ze_handler = ConversationHandler(entry_points=[start_handler], states=allstates, fallbacks=[main_handler])

dispatcher.add_handler(hum_handler)
dispatcher.add_handler(temp_handler)
dispatcher.add_handler(id_handler)
dispatcher.add_handler(home_handler)
dispatcher.add_handler(allhome_handler)
dispatcher.add_handler(nighttime_handler)
dispatcher.add_handler(daytime_handler)
dispatcher.add_handler(ze_handler)
dispatcher.add_handler(fan_manual)

dispatcher.add_error_handler(error_callback)

l2c('loading shoping list')
readGroceryList()
l2c('Found ' + str(len(groceryList)) + ' items')

startServices()

# broadcast_message("You thought I'm dead? I'm f**ing alive, baby! Check out these buttons: Write or tap /start"
#                  "  (Also in case I don't work anymore :D)")

l2c('starting updater')

updater.start_polling()