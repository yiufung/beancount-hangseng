import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="beancount-hangseng",
    version="0.0.6",
    author="Cheong Yiu Fung",
    author_email="mail@yiufung.net",
    description="Imports Hang Seng Integrated Account eStatements to beancount",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yiufung/beancount-hangseng",
    install_requires=['beancount'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)