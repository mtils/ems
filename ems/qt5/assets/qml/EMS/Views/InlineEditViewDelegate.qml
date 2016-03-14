import QtQuick 2.2

Row {

    objectName: "InlineEditViewDelegate"
    spacing: ListView.view.spacing
    height: ListView.view.delegateHeight

    function write(property, value) {
//         console.log("InlineEditViewDelegate.write row:", index, "property:", property, "value:", value)
        ListView.view.setModelProperty(index, property, value)
    }

    function bootListView(view) {
//         console.log("booting listview");
    }

    Component.onCompleted: {
        "InlineEditViewDelegate.completed"
    }
}