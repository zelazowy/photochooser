import functools
import os
import sys
from PyQt6 import QtGui, QtWidgets, QtCore

from imagesconfig import ImagesConfig

VERSION = "0.3.0"

CURRENT_DIR = os.path.dirname(__file__)

DIRECTION_PREV = "prev"
DIRECTION_NEXT = "next"
DIRECTION_FIRST = "first"
DIRECTION_LAST = "last"


class App(QtWidgets.QMainWindow):
    image_config = None
    image_id = None
    action = None

    app_width = 0
    app_height = 0

    label = None

    def __init__(self):
        super(App, self).__init__()

        self.label = QtWidgets.QLabel(self)

        self.setWindowTitle("Photochooser " + VERSION)
        self.showMaximized()

        self.app_width = self.width()
        self.app_height = self.height()

        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedWidth(self.app_width)
        self.label.setFixedHeight(self.app_height)

        self.image_config = ImagesConfig()

        self.init_menubar()
        self.init_toolbar()

        # displays photochooser logo
        # todo add special action for welcome screen
        # self.filename = os.path.join(CURRENT_DIR, "assets/photochooser_camera.png")
        # self.refresh()

        # sets focus on main window
        self.activateWindow()

    def init_menubar(self):
        open_action = QtGui.QAction(self)
        open_action.setText("Open directory")
        # open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.prepare_directory)

        menubar = self.menuBar()
        open_menu = menubar.addMenu("File")
        open_menu.addAction(open_action)

    def init_toolbar(self):
        toolbar = self.addToolBar("tb")

        # spacer widget for left
        left_spacer = QtWidgets.QWidget()
        left_spacer.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        # spacer widget for right
        # you can't add the same widget to both left and right. you need two different widgets.
        right_spacer = QtWidgets.QWidget()
        right_spacer.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)

        # here goes the left one
        toolbar.addWidget(left_spacer)

        prev_action = QtGui.QAction(QtGui.QIcon(os.path.join(CURRENT_DIR, "assets/open.png")), 'Open directory', self)
        prev_action.triggered.connect(self.prepare_directory)
        toolbar.addAction(prev_action)

        first_action = QtGui.QAction(QtGui.QIcon(os.path.join(CURRENT_DIR, "assets/first.png")), 'First image', self)
        first_action.triggered.connect(self.first_image)
        toolbar.addAction(first_action)

        prev_action = QtGui.QAction(QtGui.QIcon(os.path.join(CURRENT_DIR, "assets/prev.png")), 'Previous image', self)
        prev_action.triggered.connect(functools.partial(self.change_image, DIRECTION_PREV))
        toolbar.addAction(prev_action)

        next_action = QtGui.QAction(QtGui.QIcon(os.path.join(CURRENT_DIR, "assets/next.png")), 'Next image', self)
        next_action.triggered.connect(functools.partial(self.change_image, DIRECTION_NEXT))
        toolbar.addAction(next_action)

        rotate_left = QtGui.QAction(QtGui.QIcon(os.path.join(CURRENT_DIR, "assets/rotate_left.png")), 'Rotate left', self)
        rotate_left.triggered.connect(self.rotate_left)
        toolbar.addAction(rotate_left)

        rotate_right = QtGui.QAction(QtGui.QIcon(os.path.join(CURRENT_DIR, "assets/rotate_right.png")), 'Rotate right', self)
        rotate_right.triggered.connect(self.rotate_right)
        toolbar.addAction(rotate_right)

        love_action = QtGui.QAction(QtGui.QIcon(os.path.join(CURRENT_DIR, "assets/love.png")), 'Love image', self)
        love_action.triggered.connect(self.love_image)
        toolbar.addAction(love_action)

        delete_action = QtGui.QAction(QtGui.QIcon(os.path.join(CURRENT_DIR, "assets/trash.png")), 'Move to trash', self)
        delete_action.triggered.connect(self.trash_image)
        toolbar.addAction(delete_action)

        delete_action = QtGui.QAction(QtGui.QIcon(os.path.join(CURRENT_DIR, "assets/save.png")), 'Apply changes', self)
        delete_action.triggered.connect(self.apply)
        toolbar.addAction(delete_action)

        exit_action = QtGui.QAction(QtGui.QIcon(os.path.join(CURRENT_DIR, "assets/close.png")), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(QtCore.QCoreApplication.quit)
        toolbar.addAction(exit_action)

        # here goes the left one
        toolbar.addWidget(right_spacer)

    def apply(self):
        self.image_config.apply()
        self.change_image(DIRECTION_FIRST)

    def prepare_directory(self):
        self.image_config.open(QtWidgets.QFileDialog().getExistingDirectory())
        self.image_id = self.image_config.get_last_viewed()

        self.refresh()

    def prepare_image(self, image_id):
        # create pixmap to display image (from given filename)
        image = self.image_config.images[image_id]
        pixmap = QtGui.QPixmap(image["filename"])

        try:
            transform = QtGui.QTransform()
            transform.rotate(float(image["rotation"]))
            pixmap = pixmap.transformed(transform)
        except:
            pass

        # resize
        pixmap = pixmap.scaled(
            min(self.app_width, pixmap.width()),
            min(self.app_height, pixmap.height()),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio
        )

        return pixmap

    def display_statusbar(self):
        if not self.image_id:
            return

        self.statusBar().showMessage(
            "[%d/%d] %s" % (self.image_id, self.image_config.count, self.image_config.images[self.image_id]["filename"])
        )

    # Decides what to do when specific keys are pressed
    def keyPressEvent(self, e):
        key = e.key()
        if key == QtCore.Qt.Key.Key_Right:
            self.change_image(direction=DIRECTION_NEXT)
        elif key == QtCore.Qt.Key.Key_Left:
            self.change_image(direction=DIRECTION_PREV)
        elif key == QtCore.Qt.Key.Key_Up:
            self.love_image()
        elif key == QtCore.Qt.Key.Key_Down:
            self.trash_image()
        elif key == QtCore.Qt.Key.Key_BracketLeft:
            self.rotate_left()
        elif key == QtCore.Qt.Key.Key_BracketRight:
            self.rotate_right()
        elif key == QtCore.Qt.Key.Key_F:
            self.first_image()

        elif key == QtCore.Qt.Key.Key_1:  # debug
            self.image_config.debug_statuses()
            return
        elif key == QtCore.Qt.Key.Key_0:
            self.image_config.apply()
            QtCore.QCoreApplication.quit()
            return
        else:
            return

    def paintEvent(self, QPaintEvent):
        if not self.image_id:
            return

        painter = QtGui.QPainter(self)

        pixmap = self.prepare_image(self.image_id)
        painter.drawPixmap(self.center_position(pixmap.width(), pixmap.height()), pixmap)

        loved_icon = QtGui.QPixmap(
            os.path.join(CURRENT_DIR, "assets/love.png" if self.image_config.is_loved(self.image_id) else "assets/love_placeholder.png")
        )
        painter.drawPixmap(
            QtCore.QRect(10, self.app_height - 155, loved_icon.width(), loved_icon.height()),
            loved_icon
        )

        trashed_icon = QtGui.QPixmap(
            os.path.join(CURRENT_DIR, "assets/trash.png" if self.image_config.is_trashed(self.image_id) else "assets/trash_placeholder.png")
        )
        painter.drawPixmap(
            QtCore.QRect(10, self.app_height - 90, trashed_icon.width(), trashed_icon.height()),
            trashed_icon
        )

        painter.end()

    def resizeEvent(self, QResizeEvent):
        self.app_width = self.width()
        self.app_height = self.height()

        self.refresh()

    def center_position(self, width, height):
        rect = QtCore.QRect()
        rect.setX(int(self.app_width / 2 - width / 2))
        rect.setY(int(self.app_height / 2 - height / 2))
        rect.setWidth(width)
        rect.setHeight(height)

        return rect

    # controls image change
    def change_image(self, direction):
        try:
            if direction == DIRECTION_PREV:
                index = self.image_id - 1

                if index < 1:
                    raise IndexError
            elif direction == DIRECTION_NEXT:
                index = self.image_id + 1

                if index > self.image_config.count:
                    raise IndexError
            elif direction == DIRECTION_FIRST:
                index = 1
            else:
                raise RuntimeError

            self.image_id = index

            self.image_config.set_currently_viewed(self.image_id)

            # update view
            self.refresh()
        except IndexError:
            return

    def first_image(self):
        self.image_id = 1

        self.image_config.set_currently_viewed(self.image_id)

        # update view
        self.refresh()

    def love_image(self):
        self.image_config.toggle_loved(self.image_id)

        self.refresh()

    def trash_image(self):
        self.image_config.toggle_trashed(self.image_id)

        self.refresh()

    def rotate_left(self):
        self.image_config.rotate_left(self.image_id)

        self.refresh()

    def rotate_right(self):
        self.image_config.rotate_right(self.image_id)

        self.refresh()

    def refresh(self):
        self.display_statusbar()
        self.update()


def app():
    app = QtWidgets.QApplication(sys.argv)
    App()
    sys.exit(app.exec())


if __name__ == "__main__":
    app()
