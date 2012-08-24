from twisted.python.filepath import FilePath
from twisted.python import util


template_root = FilePath(__file__).parent().child('templates')



class Directory:


    def __init__(self, path):
        self.path = FilePath(path)


    def install(self):        
        template_root.child('bin').copyTo(self.path)

        
        