import influxdb
from datetime import datetime
from time import sleep
import read_envsensor
import mpu6050
import threading


class UploadToInfluxDB:
    def __init__(self):
        self.influx = influxdb.InfluxDBClient(
            host="localhost", port=8086, database="baby_sense"
        )
        self.env = read_envsensor.EnvSensor()
        self.env_data = self.env.read_sensor_data()
        self.mpu = mpu6050.MPU6050()
        self.mpu_data = self.mpu.get3AxisMix()
        self.thermal_cam_data = [0.0, 0.0, 0.0]
        self.json_point = []

    def run(self):
        t1 = threading.Thread(target=self.send_data)
        t2 = threading.Thread(target=self.read_sensor_data)
        t3 = threading.Thread(target=self.read_thermal_camera_data)
        t1.start()
        t2.start()
        t3.start()

    def send_data(self):
        self.json_point = [
            {
                "measurement": "home",
                "time": datetime.utcnow(),
                "fields": {
                    "tempreture": self.env_data.temperature,
                    "humidity": self.env_data.humidity,
                    "Ambient light": self.env_data.light,
                    "Barometric Pressure": self.env_data.pressure,
                    "Sound Noise": self.env_data.noise,
                    "eTVOC": self.env_data.eTVOC,
                    # "eCO2": self.env_data.eCO2,
                    # "Discomfort Index": self.env_data.thi,
                    # "Heat Stroke": self.env_data.wbgt,
                    # "Vibration Info": self.env_data.vibration,
                    # "SI Value": self.env_data.si,
                    # "Peak Ground Acceleration": self.env_data.pga,
                    # "Seismic Intensity": self.env_data.seismic_intensity,
                    "Bed Movement": self.mpu_data,
                    # "Thermal Camera": self.thermal_cam_data[0],
                    "Thermal Camera Max": self.thermal_cam_data[1],
                    # "Thermal Camera Min": self.thermal_cam_data[2]
                },
            }
        ]
        try:
            self.influx.write_points(self.json_point)
        except Exception as e:
            print(e)
        t = threading.Timer(5, self.send_data)
        t.start()

    def read_sensor_data(self):
        try:
            self.env_data = self.env.read_sensor_data()
        except Exception as e:
            print(e)
        try:
            self.mpu_data = self.mpu.get3AxisMix()
        except Exception as e:
            print(e)
        t = threading.Timer(1, self.read_sensor_data)
        t.start()

    def read_thermal_camera_data(self):
        try:
            with open("/home/ubuntu/baby_sense/temp_info.txt") as f:
                lines = f.readlines()
                if lines:
                    self.thermal_cam_data = [float(x.replace("\n", "")) for x in lines]
        except Exception as e:
            print(e)
        t = threading.Timer(1, self.read_thermal_camera_data)
        t.start()


if __name__ == "__main__":
    uploader = UploadToInfluxDB()
    uploader.run()
