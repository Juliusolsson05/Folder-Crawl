from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="folder-crawl",
    version="0.2.0",
    author="Julius Olsson",
    author_email="julius.olsson05@gmail.com",
    description="A CLI tool to display folder structure and contents with gitignore-style filtering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juliusolsson/folder-crawl",
    packages=find_packages(),
    install_requires=[
        "pathspec>=0.11.0",
    ],
    entry_points={
        "console_scripts": [
            "folder-crawl=folder_crawl.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires='>=3.7',
    keywords="cli folder tree directory structure gitignore",
)