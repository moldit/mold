from distutils.core import setup

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
