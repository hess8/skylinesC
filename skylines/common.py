def readfile(filepath):
    with open(filepath) as f:
        lines = f.read().splitlines() #strips the lines of \n
    return lines

def readfileNoStrip(filepath):
    with open(filepath) as f:
        lines = f.read().splitlines(True) #keeplinebreaks=True.  Does not strip the lines of \n
    return lines