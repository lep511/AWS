# This class provides class and methods for simple IoT device simulation

import random
import math
import datetime
import time
import json
import settings

# set some constants
MAX_BATTERY = 100.0
GPS_RADIUS = 1000

# method to move device
def gps_circle(center_lat, center_lon, radius):
    """
    Creates a circular path of GPS points for simulating thing movement around a point in meters
    """
    N = 360  # number of discrete sample points to be generated along the circle
    circle_points = []
    for k in range(N):
        # compute
        angle = math.pi * 2 * k / N
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)
        point = {}
        point['lat'] = center_lat + (180 / math.pi) * (dy / 6378137)
        point['lon'] = center_lon + (180 / math.pi) * (dx / 6378137) / math.cos(center_lat * math.pi / 180)
        # add to list
        circle_points.append(point)
    return circle_points

# define the Device class
class Device:

    def __init__(self, name, lat, lon): # initialize device with name and GPS coordinates
        self.name = name
        self.location = {}
        self.path = gps_circle(lat, lon, GPS_RADIUS) # List of 360 degree GPS points
        self.location = self.path[0] # set the initial position
        self.batteryCharge = random.uniform(1, 100)
        self.batteryDischargeRate = random.uniform(settings.BATTERY_DISCHARGE_RANGE[0], settings.BATTERY_DISCHARGE_RANGE[1])
        self.sensorRange = random.randint(5, 20)# defines the maximum value the sensor can detect - this is just to provide some randomization of the max val
        # self.sensorReading = random.randint(settings.RANDOM_INTEGER_RANGE[0],settings.RANDOM_INTEGER_RANGE[1])
        self.sensorReading = random.randint(1, self.sensorRange)
        self.timeStampEpoch = int(time.time() * 1000)
        self.timeStampIso = datetime.datetime.isoformat(datetime.datetime.now())

    def get_payload(self):
        return json.dumps({"batteryDischargeRate": self.batteryDischargeRate, "sensorReading": self.sensorReading, "deviceId": self.name, "timeStampEpoch": self.timeStampEpoch, "timeStampIso": self.timeStampIso, "batteryCharge": self.batteryCharge, "location": {"lat": self.location['lat'], "lon": self.location['lon']}})

    def update(self):
        self.batteryDischargeRate = random.uniform(settings.BATTERY_DISCHARGE_RANGE[0], settings.BATTERY_DISCHARGE_RANGE[1])
        self.batteryCharge = self.batteryCharge - self.batteryDischargeRate
        # check battery charge, and if it's zero, sensorReading "sensor" doesn't work
        if self.batteryCharge <= 0.0:
            self.batteryCharge = 0.0
            self.sensorReading = 0
        else:
            # self.sensorReading = random.randint(settings.RANDOM_INTEGER_RANGE[0],settings.RANDOM_INTEGER_RANGE[1])
            self.sensorReading = random.randint(1, self.sensorRange)
        self.timeStampEpoch = int(time.time() * 1000)  # update timestamp
        self.timeStampIso = datetime.datetime.isoformat(datetime.datetime.now()) # update timestamp
        self.move() # move the device

    def recharge_device_battery(self):
        self.batteryCharge = 100.0

    def move(self):
        """Set GPS location to the next spot on the path"""
        self.location = self.path[0] # Set current location to the next item in the path.
        # print(json.dumps(self.location))
        # print(json.dumps(self.path[0]))
        # print(len(self.path))
        # Move location to the end of the path
        self.path.remove(self.location)
        self.path.append(self.location)