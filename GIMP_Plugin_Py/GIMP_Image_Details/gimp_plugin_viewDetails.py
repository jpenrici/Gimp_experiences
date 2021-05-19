# -*- Mode: Python2; coding: utf-8; indent-tabs-mpythoode: nil; tab-width: 4 -*-

'''
    View Details
    =========

    Example to view image details.
    Use Numpy, Pandas, Scipy...

    pdb.python_fu_viewDetails(img, drw ...)
'''

# Py 2.7
import os
import sys
import datetime
from array import array

# Constantes e símbolos gimp, pdb, register e a função main
from gimpfu import *

# Descrição
LABEL = "View Details"
INFO = "Use advanced libraries to detail the image.\nSelect the exported data."
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
try:
    import pandas as pd
    log += "pandas " + pd.__version__ + " ... ok\n"
except ImportError as err:
    logError += str(err) + " not found\n"
    dependencies = False
try:
    from scipy import stats
    log += "scipy stats ... ok\n"
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
    values = array("B", rgn[0:layer.width, 0:layer.height])  # uchar -> int
    return values  # vetor


def pxRgnToNumpy(layer):
    values = pxRgnToArray(layer)
    npArray = np.array(values, dtype=np.uint8)
    return npArray.reshape(layer.height, layer.width, layer.bpp)  # matriz


def pxRgnToTxt(layer):
    # Função lenta para matriz com muitos pixels
    text = ""
    values = pxRgnToArray(layer)

    i = 1
    j = 1
    for v in values:
        text += str(v)
        if i < layer.bpp:
            text += ','
            i += 1
        else:
            i = 1
            if j < layer.width:
                text += ';'
                j += 1
            else:
                pdb.gimp_progress_pulse()
                text += '\n'
                j = 1

    return text


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


def detailsNp(npArray):
    # Detalhes obtidos do Numpy
    text = ""
    height, width, channels = npArray.shape
    max_value = str(np.amax(npArray))
    min_value = str(np.amin(npArray))
    img_type = imageType(channels)

    text = "matrix: " + str(height) + " x " + str(width) + " " + img_type
    text += "\nvalues(min, max): " + min_value + ", " + max_value + '\n'

    for i in range(channels):
        max_value = str(np.amax(npArray[:, :, i]))
        min_value = str(np.amin(npArray[:, :, i]))
        text += img_type[i] + "(min, max): " + min_value + ", " + max_value
        text += '\n'

    return text


def detailsPd(npArray):
    # Detalhes obtidos do Pandas
    height, width, channels = npArray.shape
    img_type = imageType(channels)
    z = [img_type[i] for i in range(channels)]

    names = ['y', 'x', None]
    index = pd.MultiIndex.from_product([range(height), range(width), z],
                                       names=names)

    # Data Frame
    df = pd.Series(npArray.flatten(), index=index)
    df = df.unstack()
    df = df.reset_index().reindex(columns=['x', 'y'] + z)

    return df


def detailsScipy(npArray):
    # Detalhes obtidos do Stats
    text = ""
    height, width, channels = npArray.shape
    img_type = imageType(channels)
    c = [img_type[i] for i in range(channels)]
    for i in range(0, len(c)):
        # n elementos, mínimo e máximo, média, variância, obliquidade, curtose
        nobs, minmax, mean, variance, skewness, kurtosis = stats.describe(
                npArray[:, :, i].flatten())
        temp = "[  {0}  ]\nnumber of elements: {1}\nmin: {2}\nmax: {3}\n" \
            "mean: {4}\nvariance:: {5}\nskewness: {6}\nkurtosis: {7}\n"
        text += temp.format(c[i], nobs, minmax[0], minmax[1], mean,
                            variance, skewness, kurtosis)
    return text


