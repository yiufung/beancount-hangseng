from setuptools import setup, find_packages
import platform
from os import path

with open("README.md", "r") as fh:
    long_description = fh.read()

# Explicitly list the scripts to install.
binaries = [
    ('beancount-hangseng-csv', 'beancount_hangseng.scripts.csv')
]

setup_extra_kwargs = {}
if platform.system() == 'Windows':
    setup_extra_kwargs.update(entry_points={
        'console_scripts': [
            '{} = {}:main'.format(binary, module)
            for binary, module in binaries]
    })
else:
    setup_extra_kwargs.update(scripts=[
        path.join('bin', binary)
        for binary, _ in binaries])

setup(
    name="beancount-hangseng",
    version="0.4.0",
    author="Cheong Yiu Fung",
    author_email="mail@yiufung.net",
    description="Parse Hang Seng eStatements to Beancount/CSV",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yiufung/beancount-hangseng",
    install_requires=['beancount'],
    # pacakges=find_packages(),
    packages=[
        'beancount_hangseng',
        'beancount_hangseng.scripts'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    **setup_extra_kwargs
)
