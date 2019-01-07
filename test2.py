import Adafruit_DHT

sensor = Adafruit_DHT.DHT22

humidity, temperature = Adafruit_DHT.read_retry(sensor, 4)

print(str(temperature) + ',' + str(humidity))

print(u'\u0B00')