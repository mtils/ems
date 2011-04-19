import os.path

def absPathOf(basePath, *relPaths):
    pathDict = [os.path.dirname(basePath)]
    for path in relPaths:
        pathDict.append(path)
    return os.path.abspath(os.path.sep.join(pathDict))