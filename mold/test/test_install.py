from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath


from mold.install import template_root, Directory



class ModuleTest(TestCase):


    def test_template_root(self):
        """
        Should be in mold/templates
        """ 
        me = FilePath(__file__)
        self.assertEqual(template_root, me.parent().parent().child('templates'))



class DirectoryTest(TestCase):


    def test_create(self):
        """
        You can create a directory from a template
        """
        t_root = FilePath(self.mktemp())
        t_root.makedirs()
        
        d1 = t_root.child('dir1')
        d1.makedirs()
        f1 = d1.child('foo')
        f1.setContent('foo content')
        d2 = d1.child('dir2')
        d2.makedirs()
        f2 = d2.child('bar')
        f2.setContent('bar content')

        dst = FilePath(self.mktemp())
        d = Directory(dst.path)
        # fake template root
        d.template_root = t_root
        
        d.create('dir1')
        self.assertTrue(dst.exists())
        self.assertEqual(dst.child('foo').getContent(), 'foo content')
        self.assertTrue(dst.child('dir2').exists())
        self.assertEqual(dst.child('dir2').child('bar').getContent(),
                         'bar content')



