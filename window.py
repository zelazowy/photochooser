#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys
from PyQt4 import QtGui, QtCore
import exifread
import re
import glob
import os


class Photochooser(QtGui.QWidget):
    dir = ''
    files = ''
    currentFileIndex = 0
    label = None

    def __init__(self):
        super(Photochooser, self).__init__()

        self.label = QtGui.QLabel(self)

        self.initFiles()

        filename = self.getFirstFile()
        self.showFile(filename)

    def initFiles(self):
        while True:
            self.files = glob.glob(os.path.join(self.openDir(), '*.jpg'))

            try:
                filename = self.files[0]
                break
            except IndexError:
                pass

    def showFile(self, filename):
        self.repaint()
        f = open(filename, 'rb')
        tags = exifread.process_file(f)

        try:
            rotationTag = tags['Image Orientation']
            print(rotationTag)

            rotation = re.search('[0-9]+', str(rotationTag)).group(0)
        except:
            rotation = 0


        pixmap = QtGui.QPixmap(filename)
        pixmap = pixmap.scaledToWidth(1200)

        transform = QtGui.QTransform()
        transform.rotate(float(rotation))

        pixmap = pixmap.transformed(transform)

        self.label.setPixmap(pixmap)

        self.resize(min(pixmap.width(), 1200), min(pixmap.height(), 800))

        # buttons
        # btn = QtGui.QPushButton('Hello World!', self)
        # btn.setToolTip('Elo')
        # btn.clicked.connect(exit)
        # btn.resize(btn.sizeHint())
        # btn.move(80, 100)

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
        if e.key() == QtCore.Qt.Key_Right:
            nextFile = self.getNextFile()
            print(nextFile)
            if False != nextFile:
                self.showFile(nextFile)
        elif e.key() == QtCore.Qt.Key_Left:
            prevFile = self.getPrevFile()
            print(prevFile)
            if False != prevFile:
                self.showFile(prevFile)

# Create an PyQT4 application object.
a = QtGui.QApplication(sys.argv)

# The QWidget widget is the base class of all user interface objects in PyQt4.
w = Photochooser()

# Set window title
w.setWindowTitle("Hello World!")





sys.exit(a.exec_())