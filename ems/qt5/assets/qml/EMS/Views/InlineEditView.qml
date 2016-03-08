import QtQuick 2.2
import QtQuick.Controls 1.4

Item {

    id: root
    width: 600
    height: buttonView.height + root.headerHeight + root.spacing + root.spacing

    property alias delegateHeight: itemView.delegateHeight
    property int headerHeight: 20
    property int buttonWidth: 30
    property int buttonHeight: 30
    property int spacing: 1

    property string addButtonText: "+"
    property string removeButtonText: "-"
    property variant modelDefaults
    readonly property alias itemWidth: itemView.width

    property bool submitOnChanged: false
    property alias delegate: itemView.delegate
    property alias header: itemView.header
    property alias model: itemView.model
    property alias count: itemView.count

    property string positionRole: ""

    default property alias labels: headerRow.children

    signal appended();
    signal removed(int row);
    signal modelPropertyChanged(int row, string property, variant value);
    signal submitting();
    signal submitted();

    onSubmitting: {
        if (positionRole) {
            writePositions(positionRole)
        }
    }

    function writePositions(role) {
        var position = -1;
        for (var i=0; i < root.count; i++) {
            position = i+1;
            if (itemView.model.get(i)[role] !== position) {
                itemView.model.setProperty(i, role, position);
            }
        }
    }

    function submit() {
        submitting();
        itemView.model.submit();
        submitted();
    }

    Row {
        id: headerRow
        width: parent.width
        height: headerHeight
        spacing: root.spacing
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.leftMargin: root.spacing
    }

    ListView {
        id: itemView
        anchors.top: headerRow.bottom
        width: parent.width - buttonView.width - root.spacing
        height: delegateHeight * itemView.count
        spacing: 1
        property int delegateHeight: 30

        onCountChanged: {
            buttonView.syncModel()
        }
        onModelChanged: {
            buttonView.syncModel()
        }

        function appendRow() {
            itemView.model.append(modelDefaults)
            appended();
        }

        function removeRow(row) {
            itemView.model.remove(row, 1);
            removed(row);
            if (root.submitOnChanged) {
                root.submit()
            }
        }

        function setModelProperty(row, property, value) {

            var rowData = itemView.model.get(row)

            if (rowData[property] === value) {
                return;
            }

            itemView.model.setProperty(row, property, value);
            modelPropertyChanged(row, property, value);
            if (root.submitOnChanged) {
                root.submit()
            }
        }

        // Uses black magic to hunt for the delegate instance with the given
        // index.  Returns undefined if there's no currently instantiated
        // delegate with that index.
        function getDelegateInstanceAt(index) {
            for(var i = 0; i < contentItem.children.length; ++i) {
                var item = contentItem.children[i];
                // We have to check for the specific objectName we gave our
                // delegates above, since we also get some items that are not
                // our delegates here.
                if (item.objectName == "InlineEditViewDelegate" && item.index == index)
                    return item;
            }
            return undefined;
        }

        add: Transition {
            SequentialAnimation {
                ParallelAnimation {
                    NumberAnimation { property: "opacity"; from: 0; to: 1.0; duration: 400 }
                    NumberAnimation { properties: "y"; from: 0; duration: 400; easing.type: Easing.OutBounce }
                }
            }
        }
        remove: Transition {
            SequentialAnimation {
                ScriptAction {script: console.log("ListEditor.qml:remove")}
                ParallelAnimation {
                    NumberAnimation { property: "opacity"; to: 0; duration: 400 }
                    NumberAnimation { properties: "y"; to: 0; duration: 400; easing.type: Easing.OutBounce }
                }
            }
        }

    }

    ListView {

        id: buttonView
        height: root.delegateHeight * (itemView.count+1)

        function syncModel() {
            buttonView.model.clear()
            for (var i=0; i<itemView.count; i++) {
                buttonView.model.append({"buttonText":removeButtonText})
            }
            buttonView.model.append({"buttonText":addButtonText})

        }

        anchors.left: itemView.right
        anchors.leftMargin: itemView.spacing
        anchors.top: parent.top
        anchors.topMargin: headerHeight
        width: buttonWidth + itemView.spacing
        model: buttonModel
        spacing: itemView.spacing
        delegate: Button {
            text: buttonText
            width: buttonWidth
            height: buttonHeight
            onClicked: {

                if(index === buttonView.count-1) {
                    itemView.appendRow()
                    return;
                }

                itemView.removeRow(index)
            }
        }
        Component.onCompleted: buttonView.syncModel()
    }

    ListModel {
        id: buttonModel
        ListElement {
            buttonText: '+'
        }
    }

    Component.onCompleted: {
//          modelDefaults = {};
//         console.log()
    }
}