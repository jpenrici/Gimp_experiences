# -*- Mode: Python2; coding: utf-8; indent-tabs-mpythoode: nil; tab-width: 4 -*-

'''
    Face Detection with OpenCV
    =========

    pdb.python_fu_faceDetection(img, drw, option)

    Analysis options for detected faces:
    1) option="detection" : Only mark with a rectangular border.
    2) option="selection" : Only select for later copy and paste.

    Note:
    Opencv-python and Numpy requirements.
'''

# Py 2.7
import os
import sys
import datetime
from array import array

# Constantes e símbolos gimp, pdb, register e a função main
from gimpfu import *

# Descrição
LABEL = "Face Detection"
INFO = "Detect face in image."
HELP = globals()["__doc__"]

# Local
FULL_PATH = os.path.realpath(__file__)
PATH, FILENAME = os.path.split(FULL_PATH)
ENV = PATH + "/pyenv/lib/python2.7"
HAAR_MODEL = "haarcascade_frontalface_default.xml"

# Log
now = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
log = "\nGIMP: " + now
log += "\nPlug-in: " + LABEL + '\n'
logError = "Unexpected error: "

# Virtualenv
if not os.path.isdir(ENV):
    logError += "pyenv/lib/python2.7 ... not found\n"
else:
    sys.path.extend([ENV, ENV + "/site-packages",
                     ENV + "/site-packages/setuptools"])

# Dependências
cascade_path = ""
dependencies = True

try:
    import numpy as np
    log += "numpy " + np.__version__ + " ... ok\n"
except ImportError as err:
    logError += str(err) + " not found\n"
    dependencies = False

try:
    import cv2 as cv
    log += "opencv " + cv.__version__ + " ... ok\n"
    cascade_path = os.path.join(os.path.dirname(os.path.abspath(cv.__file__)),
                                "data/" + HAAR_MODEL)
except ImportError as err:
    logError += str(err) + " not found\n"
    dependencies = False

if not os.path.isfile(cascade_path):
    logError += cascade_path + " not found\n"
    cascade_path = ENV + "/site-packages/cv2/data/" + HAAR_MODEL
elif not os.path.isfile(cascade_path):
    logError += cascade_path + " not found\n"
    cascade_path = PATH + "/" + HAAR_MODEL
elif not os.path.isfile(cascade_path):
    logError += cascade_path + " not found\n"
    dependencies = False

if os.path.isfile(cascade_path):
    log += cascade_path + " ... ok\n"

if (not dependencies):
    log += logError
# print(log)


def message(msg):
    pdb.gimp_message(msg)


def pxRgnToNumpy(layer):
    rgn = layer.get_pixel_rgn(0, 0, layer.width, layer.height, False, False)
    values = array("B", rgn[0:layer.width, 0:layer.height])  # uchar -> int
    npArray = np.array(values, dtype=np.uint8)
    return npArray.reshape(layer.height, layer.width, layer.bpp)


def createNewLayer(img, name, npArray):
    newLayer = gimp.Layer(img, name, img.width, img.height,
                          img.active_layer.type, 100, NORMAL_MODE)
    rgn = newLayer.get_pixel_rgn(0, 0, newLayer.width, newLayer.height, True)
    rgn[:, :] = np.uint8(npArray).tobytes()  # gimp.PixelRgn
    img.add_layer(newLayer, lastLayer(img))
    gimp.displays_flush()


def lastLayer(img):
    pos = 0
    for i in range(len(img.layers)):
        if(img.layers[i] == img):
            pos = i
    return pos


def exportTxt(filename, text):
    filename = filename.replace("-", "")
    filename = filename.replace(":", "")
    filename = filename.replace(" ", "_")
    try:
        filename = open(filename, "w")
        filename.write(text)
        filename.close()
    except Exception:
        pass


def saveLog(text):
    filename = "LogGimpPlugin_" + now + ".txt"
    exportTxt(filename, text)


