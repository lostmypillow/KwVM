requires python using 3.10.11

set objectName in qml otherwise can't reference it in python

only files that needs to be worried about for Python development:
KwVM_GUIContent/Screen01.qml
Python/main.py
Python/controller.py


`pyside6-rcc KwVM_GUI.qrc -o Python/autogen/resources.py`

`cd Python && pyside6-deploy`

Open file manager, then --> Edit--> Preferences --> General --> General : check option "Don't ask options on launch executable ...."