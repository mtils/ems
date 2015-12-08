
import QtQuick 2.2
import org.ems 1.0

Item {

    id: root

    property int currentRow: -1

    property bool submitOnChanged: false

    property alias delegate: view.delegate

    property QtObject model

    signal modelPropertyChanged(int row, string property, variant value);

    signal accepted();

    signal cancelled();

    function accept() {
        root.model.submit();
        accepted();
    }

    function cancel() {
        root.model.revert()
        cancelled();
    }

    function itemAt(index) {
        return view.itemAt(index);
    }

    function setModelProperty(row, property, value) {

//         console.log("setModelProperty", view.model, row, property, value)
        var targetRow = view.model.currentRow;
        var rowData = root.model.get(targetRow)

        if (rowData[property] === value) {
            return;
        }

        root.model.setProperty(targetRow, property, value);

        modelPropertyChanged(targetRow, property, value);

        if (root.submitOnChanged) {
            root.accept();
        }
    }

    Repeater {
        id: view
        anchors.fill: parent

        model: CurrentRowModel {
            currentRow: root.currentRow
            sourceModel: root.model
        }

    }
}