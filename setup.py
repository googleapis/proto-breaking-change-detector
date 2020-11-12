from setuptools import setup

setup(
    name='proto-breaking-change-detector',
    version='0.1',
    py_modules=['proto-breaking-change-detector'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        proto-breaking-change-detector=src.cli.detect:detect
    ''',
)