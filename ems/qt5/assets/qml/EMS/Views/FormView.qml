
import QtQuick 2.2
import org.ems 1.0

Item {

    id: root

    property alias currentRow: currentRowModel.currentRow

    property bool submitOnChanged: false

    property alias delegate: view.delegate

    property alias count: view.count

    property alias repeater: view

    property QtObject model

    clip: true

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

    function showError(error, msecs) {
        errorText.text = error.message
        errorNotifier.state = 'shown'
        timer.interval = msecs
        timer.running = true
    }

    function setModelProperty(row, property, value) {

        var targetRow = view.model.currentRow;

        var rowData = root.model.get(targetRow)

        console.log('writing', row, property, value, 'old:', rowData[property])
        if (rowData[property] === value) {
            return;
        }

        root.model.setProperty(targetRow, property, value);

        modelPropertyChanged(targetRow, property, value);

        if (root.submitOnChanged) {
            root.accept();
        }
    }

    Connections {
        target: model
        onError: {
            showError(error, 4000)
        }
        ignoreUnknownSignals: true
    }

    Timer {
        id: timer
        interval: 1000
        running: false
        repeat: false
        onTriggered: errorNotifier.state = ""
    }

    Repeater {
        id: view
        anchors.fill: parent

        model: CurrentRowModel {
            id: currentRowModel
            objectName: "FormView.view.model"
            parentModel: root.model
        }
    }

    Rectangle {
        id: errorNotifier
        property int bottomMargin: 0
        width: parent.width
        anchors.bottom: parent.top
        height: 120
        anchors.bottomMargin: errorNotifier.bottomMargin
        color: '#f2dede'
        Text {
            id: errorText
            color: '#a94442'
            wrapMode: Text.WordWrap
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.margins: 20
//             anchors.leftMargin: 20
        }

        states: [
            State {
                name: "shown"
                PropertyChanges { target: errorNotifier; anchors.bottomMargin: 0-errorNotifier.height }
            }
        ]

        Behavior on anchors.bottomMargin {
            NumberAnimation { duration: 500; easing.type: Easing.InOutQuart }
        }
    }

}