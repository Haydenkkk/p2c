import os


# run c code
class RunC:
    iFile = ''
    oFile = ''

    def __init__(self):
        self.DefaultConfig()

    def SetIFile(self, iFile):
        RunC.iFile = iFile

    def SetOFile(self, oFile):
        RunC.oFile = oFile

    def DefaultConfig(self):
        RunC.iFile = 'ioFile/test.in'
        RunC.oFile = 'ioFile/test.out'

    def Run(self, cFilePath):
        os.system('gcc {0} -o test'.format(cFilePath))
        os.system('test.exe < {0} > {1}'.format(RunC.iFile, RunC.oFile))

runc = RunC()
runc.Run('testResults/gcd.c')