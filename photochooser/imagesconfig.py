import os, exifread, re, shutil, sqlite3
from filesmanager import FilesManager


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

    def open(self, directory):
        files_manager = FilesManager()
        self.directory = files_manager.open_directory(directory)
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
