from PyQt5 import QtGui, QtWidgets, QtCore
import sys, glob, os, functools

DIR_PREV = "prev"
DIR_NEXT = "next"
DIR_FIRST = "first"
DIR_LAST = "last"

class App(QtWidgets.QMainWindow):
    image_manager = None

    app_width = 0
    app_height = 0

    label = None

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

        self.image_manager = ImageManager()

        self.init_toolbar()

        # displays photochooser logo
        self.display_image("../assets/photochooser_camera.png")

        self.image_manager.init_images()
        self.change_image(DIR_FIRST)

        self.activateWindow()
        # sets focus on main window

    def init_toolbar(self):
        toolbar = self.addToolBar("tb")

        exitAction = QtWidgets.QAction(QtGui.QIcon("../assets/icon_exit.png"), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(QtWidgets.qApp.quit)
        toolbar.addAction(exitAction)

        prevAction = QtWidgets.QAction(QtGui.QIcon("../assets/icon_prev.png"), 'Previous image', self)
        prevAction.triggered.connect(functools.partial(self.change_image, DIR_PREV))
        toolbar.addAction(prevAction)

        nextAction = QtWidgets.QAction(QtGui.QIcon("../assets/icon_next.png"), 'Next image', self)
        nextAction.triggered.connect(functools.partial(self.change_image, DIR_NEXT))
        toolbar.addAction(nextAction)

    def display_image(self, filename):
        # create pixmap to display image (from given filename)
        pixmap = QtGui.QPixmap(filename)
        # resize
        pixmap = pixmap.scaled(
            min(self.app_width, pixmap.width()),
            min(self.app_height, pixmap.height()),
            QtCore.Qt.KeepAspectRatio
        )
        # displays image
        self.label.setPixmap(pixmap)

    def display_statusbar(self, filename):
        self.statusBar().showMessage(
            "[%d/%d] %s" % (self.image_manager.display_index, self.image_manager.count, filename)
        )

    # Decides what to do when specific keys are pressed
    def keyPressEvent(self, e):
        key = e.key()
        direction = DIR_NEXT
        if key == QtCore.Qt.Key_Right:
            direction = DIR_NEXT
        elif key == QtCore.Qt.Key_Left:
            direction = DIR_PREV

        self.change_image(direction=direction)

    # controls image change
    def change_image(self, direction):
        filename = self.image_manager.change_image(direction)

        if not filename:
            return

        self.display_image(filename)
        self.display_statusbar(filename)


class ImageManager(object):
    images = []
    image_index = 0
    count = 0
    display_index = 1

    def init_images(self):
        self.images = FilesManager().get_images()
        self.count = len(self.images)

    def change_image(self, direction):
        try:
            if direction == DIR_PREV:
                index = self.image_index - 1

                if index < 0:
                    raise IndexError
            elif direction == DIR_NEXT:
                index = self.image_index + 1
            elif direction == DIR_FIRST:
                index = 0
            else:
                raise RuntimeError

            filename = self.images[index]

            self.image_index = index
            self.display_index = self.image_index + 1

            return filename
        except IndexError:
            return False


class FilesManager(object):
    @staticmethod
    def get_images():
        # opens dialog and gets selected directory name
        current_dir = QtWidgets.QFileDialog().getExistingDirectory()
        # gets .jpg and .png files from current_dir
        files = []
        files.extend(glob.glob(os.path.join(current_dir, '*.jpg')))
        files.extend(glob.glob(os.path.join(current_dir, '*.png')))

        return files


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    photochooser = App()
    sys.exit(app.exec_())
