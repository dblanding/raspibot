# Calibration procedure for OTOS

* Follow procedure described [here](https://www.youtube.com/watch?v=WSELKAIJeFk&t=4s)

* By default, values of LinearScalar and AngularScalar are set to 1.0
* Rotate 10 turns CCW (exactly)
* Find out what the robot's angle is:
    * in a terminal window `mosquitto_sub -h raspibot.local -t 'robot/odometry/pose' -v`
* In my case, after 10 complete turns, the angle was: 0.4 (radians)
* Calculate the value of AngularScalar = :
    * actual angle / measured angle
    * (2 * pi * 10) / (2 * pi * 10 + 0.4)
    * 62.831853 / (62.831853 + 0.4)
    * 62.831853 / 63.231
    * 0.994
* Incidentally, this appears to have no effect. Irrespective of whether the AngularScalar is set at 1.0 or 0.994, the measured angle after 10 CCW turns ends up being approximately +0.4 radians.
