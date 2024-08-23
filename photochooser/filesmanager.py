import glob, os

class FilesManager(object):
    directory = ""

    def get_images(self, directory):
        return self.filter_images(directory)

    def open_directory(self, directory):
        self.directory = directory

        return self.directory

    def filter_images(self, directory):
        images = []
        images.extend(glob.glob(os.path.join(directory, '*.jpg')))
        images.extend(glob.glob(os.path.join(directory, '*.JPG')))
        images.extend(glob.glob(os.path.join(directory, '*.png')))

        return sorted(images)