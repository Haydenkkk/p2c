import os


# run c code
class RunC:
    iFile = '' # input
    oFile = '' # output
    cFile = '' # source code

    def __init__(self):
        self.DefaultConfig()

    def SetIFilePath(self, iFile):
        RunC.iFile = iFile

    def SetOFilePath(self, oFile):
        RunC.oFile = oFile

    def SetSourceFilePath(self, cfile):
        RunC.cFile = cfile

    def SetInput(self, input):
        file = open(RunC.iFile, mode='w+')
        file.writelines(input)
        file.close()

    def SetSource(self, sourceCode):
        file = open(RunC.cFile, mode='w+')
        file.writelines(sourceCode)
        file.close()

    def GetOutput(self):
        file = open(RunC.oFile, mode='r')
        ret = '\n'.join(file.readlines())
        return ret

    def DefaultConfig(self):
        RunC.iFile = 'ioFile/test.in'
        RunC.oFile = 'ioFile/test.out'
        RunC.cFile = 'test.c'

    def Run(self):
        os.system('gcc {0} -o test'.format(RunC.cFile))
        os.system('test.exe < {0} > {1}'.format(RunC.iFile, RunC.oFile))    

runc = RunC()
# RunC.SetSourceFile()
runc.SetInput('82 40')
runc.Run()
print(runc.GetOutput())