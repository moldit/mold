from twisted.trial.unittest import TestCase

from mold.signverify import (signMessage, verifySignature)
from OpenSSL import crypto
from OpenSSL.crypto import sign, verify


def create_self_signed_cert():
    """
    thanks to 
        http://skippylovesmalorie.wordpress.com/2010/02/12/how-to-generate-a-self-signed-certificate-using-pyopenssl/
    """
          
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)

    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "US"
    cert.get_subject().ST = "Georgia"
    cert.get_subject().L = "Rome"
    cert.get_subject().O = "my company"
    cert.get_subject().OU = "my organization"
    cert.get_subject().CN = "cname"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    return k, cert


class SignVerifyTest(TestCase):
    

    def setUp(self):
        self.pkey, self.cert = create_self_signed_cert()
  

    def test_sign(self):
        """
        calls sign and returns what it ought.
        """
        pkey = self.pkey
        a = sign(pkey, "message", "sha1")
        r = signMessage("message", pkey)
        self.assertEquals(type(a), type(r))
        self.assertEquals(a, r)


    def test_verify(self):
        """
        calls verify and returns the rigth thing.
        """
        pkey, cert = self.pkey, self.cert
        data = "message"
        signature = sign(pkey, data, "sha1")
        self.assertEquals(verify(cert, signature, data, "sha1"), None)
        self.assertEquals(verifySignature(signature, data, cert), True)


    def test_verify_badcert(self):
        """
        if the cert doesn't belong with the signature
        verify returns False
        """
        cert = self.cert
        _, cert2 = create_self_signed_cert()
        data = "data"
        signature = sign(self.pkey, data, "sha1")
        self.assertFalse(verifySignature(signature, data, cert2))
