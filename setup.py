from setuptools import setup

setup(
    url='https://github.com/iffy/mold',
    author='Matt Haggard',
    author_email='haggardii@gmail.com',
    name='mold',
    version='0.1',
    packages=[
        'mold', 'mold.test',
        'twisted.plugins',
    ],
    package_data={
        'mold': [
            'util_scripts/*',
        ],
    },
    scripts=[
        'bin/mold',
    ],
)


try:
    from twisted.plugin import IPlugin, getPlugins
except ImportError:
    pass
else:
    list(getPlugins(IPlugin))
