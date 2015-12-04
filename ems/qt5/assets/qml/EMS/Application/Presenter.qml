import QtQuick 2.2

FocusScope {

    id: root

    property Item view
    property QtObject model

    property var modelToViewBindings: []
    property var viewToModelBindings: []

    Component.onCompleted: {
        root.view.anchors.fill = root;
        root.view.focus = true;

        for ( i in root.modelToViewBindings ) {
            name = root.modelToViewBindings[ i ];
            dynamicBinding.createObject( root, {
                target: root.view, property: name, source: root.model, sourceProperty: name
            } );
        }

        for ( var i in root.viewToModelBindings ) {
            var name = root.viewToModelBindings[ i ];
            dynamicBinding.createObject( root, {
                target: root.model, property: name, source: root.view, sourceProperty: name
            } );
        }
    }

    Component {
        id: dynamicBinding

        Binding {
            id: binding

            property var source
            property string sourceProperty

            value: binding.source[ binding.sourceProperty ]
        }
    }
}