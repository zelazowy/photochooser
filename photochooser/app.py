from PyQt5 import QtGui, QtWidgets, QtCore
import sys, glob, os, functools, exifread, re, shutil, sqlite3

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

        self.setWindowTitle("Photochooser v0.2.2")
        self.showMaximized()

        self.app_width = self.width()
        self.app_height = self.height()

        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setFixedWidth(self.app_width)
        self.label.setFixedHeight(self.app_height)

        self.image_config = ImagesConfig()

        self.init_menubar()
        self.init_toolbar()

        # displays photochooser logo
        # todo add special action for welcome screen
        # self.filename = "../assets/photochooser_camera.png"
        # self.refresh()

        # sets focus on main window
        self.activateWindow()

    def init_menubar(self):
        open_action = QtWidgets.QAction(self)
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
        left_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # spacer widget for right
        # you can't add the same widget to both left and right. you need two different widgets.
        right_spacer = QtWidgets.QWidget()
        right_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # here goes the left one
        toolbar.addWidget(left_spacer)

        prev_action = QtWidgets.QAction(QtGui.QIcon("../assets/open.png"), 'Open directory', self)
        prev_action.triggered.connect(self.prepare_directory)
        toolbar.addAction(prev_action)

        first_action = QtWidgets.QAction(QtGui.QIcon("../assets/first.png"), 'First image', self)
        first_action.triggered.connect(self.first_image)
        toolbar.addAction(first_action)

        prev_action = QtWidgets.QAction(QtGui.QIcon("../assets/prev.png"), 'Previous image', self)
        prev_action.triggered.connect(functools.partial(self.change_image, DIRECTION_PREV))
        toolbar.addAction(prev_action)

        next_action = QtWidgets.QAction(QtGui.QIcon("../assets/next.png"), 'Next image', self)
        next_action.triggered.connect(functools.partial(self.change_image, DIRECTION_NEXT))
        toolbar.addAction(next_action)

        rotate_left = QtWidgets.QAction(QtGui.QIcon("../assets/rotate_left.png"), 'Rotate left', self)
        rotate_left.triggered.connect(self.rotate_left)
        toolbar.addAction(rotate_left)

        rotate_right = QtWidgets.QAction(QtGui.QIcon("../assets/rotate_right.png"), 'Rotate right', self)
        rotate_right.triggered.connect(self.rotate_right)
        toolbar.addAction(rotate_right)

        love_action = QtWidgets.QAction(QtGui.QIcon("../assets/love.png"), 'Love image', self)
        love_action.triggered.connect(self.love_image)
        toolbar.addAction(love_action)

        delete_action = QtWidgets.QAction(QtGui.QIcon("../assets/trash.png"), 'Move to trash', self)
        delete_action.triggered.connect(self.trash_image)
        toolbar.addAction(delete_action)

        delete_action = QtWidgets.QAction(QtGui.QIcon("../assets/save.png"), 'Apply changes', self)
        delete_action.triggered.connect(self.apply)
        toolbar.addAction(delete_action)

        exit_action = QtWidgets.QAction(QtGui.QIcon("../assets/close.png"), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(QtWidgets.qApp.quit)
        toolbar.addAction(exit_action)

        # here goes the left one
        toolbar.addWidget(right_spacer)

    def apply(self):
        self.image_config.apply()
        self.change_image(DIRECTION_FIRST)

    def prepare_directory(self):
        self.image_config.open()
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
            QtCore.Qt.KeepAspectRatio
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
        if key == QtCore.Qt.Key_Right:
            self.change_image(direction=DIRECTION_NEXT)
        elif key == QtCore.Qt.Key_Left:
            self.change_image(direction=DIRECTION_PREV)
        elif key == QtCore.Qt.Key_Up:
            self.love_image()
        elif key == QtCore.Qt.Key_Down:
            self.trash_image()
        elif key == QtCore.Qt.Key_BracketLeft:
            self.rotate_left()
        elif key == QtCore.Qt.Key_BracketRight:
            self.rotate_right()
        elif key == QtCore.Qt.Key_F:
            self.first_image()

        elif key == QtCore.Qt.Key_1:  # debug
            self.image_config.debug_statuses()
            return
        elif key == QtCore.Qt.Key_0:
            self.image_config.apply()
            QtWidgets.qApp.quit()
            return
        else:
            return

    def paintEvent(self, QPaintEvent):
        if not self.image_id:
            return

        painter = QtGui.QPainter(self)

        pixmap = self.prepare_image(self.image_id)
        painter.drawPixmap(self.center_position(pixmap.width(), pixmap.height()), pixmap)

        if self.image_config.images[self.image_id]["status"] == self.image_config.STATUS_LOVED:
            loved_icon = QtGui.QPixmap("../assets/love.png")
        else:
            loved_icon = QtGui.QPixmap("../assets/love_placeholder.png")

        rect = QtCore.QRect()
        rect.setX(10)
        rect.setY(self.app_height - 155)
        rect.setWidth(loved_icon.width())
        rect.setHeight(loved_icon.height())

        painter.drawPixmap(rect, loved_icon)

        if self.image_config.images[self.image_id]["status"] == self.image_config.STATUS_TRASHED:
            trashed_icon = QtGui.QPixmap("../assets/trash.png")
        else:
            trashed_icon = QtGui.QPixmap("../assets/trash_placeholder.png")

        rect = QtCore.QRect()
        rect.setX(10)
        rect.setY(self.app_height - 90)
        rect.setWidth(trashed_icon.width())
        rect.setHeight(trashed_icon.height())

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
        images.extend(glob.glob(os.path.join(directory, '*.JPG')))
        images.extend(glob.glob(os.path.join(directory, '*.png')))

        return sorted(images)


class ImagesConfig(object):
    STATUS_LOVED = "Loved"
    STATUS_TRASHED = "Trashed"
    STATUS_MOVED = "Moved"
    STATUS_NONE = "None"

    connection = None
    directory = ""

    images = []
    count = 0

    loved_directory = "loved"
    trashed_directory = "trash"

    def open(self):
        files_manager = FilesManager()
        self.directory = files_manager.open_directory()
        self.loved_directory = os.path.join(self.directory, self.loved_directory)
        self.trashed_directory = os.path.join(self.directory, self.trashed_directory)

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
        c.execute('''
            CREATE TABLE images (
                image_id INTEGER PRIMARY KEY UNIQUE,
                filename VARCHAR (255),
                rotation INTEGER,
                status CHAR (10) DEFAULT none,
                processed BOOLEAN DEFAULT (0)
            );
        ''')

        c.execute('''
            CREATE TABLE info (
                id    INTEGER      PRIMARY KEY,
                name  VARCHAR (32) NOT NULL,
                value VARCHAR (32) NOT NULL
            );
        ''')

        c.execute("INSERT INTO info (`name`, `value`) VALUES ('last_image', 1)")
        self.connection.commit()

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

                c.execute('INSERT INTO images VALUES (NULL, ?, ?, "None", 0)', (img, rotation))

        self.connection.commit()

    def load_images(self):
        c = self.connection.cursor()

        c.execute("SELECT `image_id`, `filename`, `rotation`, `status` FROM images WHERE `processed` != ?", [1])

        images = c.fetchall()

        data = {}
        for i, img in enumerate(images):
            data[i + 1] = {"image_id": img[0], "filename": img[1], "rotation": img[2], "status": img[3]}

        return data

    def toggle_loved(self, image_id):
        c = self.connection.cursor()

        if self.images[image_id]["status"] == self.STATUS_LOVED:
            status = self.STATUS_NONE
        else:
            status = self.STATUS_LOVED

        c.execute("UPDATE images SET `status` = ? WHERE `image_id` = ?", (status, image_id))

        self.connection.commit()

        self.images[image_id]["status"] = status

    def toggle_trashed(self, image_id):
        c = self.connection.cursor()

        if self.images[image_id]["status"] == self.STATUS_TRASHED:
            status = self.STATUS_NONE
        else:
            status = self.STATUS_TRASHED

        c.execute("UPDATE images SET `status` = ? WHERE image_id = ?", (status, image_id))

        self.connection.commit()

        self.images[image_id]["status"] = status

    def mark_as_moved(self, image_id):
        c = self.connection.cursor()

        c.execute("UPDATE images SET `processed` = ? WHERE image_id = ?", (1, image_id))

        self.connection.commit()

    def rotate_left(self, image_id):
        c = self.connection.cursor()

        self.images[image_id]['rotation'] = 270 if self.images[image_id]['rotation'] == 0 else self.images[image_id]['rotation'] - 90

        # print(self.images[image_id]['rotation'], rotation)

        c.execute("UPDATE images SET `rotation` = ? WHERE image_id = ?", (self.images[image_id]['rotation'], image_id))

        self.connection.commit()

    def rotate_right(self, image_id):
        c = self.connection.cursor()

        self.images[image_id]['rotation'] = 0 if self.images[image_id]['rotation'] == 270 else self.images[image_id]['rotation'] + 90

        # print(self.images[image_id]['rotation'], rotation)

        c.execute("UPDATE images SET `rotation` = ? WHERE image_id = ?", (self.images[image_id]['rotation'], image_id))

        self.connection.commit()

    def apply(self):
        if not os.path.exists(self.loved_directory):
            os.makedirs(self.loved_directory)

        if not os.path.exists(self.trashed_directory):
            os.makedirs(self.trashed_directory)

        for image in self.images.values():
            if image["status"] == self.STATUS_LOVED:
                shutil.move(image["filename"], self.loved_directory)
                self.mark_as_moved(image["image_id"])
            elif image["status"] == self.STATUS_TRASHED:
                shutil.move(image["filename"], self.trashed_directory)
                self.mark_as_moved(image["image_id"])

        # refresh images
        self.images = self.load_images()
        self.count = len(self.images)

    def set_currently_viewed(self, image_id):
        c = self.connection.cursor()

        c.execute("UPDATE info SET `name` = 'last_image', `value` = ?", [str(image_id)])

        self.connection.commit()

    def get_last_viewed(self):
        c = self.connection.cursor()

        c.execute("SELECT `value` FROM info WHERE `name` = 'last_image'")

        # gets only first column
        return int(c.fetchone()[0])

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
