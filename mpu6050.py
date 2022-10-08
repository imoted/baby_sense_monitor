# -*- coding: utf-8 -*-
from smbus2 import SMBus
import math
from time import sleep
import time


class MPU6050:
    DEV_ADDR = 0x68
    ACCEL_XOUT = 0x3B
    ACCEL_YOUT = 0x3D
    ACCEL_ZOUT = 0x3F
    TEMP_OUT = 0x41
    GYRO_XOUT = 0x43
    GYRO_YOUT = 0x45
    GYRO_ZOUT = 0x47
    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C

    def __init__(self):
        self.bus = SMBus(1)
        self.bus.write_byte_data(self.DEV_ADDR, self.PWR_MGMT_1, 0)

    def read_word(self, adr):
        high = self.bus.read_byte_data(self.DEV_ADDR, adr)
        low = self.bus.read_byte_data(self.DEV_ADDR, adr + 1)
        val = (high << 8) + low
        return val

    def read_word_sensor(self, adr):
        val = self.read_word(adr)
        if val >= 0x8000:
            return -((65535 - val) + 1)
        else:
            return val

    def get_temp(self):
        temp = self.read_word_sensor(self.TEMP_OUT)
        x = temp / 340 + 36.53  # data sheet(register map)記載の計算式.
        return x

    def getGyro(self):
        x = self.read_word_sensor(self.GYRO_XOUT) / 131.0
        y = self.read_word_sensor(self.GYRO_YOUT) / 131.0
        z = self.read_word_sensor(self.GYRO_ZOUT) / 131.0
        return [x, y, z]

    def getAccel(self):
        x = self.read_word_sensor(self.ACCEL_XOUT) / 16384.0
        y = self.read_word_sensor(self.ACCEL_YOUT) / 16384.0
        z = self.read_word_sensor(self.ACCEL_ZOUT) / 16384.0
        return [x, y, z]

    def get3AxisMix(self):
        accel = self.getAccel()
        return math.sqrt(accel[0] ** 2 + accel[1] ** 2 + accel[2] ** 2) - 1


if __name__ == "__main__":
    mpu = MPU6050()
    while True:
        ax, ay, az = mpu.getAccel()
        gx, gy, gz = mpu.getGyro()
        mix_data = mpu.get3AxisMix()
        print("加速度: {:4.3f},{:4.3f},{:4.3f},{:4.3f},".format(ax, ay, az, mix_data))
        print("角加速度: {:4.3f},{:4.3f},{:4.3f}".format(gx, gy, gz, ax))
        sleep(0.3)