def imageType(channels):

    if channels == 3:
        return "RGB (Red, Green, Blue)"
    if channels == 4:
        return "RGBA (Red, Green, Blue, Alpha)"
    return None


def faceDetection(img, layer, option):

    global log

    # Checar dependências
    if (not dependencies):
        message(LABEL + ", error: missing dependencies ...")
        saveLog(log)
        return

    inform = "Processing " + img.name + " ..."
    gimp.progress_init(inform)
    pdb.gimp_image_undo_group_start(img)

    log += inform + '\n'
    log += "Face " + option + " ...\n"

    try:
        # Converter Imagem em Numpy Array
        img_copy = pxRgnToNumpy(layer)
        log += layer.name + " to Numpy Array ...\n"

        height, width, channels = img_copy.shape
        img_type = imageType(channels)

        if img_type is None:
            message("Plugin not prepared for this analysis!")
            return
        log += layer.name + ": " + img_type + '\n'

        # OpenCV
        img_gray = cv.cvtColor(img_copy, cv.COLOR_RGB2GRAY)
        log += layer.name + " to OpenCV ...\n"
        log += "image RGB to GRAY ...\n"

        # Detecção
        clf = cv.CascadeClassifier(cascade_path)
        faces = clf.detectMultiScale(img_gray, 1.3, 5)

        hits = len(faces)
        log += str(hits) + " faces detected ...\n"

        if hits > 0 and option == "detection":

            # Cor do retângulo
            color = [0 for i in range(channels)]
            if channels % 2 == 0:
                color[-1] = 255  # alterar Alpha em [R,G,B,A]

            # Marcar retângulo
            for (x, y, w, h) in faces:
                img_copy = cv.rectangle(img_copy, (x, y), (x+w, y+h),
                                        tuple(color), 2)

            name = layer.name + " faces"
            createNewLayer(img, name, img_copy)
            log += img.name + ": create layer " + name + " ...\n"

            pdb.gimp_selection_none(img)

            # exportação via OpenCV (opcional - teste)
            # img_out = cv.cvtColor(img_copy, cv.COLOR_BGR2RGB)
            # cv.imwrite("temp_" + layer.name, img_out)

        elif hits > 0 and option == "selection":

            pdb.gimp_selection_none(img)
            for (x, y, w, h) in faces:
                pdb.gimp_image_select_ellipse(img, 0, x, y, w, h)
                # pdb.gimp_image_select_rectangle(img, 0, x, y , w, h)

        else:

            message("Detection not possible.")

        pdb.gimp_image_undo_group_end(img)
        gimp.displays_flush()

        log += inform + " ok\n"

    except Exception as err:
        log += "[Error - Gimp Plugin: " + FILENAME + "]: " + str(err) + '\n'
        gimp.message(LABEL + " failed.")

    pdb.gimp_progress_end()

    print(log)      # Log no console Linux
    saveLog(log)    # Opcional


gettext.install("gimp20-python", gimp.locale_directory, unicode=True)

# Registro do plug-in
register(
    "faceDetection",       # nome da função
    N_(INFO),              # sobre o plug-in
    HELP,                  # docstring como Help
    "jpenrici",            # autor
    "GPL V2 License",      # licença
    "2020",                # data de criação (ano)
    N_(LABEL),             # rótulo do plugin no menu
    "RGB*",                # tipos de imagens suportados
    [   # parâmetros de entrada do método
        (PF_IMAGE, "img", _("_Image"), None),
        (PF_DRAWABLE, "drw", _("_Drawable"), None),
        (PF_RADIO, "option", "", "detection",
          (("Only mark with a rectangular border.", "detection"),
           ("Only select for later copy and paste.", "selection"))),
    ],
    [], # parâmetros de saída do método
    faceDetection,         # nome de chamada do método
    menu="<Image>/Image",  # caminho no menu
    domain=("gimp20-python", gimp.locale_directory)
    # on_query=None,
    # on_run=None
)

# Função princiapl, chamada após o registro do plug-in
main()
