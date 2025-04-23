from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="ion",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
    description="ION is a tool for analyzing Darshan logs.",
    python_requires='>=3.10',
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ]
)