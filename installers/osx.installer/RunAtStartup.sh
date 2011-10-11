#!/bin/sh

# A simple script to exhaustively search for python. 
# As long as the interpreter is found once than this
# will exit successfully.  Else kill the installer.

# Minimum spec is 2.7, the installer can handle the rest 
# through requirement scripts.

if [ -d /opt/local/Library/Frameworks/Python.framework/Versions/2.7 ]; then
	touch /tmp/p27_macports
elif [ -d /opt/local/Library/Frameworks/Python.framework/Versions/3.2 ]; then
	touch /tmp/p32_macports
elif [ -d /Library/Frameworks/Python.framework/Versions/2.7/ ]; then
	touch /tmp/p27_installer
elif [ -d /Library/Frameworks/Python.framework/Versions/2.7/ ]; then
	touch /tmp/p32_installer
elif [ -d /Library/Python/2.7/ ]; then
	touch /tmp/p27_lion
else
	exit 0
fi 

exit 1
