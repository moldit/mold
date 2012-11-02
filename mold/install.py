from twisted.python.filepath import FilePath
from twisted.python import util


template_root = FilePath(__file__).parent().child('templates')



class Directory:

    
    template_root = template_root


    def __init__(self, path):
        self.path = FilePath(path)


    def create(self, name):
        """
        Create a directory and update the files in it to reflect those in the
        template directory C{name}.
        """
        src = self.template_root.child(name)
        src.copyTo(self.path)
        
        