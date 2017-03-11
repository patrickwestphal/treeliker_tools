from distutils.core import setup

from pip.commands import install

setup(
    name='treelikerscripts',
    version='0.0.1',
    scripts=['bin/check_modes'],
    packages=[],
    url='',
    license='GPL',
    author='Patrick Westphal',
    author_email='',
    description='',
    install_requires=[
        'pyparsing',
        'networkx'
    ]
)
