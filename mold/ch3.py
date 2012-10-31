
import json


def fd(name, fdnumber, data):
    try:
        return json.dumps((name, fdnumber, {'line': data}))
    except UnicodeDecodeError as e:
        return json.dumps((name, fdnumber, {
            'line': data.encode('base64'),
            'encoding': 'base64',
        }))