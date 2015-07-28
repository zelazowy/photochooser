#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys
from PyQt4.QtGui import *
import exifread
import re

# Create an PyQT4 application object.
a = QApplication(sys.argv)

# The QWidget widget is the base class of all user interface objects in PyQt4.
w = QWidget()

# Set window size.
w.resize(320, 240)

# Set window title
w.setWindowTitle("Hello World!")

# Get filename using QFileDialog
filename = QFileDialog.getOpenFileName(w, 'Open File', '/')
# print(filename)

f = open(filename, 'rb')
tags = exifread.process_file(f)

rotationTag = tags['Image Orientation']

print(rotationTag)

rotation = re.search('[0-9]+', str(rotationTag)).group(0)

label = QLabel(w)
pixmap = QPixmap(filename)
pixmap = pixmap.scaledToWidth(1200)
# pixmap = pixmap.transformed(QTransform.rotate(rotation))

transform = QTransform()
transform.rotate(float(rotation))

pixmap = pixmap.transformed(transform)

label.setPixmap(pixmap)

w.resize(min(pixmap.width(), 1200), min(pixmap.height(), 800))

# buttons
btn = QPushButton('Hello World!', w)
btn.setToolTip('Elo')
btn.clicked.connect(exit)
btn.resize(btn.sizeHint())
btn.move(80, 100)

# Show window
w.show()

sys.exit(a.exec_())