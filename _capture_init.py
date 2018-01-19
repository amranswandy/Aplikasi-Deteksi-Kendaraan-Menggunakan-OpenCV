import cv2
import time
import datetime
import os
import numpy as np
import image_processing as improc
import math_operation as mo
import _vehicle_init as vehicleInit
import _trajectory_init as trajectoryInit
import shadow_removal as sr

from PyQt4 import QtGui, QtCore
from cv2 import ocl
from munkres import Munkres

# atur OpenCV
ocl.setUseOpenCL(False)

# nama class
class QtCapture:
    # method atau function
    def setVideoMode(self, video_mode):
        self.video_mode = video_mode

    def getVideoMode(self):
        return self.video_mode

    def setVideoOutput(self, video_output):
        self.video_output = video_output

    def getVideoOutput(self):
        return self.video_output

    def setBackgroundSubtraction(self, backgroundSubtraction):
        self.backgroundSubtracion = backgroundSubtraction

    def getBackgroundSubtraction(self):
        return self.backgroundSubtracion

    def setBoundary(self, boundary):
        self.boundary = boundary

    def getBoundary(self):
        return self.boundary

    def setROI(self, roi):
        self.roi = roi

    def getROI(self):
        return self.roi

    def setShadow(self, shadow):
        self.shadow = shadow

    def getShadow(self):
        return self.shadow

    def setFPS(self, fps):
        self.fps = fps

    def getFPS(self):
        return self.fps

    def setAlt(self, alt):
        self.alt = alt

    def getAlt(self):
        return self.alt

    def setElevated(self, elevated):
        self.elevated = elevated

    def getElevated(self):
        return self.elevated

    def setFocal(self, focal):
        self.focal = focal

    def getFocal(self):
        return self.focal

    def setSensorSize(self, height, width):
        self.sensorHeight = height
        self.sensorWidth = width

    def getSensorSize(self):
        return self.sensorHeight, self.sensorWidth

    def setLengthLV(self, lenghtLV):
        self.lengthLV = lenghtLV

    def getLengthLV(self):
        return self.lengthLV

    def setWidthLV(self, widthLV):
        self.widthLV = widthLV

    def getWidthLV(self):
        return self.widthLV

    def setHighLV(self, highLV):
        self.highLV = highLV

    def getHighLV(self):
        return self.highLV

    def setLengthHV(self, lenghtHV):
        self.lengthHV = lenghtHV

    def getLengthHV(self):
        return self.lengthHV

    def setWidthHV(self, widthHV):
        self.widthHV = widthHV

    def getWidthHV(self):
        return self.widthHV

    def setHighHV(self, highHV):
        self.highHV = highHV

    def getHighHV(self):
        return self.highHV

    def setDetectionLine(self, x1, y1, x2, y2):
        self.detectX1 = int(x1)
        self.detectY1 = int(y1)
        self.detectX2 = int(x2)
        self.detectY2 = int(y2)

    def getDetectionLine(self):
        return self.detectX1, self.detectY1, self.detectX2, self.detectY2

    def setRegistrationLine(self, x1, y1, x2, y2):
        self.registX1 = int(x1)
        self.registY1 = int(y1)
        self.registX2 = int(x2)
        self.registY2 = int(y2)

    def getRegistrationLine(self):
        return self.registX1, self.registY1, self.registX2, self.registY2

    def getTotalLV(self):
        return self.total_LV

    def getTotalHV(self):
        return self.total_HV

    def getFrameCount(self):
        return self.frame

    # Method Spesial
    def __init__(self, filename, frame):
        self.video_frame = frame

        # Variabel Global
        self.start_time = None
        self.width_frame = 1120
        self.height_frame = 630
        self.init_time = 5
        self.frame = 0
        self.total_LV = 0
        self.total_HV = 0
        self.totalVehicle = 0
        self.avg = 0
        self.currentListVehicle = []
        self.tempListVehicle = []
        self.pastListVehicle = []
        self.currentTrajectory = []

        # memulai Video
        self.filename = filename
        self.cap = cv2.VideoCapture(filename)
        self.statusNextFrame = True

        # inisiasi lintasan kendaraan modul
        self.vehicle = vehicleInit.vehicle
        self.trajectory = trajectoryInit.trajectory

        # Fps (frame per detik)
        self.firstFrame = 0
        self.endFrame = 0
        self.processTime = 0

        # inisiasi moving average
        _, PrimImg_frame = self.cap.read()
        PrimImg_frame = improc.cvtBGR2RGB(PrimImg_frame)
        PrimImg_frame = cv2.resize(PrimImg_frame, (self.width_frame, self.height_frame))
        self.avg = np.float32(PrimImg_frame)

    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.start(1000. / self.getFPS())
        self.timer.timeout.connect(self.timeFirstFrame)
        self.timer.timeout.connect(self.getNextStatusFrame)
        self.timer.timeout.connect(self.timeEndFrame)
        self.start_time = time.time()

        # inisiasi file
        if self.getVideoOutput():
            now = datetime.datetime.now()
            formatDate = now.strftime("%d-%m-%Y %H-%M")
            self.file = open("output/{0}.csv".format(formatDate), "a")
            if os.stat("output/{0}.csv".format(formatDate)).st_size == 0:
                self.file.write("No,Waktu,Jenis Kendaraan,Panjang,Gambar\n")

            # inisiasi folder
            path = "output"
            self.formatFolder = now.strftime("{0}/%d-%m-%Y %H-%M").format(path)
            if not os.path.isdir(self.formatFolder):
                os.makedirs(self.formatFolder)

    def stop(self):
        self.timer.stop()

    def timeFirstFrame(self):
        self.firstFrame = time.time()
        return self.firstFrame

    def timeEndFrame(self):
        self.endFrame = time.time()
        self.processTime = self.endFrame - self.firstFrame
        return self.processTime

    def deleteLater(self):
        # berhenti capture
        self.cap.release()

        # tutup file
        if self.getVideoOutput():
            self.file.write("Nama File:" + "," + str(self.filename) + "\n" +
                            "Fokus:" + "," + str(self.getFocal()) + "\n" +
                            "Sudut:" + "," + str(self.getElevated()) + "\n" +
                            "Ketinggian:" + "," + str(self.getAlt()) + "\n" +
                            "Total Kendaraan Sedang:" + "," + str(self.total_LV) + "\n" +
                            "Total Kendaraan Panjang:" + "," + str(self.total_HV) + "\n" +
                            "Total Kendaraan:" + "," + str(self.total_HV + self.total_LV) + "\n")
            self.file.flush()
            self.file.close()

        self.total_HV = 0
        self.total_LV = 0
        self.frame = 0

    def getNextStatusFrame(self):
        totalFrame = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        if self.frame == totalFrame:
            self.stop()
            self.deleteLater()
            self.statusNextFrame = False
        elif self.statusNextFrame is True:
            self.nextFrame()


    def nextFrame(self):
        initTime = time.time()
        ret, PrimImg_frame = self.cap.read()
        self.frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

        # settingan dari warna awal
        PrimResize_frame = cv2.resize(PrimImg_frame, (self.width_frame, self.height_frame))
        PrimRGB_frame = improc.cvtBGR2RGB(PrimResize_frame)

        # inisiasi background subtraction
        # awal State       : RGB - primary frame
        if self.getBackgroundSubtraction() == "MA":
            # Moving Average
            cvtScaleAbs = improc.backgroundSubtractionAverage(PrimRGB_frame, self.avg, 0.01)
            movingAverage_frame = cvtScaleAbs
            PrimGray_frame = improc.cvtRGB2GRAY(PrimRGB_frame)
            BackgroundGray_frame = improc.cvtRGB2GRAY(movingAverage_frame)
            PrimHSV_frame = cv2.cvtColor(PrimRGB_frame, cv2.COLOR_RGB2HSV)
            BackgroundHSV_frame = cv2.cvtColor(movingAverage_frame, cv2.COLOR_RGB2HSV)
            PrimHue, PrimSat, PrimVal = cv2.split(PrimHSV_frame)
            BackHue, BackSat, BackVal = cv2.split(BackgroundHSV_frame)

            # Background
            ImgDiffRGB = cv2.absdiff(PrimGray_frame, BackgroundGray_frame)
            ImgDiffHSV = cv2.absdiff(PrimVal, BackVal)
            combineRGBHSV = cv2.bitwise_or(ImgDiffRGB, ImgDiffHSV)

            # Smoothing dan
            blurLevel = 15
            (combineRGBHSV, blurLevel)
            gaussianBlur_frame = cv2.GaussianBlur(combineRGBHSV, (blurLevel, blurLevel), 0)
            # Thresholds to Binary
            thresholdLevel = 50
            _, threshold = cv2.threshold(gaussianBlur_frame, thresholdLevel, 255, cv2.THRESH_BINARY)
            bin_frame = threshold.copy()
        # deteksi dan lintasan garis
        thick = 2
        detectLine_color = (255, 0, 0)
        registLine_color = (0, 0, 255)

        detectX1, detectY1, detectX2, detectY2 = self.getDetectionLine()
        registX1, registY1, registX2, registY2 = self.getRegistrationLine()

        if self.getROI():
            cv2.line(PrimRGB_frame, (detectX1, detectY1), (detectX2, detectY2), detectLine_color, thick)
            cv2.line(PrimRGB_frame, (registX1, registY1), (registX2, registY2), registLine_color, thick)

        # Morphological Operation
        kernel = np.array([
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0]],
            dtype=np.uint8)
        morph_frame = cv2.erode(bin_frame, kernel, iterations=3)
        morph_frame = cv2.dilate(morph_frame, kernel, iterations=2)
        bin_frame = morph_frame

        # Shadow Removal
        kernel = np.array([
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0]],
            dtype=np.uint8)
        shadowThreshold = 0.1
        maskBin = cv2.merge([bin_frame, bin_frame, bin_frame])
        maskRgbAndBin = cv2.bitwise_and(PrimRGB_frame, maskBin)

        if self.getShadow():
            hsvShadowRemoval = sr.hsvPassShadowRemoval(maskRgbAndBin, shadowThreshold)
            hsvMerge = cv2.merge([hsvShadowRemoval, hsvShadowRemoval, hsvShadowRemoval])

            maskShadow = cv2.bitwise_and(maskRgbAndBin, hsvMerge)
            gaussianBlur_shadowFrame = cv2.GaussianBlur(maskShadow, (5, 5), 0)
            grayShadow = cv2.cvtColor(gaussianBlur_shadowFrame, cv2.COLOR_RGB2GRAY)
            _, thresholdShadow = cv2.threshold(grayShadow, 5, 255, cv2.THRESH_BINARY)
            dilateShadow = cv2.dilate(thresholdShadow, kernel, iterations=3)
            erodeShadow = cv2.erode(dilateShadow, kernel, iterations=1)
            bin_frame = erodeShadow
            binMerge = cv2.merge([bin_frame, bin_frame, bin_frame])
            maskShadow = cv2.bitwise_and(PrimRGB_frame, binMerge)

        # ROI
        color = (255, 255, 0)
        roiThreshold = 0
        ImgZero_frame = np.zeros((self.height_frame, self.width_frame), np.uint8)
        x1ROI = mo.funcX_line(detectX1, detectY1, registX1, registY1, detectY1)
        x2ROI = mo.funcX_line(detectX2, detectY2, registX2, registY2, detectY2)
        x3ROI = mo.funcX_line(detectX1, detectY1, registX1, registY1, self.height_frame)
        x4ROI = mo.funcX_line(detectX2, detectY2, registX2, registY2, self.height_frame)

        pts = np.array([
            [x1ROI - roiThreshold, detectY1], [x2ROI + roiThreshold, detectY2],
            [x4ROI + roiThreshold, self.height_frame], [x3ROI - roiThreshold, self.height_frame]])
        cv2.fillPoly(ImgZero_frame, [pts], color)
        roiBinary_frame = cv2.bitwise_and(ImgZero_frame, bin_frame)

        # garis Detection
        image, contours, hierarchy = cv2.findContours(roiBinary_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contoursList = len(contours)

        for i in range(0, contoursList):
            cnt = contours[i]
            areaContours = cv2.contourArea(cnt)
            xContour, yContour, widthContour, highContour = cv2.boundingRect(cnt)
            areaBoundary = widthContour * highContour

            # Pin Hole Model
            focal = self.getFocal()
            theta = self.getElevated()
            sensorHeight, sensorWidth = self.getSensorSize()
            altitude = self.getAlt()
            maxHighLV = self.getHighLV()
            maxHighHV = self.getHighHV()
            maxLengthLV = self.getLengthLV()
            maxLengthHV = self.getLengthHV()
            maxWidthHV = self.getWidthHV()

            heightInFullFrame = (self.width_frame * 2.0) / 3
            heightSurplus = (heightInFullFrame - self.height_frame) / 2
            y1Vehicle = (self.height_frame + heightSurplus) - (yContour + highContour)
            y2Vehicle = (self.height_frame + heightSurplus) - yContour
            aspectRatioHeight = (sensorWidth / self.width_frame) * heightInFullFrame
            horizontalFocal = (((focal * 1) / aspectRatioHeight) * self.height_frame)
            lengthVehicle = mo.vertikalPinHoleModel(heightInFullFrame, horizontalFocal, altitude, theta, y1Vehicle, y2Vehicle, maxHighLV, maxHighHV, maxLengthLV)
            centerVehicle = mo.centeroidPinHoleMode(heightInFullFrame, horizontalFocal, altitude, theta, y1Vehicle)
            widthVehicle = mo.horizontalPinHoleModel(self.width_frame, horizontalFocal, altitude, xContour, (xContour + widthContour), centerVehicle)

            alternative = False
            if alternative:
                fov = 160.0
                theta = 90.0 - theta
                horizontalFOV, verticalFOV = mo.transformDiagonalFOV(fov)
                focal = mo.getFocalfromFOV(self.height_frame, verticalFOV)
                lengthVehicle = mo.vertikalPinHoleModel(self.height_frame, focal, altitude, theta, y1Vehicle, y2Vehicle,
                                                    maxHighLV, maxHighHV, maxLengthLV)  ##

            # garis Boundary
            colorLV = (0, 255, 0)
            colorHV = (0, 0, 255)
            thick = 2
            size = 2
            areaThreshold = 10

            if (widthVehicle >= 1.0) and (widthVehicle <= 3.0) and (lengthVehicle >= 2) and (lengthVehicle < 18) and (areaContours >= (float(areaBoundary) * (float(areaThreshold) / 100))):
                # Get moment for centroid
                Moment = cv2.moments(cnt)
                xCentroid = int(Moment['m10'] / Moment['m00'])
                yCentroid = int(Moment['m01'] / Moment['m00'])

                # Deteksi



                if lengthVehicle <= maxLengthLV:
                    vehicleClassification = "LV"
                    color = colorLV
                else:
                    vehicleClassification = "HV"
                    color = colorHV

                if self.getBoundary():
                    cv2.rectangle(PrimRGB_frame, (xContour + widthContour, yContour + highContour), (xContour, yContour), color, thick)
                    improc.addText(bin_frame, lengthVehicle, size, xContour, (yContour - 3))

                # ciri2 kendaraan
                xPredictLeftRoad = mo.funcX_line(detectX1, detectY1, registX1, registY1, y1Vehicle)
                distLeftRoadtoVehicle = mo.horizontalPinHoleModel(self.width_frame, horizontalFocal, altitude, xPredictLeftRoad, (xContour + (widthContour / 2)), centerVehicle)
                self.currentListVehicle.append(self.vehicle(self.totalVehicle + 1 + self.currentListVehicle.__len__(), xCentroid, yCentroid, distLeftRoadtoVehicle, centerVehicle, lengthVehicle, widthVehicle, vehicleClassification, xContour, yContour, widthContour, highContour, False))
                self.currentTrajectory.append(self.trajectory(self.totalVehicle + 1 + self.currentListVehicle.__len__(), xCentroid, yCentroid))

        if self.pastListVehicle.__len__() == 0:
            self.pastListVehicle = self.currentListVehicle
        elif self.pastListVehicle.__len__() != self.currentListVehicle.__len__():
            self.pastListVehicle = self.currentListVehicle
        elif self.currentListVehicle.__len__() < self.pastListVehicle.__len__():
            self.currentListVehicle = self.pastListVehicle

        # Algoritma Hungarian
        # Hungarian algorithm by munkres
        hungarianAlgorithmStatus = True
        trackingStatus = False
        if self.pastListVehicle.__len__() != 0 and self.currentListVehicle.__len__() != 0 and hungarianAlgorithmStatus is True:
            distance = [[0 for i in range(self.pastListVehicle.__len__())]
                        for j in range(self.currentListVehicle.__len__())]

            for i in range(self.pastListVehicle.__len__()):
                for j in range(self.currentListVehicle.__len__()):
                    x1 = self.pastListVehicle[i].distLeft
                    y1 = self.pastListVehicle[i].distFront
                    x2 = self.currentListVehicle[j].distLeft
                    y2 = self.currentListVehicle[j].distFront
                    distance[j][i] = mo.euclideanDistance(x1, y1, x2, y2)
            hungarian = Munkres()
            indexes = hungarian.compute(distance)

            for row, column in indexes:
                self.currentListVehicle[row].idState = self.pastListVehicle[column].idState
            trackingStatus = True

        # cetak lintasan
        thick = 2
        size = 1
        trajectoryThreshold = 30

        if self.currentTrajectory.__len__() > trajectoryThreshold:
            self.currentTrajectory.pop(0)

        for i in range(self.currentTrajectory.__len__()):
            xTrajectory = self.currentTrajectory[i].xCoordinate
            yTrajectory = self.currentTrajectory[i].yCoordinate
            yPredictTrajectory = mo.funcY_line(registX1, registY1, registX2, registY2, xTrajectory)

            if (yTrajectory < yPredictTrajectory) and (xTrajectory >= registX1) and (xTrajectory <= registX2):
                cv2.circle(PrimRGB_frame, (xTrajectory, yTrajectory), size, (0, 255, 255), thick)

        # hitung deteksi
        font = cv2.FONT_HERSHEY_DUPLEX
        thick = 2
        size = 2
        stopGap = 200
        changeRegistLine_color = (255, 255, 255)
        changeThick = 4

        if trackingStatus is True:
            for i in range(self.currentListVehicle.__len__()):
                vehicleID = self.currentListVehicle[i].vehicleID
                xCentroid = self.currentListVehicle[i].xCoordinate
                yCentroid = self.currentListVehicle[i].yCoordinate
                yFront = self.currentListVehicle[i].yContour + self.currentListVehicle[i].highContour
                lengthVehicle = self.currentListVehicle[i].vehicleLength
                vehicleClassification = self.currentListVehicle[i].vehicleClass
                idState = self.currentListVehicle[i].idState
                yPredictRegist = mo.funcY_line(registX1, registY1, registX2, registY2, xCentroid)
                yPredictDetect = mo.funcY_line(detectX1, detectY1, detectX2, detectY2, xCentroid)
                countClass = improc.initCounting(registX1, registY1, registX2, registX2, xCentroid, yPredictRegist, vehicleClassification)

                if (yFront > yPredictDetect + stopGap) and (yFront < yPredictRegist) and (xCentroid >= registX1) and (xCentroid <= registX2) and (idState is False):
                    self.pastListVehicle[i].idState = True

                if (yFront < yPredictRegist) and (xCentroid >= registX1) and (xCentroid <= registX2):
                    cv2.circle(PrimRGB_frame, (xCentroid, yFront), size, (0, 0, 255), thick)
                    cv2.putText(PrimRGB_frame, "{0}".format(vehicleID), (xCentroid + 1, yCentroid + 1), font, 1, (0, 0, 255))

                if (yFront > yPredictRegist) and (xCentroid >= registX1) and (xCentroid <= registX2) and (idState is True):
                    if countClass == "LV":
                        self.total_LV += 1
                    elif countClass == "HV":
                        self.total_HV += 1

                    self.totalVehicle = self.total_LV + self.total_HV
                    self.pastListVehicle[i].idState = False

                    improc.addText(PrimRGB_frame, vehicleID, size, (xCentroid + 5), (yCentroid - 5))
                    cv2.line(PrimRGB_frame, (registX1, registY1), (registX2, registY2), changeRegistLine_color, changeThick)
                    print "Total LV: {0} | Total HV: {1} | class: {2} length: {3} width: {4}".format(self.total_LV, self.total_HV, countClass, lengthVehicle, widthVehicle)

                    # ambil gambar
                    xContour = self.currentListVehicle[i].xContour
                    yContour = self.currentListVehicle[i].yContour
                    widthContour = self.currentListVehicle[i].widthContour
                    highContour = self.currentListVehicle[i].highContour

                    if self.getVideoOutput():
                        now = datetime.datetime.now()
                        formatDate = now.strftime("%d%m%Y_%H%M%S")

                        formatFileName = "{0}/{1}_{2:03}_{3}.jpg".format(self.formatFolder, countClass, (self.total_LV + self.total_HV), formatDate)
                        cropping_frame = PrimResize_frame[yContour:yContour + highContour, xContour:xContour + widthContour]
                        cv2.imwrite(formatFileName, cropping_frame)

                        # simpan file ke excel
                        formatDate = now.strftime("%d:%m:%Y %H:%M:%S")
                        self.file.write(str(self.totalVehicle) + "," +
                                        str(formatDate) + "," +
                                        str(countClass) + "," +
                                        str(lengthVehicle) + "," +
                                        str(formatFileName) + "\n")
                        self.file.flush()

        # Return variable
        self.currentListVehicle = []

        # settingan dari warna awal
        if self.getVideoMode() == "RGB":
            show_frame = PrimRGB_frame
            img = QtGui.QImage(show_frame, show_frame.shape[1], show_frame.shape[0], QtGui.QImage.Format_RGB888)
            # RGB image - Format_RGB888
        else:
            show_frame = PrimSat
            img = QtGui.QImage(show_frame, show_frame.shape[1], show_frame.shape[0], QtGui.QImage.Format_RGB16)
            # Gray scale, binary image - Format_Indexed8

        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)