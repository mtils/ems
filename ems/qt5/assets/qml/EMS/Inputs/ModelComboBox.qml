
import QtQuick 2.2
import QtQuick.Controls 1.4

ComboBox {

    id: root

    property string idRole: 'ID'

    property var currentId: ""

    property var bindId: "";

    property bool __isSelfWriting: false

    function findId(modelId) {

        if (!root.model) {
            return -1;
        }

        for (var i=0; i < root.model.count; i++) {

            var rowData = root.model.get(i);

            if (rowData[idRole] === modelId) {
                return i
            }

        }

        return -1;

    }

    function _setCurrentIdByIndex(idx) {
        if (root.__isSelfWriting) {
            return;
        }

        if (!root.model || typeof root.model.get !== 'function') {
            return;
        }

        if (idx === -1) {
            root.__isSelfWriting = true;
            root.currentId = '';
            root.__isSelfWriting = false;
            return;
        }


        var rowData = root.model.get(idx);

        root.__isSelfWriting = true;
        root.currentId = rowData[root.idRole];
        root.__isSelfWriting = false;

    }

    onActivated: {
        _setCurrentIdByIndex(index)
    }

    onCurrentIndexChanged: {
        _setCurrentIdByIndex(root.currentIndex)
    }

    onCurrentIdChanged: {
        if (!root.__isSelfWriting) {
            throw "Only write to bindId, otherwise the binding gets lost";
        }
        return;
    }

    onBindIdChanged: {
        var idIndex = root.findId(root.bindId);

        if (idIndex !== root.currentIndex) {
            root.__isSelfWriting = true;
            root.currentIndex = idIndex;
            root.currentId = root.bindId;
            root.__isSelfWriting = false;
        }
    }

    onModelChanged: {
        if (!root.currentId) {
            return;
        }

        var idIndex = root.findId(root.currentId);
        root.__isSelfWriting = true;
        root.currentIndex = idIndex;
        root.__isSelfWriting = false;
    }
}