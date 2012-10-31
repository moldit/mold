
import json


decode = json.loads
encode = json.dumps


def fd(name, fdnumber, data):
    """
    XXX
    """
    try:
        return encode((name, fdnumber, {'line': data}))
    except UnicodeDecodeError as e:
        return encode((name, fdnumber, {
            'line': data.encode('base64'),
            'encoding': 'base64',
        }))