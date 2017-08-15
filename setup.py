from setuptools import setup


def readme():
    with open("README.md", 'r') as f:
        return f.read()

setup(
    name="solenc",
    description="A python implementation of Bruce Schneier's " +
    "solitaire encryption algorithm",
    long_description = readme(),
    py_modules = ["solitaire"],
    entry_points = {
        'console_scripts': [
            'solenc = solenc:main'
        ]
    }
)
