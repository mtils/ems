
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

function parseResourceUri(uri) {

    var linkParts = uri.split('/');

    if(linkParts.length == 3) {
        return {
            'resource': linkParts[0],
            'resourceId': linkParts[1],
            'action': linkParts[2]
        }
    }

    if(linkParts.length == 2) {
        return {
            'resource': linkParts[0],
            'resourceId': 0,
            'action': linkParts[1]
        }
    }

    if(linkParts.length == 1) {
        return {
            'resource': linkParts[0],
            'resourceId': 0,
            'action': 'index'
        }
    }
}

function toResourceRoute(parsed) {
    return parsed['resource'] + '.' + parsed['action'];
}

function dispatch(link, parent) {
    var parsed = parseResourceUri(link);
    return viewComponent(toResourceRoute(parsed));
}

function view(name, parent) {
    return make("views", name, parent);
}

function model(name, parent) {
    return make("models", name, parent);
}

function pyFloat() {
    if (qmlApp !== undefined) {
        return qmlApp.getFloat.apply(null, arguments);
    }
}

function pyInt() {
    if (qmlApp !== undefined) {
        return qmlApp.getInt.apply(null, arguments);
    }
}

function pyString() {
    if (qmlApp !== undefined) {
        return qmlApp.getString.apply(null, arguments);
    }
}

function pyBool() {
    if (qmlApp !== undefined) {
        return qmlApp.getBool.apply(null, arguments);
    }
}

function pyDict() {
    if (qmlApp !== undefined) {
        return qmlApp.getDict.apply(null, arguments);
    }
}

function pyList() {
    if (qmlApp !== undefined) {
        return qmlApp.getList.apply(null, arguments);
    }
}

function pyObject() {
    if (qmlApp !== undefined) {
        return qmlApp.getNativeObject.apply(null, arguments);
    }
}

function qtObject(binding) {
    if (qmlApp !== undefined) {
        return qmlApp.make(binding);
    }
}