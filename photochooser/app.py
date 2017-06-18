from PyQt5 import QtGui, QtWidgets, QtCore
import sys, glob, os, functools, exifread, re, shutil, sqlite3

DIR_PREV = "prev"
DIR_NEXT = "next"
DIR_FIRST = "first"
DIR_LAST = "last"

class App(QtWidgets.QMainWindow):
    image_config = None
    id = None
    action = None

    app_width = 0
    app_height = 0

    label = None

    loved_dir = "favourites"
    trashed_dir = "trash"

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

        self.image_config = ImagesConfig()

        self.init_toolbar()

        # displays photochooser logo
        # todo add special action for welcome screen
        # self.filename = "../assets/photochooser_camera.png"
        # self.refresh()

        self.loved_dir = os.path.join(self.image_config.directory, self.loved_dir)
        self.trashed_dir = os.path.join(self.image_config.directory, self.trashed_dir)

        self.change_image(DIR_FIRST)

        # sets focus on main window
        self.activateWindow()

    def init_toolbar(self):
        toolbar = self.addToolBar("tb")

        # spacer widget for left
        left_spacer = QtWidgets.QWidget()
        left_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # spacer widget for right
        # you can't add the same widget to both left and right. you need two different widgets.
        right_spacer = QtWidgets.QWidget()
        right_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # here goes the left one
        toolbar.addWidget(left_spacer)

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

        # here goes the left one
        toolbar.addWidget(right_spacer)

    def prepare_image(self, id):
        # create pixmap to display image (from given filename)
        image = self.image_config.images[id]
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
            QtCore.Qt.KeepAspectRatio
        )

        return pixmap

    def display_statusbar(self):
        self.statusBar().showMessage(
            "[%d/%d] %s" % (self.id, self.image_config.count, self.image_config.images[self.id]["filename"])
        )

    # Decides what to do when specific keys are pressed
    def keyPressEvent(self, e):
        key = e.key()
        if key == QtCore.Qt.Key_Right:
            direction = DIR_NEXT
        elif key == QtCore.Qt.Key_Left:
            direction = DIR_PREV
        elif key == QtCore.Qt.Key_1:
            self.image_config.debug_statuses()
            return
        else:
            return

        self.change_image(direction=direction)

    def paintEvent(self, QPaintEvent):
        if not self.id:
            return

        painter = QtGui.QPainter(self)

        pixmap = self.prepare_image(self.id)
        painter.drawPixmap(self.center_position(pixmap.width(), pixmap.height()), pixmap)

        if self.image_config.images[self.id]["status"] == self.image_config.STATUS_LOVED:
            loved_icon = QtGui.QPixmap("../assets/loved.png")
        else:
            loved_icon = QtGui.QPixmap("../assets/loved_placeholder.png")

        rect = QtCore.QRect()
        rect.setX(10)
        rect.setY(self.app_height - 80)
        rect.setWidth(loved_icon.width())
        rect.setHeight(loved_icon.height())

        painter.drawPixmap(rect, loved_icon)

        if self.image_config.images[self.id]["status"] == self.image_config.STATUS_TRASHED:
            trashed_icon = QtGui.QPixmap("../assets/trashed.png")
        else:
            trashed_icon = QtGui.QPixmap("../assets/trashed_placeholder.png")

        rect = QtCore.QRect()
        rect.setX(10)
        rect.setY(self.app_height - 145)
        rect.setWidth(trashed_icon.width())
        rect.setHeight(trashed_icon.height())

        # painter.drawPixmap(self.center_position(action_pixmap.width(), action_pixmap.height()), action_pixmap)
        painter.drawPixmap(rect, trashed_icon)

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
        try:
            if direction == DIR_PREV:
                index = self.id - 1

                if index < 1:
                    raise IndexError
            elif direction == DIR_NEXT:
                index = self.id + 1

                if index > self.image_config.count:
                    raise IndexError
            elif direction == DIR_FIRST:
                index = 1
            else:
                raise RuntimeError

            self.id = index

            # update view
            self.refresh()
        except IndexError:
            return

    def love_image(self):
        self.image_config.mark_as_loved(self.id)

        # mark image as loved
        # if not os.path.exists(self.loved_dir):
        #     os.makedirs(self.loved_dir)
        #
        # shutil.copy2(self.filename, self.loved_dir)

        # update view
        self.refresh()

    def delete_image(self):
        self.image_config.mark_as_trashed(self.id)

        # mark image as trashed
        # if not os.path.exists(self.trashed_dir):
        #     os.makedirs(self.trashed_dir)
        #
        # shutil.copy2(self.filename, self.trashed_dir)

        # update view
        self.refresh()

    def refresh(self):
        self.display_statusbar()
        self.update()


