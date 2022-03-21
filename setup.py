"""This module contains setup instructions for yt_dl."""
import codecs
import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

with open(os.path.join(here, "pytube", "version.py")) as fp:
    exec(fp.read())

setup(name="yt_dl",
    version=__version__,
    author="dmitrymazitov",
    author_email="jay-d@mail.ru",
    packages=["yt_dl"],
    package_data={"": ["LICENSE"],},
    url="https://github.com/dmitrymazitov/yt_dl",
    license="The Unlicense (Unlicense)",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
    description=("Module for downloading the videos from Youtube written in Python 3.10."),
    include_package_data=True,
    long_description_content_type="text/markdown",
    long_description=long_description,
    zip_safe=True,
    python_requires=">=3.10",
    project_urls={
        "Home-Url": "https://github.com/dmitrymazitov/yt_dl"
    },
    keywords=["youtube", "download", "video", "stream",],
)