import unittest
from photochooser.app import *


class ImageManagerTest(unittest.TestCase):
    def setUp(self):
        self.image_manager = App()
        self.image_manager.images = ["1.jpg", "2.jpg", "3.jpg"]

    def test_change_image_first(self):
        filename = self.image_manager.change_image("first")

        self.assertEqual("1.jpg", filename)

    def test_change_image_next(self):
        filename = self.image_manager.change_image("next")

        self.assertEqual("2.jpg", filename)

        self.image_manager.id = 1
        filename = self.image_manager.change_image("next")

        self.assertEqual("3.jpg", filename)

    def test_change_image_prev(self):
        self.image_manager.id = 2
        filename = self.image_manager.change_image("prev")

        self.assertEqual("2.jpg", filename)

        filename = self.image_manager.change_image("prev")

        self.assertEqual("1.jpg", filename)

    def test_change_image_out_of_range(self):
        self.image_manager.id = 0
        filename = self.image_manager.change_image("prev")

        self.assertEqual(False, filename)

        self.image_manager.id = 2
        filename = self.image_manager.change_image("next")

        self.assertEqual(False, filename)


if __name__ == "__main__":
    unittest.main()
