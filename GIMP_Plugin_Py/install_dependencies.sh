#!/bin/bash
# Checar dependências Python para uso no GIMP Plugin.

GIMP_PATH="$HOME/.gimp-2.8"					# GIMP 2.8
# GIMP_PATH="$HOME/.config/GIMP/2.10"		# GIMP 2.10
PYENV="$GIMP_PATH/plug-ins/pyenv"

separator="--------------------------------------------------------------------"
pyVersion=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

echo $separator
echo "Python: $pyVersion"

if [ $pyVersion != "2.7" ]; then
	echo "Python 2.7 is necessary for the Plugin to work."
	exit
fi

echo "Virtualenv ..."
if [ ! -d "$PYENV" ]; then

	echo "Installing $PYENV ..."

	virtualenv --python="$(which python2.7)" $PYENV
	
	source $PYENV/bin/activate
	python -m pip install --upgrade pip
	python -m pip install numpy
	python -m pip install pandas
	python -m pip install scipy
	python -m pip install opencv-python==4.2.0.32
	deactivate

	echo ""
	echo "Finished."

else
	echo "Environment already setup!"
fi

echo $separator
echo ""