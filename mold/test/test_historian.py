from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath


from StringIO import StringIO
from mold.historian import RawLogHistorian



class RawLogHistorianTest(TestCase):


    def test_basic(self):
        """
        It should take all the string messages it receives and write them to
        a file as netstrings.
        """
        fh = StringIO()
        
        h = RawLogHistorian(fh)
        h.write('foo')
        h.write('SOMETHING')
        h.write('\x00\x01\xff')
        self.assertEqual(fh.getvalue(),
            "3:foo,"
            "9:SOMETHING,"
            "3:\x00\x01\xff,")
