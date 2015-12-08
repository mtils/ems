
import QtQuick 2.2
import QtQuick.Controls 1.4

ComboBox {

    id: root

    property string idRole: 'ID'

    property string currentId: ""

    property bool __isWriting: false

    function findId(modelId) {

        if (!root.model) {
            return -1;
        }

        if (typeof modelId !== 'string') {
            modelId = modelId.toString()
        }

        for (var i=0; i < root.model.count; i++) {
            var rowData = root.model.get(i);
            var rowValue = rowData[idRole];

            if (typeof rowValue !== 'string') {
                rowValue = rowValue.toString();
            }

            if (rowValue === modelId) {
                return i;
            }
        }

        return -1;

    }

    function _setCurrentIdByIndex(idx) {

        if (root.__isWriting) {
            return;
        }

        if (!root.model) {
            return
        }

        if (idx == -1) {
            root.__isWriting = true;
            currentId = '';
            root.__isWriting = false;
            return;
        }

        console.log("onCurrentIndexChanged", idx)

        var rowData = root.model.get(idx);

        root.__isWriting = true;
        root.currentId = rowData[root.idRole].toString();
        root.__isWriting = false;

    }

    onActivated: {
        _setCurrentIdByIndex(index)
        console.log("inner.activated", currentIndex, index, currentId)
    }

    onCurrentIndexChanged: _setCurrentIdByIndex(root.currentIndex)

    onCurrentIdChanged: {
        console.log("currentId changed to", root.currentId)
        if (root.__isWriting) {
            return;
        }
        var idIndex = root.findId(root.currentId);
        if (idIndex !== root.currentIndex) {
            root.currentIndex = idIndex;
        }
    }

    onModelChanged: {

        if (!root.currentId) {
            return;
        }

        var idIndex = root.findId(root.currentId);
        root.__isWriting = true;
        root.currentIndex = idIndex;
        root.__isWriting = false;
    }
}