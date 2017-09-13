from setuptools import setup, find_packages


def readme():
    with open("README.md", 'r') as f:
        return f.read()


setup(
    name="solenc",
    description="An implementation of Bruce Schneier's Solitaire encryption algorithm.",
    version="1.0.1",
    long_description=readme(),
    author="Brian Balsamo",
    author_email="brian@brianbalsamo.com",
    packages=find_packages(
        exclude=[
        ]
    ),
    include_package_data=True,
    url='https://github.com/bnbalsamo/solenc',
    install_requires=[
    ],
    tests_require=[
        'pytest'
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'solenc = solenc:main'
        ]
    }
)
