import sys
import unittest
from PyQt5 import QtWidgets
from photochooser.app import App

app = QtWidgets.QApplication(sys.argv)


class AppTest(unittest.TestCase):
    def setUp(self):
        self.form = App()

    def test_init(self):
        self.assertEqual("Photochooser v0.2.0", self.form.windowTitle())


if __name__ == "__main__":
    unittest.main()
