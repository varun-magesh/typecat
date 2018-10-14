# Typecat

![](https://github.com/LordPharaoh/typecat/raw/master/typecat.gif)

Typecat allows you to search and filter fonts based on visual features including
* width
* height
* aspect ratio
* thickness
* thickness variation
* category
* similarity *almost*
## Dependencies
Most python dependencies will be auto-installed by pip. 

These are the other dependences required:
* [python3](https://www.python.org/download)
* [GTK3](https://www.gtk.org/download)
* [PyGObject Introspection]( https://pygobject.readthedocs.io/en/latest/getting_started.html)


### Linux
Most Linux installations will have what typecat requires. If not, find the necessary packages in your package manager.

### Mac
Run `bash /path/to/typecat/mac-install.sh` to install all necessary dependencies with [brew](https://brew.sh/). If brew is not installed it will be installed automatically.

### Windows
Install [MSYS2](http://www.msys2.org/) and run this in msys: `pacman -S mingw-w64-x86_64-gtk3 mingw-w64-x86_64-python3-gobject`

> Disclaimer! Due to lack of access to a Windows machine, this installation process has never been tested. 

## Installation
Once the dependencies have been installed, navigate to the typecat github directory and run `pip3 install .` (you may need root/admin privileges).
You can now run it from anywhere on the system with `python3 -m typecat`.
## Status
While it is currently fully functioning, there remains to be a lot of room for improvement.

* Better feature spreading
* Categorization (That's happening like, right now)
* Feature/font similarity
* Font pairings
* Config/reload window

