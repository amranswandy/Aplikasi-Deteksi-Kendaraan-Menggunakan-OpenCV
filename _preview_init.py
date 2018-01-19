import cv2
# import _main_init as mainFrame
import numpy as np
import image_processing as improc

from PyQt4 import uic
from PyQt4 import QtCore
from PyQt4.QtGui import *

preview_ui = uic.loadUiType("gtk/preview.ui")[0]

class PreviewInit(QFrame, preview_ui):
    def __init__(self, filename, parent=None):
        QFrame.__init__(self, parent)
        self.setupUi(self)

        # Global variable
        self.width_frame = 720
        self.height_frame = 480
        self.filename = filename

        # Radio button
        self.radioButton_detectionLine.setChecked(True)
        self.radioButton_registrationLine.setChecked(False)

        # Set registration line
        self.setDetectionLine(0, 0, 0, 0)
        self.setRegistrationLine(0, 0, 0, 0)

        # Mulai ambil Video
        self.cap = cv2.VideoCapture(filename)
        _, PrimImg_frame = self.cap.read()
        PrimImg_frame = cv2.cvtColor(PrimImg_frame, cv2.COLOR_BGR2RGB)
        PrimImg_frame = cv2.resize(PrimImg_frame, (self.width_frame, self.height_frame))
        self.avg = np.float32(PrimImg_frame)

    def closeConfig(self):
        self.stop()
        self.cap.release()
        self.close()

    def saveConfig(self):
        # Set Registration Line
        detectX1, detectY1, detectX2, detectY2 = self.getDetectLine()
        registX1, registY1, registX2, registY2 = self.getRegistrationLine()

        print detectX1, detectY1, detectX2, detectY2
        print registX1, registY1, registX2, registY2

        self.stop()
        self.cap.release()
        self.close()

    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextframe)
        self.timer.start(1000. / 30)

    def stop(self):
        self.timer.stop()

    def deleteLater(self):
        print "stop brooo"

    def setRegistrationLine(self, x1, y1, x2, y2):
        self.lineEdit_registX1.setText(format(x1))
        self.lineEdit_registY1.setText(format(y1))
        self.lineEdit_registX2.setText(format(x2))
        self.lineEdit_registY2.setText(format(y2))

    def getRegistrationLine(self):
        registX1 = self.lineEdit_registX1.text()
        registY1 = self.lineEdit_registY1.text()
        registX2 = self.lineEdit_registX2.text()
        registY2 = self.lineEdit_registY2.text()
        return registX1, registY1, registX2, registY2

    def setDetectionLine(self, x1, y1, x2, y2):
        self.lineEdit_detectX1.setText(format(x1))
        self.lineEdit_detectY1.setText(format(y1))
        self.lineEdit_detectX2.setText(format(x2))
        self.lineEdit_detectY2.setText(format(y2))

    def getDetectLine(self):
        detectX1 = self.lineEdit_detectX1.text()
        detectY1 = self.lineEdit_detectY1.text()
        detectX2 = self.lineEdit_detectX2.text()
        detectY2 = self.lineEdit_detectY2.text()
        return detectX1, detectY1, detectX2, detectY2

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            xCoordinate = QMouseEvent.x() - 10
            yCoordinate = QMouseEvent.y() - 10
            if self.radioButton_detectionLine.isChecked():
                self.lineEdit_detectX1.setText(format(xCoordinate))
                self.lineEdit_detectY1.setText(format(yCoordinate))
            else:
                self.lineEdit_registX1.setText(format(xCoordinate))
                self.lineEdit_registY1.setText(format(yCoordinate))

            self.label_xCoordinate.setText("X: {0}".format(xCoordinate))
            self.label_yCoordinate.setText("Y: {0}".format(yCoordinate))

    def mouseReleaseEvent(self, QMouseEvent):
        xCoordinate = QMouseEvent.x() - 10
        yCoordinate = QMouseEvent.y() - 10
        if self.radioButton_detectionLine.isChecked():
            self.lineEdit_detectX2.setText(format(xCoordinate))
            self.lineEdit_detectY2.setText(format(yCoordinate))
        else:
            self.lineEdit_registX2.setText(format(xCoordinate))
            self.lineEdit_registY2.setText(format(yCoordinate))
        self.label_xCoordinate.setText("X: {0}".format(xCoordinate))
        self.label_yCoordinate.setText("Y: {0}".format(yCoordinate))

    def setTextLabelPosition(self, xCoordinate, yCoordinate):
        self.xCoordinate = xCoordinate
        self.yCoordinate = yCoordinate
        self.label_xCoordinate.setText("X: {0}".format(self.xCoordinate))
        self.label_yCoordinate.setText("Y: {0}".format(self.yCoordinate))

    def nextframe(self):
        _, PrimFrame = self.cap.read()
        PrimRGB_frame = cv2.cvtColor(PrimFrame, cv2.COLOR_BGR2RGB)
        PrimResize_frame = cv2.resize(PrimRGB_frame, (self.width_frame, self.height_frame))

        cvtScaleAbs = improc.backgroundSubtractionAverage(PrimResize_frame, self.avg, 0.01)
        movingAverage_frame = cvtScaleAbs

        if self.getRegistrationLine is not None:
            color = (255, 0, 0)
            registX1, registY1, registX2, registY2 = self.getRegistrationLine()
            registX1 = int(registX1)
            registX2 = int(registX2)
            registY1 = int(registY1)
            registY2 = int(registY2)
            cv2.line(movingAverage_frame, (registX1, registY1), (registX2, registY2), color, 1)
        if self.getDetectLine is not None:
            color = (255, 0, 255)
            detectX1, detectY1, detectX2, detectY2 = self.getDetectLine()
            detectX1 = int(detectX1)
            detectY1 = int(detectY1)
            detectX2 = int(detectX2)
            detectY2 = int(detectY2)
            cv2.line(movingAverage_frame, (detectX1, detectY1), (detectX2, detectY2), color, 1)

        show_frame = movingAverage_frame
        img = QImage(show_frame, show_frame.shape[1], show_frame.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.videoFrame.setPixmap(pix)

