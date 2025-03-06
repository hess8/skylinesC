def readfile(filepath):
    with open(filepath) as f:
        lines = f.read().splitlines() #strips the lines of \n
    return lines

def readfileNoStrip(filepath):
    with open(filepath) as f:
        lines = f.read().splitlines(True) #keeplinebreaks=True.  Does not strip the lines of \n
    return lines

def writefile(lines,filepath): #need to have \n's inserted already
    file1 = open(filepath,'w')
    file1.writelines(lines)
    file1.close()
    return

