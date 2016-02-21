import sys
from PyQt4 import QtGui, QtCore
import exifread
import re
import glob
import os
import shutil


class Photochooser(QtGui.QWidget):
    dir = ''
    copyDir = ''
    files = ''
    currentFileIndex = 0
    currentFile = ''
    label = None
    copyBtn = None

    def __init__(self):
        super(Photochooser, self).__init__()

        self.label = QtGui.QLabel(self)

        self.initButton()
        self.initFiles()

        self.showFile(self.getFirstFile())

    def initFiles(self):
        while True:
            currentDir = self.openDir()
            self.files = glob.glob(os.path.join(currentDir, '*.jpg'))

            # if dir contains any images then break, continue choosing dir otherwise
            if 0 < len(self.files):
                self.copyDir = os.path.join(currentDir, 'copy')
                print(self.copyDir)
                break

    def initButton(self):
        # buttons
        self.copyBtn = QtGui.QPushButton('Copy!', self)
        self.copyBtn.clicked.connect(lambda: self.copyPhoto())
        self.copyBtn.resize(self.copyBtn.sizeHint())
        self.copyBtn.move(5, 5)

        # prevents button from getting ficused, required for arrow support in windows
        self.copyBtn.setFocusPolicy(QtCore.Qt.NoFocus)

    def showFile(self, filename):
        self.copyBtn.setText('Copy!')

        self.currentFile = filename

        f = open(filename, 'rb')

        pixmap = QtGui.QPixmap(filename)
        pixmap = pixmap.scaledToWidth(1200)

        try:
            tags = exifread.process_file(f)
            rotationTag = tags['Image Orientation']
            # print(rotationTag)

            rotation = re.search('[0-9]+', str(rotationTag)).group(0)

            transform = QtGui.QTransform()
            transform.rotate(float(rotation))


            pixmap = pixmap.transformed(transform)
        except:
            pass

        self.label.setPixmap(pixmap)
        self.resize(min(pixmap.width(), 1200), min(pixmap.height(), 800))

        # Show window
        self.show()

    def getFirstFile(self):
        return self.files[0]

    def getNextFile(self):
        try:
            nextFile = self.files[self.currentFileIndex + 1]
            self.currentFileIndex += 1

            return nextFile
        except:
            return False

    def getPrevFile(self):
        if 0 >= self.currentFileIndex - 1:
            return False

        try:
            prevFile = self.files[self.currentFileIndex - 1]
            self.currentFileIndex -= 1

            return prevFile
        except:
            return False

    def openDir(self):
        return QtGui.QFileDialog.getExistingDirectory()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Right or e.key() == QtCore.Qt.Key_Period:
            nextFile = self.getNextFile()
            # print(nextFile)
            if False != nextFile:
                self.showFile(nextFile)
        elif e.key() == QtCore.Qt.Key_Left or e.key() == QtCore.Qt.Key_Comma:
            prevFile = self.getPrevFile()
            # print(prevFile)
            if False != prevFile:
                self.showFile(prevFile)
        elif e.key() == QtCore.Qt.Key_C:
            self.copyPhoto()

        QtGui.QWidget.keyPressEvent(self, e)

    def copyPhoto(self):
        if not os.path.exists(self.copyDir):
            os.makedirs(self.copyDir)

        shutil.copy2(self.currentFile, self.copyDir)

        self.copyBtn.setText('Copied')

# Create an PyQT4 application object.
a = QtGui.QApplication(sys.argv)

# The QWidget widget is the base class of all user interface objects in PyQt4.
w = Photochooser()

# Set window title
w.setWindowTitle("Photo Chooser")

sys.exit(a.exec_())
