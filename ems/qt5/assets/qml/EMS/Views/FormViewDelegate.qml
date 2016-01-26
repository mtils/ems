
import QtQuick 2.2

Item {

    objectName: "InlineEditViewDelegate"

    function write(property, value) {
         parent.setModelProperty(index, property, value);
    }

}