def viewDetails(img, layer, directory, saveSummary, saveDataNp,
                saveDataPd, saveDataTxt):

    global log

    # Checar solicitações
    if not (saveSummary or saveDataNp or saveDataPd or saveDataTxt):
        log += "nothing to do ...\n"
        print(log)
        return

    # Checar dependências
    if not dependencies:
        message(LABEL + ", error: missing dependencies ...")
        saveLog(log)
        return

    inform = "Processing " + img.name + " ..."
    gimp.progress_init(inform)

    log += inform + '\n'
    filename = directory + "/" + (layer.name).replace('.', '_')  # export

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

        # Numpy -> Summary
        summary = layer.name + '\n' + now + '\n'
        summary += "\nNumpy:\n"
        summary += detailsNp(img_copy) + '\n'

        # Pandas -> Summary
        df = detailsPd(img_copy)
        summary += "\nPandas:\n"
        summary += df.describe().to_string() + '\n'
        log += layer.name + " to Pandas Data Frame ...\n"

        # Scipy -> Summary
        text = detailsScipy(img_copy)
        summary += "\nScipy Stats:\n"
        summary += text + '\n'
        log += layer.name + " to Scipy Stats ...\n"

        # Local para exportação de dados
        log += "local: " + directory + " ...\n"

        # Exportar
        if saveSummary:
            # Salvar informações úteis
            log += layer.name + " ... export Summary ...\n"
            exportTxt(filename + "_summary_" + now + ".txt", summary)

        if saveDataNp:
            # Salvar matriz Numpy
            log += layer.name + " ... export data: Numpy ...\n"
            pdb.gimp_progress_set_text("saving Numpy file ...")
            np.save(filename, img_copy)
            log += "saving Numpy file ...\n"

        if saveDataPd:
            # Salvar dados do Pandas
            log += layer.name + " ... export data: Pandas ...\n"
            pdb.gimp_progress_set_text("saving Pandas files ...")

            # Formato Python Pickle
            pdb.gimp_progress_set_text("saving Python Pickle Format ...")
            log += "saving Pandas Data Frame to Python Pickle Format ...\n"
            df.to_pickle(filename + ".pkl")

            # Formato CSV
            pdb.gimp_progress_set_text("saving Pandas Data Frame to CSV ...")
            log += "saving Pandas Data Frame to CSV ...\n"
            df.to_csv(filename + ".csv", sep=';', encoding='utf-8')

        if saveDataTxt:
            # Salvar matriz de pixels em Txt para uso em planilhas
            # Método lento, leitura pixel a pixel
            # Saída: Canal 1, Canal 2, Canal 3, Canal N; ... (Texto)
            pdb.gimp_progress_set_text("converting matrix to text, please wait ...")
            start = datetime.datetime.now()
            data = pxRgnToTxt(layer)
            pdb.gimp_progress_set_text("saving TXT file ...")
            exportTxt(filename + ".txt", data)
            end = datetime.datetime.now()
            log += layer.name + " ... export data: Txt ... "
            log += "time: " + str((end - start).seconds) + " seconds ...\n"

        if saveSummary:
            message("Check summary in " + filename + ".txt")
        else:
            message("Finished.")

    except Exception as err:
        log += "[Error - Gimp Plugin: " + FILENAME + "]: " + str(err) + '\n'
        gimp.message(LABEL + " failed.")
        saveLog(log)

    pdb.gimp_progress_end()

    print(log)      # Log no console Linux


gettext.install("gimp20-python", gimp.locale_directory, unicode=True)

# Registro do plug-in
register(
    "viewDetails",         # nome da função
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
        (PF_DIRNAME, "directory", _("Local"), HOME),
        (PF_BOOL, "saveSummary", _("Summary"), True),
        (PF_BOOL, "saveDataNp", "Data Numpy", False),
        (PF_BOOL, "saveDataPd", "Data Pandas", False),
        (PF_BOOL, "saveDataTxt", "Data Text (Slow)", False),
    ],
    [], # parâmetros de saída do método
    viewDetails,           # nome de chamada do método
    menu="<Image>/Image",  # caminho no menu
    domain=("gimp20-python", gimp.locale_directory)
    # on_query=None,
    # on_run=None
)

# Função princiapl, chamada após o registro do plug-in
main()
