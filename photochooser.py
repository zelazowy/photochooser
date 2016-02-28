import sys
from PyQt4 import QtGui, QtCore
import exifread
import re
import glob
import os
import shutil


class Photochooser(QtGui.QWidget):
    app_width = 1200
    app_height = 800

    dir = ''
    copy_dir = ''
    delete_dir = ''
    files = []
    current_file_index = 0
    current_file = ''
    label = None

    # buttons
    copy_btn = None
    delete_btn = None
    soft_delete_btn = None

    # QWidget init
    def __init__(self, screen_width, screen_height):
        super(Photochooser, self).__init__()

        self.setWindowTitle("Photo Chooser")

        self.app_width = screen_width
        self.app_height = screen_height

        self.init_app()

    # Initializes application
    def init_app(self):
        self.label = QtGui.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.init_buttons()
        self.init_files()

        # show first file
        self.show_file(self.files[0])

        self.showMaximized()

        # once window is maximized size of label can be set to window size
        self.label.setFixedWidth(self.width())
        self.label.setFixedHeight(self.height())

    # Displays directory choose dialog and puts into self.files list all .jpg and .png files
    def init_files(self):
        while True:
            current_dir = QtGui.QFileDialog.getExistingDirectory()
            self.files.extend(glob.glob(os.path.join(current_dir, '*.jpg')))
            self.files.extend(glob.glob(os.path.join(current_dir, '*.png')))

            # if dir contains any images then break, continue choosing dir otherwise
            if 0 < len(self.files):
                self.copy_dir = os.path.join(current_dir, 'copy')
                self.delete_dir = os.path.join(current_dir, 'delete')
                print(self.copy_dir)
                break

    # Initializes app buttons: copy, delete and delete?
    def init_buttons(self):
        # buttons
        self.copy_btn = QtGui.QPushButton('Copy!', self)
        self.copy_btn.clicked.connect(lambda: self.copy_photo())
        self.copy_btn.resize(self.copy_btn.sizeHint())
        self.copy_btn.move(5, 5)

        # prevents button from getting focused, required for arrow support in windows
        self.copy_btn.setFocusPolicy(QtCore.Qt.NoFocus)

        self.delete_btn = QtGui.QPushButton('Delete!', self)
        self.delete_btn.clicked.connect(lambda: self.delete_photo())
        self.delete_btn.resize(self.delete_btn.sizeHint())
        self.delete_btn.move(5, 30)

        # prevents button from getting focused, required for arrow support in windows
        self.delete_btn.setFocusPolicy(QtCore.Qt.NoFocus)

        self.soft_delete_btn = QtGui.QPushButton('Delete?', self)
        self.soft_delete_btn.clicked.connect(lambda: self.soft_delete_photo())
        self.soft_delete_btn.resize(self.soft_delete_btn.sizeHint())
        self.soft_delete_btn.move(5, 55)

        # prevents button from getting focused, required for arrow support in windows
        self.soft_delete_btn.setFocusPolicy(QtCore.Qt.NoFocus)

    # Resets buttons to initial state before every image change
    def reset_buttons(self):
        self.copy_btn.setText('Copy!')
        self.delete_btn.setText('Delete!')
        self.soft_delete_btn.setText('Delete?')

    # Shows file in application: scaled and centered
    def show_file(self, filename):
        self.reset_buttons()

        self.current_file = filename

        f = open(filename, 'rb')

        pixmap = QtGui.QPixmap(filename)

        try:
            tags = exifread.process_file(f)
            rotation_tag = tags['Image Orientation']

            rotation = re.search('[0-9]+', str(rotation_tag)).group(0)
            transform = QtGui.QTransform()
            transform.rotate(float(rotation))
            pixmap = pixmap.transformed(transform)
        except:
            pass

        # resize
        pixmap = pixmap.scaled(
            min(self.app_width, pixmap.width()),
            min(self.app_height, pixmap.height()),
            QtCore.Qt.KeepAspectRatio
        )

        self.label.setPixmap(pixmap)

    # Gets next file or False if current was the last one
    def get_next_file(self):
        try:
            next_file = self.files[self.current_file_index + 1]
            self.current_file_index += 1

            return next_file
        except:
            QtGui.QMessageBox.information(
                self,
                'No more files in directory',
                'That was the last one photo in directory',
                QtGui.QMessageBox.Ok
            )

            return False

    # Gets previous file or False if current was the first one
    def get_prev_file(self):
        if 0 > self.current_file_index - 1:
            return False

        try:
            prev_file = self.files[self.current_file_index - 1]
            self.current_file_index -= 1

            return prev_file
        except:
            return False

    # Decides what to do when specific keys are pressed
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Right or e.key() == QtCore.Qt.Key_Period:
            next_file = self.get_next_file()
            if False != next_file:
                self.show_file(next_file)
        elif e.key() == QtCore.Qt.Key_Left or e.key() == QtCore.Qt.Key_Comma:
            prev_file = self.get_prev_file()
            if False != prev_file:
                self.show_file(prev_file)
        elif e.key() == QtCore.Qt.Key_C:
            self.copy_photo()
        elif e.key() == QtCore.Qt.Key_D:
            self.soft_delete_photo()
        elif e.key() == QtCore.Qt.Key_Backspace:
            self.delete_photo()

        QtGui.QWidget.keyPressEvent(self, e)

    # Copies photo to subdirectory
    def copy_photo(self):
        if not os.path.exists(self.copy_dir):
            os.makedirs(self.copy_dir)

        shutil.copy2(self.current_file, self.copy_dir)

        self.copy_btn.setText('Copied')

    # Moves photo to "delete" directory when user is not certain if she/he wants to delete photo
    def soft_delete_photo(self):
        if not os.path.exists(self.delete_dir):
            os.makedirs(self.delete_dir)

        shutil.move(self.current_file, self.delete_dir)
        self.__after_delete_photo()

        self.soft_delete_btn.setText('Deleted')

    # Deletes photo
    def delete_photo(self):
        os.remove(self.current_file)
        self.__after_delete_photo()

        self.delete_btn.setText('Deleted')

    # Contains all actions that must be triggered after photo was deleted: remove file from self.files list, displays
    # next or previous photo according to current photo position in list
    def __after_delete_photo(self):
        del self.files[self.current_file_index]
        # decrement current file index, because deleting file from list moves all next files one index down
        # now getting next file would get proper next file
        self.current_file_index -= 1

        next_file = self.get_next_file()
        if next_file:
            self.show_file(next_file)
        else:
            # its a little tricky, but to get previous file the index must be incremented so getting prev file wold get
            # proper previous file
            self.current_file_index += 1

            prev_file = self.get_prev_file()
            if prev_file:
                self.show_file(prev_file)
            else:
                QtGui.QMessageBox.information(
                    self,
                    'No files in directory',
                    'Chosen directory does not contain any images',
                    QtGui.QMessageBox.Ok
                )
                exit()


# Create an PyQT4 application object.
a = QtGui.QApplication(sys.argv)

# Get screen resolution, useful to calculate scale factor for photos
screen_resolution = a.desktop().screenGeometry()
screen_width, screen_height = screen_resolution.width(), screen_resolution.height()

# Create new instance of Photochooser class
w = Photochooser(screen_width, screen_height)

sys.exit(a.exec_())
