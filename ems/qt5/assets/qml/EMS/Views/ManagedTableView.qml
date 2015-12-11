import QtQuick 2.2
import QtQuick.Controls 1.4

TableView {

    id: root

    property alias autoSelectionDelay: selectionTimer.interval

    property bool hasSelection: selection.count > 0

    function append(data) {
        model.append(data);
        selectLastDelayed();
    }

    function deleteSelected() {
        selection.forEach( function(rowIndex) {
            model.remove(rowIndex, 1);
        })
    }

    function selectLastDelayed() {
        selectionTimer.running = true;
    }

    Timer {
        id: selectionTimer
        interval: 300
        running: false
        repeat: false
        onTriggered: {
            root.selection.clear()
            root.selection.select(root.model.count-1)
        }
    }

    Connections {
        target: root.selection
        onSelectionChanged: {
            root.selection.forEach(function(rowIndex){
                root.currentRow = rowIndex;
            }); 
        }
    }

}