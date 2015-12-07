import QtQuick 2.2

Row {

    objectName: "InlineEditViewDelegate"
    spacing: ListView.view.spacing
    height: ListView.view.delegateHeight

    function write(property, value) {
        ListView.view.setModelProperty(index, property, value)
    }

    function bootListView(view) {
        console.log("booting listview");
    }

    Component.onCompleted: {
        "InlineEditViewDelegate.completed"
    }
}