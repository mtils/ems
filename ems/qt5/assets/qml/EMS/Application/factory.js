
.pragma library

var config = {
    modules: {},
    urls: { views: "views/", models: "models/" }
};

var qmlApp;

function makeComponent(type, name, parent) {

    var module = config.modules[type];

    if (module !== undefined) {
        var qml = "import " + module + "; " + name + " {}";
        return Qt.createQmlObject(qml, parent);
    }

    var url = config.urls[type];

    if (url === undefined) {
        console.log("Factory is not configured for " + type);
        return null;
    }

    var fileName = url + '/' + name.replace('.','/') + ".qml";

    if (parent === undefined) {
        var component = Qt.createComponent(fileName);
    }
    else {
        var component = Qt.createComponent(fileName, Qt.Synchronous, parent);
    }

    return component

    var object = component.createObject(parent);

    if (object === null) {
        console.log("Could not create " + name + ":\n" + component.errorString());
    }

    return object;
}

function make(type, name, parent) {

    if (qmlApp !== undefined && type == 'models') {
        return qmlApp.make(name + ".model", parent);
    }

    var component = makeComponent(type, name, parent);
    var object = component.createObject(parent);

    if (object === null) {
        console.log("Could not create " + name + ":\n" + component.errorString());
    }

    return object;
}

function viewComponent(name, parent) {
    return makeComponent("views", name, parent);
}

function modelComponent(name, parent) {
    return make("models", name, parent);
}

function view(name, parent) {
    return make("views", name, parent);
}

function model(name, parent) {
    return make("models", name, parent);
}

function float() {
//     for (var i = 0; i < arguments.length; i++) {
//         console.log(arguments[i]);
//     }
    if (qmlApp !== undefined) {
        return qmlApp.getFloat.apply(null, arguments);
    }
}