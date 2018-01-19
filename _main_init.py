import time
import psutil
import _capture_init as cap_init

from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from _help_init import HelpInit
from _about_init import AboutInit
from _preview_init import PreviewInit
from _coordinate_init import GetCoordinate

# Interface
main_ui = uic.loadUiType("gtk/main.ui")[0]

class MainInit(QMainWindow, main_ui):
    def __init__(self, parent=None):
        # inisiasi file main interface dari QT ke Python
        QMainWindow.__init__(self, parent)

        # Variable
        self.setupUi(self)
        self.capture = None
        self.fileLoc = 0

        port_cam = ["0", "1", "2"]

        # 1. Aturan
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.setTabEnabled(1, False)
        self.tabWidget.setTabEnabled(2, True)

        # 1.1.  Video Masukkan
        self.radioButton_choseDevice.setChecked(True)
        self.radioButton_choseFile.setChecked(False)
        self.checkBox_saveOutput.setChecked(False)

        self.radioButton_choseFile.toggled.connect(self.selectFile)
        self.radioButton_choseDevice.toggled.connect(self.selectDevice)

        self.comboBox_choseDevice.setEnabled(True)
        self.comboBox_choseDevice.addItems(port_cam)
        self.comboBox_choseDevice.currentIndexChanged.connect(self.selectionDevice)

        self.label_selectFile.setText('')
        self.pushButton_selectFile.setVisible(False)
        self.pushButton_selectFile.setEnabled(False)
        self.pushButton_selectFile.clicked.connect(self.selectVideoFile)

        # 1.2.  Video Tipe
        self.radioButton_rgbVM.setChecked(True)
        # self.radioButton_binVM.setChecked(False)
        self.checkBox_showboundaryVM.setChecked(False)
        self.checkBox_showroiVM.setChecked(False)
        self.checkBox_shadowRemoval.setChecked(False)

        # self.radioButton_binVM.toggled.connect(self.selectBinary)

        # 1.3 Background Subtraction
        self.radioButton_BsMA.setChecked(True)
        # self.radioButton_BsMOG.setChecked(False)

        # 1.4   Data Input
        # 1.4.1 Camera
        # sensorType = [""]
        # croppingFactor = [""]

        self.setAlt(7.4)
        self.setElevated(72)
        self.setFps(30)
        self.setFocal(18)

        # 1.4.2 Dimensi kendaraan
        # 1.4.2.1 Light Vehicle
        self.setLengthLV(8)
        self.setWidthLV(2.1)
        self.setHighLV(1.6)
        # 1.4.2.1 Heavy Vehicle
        self.setLengthHV(30)
        self.setWidthHV(2.5)
        self.setHighHV(3.2)

        # 1.4.3 deteksi dan lintasan garis
        self.pushButton_preview.clicked.connect(self.previewVideo)
        self.pushButton_calculate.clicked.connect(self.calculateCoordinate)
        # 1.4.3.1 garis lintasan
        self.setDetectionLine("480", "122", "635", "122")
        # 1.4.3.2 Garis Lintasan
        self.setRegistrationLine("365", "424", "772", "424")

        # 1.5 Tombol bantuan dan Mulai
        self.pushButton_helpSetting.clicked.connect(self.helpSetting)
        self.pushButton_tentang.clicked.connect(self.tentang)
        self.pushButton_setSetting.clicked.connect(self.setSetting)

        # 2.    Video
        # 2.1   Video Mulai
        self.pushButton_startVideo.clicked.connect(self.startVideo)
        self.pushButton_showLog.setVisible(False)
        self.pushButton_showLog.clicked.connect(self.showLog)

        # 2.2   Ambil Gambar
        self.startThread()
        self.startCountFrame()

        # Hitung
        self.setTotalLV(0)
        self.setTotalHV(0)
        self.setFrameCount(0)


        # 3.    catatan
        # 3.1   cari
        self.dateEdit_fromDate.setDateTime(QDateTime.currentDateTime())
        self.dateEdit_fromDate.setCalendarPopup(True)

        self.dateEdit_untilDate.setDateTime(QDateTime.currentDateTime())
        self.dateEdit_untilDate.setCalendarPopup(True)

        self.pushButton_searchLog.clicked.connect(self.searchLog)
        self.pushButton_clearLog.clicked.connect(self.clearLog)

        # 3.2   tampilkan catatan
        self.setLogCountLV("0")
        self.setLogCountHV("0")

    # Set Variable
    def setAlt(self, value):
        self.lineEdit_altitudeCam.setText(format(value))

    def getAlt(self):
        return self.lineEdit_altitudeCam.text()

    def setElevated(self, value):
        self.lineEdit_elevatedCam.setText(format(value))

    def getElevated(self):
        return self.lineEdit_elevatedCam.text()

    def setFps(self, value):
        self.lineEdit_fps.setText(format(value))

    def getFps(self):
        return self.lineEdit_fps.text()

    def setFocal(self, value):
        self.lineEdit_focalCam.setText(format(value))

    def getFocal(self):
        return self.lineEdit_focalCam.text()

    def setLengthLV(self, value):
        self.lineEdit_pLV.setText(format(value))

    def getLengthLV(self):
        return self.lineEdit_pLV.text()

    def setWidthLV(self, value):
        self.lineEdit_lLV.setText(format(value))

    def getWidthLV(self):
        return self.lineEdit_lLV.text()

    def setHighLV(self, value):
        self.lineEdit_tLV.setText(format(value))

    def getHighLV(self):
        return self.lineEdit_tLV.text()

    def setLengthHV(self, value):
        self.lineEdit_pHV.setText(format(value))

    def getLengthHV(self):
        return self.lineEdit_pHV.text()

    def setWidthHV(self, value):
        self.lineEdit_lHV.setText(format(value))

    def getWidthHV(self):
        return self.lineEdit_lHV.text()

    def setHighHV(self, value):
        self.lineEdit_tHV.setText(format(value))

    def getHighHV(self):
        return self.lineEdit_tHV.text()

    def setTotalLV(self, value):
        self.label_countShortVehicle.setText(format(value))

    def setTotalHV(self, value):
        self.label_countLongVehicle.setText(format(value))

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

    def setFrameCount(self, value):
        self.label_frameCount.setText(": {0}".format(value))

    def setLogCountLV(self, value):
        self.label_logcountShortVehicle.setText(value)

    def setLogCountHV(self, value):
        self.label_logcountLongVehicle.setText(value)

    def setCPUProcess(self):
        value = psutil.cpu_percent()
        self.progressBar_cpuPercentage.setValue(value)

    # Get Variable
    def getVideoMode(self):
        if self.radioButton_rgbVM.isChecked():
            video_mode = "RGB"
        return video_mode

    def getSensoryType(self):
        select = self.comboBox_choseDevice.currentIndex()
        if select == 0:
            sensorHeight = 15.4
            sensorWidth = 23.1
        else:
            sensorHeight = 0
            sensorWidth = 0

        return sensorHeight, sensorWidth

    def getSavingOutput(self):
        return self.checkBox_saveOutput.isChecked()

    def getBoundary(self):
        return self.checkBox_showboundaryVM.isChecked()

    def getRoi(self):
        return self.checkBox_showroiVM.isChecked()

    def getShadowRemoval(self):
        return self.checkBox_shadowRemoval.isChecked()

    def getBackgroundSubtraction(self):
        if self.radioButton_BsMA.isChecked():
            background_subtraction = "MA"
        return background_subtraction

    def getTotalVehicleFromVideo(self):
        if self.capture:
            totalLV = self.capture.getTotalLV()
            totalHV = self.capture.getTotalHV()
            self.setTotalLV(totalLV)
            self.setTotalHV(totalHV)

    def getFrameCountFromVideo(self):
        if self.capture:
            frame = self.capture.getFrameCount()
            self.setFrameCount(frame)

    def startThread(self):
        self.timerThread = QTimer()
        self.timerThread.timeout.connect(self.setCPUProcess)
        self.timerThread.timeout.connect(self.getTotalVehicleFromVideo)
        self.timerThread.start(800)

    def startCountFrame(self):
        self.timerFrame = QTimer()
        fps = int(self.getFps())
        self.timerFrame.timeout.connect(self.getFrameCountFromVideo)
        self.timerFrame.start(1000. / fps)

    # Awal
    def selectVideoFile(self):
        file_filter = "Movie (*.mp4 *.avi *.mkv *.MOV)"
        videoFilename = QFileDialog.getOpenFileName(self, "Buka Folder File Video", 'samples', file_filter, None,
                                                    QFileDialog.DontUseNativeDialog)
        if videoFilename:
            print "file yg di select {0}".format(videoFilename)
            self.label_selectFile.setText(format(videoFilename))

            self.fileLoc = format(videoFilename)
            return self.fileLoc

    def selectionDevice(self):
        select = self.comboBox_choseDevice.currentText()
        print "Indeks Seleksi", select

        self.fileLoc = int(select)
        return self.fileLoc

    def selectFile(self, enabled):
        if enabled:
            self.pushButton_selectFile.setEnabled(True)
            self.selectVideoFile()

            self.pushButton_selectFile.setVisible(True)
        else:
            self.pushButton_selectFile.setEnabled(False)

    def selectBinary(self, enabled):
        if enabled:
            self.checkBox_showboundaryVM.setChecked(False)
            self.checkBox_showroiVM.setChecked(False)
            self.checkBox_showboundaryVM.setEnabled(False)
            self.checkBox_showroiVM.setEnabled(False)
        else:
            self.checkBox_showboundaryVM.setEnabled(True)
            self.checkBox_showroiVM.setEnabled(True)

    def selectDevice(self, enabled):
        if enabled:
            self.comboBox_choseDevice.setEnabled(True)
            self.fileLoc = 0
        else:
            self.comboBox_choseDevice.setEnabled(False)

    def setSetting(self):
        # Get video mode
        video_mode = self.getVideoMode()
        savingOutput = self.getSavingOutput()
        boundary = self.getBoundary()
        roi = self.getRoi()
        shadow = self.getShadowRemoval()

        # Get background subtraction
        background_subtraction = self.getBackgroundSubtraction()

        # Aturan Kamera
        alt = float(self.getAlt())
        elevated = float(self.getElevated())
        fps = float(self.getFps())
        sensorHeight, sensorWidth = self.getSensoryType()
        focal = float(self.getFocal())

        # Dimensi kendaraan sedang
        length_LV = float(self.getLengthLV())
        width_LV = float(self.getWidthLV())
        high_LV = float(self.getHighLV())

        # Dimensi kendaraan panjang
        length_HV = float(self.getLengthHV())
        width_HV = float(self.getWidthHV())
        high_HV = float(self.getHighHV())

        # deteksi dan lintasan garis
        detectX1, detectY1, detectX2, detectY2 = self.getDetectLine()
        registX1, registY1, registX2, registY2 = self.getRegistrationLine()

        print "Camera Input"
        print "video input: {0}".format(self.fileLoc)
        print "video mode: {0}".format(video_mode)
        print "saving output: {0}".format(savingOutput)
        print "background subtraction: {0}".format(background_subtraction)
        print "boundary: {0} | roi: {1} | shadow removal: {2}".format(boundary, roi, shadow)
        print "sensor height: {0} | sensor width: {1}".format(sensorHeight, sensorWidth)
        print "alt: {0} | elevated: {1} | fps: {2} | focal:{3}".format(alt, elevated, fps, focal)
        print "Vehicle Input"
        print "LV >> length: {0} | width: {1} | high: {2}".format(length_LV, width_LV, high_LV)
        print "HV >> length: {0} | width: {1} | high: {2}".format(length_HV, width_HV, high_HV)
        print "Registration and Detection Line"
        print "Detection Line >> ({0},{1}) | ({2},{3})".format(detectX1, detectY1, detectX2, detectY2)
        print "Registration Line >> ({0},{1}) | ({2},{3})".format(registX1, registY1, registX2, registY2)
        time.sleep(1)

        self.tabWidget.setTabEnabled(1, True)
        self.tabWidget.setCurrentIndex(1)

    def helpSetting(self):
        title = "UP. SPLL Dishub DKI Jakarta"
        filename = "conf/help.txt"

        print "Buka UI Bantuan"
        self.help_win = HelpInit(title, filename, None)
        self.help_win.show()

    def tentang(self):
        title = "UP. SPLL Dishub DKI Jakarta"
        filename = "conf/about.txt"

        print "Buka UI Tentang"
        self.help_win = AboutInit(title, filename, None)
        self.help_win.show()

    def previewVideo(self):
        self.preview = PreviewInit(self.fileLoc)
        self.preview.start()
        self.preview.show()

    def calculateCoordinate(self):
        # Variable
        altitude = float(self.getAlt())
        focal = float(self.getFocal())
        theta = int(self.getElevated())

        # Set threshold Jarak antara lintasan dan deteksi garis
        distanceRegistrationLine = 1.5
        distanceDetectionLine = 2 * float(self.getLengthHV())

        self.getCoordinate = GetCoordinate(altitude, focal, theta)
        OB = self.getCoordinate.getDistanceOB()

        # Ambil jarak Lreg and Ldet
        Lreg = OB + distanceRegistrationLine
        Ldet = OB + distanceRegistrationLine + distanceDetectionLine

        # Get coordinate Yreg and Ydet
        Yreg = int(self.getCoordinate.getCoordinate(Lreg))
        Ydet = int(self.getCoordinate.getCoordinate(Ldet))

        # Set to variable detection line and registration line
        detectX1, detectY1, detectX2, detectY2 = self.getDetectLine()
        registX1, registY1, registX2, registY2 = self.getRegistrationLine()
        self.setRegistrationLine(registX1, Yreg, registX2, Yreg)
        self.setDetectionLine(detectX1, Ydet, detectX2, Ydet)

        print "registration line distance: {0} | detection line distance: {1}".format(distanceRegistrationLine, distanceDetectionLine)
        print "distance |OB|: {0}".format(OB)
        print "distance Lreg: {0} | distance Ldet :{1}".format(Lreg, Ldet)
        print "Coordinate Yreg: {0} | Ydet: {1}".format(Yreg, Ydet)

    # Function Tab 2. Proses
    def startVideo(self):
        # Get video mode
        video_mode = self.getVideoMode()
        savingOutput = self.getSavingOutput()
        boundary = self.getBoundary()
        roi = self.getRoi()
        shadow = self.getShadowRemoval()

        # Get background subtraction
        background_subtraction = self.getBackgroundSubtraction()

        # Camera
        alt = float(self.getAlt())
        elevated = int(self.getElevated())
        fps = float(self.getFps())
        sensorHeight, sensorWidth = self.getSensoryType()
        focal = float(self.getFocal())

        # Light vehicle dimension
        length_LV = float(self.getLengthLV())
        width_LV = float(self.getWidthLV())
        high_LV = float(self.getHighLV())

        # Heavy vehicle dimension
        length_HV = float(self.getLengthHV())
        width_HV = float(self.getWidthHV())
        high_HV = float(self.getHighHV())

        # Registration and detection line
        detectX1, detectY1, detectX2, detectY2 = self.getDetectLine()
        registX1, registY1, registX2, registY2 = self.getRegistrationLine()

        self.tabWidget.setTabEnabled(0, True)
        self.tabWidget.setTabEnabled(1, True)
        self.tabWidget.setCurrentIndex(1)

        time.sleep(1)

        if not self.capture:
            self.capture = cap_init.QtCapture(self.fileLoc, self.video_frame)

            self.pushButton_pauseVideo.clicked.connect(self.capture.stop)
            self.pushButton_stopVideo.clicked.connect(self.stopVideo)
            self.tabWidget.setTabEnabled(2, False)

            self.capture.setVideoMode(video_mode)
            self.capture.setVideoOutput(savingOutput)
            self.capture.setBackgroundSubtraction(background_subtraction)
            self.capture.setROI(roi)
            self.capture.setBoundary(boundary)
            self.capture.setShadow(shadow)

            self.capture.setFPS(fps)
            self.capture.setAlt(alt)
            self.capture.setElevated(elevated)
            self.capture.setFocal(focal)
            self.capture.setSensorSize(sensorHeight, sensorWidth)

            self.capture.setLengthLV(length_LV)
            self.capture.setWidthLV(width_LV)
            self.capture.setHighLV(high_LV)

            self.capture.setLengthHV(length_HV)
            self.capture.setWidthHV(width_HV)
            self.capture.setHighHV(high_HV)

            self.capture.setDetectionLine(detectX1, detectY1, detectX2, detectY2)
            self.capture.setRegistrationLine(registX1, registY1, registX2, registY2)

        self.capture.start()

    def stopVideo(self):
        if self.capture:
            self.capture.stop()
            time.sleep(0.1)
            self.capture.deleteLater()
            self.capture = None

        self.tabWidget.setTabEnabled(0, True)
        self.pushButton_showLog.setVisible(True)

    def showLog(self):
        time.sleep(1)

        self.tabWidget.setTabEnabled(2, True)
        self.tabWidget.setCurrentIndex(2)

    # Function Tab 3. Catatan
    def searchLog(self):
        hLabel = ["No", "Date", "Time", "Type", "Speed", "Picture"]
        row = 4
        column = 6

        fromDate = self.dateEdit_untilDate.date().toPyDate()
        untilDate = self.dateEdit_untilDate.date().toPyDate()

        self.tableWidget_searchLog.setRowCount(row)
        self.tableWidget_searchLog.setColumnCount(column)
        self.tableWidget_searchLog.setHorizontalHeaderLabels(hLabel)

        self.tableWidget_searchLog.setItem(0, 0, QTableWidgetItem("Item (0,0)"))
        self.tableWidget_searchLog.setItem(0, 1, QTableWidgetItem("Item (3,0)"))
        self.tableWidget_searchLog.setItem(2, 3, QTableWidgetItem("Item (1,0)"))

        print "mulai dari tanggal {0}".format(fromDate)
        print "hingga tanggal {0}".format(untilDate)

        self.label_logcountShortVehicle.setText("20")
        self.label_logcountLongVehicle.setText("100")

    def clearLog(self):
        self.tableWidget_searchLog.clear()

        hLabel = ["No", "Date", "Time", "Type", "Speed", "Picture"]
        self.tableWidget_searchLog.setHorizontalHeaderLabels(hLabel)

        self.label_logcountShortVehicle.setText("0")
        self.label_logcountLongVehicle.setText("0")
