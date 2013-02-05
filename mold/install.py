from twisted.python.filepath import FilePath
from twisted.python import util


template_root = FilePath(__file__).parent().child('templates')



class Directory(FilePath):

    
    template_root = template_root


    def create(self, name):
        """
        Create a directory and update the files in it to reflect those in the
        template directory C{name}.
        """
        src = self.template_root.child(name)
        src.copyTo(self)


    def makeExecutable(self):
        for f in self.walk():
            f.chmod(0755)
        
        