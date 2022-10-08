from flask import Flask
import servo

app = Flask(__name__)
base = servo.BaseJoint()
angle = servo.AngleJoint()


@app.route("/servo/<direction>", methods=["POST"])
def api_servo(direction):
    if direction == "left":
        base.step_angle("left")
    elif direction == "right":
        base.step_angle("right")
    elif direction == "up":
        angle.step_angle("up")
    elif direction == "down":
        angle.step_angle("down")
    return "success", 200


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=4000)
