import QtQuick 2.2
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.2

Item {

    id: root

    property int margin: 11

    property QtObject model;

    default property alias form: formPlaceholder.children

    property alias view: viewPlaceholder.children

    property string newButtonText: qsTr("New...")

    property string deleteButtonText: qsTr("Delete")

    property alias newButtonEnabled: newButton.enabled

    property alias deleteButtonEnabled: deleteButton.enabled

    property string saveButtonText: qsTr("Save")

    property string cancelButtonText: qsTr("Cancel")

    property alias saveButtonEnabled: saveButton.enabled

    property alias cancelButtonEnabled: cancelButton.enabled

    property var modelDefaults: {}

    signal searchRequested(string text);

    signal createRequested();

    signal deleteRequested();

    signal saveRequested();

    signal cancelRequested();

    property int currentRow: -1;

    signal currentRowChangedTo(int row);

    onCurrentRowChanged: {
        currentRowChangedTo(root.currentRow);
    }

    SplitView {

        id: mainLayout
        anchors.fill: parent
        anchors.margins: margin

        ColumnLayout {

            Layout.minimumWidth: 380

            TextField {
                id: search
                Layout.fillWidth: true
                placeholderText: qsTr("Search")
                onTextChanged: searchRequested(search.text)
            }

            Item {
                id: viewPlaceholder
                Layout.fillWidth: true
                Layout.fillHeight: true
            }

            RowLayout {
                anchors.topMargin: 6
                anchors.left: parent.left
                anchors.leftMargin: 6
                anchors.top: viewPlaceholder.bottom

                Button {
                    id: newButton
                    text: newButtonText
                    enabled: true
                    onClicked: root.createRequested()
                }

                Button {
                    id: deleteButton
                    text: deleteButtonText
                    onClicked: root.deleteRequested()
                }
            }

        }

        Rectangle {

            Layout.fillWidth: true

            Item {
                id: formPlaceholder
                width: parent.width
                height: parent.height - buttonBox.height
            }

            Row {
                id: buttonBox
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                spacing: 10
                visible: currentRow != -1
                Button {
                    id: saveButton
                    text: saveButtonText
                    onClicked: root.saveRequested()
                }

                Button {
                    id: cancelButton
                    text: cancelButtonText
                    onClicked: root.cancelRequested()
                }
            }
        }

    }

}