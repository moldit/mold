from OpenSSL.crypto import sign, verify


def signMessage(message, key):
    """
    Produces a signature using a private key.
    
    @param message: string of data to sign

    @param key: instance of OpenSSL.crypto.PKey

    """
    return sign(key, message, "sha1")


def verifySignature(signature, message, cert):
    """
    Returns True if the given cert was used to sign the message.
    @param signature: string of signature data

    @param message: string of message data

    @param cert: instance of OpenSSL.crypto.X509
    """
    try:
        res = verify(cert, signature, message, "sha1")
    except Exception, e:
        res = e
    return None == res