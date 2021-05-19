Gimp_Face_Detection
===================

In this plug-in, the potential of OpenCV and the GIMP Plugin to experience faces in the image using the Haar Cascades feature is experienced. <br>

[README-pt-BR](https://github.com/jpenrici/Gimp_experiences/blob/main/GIMP_Plugin_Py/GIMP_Face_Detection/README-pt-BR.md) <br>

Installation Steps
===================

[1] Install OpenCV and NumPy for Python version 2.7, as indicated by the official websites. <br>
[2] Follow the steps for the standard installation of a GIMP Plugin. <br>
[3] Copy the `gimp_plugin_faceDetection.py` file to the `plug-ins` directory. Copy the `haarcascade_frontalface_default.xml` in due course. <br>
[4] On Linux, if necessary, install `virtualenv`. Give the `install_dependencies.sh` file permission and run the code. <br>
[5] Follow the final steps of the standard GIMP Plugin installation. <br>

Requeriments
============

[OpenCV](https://opencv.org/) <br>
[NumPy](https://numpy.org/) <br>
[Virtualenv](https://pypi.org/project/virtualenv/) (Optional) <br>

References
==========

[OpenCV](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_objdetect/py_face_detection/py_face_detection.html) : Face detection using Haar Cascades. <br>
[GIMP Developer](https://developer.gimp.org/plug-ins.html) : Tutorial GIMP Plugin. <br>
[Paul Bourke](http://paulbourke.net/) : Computer Graphics Algorithms. <br>
[Akkana e Joao](https://shallowsky.com/blog/gimp/pygimp-pixel-ops.html) : Pixel operations algorithm in GIMP. <br>
[Kritik Soman](https://arxiv.org/abs/2004.13060) : Inspiration in the use of GIMP Python Plugins in Computer Vision. <br>
