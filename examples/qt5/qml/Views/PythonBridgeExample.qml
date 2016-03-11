
import QtQuick 2.2
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.2

import org.ems 1.0
import EMS.Application 1.0
import EMS.Editors 1.0
import EMS.Views 1.0
import EMS.Inputs 1.0

Item {

    id: root

    width: 1076
    height: 800

    GridLayout {

        columns: 2

        Button {
            id: floatButton
            text: "Push for a float"
            onClicked: {
                floatLabel.text = "" + Application.pyFloat("floats.multiply", 3, 4) + ""
            }
        }

        Label {
            id: floatLabel
            text: ""
        }

        Button {
            id: intButton
            text: "Push for an int"
            onClicked: {
                intLabel.text = "" + Application.pyInt("ints.add", 6, 4) + ""
            }
        }

        Label {
            id: intLabel
            text: ""
        }

        Button {
            id: stringButton
            text: "Push for a string"
            onClicked: {
                stringLabel.text = Application.pyString("strings.hello","World")
            }
        }

        Label {
            id: stringLabel
            text: ""
        }

        Button {
            id: boolButton
            text: "Push for a bool"
            onClicked: {
                boolLabel.text = "" + Application.pyString("bools.opposite", false)
            }
        }

        Label {
            id: boolLabel
            text: ""
        }

        Button {
            id: dictButton
            text: "Push for a dict"
            onClicked: {
                dictLabel.text = JSON.stringify(Application.pyDict("dicts.sample"))
            }
        }

        Label {
            id: dictLabel
            text: ""
        }

        Button {
            id: listButton
            text: "Push for a list"
            onClicked: {
                listLabel.text = JSON.stringify(Application.pyList("lists.sample"))
            }
        }

        Label {
            id: listLabel
            text: ""
        }

        Button {
            id: objectsButton
            text: "Push for some objects"
            onClicked: {
                objectsLabel.text = JSON.stringify(Application.pyList("objects.samples"))
            }
        }

        Label {
            id: objectsLabel
            text: ""
        }

    }


    Component.onCompleted: {

        if (typeof qmlApp !== 'undefined') {
            Application.qmlApp = qmlApp;
        }

//         root.model.sourceModel = Application.model("contacts");
    }

}