from setuptools import setup, find_packages

# Read README for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="accessgrid",
    version="0.1.1",
    author="Auston Bunsen",
    author_email="your.email@example.com",
    description="Python SDK for the AccessGrid API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/access-grid/accessgrid-py",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
            "pytest-cov>=4.0.0",
            "black>=22.3.0",
            "isort>=5.10.1",
            "flake8>=4.0.1",
            "mypy>=0.981",
            "build>=0.10.0",
            "twine>=4.0.2",
        ],
    },
)