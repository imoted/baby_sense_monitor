import pigpio
from time import sleep
# 実行前にsudo pigpiodを忘れずに


class ServoCtrl:
    def __init__(self, pin):
        self.pig = pigpio.pi()
        self.pig.set_mode(pin, pigpio.ALT0)
        self.pig.hardware_PWM(pin, 50, 72500)
        self.angle = 0
        self.pin = pin

    def set_angle(self, angle):
        # 0.5ms-2.4msのパルスを出力
        if angle < -100:
            angle = -100
        elif angle > 100:
            angle = 100
        percentage = (angle + 90) / 180 * (12 - 2.5) + 2.5
        self.pig.hardware_PWM(self.pin, 50, int(percentage * 10000))

    def stop(self):
        self.pig.stop()

    def __del__(self):
        self.stop()


class BaseJoint:
    def __init__(self):
        self.servo = ServoCtrl(13)
        self.servo.set_angle(0)
        self.angle = 0

    def step_angle(self, direction):
        if direction == "left":
            self.angle = self.angle - 5
        elif direction == "right":
            self.angle = self.angle + 5
        if self.angle < -25:
            self.angle = -25
        elif self.angle > 25:
            self.angle = 25
        self.servo.set_angle(self.angle)

    def stop(self):
        self.servo.stop()

    def __del__(self):
        self.stop()


class AngleJoint:
    def __init__(self):
        self.servo = ServoCtrl(12)
        self.servo.set_angle(95)
        self.angle = 95

    def step_angle(self, direction):
        if direction == "up":
            self.angle = self.angle - 5
        elif direction == "down":
            self.angle = self.angle + 5
        if self.angle < 30:
            self.angle = 30
        elif self.angle > 95:
            self.angle = 95
        self.servo.set_angle(self.angle)

    def stop(self):
        self.servo.stop()

    def __del__(self):
        self.stop()


if __name__ == "__main__":
    base = BaseJoint()
    angle = AngleJoint()
    while True:
        for _ in range(5):
            base.step_angle("right")
            angle.step_angle("up")
            sleep(0.1)
        for _ in range(10):
            base.step_angle("left")
            angle.step_angle("down")
            sleep(0.1)
        for _ in range(5):
            base.step_angle("right")
            angle.step_angle("up")
            sleep(0.1)
