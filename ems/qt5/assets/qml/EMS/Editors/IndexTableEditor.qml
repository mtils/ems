import QtQuick 2.2
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.2

Item {

    id: root

    property int margin: 11

    property QtObject model;

    default property alias contents: formPlaceholder.children

    property alias tableView: resourcesView

    property string newButtonText: qsTr("New...")

    property string deleteButtonText: qsTr("Delete")

    property var modelDefaults: {}

    signal searchRequested(string text);

    property int currentRow: -1;

    signal currentRowChangedTo(int row);

    onCurrentRowChanged: {
        currentRowChangedTo(root.currentRow);
    }

    Timer {
        id: selectionTimer
        interval: 300
        running: false
        repeat: false
        onTriggered: {
            resourcesView.selection.clear()
            resourcesView.selection.select(resourcesView.model.count-1)
        }
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

            TableView {
                id: resourcesView
                focus: true
                Layout.fillWidth: true
                Layout.fillHeight: true

                model: root.model

            }

            Connections {
                target: resourcesView.selection
                onSelectionChanged: {
                    resourcesView.selection.forEach(function(rowIndex){
                        root.currentRow = rowIndex;
                    }); 
                }
            }

            RowLayout {
                anchors.topMargin: 6
                anchors.left: parent.left
                anchors.leftMargin: 6
                anchors.top: resourcesView.bottom

                Button {
                    id: newModel
                    text: newButtonText
                    enabled: true
                    onClicked: {
                        if (typeof(modelDefaults) === 'undefined') {
                            resourcesView.model.append({})
                        }
                        else {
                            resourcesView.model.append(modelDefaults)
                        }
                        selectionTimer.running = true
                    }
                }

                Button {
                    id: deleteModel
                    text: deleteButtonText
                    enabled: resourcesView.selection.count > 0
                    onClicked: {
                        resourcesView.selection.forEach( function(rowIndex) {
                             resourcesView.model.remove(rowIndex, 1);
                        })
                    }
                }
            }

        }

        Item {
            id: formPlaceholder
            Layout.minimumWidth: 480
            Layout.fillWidth: true
        }

    }

}