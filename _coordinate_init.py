import math
import math_operation as mo

# nama class
class GetCoordinate:
    #method atau function
    def __init__(self, altitude, magnifier, theta):
        self.width_frame = 720  # pixel
        self.height_frame = 480   # pixel
        self.altitude = altitude
        self.theta = theta

        sensorHeight = 15.4
        sensorWidth = 23.1

        self.heightInFullFrame = (self.width_frame * 2.0) / 3
        self.heightSurplus = (self.heightInFullFrame - self.height_frame) / 2
        aspectRatioHeight = (sensorWidth / self.width_frame) * self.heightInFullFrame
        self.focal = (((magnifier * 1) / aspectRatioHeight) * self.height_frame)

    def getDistanceOB(self):
        yCoordinate = (self.height_frame + self.heightSurplus) - self.height_frame
        OB = mo.centeroidPinHoleMode(self.heightInFullFrame, self.focal, self.altitude, self.theta, yCoordinate)

        return OB

    def getCoordinate(self, distance):
        yCoordinate = mo.getCoordinateFromDistance(self.height_frame, self.focal, self.altitude, self.theta, distance)
        return yCoordinate
