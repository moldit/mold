from OpenSSL.crypto import sign, verify


def signMessage(message, key):
    """
    Produces a signature using a private key.
    """
    return sign(key, message, "sha1")


def verifySignature(signature, message, cert):
    """
    Returns True if the given cert was used to sign the message.
    """
    try:
        res = verify(cert, signature, message, "sha1")
    except Exception, e:
        res = e
    return None == res