from setuptools import setup, find_packages

setup(
    name="folder_crawl",
    version="0.1.0",
    author="Julius Olsson",
    author_email="julius.olsson05@gmail.com",
    description="A CLI tool to print directory structure and display contents of text files.",
    long_description="Got tired of copying with LLMs so decided to write a quick tool for it.",
    long_description_content_type="text/markdown",
    url="https://github.com/juliusolsson/folder_crawl",  # Optional, replace with your actual repo URL
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "folder-crawl=folder_crawl.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

