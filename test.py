import os

hostname = "e5823"
response = os.system("ping -c 1 " + hostname)
print (response)

if response == 0:
    print ('Carl is home')