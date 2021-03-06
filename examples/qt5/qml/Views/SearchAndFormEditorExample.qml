
import QtQuick 2.2
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.2

import org.ems 1.0
import EMS.Application 1.0
import EMS.Editors 1.0
import EMS.Views 1.0
import EMS.Inputs 1.0

SearchAndFormEditor {

    id: root

    width: 1076
    height: 800

    model: FilterModel {
        filterKey: "surname"
    }

    modelDefaults: {
        "company":"",
        "forename":"",
        "surname":"",
        "phone":"",
        "fax":"",
        "memo":""
    }

    onSearchRequested: model.setFilterWildcard(text)

    onCreateRequested: view.append(root.modelDefaults)

    onDeleteRequested: view.deleteSelected()

    onSaveRequested: form.accept()

    onCancelRequested: form.cancel()

    view: ManagedTableView {
        id: view

        anchors.fill: parent
        model: root.model

        onCurrentRowChanged: root.currentRow = view.currentRow

        TableViewColumn {
            role: "surname"
            title: "Surname"
        }
        TableViewColumn {
            role: "forename"
            title: "Forename"
        }
        TableViewColumn {
            role: "company"
            title: "Company"
        }
    }

    FormView {

        id: form
        anchors.fill: parent

        model: root.model
        currentRow: root.currentRow


        delegate: FormViewDelegate {

            anchors.fill: parent

            GridLayout {

                anchors.top: parent.top
                anchors.topMargin: 12
                anchors.horizontalCenter: parent.horizontalCenter
                width: parent.width - 80
                columnSpacing: 8
                rowSpacing: 8
                columns: 6

                Label {
                    text: qsTr("Contact Type")
                    Layout.columnSpan: 3
                }

                Label {
                    text: qsTr("Company")
                    Layout.columnSpan: 3
                }

                ModelComboBox {

                    id: contact_typeInput

                    Layout.fillWidth: true
                    Layout.columnSpan: 3
                    bindId: contact_type
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
                        write('contact_type', contact_typeInput.currentId)
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