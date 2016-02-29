# photochooser
photochooser is an application that helps you in photos managing (or images in general).
Do you ever have to choose photos from holidays to print? Do you have tons of useful, ugly and duplicate photos?
Now you can use photochooser to help you deal it 8)

pchotochooser is simple:
  1. choose directory with photos (only .png and .jpg files are supported at the time)
  2. use arrows to change images
  3. decide what to do:
    * do nothing
    * copy image to "copy" subdirectory if you'd like to print it (it will not affect original image) - use `c` key or `copy` button
    * delete image permanently - use `backspace` key or `delete` button
    * if you're not sure you can "soft delete" image - it will be moved to "delete" subdirectory - use `d` key or `delete?` button

Aaand... this is it! In no time you have clean directory without crappy images and nice subdirectory with photos you'd like to have in your album.

## installation
At the time there is no executable app (I'm working on it!).
To use the app you'd need:
* python 3.4
* PyQt4
* exifread

To run the app download `photochooser.py` file and execute it from command line:
```bash
$ python photochooser.py
```

You can do it on Windows, OS X and Unix.
