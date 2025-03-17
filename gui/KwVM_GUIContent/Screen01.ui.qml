

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: main_screen
    objectName: "main_screen"
    width: 400
    height: 400
    color: "#ffffff"

    ColumnLayout {
        id: main_layout
        objectName: "main_layout"
        anchors.fill: parent
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        anchors.topMargin: 10
        anchors.bottomMargin: 10

        Rectangle {
            id: title_section
            objectName: "title_section"
            width: 200
            height: 50
            color: "#ffffff"
            z: 100
            Layout.minimumHeight: 80
            Layout.maximumHeight: 80
            Layout.fillWidth: true
            RowLayout {
                id: title_layout
                objectName: "title_layout"
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 5
                anchors.rightMargin: 5
                anchors.topMargin: 5
                anchors.bottomMargin: 5

                Image {
                    id: title_image
                    objectName: "title_image"
                    source: "images/logo.png"
                    Layout.preferredHeight: title_layout.height
                    Layout.preferredWidth: Layout.preferredHeight // Keep it square
                    Layout.alignment: Qt.AlignVCenter
                    fillMode: Image.PreserveAspectFit
                }

                Text {
                    id: title_name
                    objectName: "title_name"
                    text: qsTr("高偉虛擬機")
                    font.pixelSize: Math.max(20, title_layout.height * 0.5)
                    // Scale text size based on height
                }
                Item {
                    id: spacer_1
                    Layout.fillWidth: true // Pushes the last text to the right
                }
            }
        }

        Rectangle {
            id: input_section
            objectName: "input_section"
            width: 200
            height: 50
            color: "#ffffff"
            z: 100
            Layout.minimumHeight: 80
            Layout.fillWidth: true
            Layout.maximumHeight: 80

            RowLayout {
                id: input_layout
                objectName: "input_layout"
                anchors.fill: parent
                anchors.leftMargin: 5
                anchors.rightMargin: 5
                anchors.topMargin: 5
                anchors.bottomMargin: 5

                TextField {
                    id: input_id
                    objectName: "input_id"
                    text: ""
                    font.pixelSize: 36
                    inputMask: ""
                    hoverEnabled: false
                    focus: true
                    Layout.minimumHeight: 40
                    Layout.fillHeight: true
                    font.family: "Sarasa Fixed TC"
                    Layout.fillWidth: true
                    placeholderText: qsTr("請輸入員工編號")
                }

                Button {
                    id: input_btn
                    objectName: "input_btn"
                    text: qsTr("查詢")
                    display: AbstractButton.TextBesideIcon
                    Layout.maximumHeight: 70
                    Layout.minimumHeight: 70
                    Layout.fillHeight: true
                    icon.source: "images/search.svg"
                    font.pointSize: 16
                    font.family: "Sarasa Fixed TC"
                }
            }
        }

        Rectangle {
            id: status_or_selection
            width: 200
            height: 200
            color: "#ffffff"
            Layout.fillHeight: true
            Layout.fillWidth: true

            Text {
                id: status_view
                objectName: "status_view"
                visible: true
                text: qsTr("準備就緒!")
                anchors.verticalCenter: parent.verticalCenter
                font.pixelSize: 36
                font.family: "Sarasa Fixed TC"
                anchors.horizontalCenter: parent.horizontalCenter
            }

            ListView {
                id: selection_view
                objectName: "selection_view"
                visible: false
                anchors.fill: parent
                anchors.leftMargin: 5
                anchors.rightMargin: 5
                z: 100
                pixelAligned: false
                synchronousDrag: false
                model: ListModel {// ListElement {
                    //     name: "Red"
                    // }

                    // ListElement {
                    //     name: "Green"
                    // }

                    // ListElement {
                    //     name: "Blue"
                    // }
                }
                delegate: Item {
                    width: selection_view.width
                    height: 60

                    RowLayout {
                        anchors.fill: parent
                        spacing: 20

                        Text {
                            text: name
                            Layout.alignment: Qt.AlignLeft
                            verticalAlignment: Text.AlignVCenter
                        }

                        Button {
                            text: "登入"
                            Layout.alignment: Qt.AlignRight
                            implicitHeight: 50
                            font.pixelSize: 16
                            font.family: "Sarasa Fixed TC"
                            display: AbstractButton.TextBesideIcon
                            icon.source: "images/log-in.svg"
                        }
                    }
                }
            }
        }
    }
}
