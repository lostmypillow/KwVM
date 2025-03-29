requires python using 3.10.11

set objectName in qml otherwise can't reference it in python

only files that needs to be worried about for Python development:
KwVM_GUIContent/Screen01.qml
Python/main.py
Python/controller.py

0.0.1 changelog
Beta release. Can open both VMs. 0.0.2 will produce .desktop files on 'setup' input, build.sh for Linux, test with deployed API, better organized Python code for PySide6

0.0.2 changelog
Produces .desktop files on 'setup', prepare for test with deployed API

0.0.3 ONLY API CHANGES
Finalized basic API functionality, only hard coded data

0.0.4
Added supplied spice proxy instead of pve proxy
change to production values

0.0.5
Moved packages installation into "setup" in CentralController

0.0.6-alpha1
Moved package installation to start of program and added checks to avoid multiple sudo prompts

`pyside6-rcc KwVM_GUI.qrc -o Python/autogen/resources.py`

`cd Python && pyside6-deploy`

Open file manager, then --> Edit--> Preferences --> General --> General : check option "Don't ask options on launch executable ...."