def ceilInt(value, digits=1):
    if digits < 1:
        return int(value)
    strVal = str(int(value))
    strLen = len(strVal)
    splitPoint = strLen-digits
    preNumberStr = strVal[0:splitPoint]
    smallestNumber = 10**digits
    if value < smallestNumber:
        return int(smallestNumber)
    if len(preNumberStr):
        preNumber = int(preNumberStr)
        preNumber += 1
    return int(preNumber*(smallestNumber))