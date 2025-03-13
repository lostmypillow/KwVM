requires python < 3.13 >= 3.8, using 3.10.11

set objectName in qml otherwise can't reference it in python

only files that needs to be worried about for Python development:
KwVM_GUIContent/Screen01.qml
Python/main.py
Python/controller.py

0.2.0 changelog
Switched to QT Quick (QML) + PySide6
Improved API call (no longer freezes main loop)

`pyside6-deploy --name kwmathconsult --mode standalone`
`pyside6-rcc KwVM_GUI.qrc -o Python/autogen/resources.py`

Open file manager, then --> Edit--> Preferences --> General --> General : check option "Don't ask options on launch executable ...."