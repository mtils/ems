'''
Created on 15.01.2012

@author: michi
'''
def nearest(inputValue, dictionary, returnIndex=False):
    
    inputValue = float(inputValue)
    firstKey = dictionary.keys()[0]
    lowestDifference = abs(float(dictionary[firstKey]) - inputValue)
    nearestIndex = 0
    nearestValue = dictionary[firstKey]
    
    for key in dictionary:
        difference = abs(float(dictionary[key]) - inputValue)
        if difference < lowestDifference:
            lowestDifference = difference
            nearestIndex = key
            nearestValue = dictionary[key]
    
    if not returnIndex:
        return nearestValue
    return nearestIndex

if __name__ == '__main__':
    test = {}
    for i in range(1,19):
        test[float(i)] = (1304000 - 280000) / float((1 << i) * 500)
    print test
    print nearest(0.2499985488745, test, True)
    