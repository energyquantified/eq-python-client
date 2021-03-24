import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))


# Requirements
install_requires = [
    "requests==2.25.1",
    "pytz",
    "tzlocal",
    "python-dateutil==2.8.1",
]
# tests_require = [
#     "pytest",
#     "requests-mock",
# ]

# Get package info
about = {}
package_info_filename = os.path.join(here, "energyquantified", "__version__.py")
with open(package_info_filename, "r", encoding="utf-8") as f:
    exec(f.read(), about)

# Get the README.md file (long description)
with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as f:
    readme = f.read()

# Classifiers
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Financial and Insurance Industry",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Topic :: Office/Business :: Financial",
    "Topic :: Software Development :: Libraries :: Python Modules",
]


setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    url=about["__url__"],
    packages=find_packages(include=["energyquantified", "energyquantified.*"]),
    package_data={
        '': ["LICENSE"],
    },
    python_requires=">=3.7",
    install_requires=install_requires,
    # tests_require=tests_require,
    project_urls={
        "Documentation": "https://energyquantified-python.readthedocs.io",
        "Source": "https://github.com/energyquantified/eq-python-client",
    },
    classifiers=classifiers
)
