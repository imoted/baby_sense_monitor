#!/usr/bin/env python3
import time
from datetime import datetime, timedelta, tzinfo
from omron_2jcie_bu01 import Omron2JCIE_BU01


class EnvSensor:
    VI = [
        "NONE",
        "During vibration (Earthquake judgment in progress)",
        "During earthquake",
    ]

    def __init__(self):
        self.sensor = Omron2JCIE_BU01.serial("/dev/ttyUSB0")

    def read_sensor_data(self):
        info = self.sensor.latest_data_long()
        return info

    def read_sensor_info(self):
        dev = self.sensor.info()
        return dev


if __name__ == "__main__":
    env = EnvSensor()
    while True:
        CurrentTZ = type(time.tzname[0], (tzinfo,), {
            "tzname": lambda self, dt: time.tzname[0],
            "utcoffset": lambda self, dt: timedelta(seconds=-time.timezone),
            "dst": lambda self, dt: timedelta(seconds=time.timezone - time.altzone),
        })()
        info = env.read_sensor_data()
        dev = env.read_sensor_info()
        # dt = datetime.now(CurrentTZ)
        # print(f" Date                : {dt.strftime('%Y-%m-%d %H:%M:%S%z')}")
        # print(f" Sequence Number     : {info.seq}")
        print(f" Temperature         : {info.temperature} degC")
        print(f" Relative humidity   : {info.humidity} %RH")
        print(f" Ambient light       : {info.light} lx")
        print(f" Barometric pressure : {info.pressure} hPa")
        print(f" Sound noise         : {info.noise} dB")
        print(f" eTVOC               : {info.eTVOC} ppb")
        print("================================================")
        print(f" eCO2                : {info.eCO2} ppm")
        print(f" Discomfort index    : {info.thi}")
        print(f" Heat stroke         : {info.wbgt} degC")
        print(f" Vibration info      : {env.VI[info.vibration]}")
        print(f" SI value            : {info.si} kine")
        print(f" peak ground acceleration : {info.pga} gal")
        print(f" Seismic intensity   : {info.seismic_intensity}")
        print("================================================")
        print(f" Model               : {dev.model}")
        print(f" Serial              : {dev.serial}")
        print(f" Firmware rev.       : {dev.fw_rev}")
        print(f" Hardware rev.       : {dev.hw_rev}")
        print(f" Manufacture         : {dev.manufacturer}")
        print("================================================")
        time.sleep(1)
