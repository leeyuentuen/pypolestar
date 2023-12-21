from setuptools import setup, find_packages
import pypolestar

long_description = open("README.md").read()

setup(
    name="pypolestar",
    version=pypolestar.__version__,
    author="Tuen Lee",
    author_email="leeyuentuen@gmail.com",
    description="Python library to connect to Polestar",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leeyuentuen/pypolestar",
    packages=["pypolestar"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=[
        # Add your dependencies here
        "aiohttp"
    ],
)





