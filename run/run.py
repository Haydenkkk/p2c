import os


# run c code
class RunC:
    iFile = '' # input
    oFile = '' # output
    cFile = '' # source code

    def __init__(self):
        self.DefaultConfig()

    def SetIFile(self, iFile):
        RunC.iFile = iFile

    def SetOFile(self, oFile):
        RunC.oFile = oFile

    def SetSourceFile(self, cfile):
        RunC.cFile = cfile

    def DefaultConfig(self):
        RunC.iFile = 'ioFile/test.in'
        RunC.oFile = 'ioFile/test.out'
        RunC.cFile = 'test.c'

    def Run(self):
        os.system('gcc {0} -o test'.format(RunC.cFile))
        os.system('test.exe < {0} > {1}'.format(RunC.iFile, RunC.oFile))

runc = RunC()
# RunC.SetSourceFile()
runc.Run()