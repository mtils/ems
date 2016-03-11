
.pragma library

function rowOfValue(model, key, value) {
    for (var i=0; i < model.count; i++) {
        if (model.get(i)[key] === value) {
            return i;
        }
    }
}