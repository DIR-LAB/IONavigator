from setuptools import setup, find_packages

setup(
    name="ion-extractor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "darshan",
        "pandas",
        "rich",
        "tqdm"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A package for extracting ION data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ION-Extractor",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)