from PyQt5 import QtGui, QtWidgets, QtCore
import sys, glob, os, functools, exifread, re

DIR_PREV = "prev"
DIR_NEXT = "next"
DIR_FIRST = "first"
DIR_LAST = "last"

class App(QtWidgets.QMainWindow):
    image_manager = None
    filename = None
    action = None

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
        self.filename = "../assets/photochooser_camera.png"
        self.refresh()

        self.image_manager.init_images()
        self.change_image(DIR_FIRST)

        self.activateWindow()
        # sets focus on main window

    def init_toolbar(self):
        toolbar = self.addToolBar("tb")

        exit_action = QtWidgets.QAction(QtGui.QIcon("../assets/icon_exit.png"), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(QtWidgets.qApp.quit)
        toolbar.addAction(exit_action)

        prev_action = QtWidgets.QAction(QtGui.QIcon("../assets/icon_prev.png"), 'Prev', self)
        prev_action.triggered.connect(functools.partial(self.change_image, DIR_PREV))
        toolbar.addAction(prev_action)

        next_action = QtWidgets.QAction(QtGui.QIcon("../assets/icon_next.png"), 'Next', self)
        next_action.triggered.connect(functools.partial(self.change_image, DIR_NEXT))
        toolbar.addAction(next_action)

        love_action = QtWidgets.QAction(QtGui.QIcon("../assets/icon_love.png"), 'Love', self)
        love_action.triggered.connect(self.love_image)
        toolbar.addAction(love_action)

        delete_action = QtWidgets.QAction(QtGui.QIcon("../assets/icon_trash.png"), 'Next image', self)
        delete_action.triggered.connect(self.delete_image)
        toolbar.addAction(delete_action)

    def prepare_image(self, filename):
        # create pixmap to display image (from given filename)
        pixmap = QtGui.QPixmap(filename)

        try:
            with open(filename, 'rb') as file:
                tags = exifread.process_file(file)

                rotation_tag = tags['Image Orientation']
                rotation = re.search('[0-9]+', str(rotation_tag)).group(0)

                print(rotation)

                transform = QtGui.QTransform()
                transform.rotate(float(rotation))
                pixmap = pixmap.transformed(transform)
        except:
            print("ups")
            pass

        # resize
        pixmap = pixmap.scaled(
            min(self.app_width, pixmap.width()),
            min(self.app_height, pixmap.height()),
            QtCore.Qt.KeepAspectRatio
        )

        return pixmap

    def display_statusbar(self):
        self.statusBar().showMessage(
            "[%d/%d] %s" % (self.image_manager.display_index, self.image_manager.count, self.filename)
        )

    # Decides what to do when specific keys are pressed
    def keyPressEvent(self, e):
        key = e.key()
        if key == QtCore.Qt.Key_Right:
            direction = DIR_NEXT
        elif key == QtCore.Qt.Key_Left:
            direction = DIR_PREV
        else:
            return

        self.change_image(direction=direction)

    def paintEvent(self, QPaintEvent):
        if not self.filename:
            return

        painter = QtGui.QPainter(self)

        pixmap = self.prepare_image(self.filename)
        painter.drawPixmap(self.center_position(pixmap.width(), pixmap.height()), pixmap)

        if self.action == "loved":
            action_pixmap = QtGui.QPixmap("../assets/loved.png")
            painter.drawPixmap(self.center_position(action_pixmap.width(), action_pixmap.height()), action_pixmap)

            self.action = None
        elif self.action == "trashed":
            action_pixmap = QtGui.QPixmap("../assets/trashed.png")
            painter.drawPixmap(self.center_position(action_pixmap.width(), action_pixmap.height()), action_pixmap)

            self.action = None

        painter.end()

    def center_position(self, width, height):
        rect = QtCore.QRect()
        rect.setX(self.app_width / 2 - width / 2)
        rect.setY(self.app_height / 2 - height / 2)
        rect.setWidth(width)
        rect.setHeight(height)

        return rect

    # controls image change
    def change_image(self, direction):
        filename = self.image_manager.change_image(direction)

        if not filename:
            return

        # set current filename
        self.filename = filename

        # update view
        self.refresh()

    def love_image(self):
        # set action
        self.action = "loved"

        # update view
        self.refresh()

    def delete_image(self):
        # set action
        self.action = "trashed"

        # update view
        self.refresh()

    def refresh(self):
        self.display_statusbar()
        self.update()


class ImageManager(object):
    images = []
    image_index = 0
    count = 0
    display_index = 1

    def init_images(self):
        files_manager = FilesManager()
        self.images = files_manager.get_images()
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
    def get_images(self):
        return self.filter_images(self.open_directory() )

    def open_directory(self):
        return QtWidgets.QFileDialog().getExistingDirectory()

    def filter_images(self, directory):
        images = []
        images.extend(glob.glob(os.path.join(directory, '*.jpg')))
        images.extend(glob.glob(os.path.join(directory, '*.png')))

        return images


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    photochooser = App()
    sys.exit(app.exec_())
