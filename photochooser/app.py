from PyQt5 import QtGui, QtWidgets, QtCore
import sys, glob, os, time


class App(QtWidgets.QMainWindow):
    app_height = 0
    app_width = 0

    label = None

    images = []
    image_index = 0

    def __init__(self):
        super(App, self).__init__()

        self.label = QtWidgets.QLabel(self)

        self.setWindowTitle("Photochooser v0.2.0")
        self.showMaximized()

        self.app_width = self.width()
        self.app_height = self.height()

        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFixedWidth(self.app_width)
        self.label.setFixedHeight(self.app_height)

        self.images = self.get_images()

        self.display_image(self.images[0])

    def get_images(self):
        # opens dialog and gets selected directory name
        current_dir = QtWidgets.QFileDialog().getExistingDirectory()
        # gets .jpg and .png files from current_dir
        files = []
        files.extend(glob.glob(os.path.join(current_dir, '*.jpg')))
        files.extend(glob.glob(os.path.join(current_dir, '*.png')))
        # debug print filenames from selected directory
        for file in files:
            print(file)

        return files

    def display_image(self, filename):
        # create pixmap to display image (from given filename)
        print("display_image " + filename)
        pixmap = QtGui.QPixmap(filename)
        # resize
        pixmap = pixmap.scaled(
            min(self.app_width, pixmap.width()),
            min(self.app_height, pixmap.height()),
            QtCore.Qt.KeepAspectRatio
        )
        # displays image
        self.label.setPixmap(pixmap)

        self.statusBar().showMessage(filename)

    # Decides what to do when specific keys are pressed
    def keyPressEvent(self, e):
        print("key: " + str(e.key()))
        try:
            index = self.image_index

            if e.key() == QtCore.Qt.Key_Right or e.key() == QtCore.Qt.Key_Period:
                index = self.image_index + 1
            elif e.key() == QtCore.Qt.Key_Left or e.key() == QtCore.Qt.Key_Comma:
                index = self.image_index - 1

                if index < 0:
                    raise IndexError

            self.display_image(self.images[index])

            self.image_index = index
            print("index " + str(index))
        except IndexError:
            pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    photochooser = App()
    sys.exit(app.exec_())
