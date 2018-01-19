import _main_init
import sys
from PyQt4.QtGui import *

App = QApplication(sys.argv)
# App.setStyle('cleanlooks')
myMainWindow = _main_init.MainInit(None)
myMainWindow.show()
App.exec_()
