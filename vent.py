import RPi.GPIO as GPIO

class Vent():
    p = None
    active = False

    def __init__(self, ventPin=0):
        if ventPin != 0:
            self.active = True
            
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(14, GPIO.OUT)
            global p
            p = GPIO.PWM(14, 60)
            p.start(0)

    def setVent(self, val, freq=60):
        if self.active:
            global p
            p.ChangeDutyCycle(val)
            p.ChangeFrequency(freq)
    
    def end(self):
        self.setVent(0)
        GPIO.cleanup()