from PyQt5 import QtGui, QtWidgets, QtCore
import sys, glob, os, functools, exifread, re, shutil, sqlite3

DIR_PREV = "prev"
DIR_NEXT = "next"
DIR_FIRST = "first"
DIR_LAST = "last"

class App(QtWidgets.QMainWindow):
    image_manager = None
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

        self.image_manager = ImageManager()

        self.init_toolbar()

        # displays photochooser logo
        # self.filename = "../assets/photochooser_camera.png"
        # self.refresh()

        self.image_manager.init_images()

        self.image_config = ImagesConfig(self.image_manager.directory)

        self.loved_dir = os.path.join(self.image_manager.directory, self.loved_dir)
        self.trashed_dir = os.path.join(self.image_manager.directory, self.trashed_dir)

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

    def prepare_image(self, id):
        # create pixmap to display image (from given filename)
        image = self.image_manager.images[id]
        pixmap = QtGui.QPixmap(image["filename"])

        try:


            # with open(filename, 'rb') as file:
            #     tags = exifread.process_file(file)
            #
            #     rotation_tag = tags['Image Orientation']
            #     rotation = re.search('[0-9]+', str(rotation_tag)).group(0)
            #
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
            "[%d/%d] %s" % (self.id, self.image_manager.count, self.image_manager.images[self.id]["filename"])
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
        if not self.id:
            return

        painter = QtGui.QPainter(self)

        pixmap = self.prepare_image(self.id)
        painter.drawPixmap(self.center_position(pixmap.width(), pixmap.height()), pixmap)

        if self.action == "loved":
            action_pixmap = QtGui.QPixmap("../assets/loved.png")
            self.action = None

            painter.drawPixmap(self.center_position(action_pixmap.width(), action_pixmap.height()), action_pixmap)
        elif self.action == "trashed":
            action_pixmap = QtGui.QPixmap("../assets/trashed.png")
            self.action = None

            painter.drawPixmap(self.center_position(action_pixmap.width(), action_pixmap.height()), action_pixmap)

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
        id = self.image_manager.change_image(direction)

        if not id:
            return

        # set current filename
        self.id = id

        # update view
        self.refresh()

    def love_image(self):
        # set action
        self.action = "loved"

        # mark image as loved
        # if not os.path.exists(self.loved_dir):
        #     os.makedirs(self.loved_dir)
        #
        # shutil.copy2(self.filename, self.loved_dir)

        # update view
        self.refresh()

    def delete_image(self):
        # set action
        self.action = "trashed"

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


class ImageManager(object):
    image_config = None

    images = []
    id = 1
    count = 0
    directory = ""

    def init_images(self):
        files_manager = FilesManager()
        images = files_manager.get_images()
        self.directory = files_manager.directory

        self.image_config = ImagesConfig(self.directory)
        self.image_config.init_images(images)

        self.images = self.image_config.load_images()
        self.count = len(self.images)

    def change_image(self, direction):
        try:
            if direction == DIR_PREV:
                index = self.id - 1

                if index < 1:
                    raise IndexError
            elif direction == DIR_NEXT:
                index = self.id + 1

                if index > self.count:
                    raise IndexError
            elif direction == DIR_FIRST:
                index = 1
            else:
                raise RuntimeError

            self.id = index

            return self.id
        except IndexError:
            return False


class FilesManager(object):
    directory = ""

    def get_images(self):
        return self.filter_images(self.open_directory())

    def open_directory(self):
        self.directory = QtWidgets.QFileDialog().getExistingDirectory()

        return self.directory

    def filter_images(self, directory):
        images = []
        images.extend(glob.glob(os.path.join(directory, '*.jpg')))
        images.extend(glob.glob(os.path.join(directory, '*.png')))

        return images


class ImagesConfig(object):
    connection = None

    def __init__(self, directory):
        db_path = os.path.join(directory, "photochooser.db")

        if not os.path.exists(db_path):
            self.connection = sqlite3.connect(db_path)
            self.init_db()
        else:
            self.connection = sqlite3.connect(db_path)

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

                c.execute('INSERT INTO images VALUES (NULL, ?, ?, NULL)', (img, rotation))

        self.connection.commit()

    def load_images(self):
        c = self.connection.cursor()

        c.execute("SELECT id, filename, rotation, status FROM images")

        images = c.fetchall()

        data = {}
        for img in images:
            data[img[0]] = {"id": img[1], "filename": img[1], "rotation": img[2], "status": img[3]}

        return data


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    photochooser = App()
    sys.exit(app.exec_())
