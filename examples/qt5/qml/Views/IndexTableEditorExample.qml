
import QtQuick 2.2
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.2

import org.ems 1.0
import EMS.Application 1.0
import EMS.Editors 1.0
import EMS.Views 1.0
import EMS.Inputs 1.0

IndexTableEditor {

    id: root

    width: 1076
    height: 800

    model: FilterModel {
        filterKey: "surname"
    }

    onSearchRequested: model.setFilterWildcard(text)

    tableView {
        resources: [
            TableViewColumn {
                role: "surname"
                title: "Surname"
            },
            TableViewColumn {
                role: "forename"
                title: "Forename"
            },
            TableViewColumn {
                role: "company"
                title: "Company"
            }
        ]
    }

    FormView {

        id: form
        anchors.fill: parent

        model: root.model
        currentRow: root.currentRow


        delegate: FormViewDelegate {

            function setContactType(contactType) {
                contact_typeInput.currentId = contactType;
            }

            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width - 80
            height: 300
            anchors.top: parent.top

            GridLayout {

                anchors.fill: parent
                columnSpacing: 8
                rowSpacing: 8
                columns: 6

                Label {
                    text: qsTr("Contact Type")
                    Layout.columnSpan: 3
                }

                Label {
                    text: qsTr("Company") + " " + contact_type
                    Layout.columnSpan: 3
                }

                ModelComboBox {

                    id: contact_typeInput

                    Layout.fillWidth: true
                    Layout.columnSpan: 3
                    currentId: contact_type
                    textRole: 'name'
                    model: ListModel {
                        ListElement {
                            ID: 'PERSON'
                            name: 'Person'
                        }
                        ListElement {
                            ID: 'ORGANISATION'
                            name: 'Organisation'
                        }
                    }
                    onActivated: {
                        write('contact_type', currentId)
                    }
                }

                TextField {
                    Layout.columnSpan: 3
                    Layout.fillWidth: true
                    text: company
                    onEditingFinished: write('company', text)
                }

                Label {
                    text: qsTr("Forename")
                    Layout.columnSpan: 3
                }

                Label {
                    text: qsTr("Surname")
                    Layout.columnSpan: 3
                }

                TextField {
                    Layout.columnSpan: 3
                    Layout.fillWidth: true
                    text: forename
                    onEditingFinished: write('forename', text)
                }

                TextField {
                    Layout.columnSpan: 3
                    Layout.fillWidth: true
                    text: surname
                    onEditingFinished: write('surname', text)
                }

                Label {
                    text: qsTr("Phone")
                    Layout.columnSpan: 3
                }

                Label {
                    text: qsTr("Fax")
                    Layout.columnSpan: 3
                }

                TextField {
                    Layout.columnSpan: 3
                    Layout.fillWidth: true
                    text: phone
                    onEditingFinished: write('phone', text)
                }

                TextField {
                    Layout.columnSpan: 3
                    Layout.fillWidth: true
                    text: fax
                    onEditingFinished: write('fax', text)
                }

                Label {
                    text: qsTr("Notes")
                    Layout.columnSpan: 6
                }

                TextArea {
                    Layout.columnSpan: 6
                    Layout.fillWidth: true
                    text: memo
                    onActiveFocusChanged: {
                        if (!activeFocus) {
                            write('memo', text);
                        }
                    }
                }

                Button {
                    text: qsTr("Save")
                    Layout.columnSpan: 1
                    onClicked: form.accept()
                }

                Button {
                    text: qsTr("Cancel")
                    Layout.columnSpan: 1
                    onClicked: {
//                         form.cancel()
//                         form.setModelProperty(0, "contact_type", "PERSON")
                            form.itemAt(0).setContactType("PERSON");
                    }
                }
            }

        }
    }


    Component.onCompleted: {

        if (typeof qmlApp !== 'undefined') {
            Application.qmlApp = qmlApp;
        }

        root.model.sourceModel = Application.model("contacts");
    }

}