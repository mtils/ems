
import QtQuick 2.2
import QtQuick.Controls 1.4

ComboBox {

    id: root

    property string idRole: 'ID'

    property string currentId: ''

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

    onCurrentIndexChanged: {

        if (!root.model) {
            return
        }

        if (root.currentIndex == -1) {
            currentId = '';
            return;
        }

        var rowData = root.model.get(root.currentIndex);

        root.currentId = rowData[root.idRole].toString();

    }

    onCurrentIdChanged: {
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

        root.currentIndex = idIndex;
    }
}