class FilesManager(object):
    directory = ""

    def get_images(self, directory):
        return self.filter_images(directory)

    def open_directory(self):
        self.directory = QtWidgets.QFileDialog().getExistingDirectory()

        return self.directory

    def filter_images(self, directory):
        images = []
        images.extend(glob.glob(os.path.join(directory, '*.jpg')))
        images.extend(glob.glob(os.path.join(directory, '*.png')))

        return images


class ImagesConfig(object):
    STATUS_LOVED = "Loved"
    STATUS_TRASHED = "Trashed"
    STATUS_NONE = "None"

    connection = None
    directory = ""

    images = []
    count = 0

    def __init__(self):
        files_manager = FilesManager()
        self.directory = files_manager.open_directory()

        db_path = os.path.join(self.directory, "photochooser.db")

        if not os.path.exists(db_path):
            self.connection = sqlite3.connect(db_path)
            self.init_db()

            images = files_manager.get_images(self.directory)
            self.init_images(images)
        else:
            self.connection = sqlite3.connect(db_path)

        self.images = self.load_images()
        self.count = len(self.images)

    def init_db(self):
        c = self.connection.cursor()

        # Create table
        c.execute('''CREATE TABLE images (
                id INTEGER PRIMARY KEY UNIQUE,
                filename VARCHAR (255),
                rotation INTEGER,
                status CHAR (10) DEFAULT none
            );''')

    def init_images(self, images):
        # todo:
        # check if all images are loaded into db (select * where filenames in [images]?
        # insert only non loaded images

        c = self.connection.cursor()

        for img in images:
            with open(img, 'rb') as file:
                try:
                    tags = exifread.process_file(file)

                    rotation_tag = tags['Image Orientation']
                    rotation = re.search('[0-9]+', str(rotation_tag)).group(0)
                except:
                    rotation = 0

                c.execute('INSERT INTO images VALUES (NULL, ?, ?, "None")', (img, rotation))

        self.connection.commit()

    def load_images(self):
        c = self.connection.cursor()

        c.execute("SELECT `id`, `filename`, `rotation`, `status` FROM images")

        images = c.fetchall()

        data = {}
        for img in images:
            data[img[0]] = {"id": img[1], "filename": img[1], "rotation": img[2], "status": img[3]}

        return data

    def mark_as_loved(self, id):
        c = self.connection.cursor()

        c.execute("UPDATE images SET `status` = ? WHERE `id` = ?", (self.STATUS_LOVED, id))

        self.connection.commit()

        self.images[id]["status"] = self.STATUS_LOVED

    def mark_as_trashed(self, id):
        c = self.connection.cursor()

        c.execute("UPDATE images SET `status` = ? WHERE id = ?", (self.STATUS_TRASHED, id))

        self.connection.commit()

        self.images[id]["status"] = self.STATUS_TRASHED

    def debug_statuses(self):
        c = self.connection.cursor()

        c.execute("SELECT * FROM images")

        images = c.fetchall()
        for img in images:
            print(img)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    photochooser = App()
    sys.exit(app.exec_())
