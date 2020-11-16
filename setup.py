from setuptools import setup

setup(
    name="proto-breaking-change-detector",
    version="0.1",
    py_modules=["proto-breaking-change-detector"],
    install_requires=[
        "Click",
        "protobuf >= 3.12.0",
        "google-api-core >= 1.17.0",
        "googleapis-common-protos >= 1.6.0",
    ],
    entry_points="""
        [console_scripts]
        proto-breaking-change-detector=src.cli.detect:detect
    """,
)
