# 3D Grav

**_Gravity simulator desktop app_**

[![3D Demonstration](https://raw.githubusercontent.com/zotho/geometry-np/master/1_3D_Demo.png)](https://youtu.be/_jQh-shTCy8)

See **gravity** demo [video](https://youtu.be/_jQh-shTCy8)

[![3D Demonstration](https://raw.githubusercontent.com/zotho/geometry-np/master/2_3D_Demo.png)](https://youtu.be/_jQh-shTCy8)

You can write custom update function.

  - Gravity simulation
  - Simulating charged particles
  - Custom motion law

E.g. magnetic field:

[![Charge Demonstration](https://raw.githubusercontent.com/zotho/geometry-np/master/3_Charge_Demo.png)](https://youtu.be/tkRY8Td1pC8)

See **magnetic** demo [video](https://youtu.be/tkRY8Td1pC8)

## Dependencies

* [Kivy framework](https://kivy.org) - open source Python library for developing apps
* [NumPy](http://www.numpy.org/) - fundamental package for scientific computing with Python
* [mgen](https://pypi.org/project/mgen/) - Convenient matrix generation functions
* [Buildozer](https://github.com/kivy/buildozer) - tool for creating APK for Android (optional)

## Installation

```sh
$ git clone https://github.com/zotho/3D_Grav.git
$ cd 3D_Grav
$ python3 -m venv env
$ source env/bin/activate
$ pip install --upgrade pip
$ pip install numpy mgen kivy
$ python3 main.py
```
### Controls:

* _LMB_ – add planets
* _Shift + LMB(or arrows)_ – rotate
* _D_ – show/hide debug
* _Arrows and spacebar_ – control simulation speed
* _Q_ – quit

To exit virtual environment
```sh
$ deactivate
```

## Android

For Android you can [Download APK](https://github.com/zotho/geometry-np/tree/master/Test_Grav/Buildozer_Test/APK) | [Check Virustotal](https://www.virustotal.com/#/file/41301ab4ee37b7bf6c27ad900213702bff3455d2fb91e2cdadfe66fe08417850/detection)

[![Android Demonstration](https://raw.githubusercontent.com/zotho/geometry-np/master/4_Android_Demo.png)](https://github.com/zotho/geometry-np/tree/master/Test_Grav/Buildozer_Test/APK)

## License

GNU General Public License v3.0
