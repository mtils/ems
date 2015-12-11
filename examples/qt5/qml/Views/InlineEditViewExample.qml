
import QtQuick 2.2
import QtQuick.Controls 1.4

import EMS.Views 1.0
import EMS.Inputs 1.0

Item {
    id: root
    width: 800
    height: 600

    InlineEditView {

        id: editor
        delegate: itemDelegate
        width: root.width
        model: productItemsModel
        submitOnChanged: true

        modelDefaults: {
            "product_id": 1,
            "note": "",
            "quantity": 1,
            "price": 0.0
        }

        Label {
            text: "Product"
            width: 200
        }
        Label {
            text: "Quantity"
            width: 50
        }
        Label {
            text: "Description"
            width: 200
        }
        Label {
            text: "Amount"
            width: 120
        }

        onAppended: {
            console.log("appended")
        }

        onModelPropertyChanged: {
            console.log("modelPropertyChanged(" + row + "," + property + "," + value + ")")
        }

        onRemoved: {
            console.log("removed", row)
        }

        onSubmitted: {
            console.log("submitted")
        }

    }

    Component {
        id: itemDelegate
        InlineEditViewDelegate {
            ModelComboBox {
                width: 200
                model: productsModel
                textRole: "name"
                bindId: product_id
                onCurrentIdChanged: write("product_id", parseInt(currentId))
            }
            SpinBox {
                width: 50
                value: quantity
                horizontalAlignment: Qt.AlignRight
                onEditingFinished: write("quantity", value)
            }
            TextField {
                width: 200
                text: note
                onEditingFinished: write("note", text)
            }
            SpinBox {
                width: 120
                value: price
                decimals: 2
                suffix: " $"
                horizontalAlignment: Qt.AlignRight
                onEditingFinished: write("price", value)
            }
        }
    }

    ListModel {
        id: productItemsModel
        ListElement {
            product_id: 1
            note: 'Basic Cleaning'
            quantity: 1
            price: 75.99
        }
        ListElement {
            product_id: 3
            note: 'Polish'
            quantity: 1
            price: 25.99
        }
    }

    ListModel {
        id: productsModel
        ListElement {
            ID: 1
            name: 'Basic Cleaning'
            price: 75.99
        }
        ListElement {
            ID: 2
            name: 'Polish'
            price: 25.99
        }
        ListElement {
            ID: 3
            name: 'Remove Garbage'
            price: 35.78
        }
    }
}