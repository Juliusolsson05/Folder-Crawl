```markdown
# Folder Crawl

**Folder Crawl** is a command-line tool designed to print the structure of a directory and display the contents of text files. Tired of manually navigating and copying with Large Language Models (LLMs)? This tool simplifies the process by giving you a quick overview of your file system with the ability to ignore specific files or folders.

## Features

- Recursively prints the directory structure, similar to the `tree` command.
- Displays the contents of non-empty text files, encapsulated within triple quotes.
- Allows ignoring specific files or folders using patterns.

## Installation

You can install Folder Crawl using `pip`. First, clone the repository and navigate to the project directory:

```bash
git clone https://github.com/juliusolsson/folder_crawl.git
cd folder_crawl
```

Then install the package locally:

```bash
pip install .
```

This will make the `folder-crawl` command available globally on your system.

## Usage

The basic usage of Folder Crawl is simple. Run the following command:

```bash
folder-crawl [OPTIONS] [DIRECTORY]
```

### Arguments

- **DIRECTORY**: The directory to print the tree structure for. Defaults to the current directory if not specified.

### Options

- `-I`, `--ignore`: Specify patterns to ignore files or directories. For example: `__pycache__|*.pyc`.

### Examples

1. **Print the tree structure of the current directory:**

   ```bash
   folder-crawl
   ```

2. **Print the tree structure of a specific directory:**

   ```bash
   folder-crawl /path/to/directory
   ```

3. **Ignore specific files or folders:**

   ```bash
   folder-crawl -I "__pycache__|*.pyc" /path/to/directory
   ```

   This command will ignore files and folders matching the specified patterns.

## Why Folder Crawl?

While working with Large Language Models and development projects, constantly navigating directories and copying file contents can be cumbersome. Folder Crawl offers a quick and efficient way to explore directories and view file contents without leaving your terminal.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

**Julius Olsson**  
Email: [julius.olsson05@gmail.com](mailto:julius.olsson05@gmail.com)

Got tired of copying with LLMs, so I decided to write a quick tool for it!
