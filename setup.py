from distutils.core import setup
setup(
    name='FixMyPPPoE',
    version='0.1',
    packages=['fixmypppoe'],
    author="Sarfaraz Ahmad",
    author_email='ahmad.sarfaraz1989@gmail.com',
    license='Apache-2.0',
    install_requires=[
        'Click',
        'selenium',
        'requests',
        'PyVirtualDisplay'
    ],
    entry_points='''
        [console_scripts]
        fixmypppoe=fixmypppoe.redialer:main
    '''
)
