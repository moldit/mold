from distutils.core import setup

# find template
import os
template_files = []
for root, dirs, files in os.walk('mold/templates'):
    template_files.extend((os.path.join(root, x)[len('mold/'):] for x in files))


setup(
    url='https://github.com/iffy/mold',
    author='Matt Haggard',
    author_email='haggardii@gmail.com',
    name='mold',
    version='0.1',
    packages=[
        'mold', 'mold.test',
        'mold.resources',
        'mold.script', 'mold.script.test',
        'twisted.plugins',
    ],
    package_data={
        'mold': template_files,
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
