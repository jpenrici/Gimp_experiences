# -*- Mode: Python2; coding: utf-8; indent-tabs-mpythoode: nil; tab-width: 4 -*-

'''
    Colors experience
    =========

    View the pixel ordering experience.
    New layer will be created with the image pixel by pixel.

    Use Numpy.
'''

# Py 2.7
import os
import sys
import datetime
from array import array

# Constantes e símbolos gimp, pdb, register e a função main
from gimpfu import *

# Descrição
LABEL = "Colors experience"
INFO = "Example of visualization of grouped colors."
HELP = globals()["__doc__"]

# Local
HOME = os.environ['HOME']
FULL_PATH = os.path.realpath(__file__)
PATH, FILENAME = os.path.split(FULL_PATH)
ENV = PATH + "/pyenv/lib/python2.7"

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
dependencies = True
try:
    import numpy as np
    log += "numpy " + np.__version__ + " ... ok\n"
except ImportError as err:
    logError += str(err) + " not found\n"
    dependencies = False

if not dependencies:
    log += logError
# print(log)


def message(msg):
    pdb.gimp_message(msg)


def pxRgnToArray(layer):
    rgn = layer.get_pixel_rgn(0, 0, layer.width, layer.height, False, False)
    # print(rgn)  # <gimp.PixelRgn for drawable 'layer'>
    values = array("B", rgn[0:layer.width, 0:layer.height])  # uchar -> int
    return values  # vetor


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

    if channels == 1:
        return "Level (Gray)"
    if channels == 2:
        return "LA (Gray, Alpha)"
    if channels == 3:
        return "RGB (Red, Green, Blue)"
    if channels == 4:
        return "RGBA (Red, Green, Blue, Alpha)"
    return None


def colorsExperience(img, layer):

    global log

    # Checar dependências
    if not dependencies:
        message(LABEL + ", error: missing dependencies ...")
        saveLog(log)
        return

    inform = "Processing " + img.name + " ..."
    gimp.progress_init(inform)

    log += inform + '\n'

    try:
        # Coleta das informações
        height = layer.height
        width = layer.width
        channels = layer.bpp
        img_type = imageType(channels)

        if img_type is None:
            message("Plugin not prepared for this analysis!")
            return
        log += layer.name + ": " + img_type + '\n'

        # Contagem de tempo para imagem de dimensões altas
        start = datetime.datetime.now()

        # Converter Imagem em Array
        img_copy = pxRgnToArray(layer)
        log += layer.name + " to Array ...\n"
        pdb.gimp_progress_pulse()

        # Preparar, remodelar Array
        img_temp = [i for i in img_copy]    # copiar inteiros
        img_temp = [img_temp[i:i+channels] for i in range(0, height * width
                    * channels, channels)]  # separar pixels novamente
        log += layer.name + " initial preparation ...\n"
        pdb.gimp_progress_pulse()

        # Ordenação crescente
        for c in range(0, channels):
            # Ordenar do último canal para o primeiro
            i = channels - c - 1
            img_temp.sort(key=lambda value: value[i])
            log += layer.name + " sorting by channel " + str(i) + " ...\n"
            pdb.gimp_progress_pulse()  # visualizar execução, processo lento

        # Converter em Numpy Array
        npArray = np.array(img_temp, dtype=np.uint8)
        log += layer.name + " to Numpy Array ...\n"
        pdb.gimp_progress_pulse()

        npArray = npArray.flatten()                         # abrir
        npArray = npArray.reshape(height, width, channels)  # remodelar
        log += layer.name + " reshape ...\n"
        pdb.gimp_progress_pulse()

        end = datetime.datetime.now()
        log += "time: " + str((end - start).seconds) + " seconds ...\n"

        # Criar camada com resultado
        name = layer.name + " ordered"
        createNewLayer(img, name, npArray)
        log += img.name + " create layer " + name + " ...\n"

        pdb.gimp_selection_none(img)

    except Exception as err:
        log += "[Error - Gimp Plugin: " + FILENAME + "]: " + str(err) + '\n'
        gimp.message(LABEL + " failed.")
        saveLog(log)

    pdb.gimp_progress_end()

    print(log)      # Log no console Linux


gettext.install("gimp20-python", gimp.locale_directory, unicode=True)

# Registro do plug-in
register(
    "colorsExperience",         # nome da função
    N_(INFO),              # sobre o plug-in
    HELP,                  # docstring como Help
    "jpenrici",            # autor
    "GPL V2 License",      # licença
    "2020",                # data de criação (ano)
    N_(LABEL),             # rótulo do plugin no menu
    "RGB*, GRAY*",         # tipos de imagens suportados
    [   # parâmetros de entrada do método
        (PF_IMAGE, "img", _("_Image"), None),
        (PF_DRAWABLE, "drw", _("_Drawable"), None),
    ],
    [], # parâmetros de saída do método
    colorsExperience,      # nome de chamada do método
    menu="<Image>/Image",  # caminho no menu
    domain=("gimp20-python", gimp.locale_directory)
    # on_query=None,
    # on_run=None
)

# Função princiapl, chamada após o registro do plug-in
main()
