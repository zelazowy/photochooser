import sys
from PyQt4 import QtGui, QtCore
import exifread
import re
import glob
import os
import shutil


class Photochooser(QtGui.QWidget):
    WIDTH = 1200
    HEIGHT = 800

    dir = ''
    copyDir = ''
    deleteDir = ''
    files = []
    currentFileIndex = 0
    currentFile = ''
    label = None

    # buttons
    copyBtn = None
    deleteBtn = None
    softDeleteBtn = None

    def __init__(self):
        super(Photochooser, self).__init__()

        self.label = QtGui.QLabel(self)

        self.initButtons()
        self.initFiles()

        self.showFile(self.getFirstFile())

    def initFiles(self):
        while True:
            currentDir = self.openDir()
            self.files = glob.glob(os.path.join(currentDir, '*.jpg'))

            # if dir contains any images then break, continue choosing dir otherwise
            if 0 < len(self.files):
                self.copyDir = os.path.join(currentDir, 'copy')
                self.deleteDir = os.path.join(currentDir, 'delete')
                print(self.copyDir)
                break

    def initButtons(self):
        # buttons
        self.copyBtn = QtGui.QPushButton('Copy!', self)
        self.copyBtn.clicked.connect(lambda: self.copyPhoto())
        self.copyBtn.resize(self.copyBtn.sizeHint())
        self.copyBtn.move(5, 5)

        # prevents button from getting focused, required for arrow support in windows
        self.copyBtn.setFocusPolicy(QtCore.Qt.NoFocus)

        self.deleteBtn = QtGui.QPushButton('Delete!', self)
        self.deleteBtn.clicked.connect(lambda: self.deletePhoto())
        self.deleteBtn.resize(self.deleteBtn.sizeHint())
        self.deleteBtn.move(5, 30)

        # prevents button from getting focused, required for arrow support in windows
        self.deleteBtn.setFocusPolicy(QtCore.Qt.NoFocus)

        self.softDeleteBtn = QtGui.QPushButton('Delete?', self)
        self.softDeleteBtn.clicked.connect(lambda: self.softDeletePhoto())
        self.softDeleteBtn.resize(self.softDeleteBtn.sizeHint())
        self.softDeleteBtn.move(5, 55)

        # prevents button from getting focused, required for arrow support in windows
        self.softDeleteBtn.setFocusPolicy(QtCore.Qt.NoFocus)

    def resetButtons(self):
        self.copyBtn.setText('Copy!')
        self.deleteBtn.setText('Delete!')
        self.softDeleteBtn.setText('Delete?')

    def showFile(self, filename):
        self.resetButtons()

        self.currentFile = filename

        f = open(filename, 'rb')

        pixmap = QtGui.QPixmap(filename)
        pixmap = pixmap.scaledToWidth(self.WIDTH)

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
        self.resize(min(pixmap.width(), self.WIDTH), min(pixmap.height(), self.HEIGHT))

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
        if 0 > self.currentFileIndex - 1:
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
        elif e.key() == QtCore.Qt.Key_D:
            self.softDeletePhoto()
        elif e.key() == QtCore.Qt.Key_Backspace:
            self.deletePhoto()

        QtGui.QWidget.keyPressEvent(self, e)

    def copyPhoto(self):
        if not os.path.exists(self.copyDir):
            os.makedirs(self.copyDir)

        shutil.copy2(self.currentFile, self.copyDir)

        self.copyBtn.setText('Copied')

    def softDeletePhoto(self):
        if not os.path.exists(self.deleteDir):
            os.makedirs(self.deleteDir)

        shutil.move(self.currentFile, self.deleteDir)
        self.__afterDeletePhoto()

        self.softDeleteBtn.setText('Deleted')

    def deletePhoto(self):
        os.remove(self.currentFile)
        self.__afterDeletePhoto()

        self.deleteBtn.setText('Deleted')

    def __afterDeletePhoto(self):
        del self.files[self.currentFileIndex]
        # decrement current file index, because deleting file from list moves all next files one index down
        # now getting next file would get proper next file
        self.currentFileIndex -= 1

        nextFile = self.getNextFile()
        if False != nextFile:
            self.showFile(nextFile)
        else:
            # its a little tricky, but to get previous file the index must be incremented so getting prev file wold get proper previous file
            self.currentFileIndex += 1

            prevFile = self.getPrevFile()
            if False != prevFile:
                self.showFile(prevFile)
            else:
                t = QtGui.QMessageBox.information(
                    self,
                    'No files in directory',
                    'Chosen directory does not contain any images',
                    QtGui.QMessageBox.Ok
                )
                print(t)
                exit()

# Create an PyQT4 application object.
a = QtGui.QApplication(sys.argv)

# The QWidget widget is the base class of all user interface objects in PyQt4.
w = Photochooser()

# Set window title
w.setWindowTitle("Photo Chooser")

sys.exit(a.exec_())
