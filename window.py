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

    def __init__(self):
        super(Photochooser, self).__init__()

        filename = self.getFirstFile()
        self.showFile(filename)

    def showFile(self, filename):
        f = open(filename, 'rb')
        tags = exifread.process_file(f)

        try:
            rotationTag = tags['Image Orientation']
            print(rotationTag)

            rotation = re.search('[0-9]+', str(rotationTag)).group(0)
        except:
            rotation = 0

        label = QtGui.QLabel(self)
        pixmap = QtGui.QPixmap(filename)
        pixmap = pixmap.scaledToWidth(1200)
        # pixmap = pixmap.transformed(QTransform.rotate(rotation))

        transform = QtGui.QTransform()
        transform.rotate(float(rotation))

        pixmap = pixmap.transformed(transform)

        label.setPixmap(pixmap)

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
        while True:
            self.files = glob.glob(os.path.join(self.openDir(), '*.jpg'))

            try:
                filename = self.files[0]
                break
            except IndexError:
                pass

        return filename

    def openDir(self):
        return QtGui.QFileDialog.getExistingDirectory()

# Create an PyQT4 application object.
a = QtGui.QApplication(sys.argv)

# The QWidget widget is the base class of all user interface objects in PyQt4.
w = Photochooser()

# Set window size.
w.resize(320, 240)

# Set window title
w.setWindowTitle("Hello World!")





sys.exit(a.exec_())