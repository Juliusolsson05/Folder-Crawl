import os
import argparse
import mimetypes

# List of common file extensions in development environments
COMMON_DEV_EXTENSIONS = {
    # Web development
    '.html', '.htm', '.css', '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte',
    # Server-side languages
    '.py', '.rb', '.php', '.java', '.go', '.rs', '.cs', '.cpp', '.c', '.h',
    # Data and config files
    '.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.env',
    # Markup and documentation
    '.md', '.rst', '.tex', '.txt',
    # Shell and scripts
    '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd',
    # Database
    '.sql', '.sqlite',
    # DevOps and configuration management
    '.tf', '.hcl', '.dockerignore', '.gitignore', 'Dockerfile', 'docker-compose.yml',
    # Build and package management
    'Makefile', '.gradle', 'pom.xml', 'package.json', 'requirements.txt', 'Gemfile',
    # iOS and Android development
    '.swift', '.kt', '.gradle',
    # Other common formats
    '.csv', '.log', '.conf'
}

def get_full_tree(directory, prefix="", ignore_patterns=None):
    """Recursively build the full tree structure of a directory."""
    ignore_patterns = ignore_patterns or []

    # Get list of items in the directory, ignoring hidden files and folders
    items = sorted([item for item in os.listdir(directory) if not item.startswith('.')])

    # Filter items based on ignore patterns
    if ignore_patterns:
        items = [item for item in items if not any(
            pattern in item or item.endswith(pattern) for pattern in ignore_patterns)]

    # Initialize a list to store the tree structure
    tree_lines = []

    # Iterate over items
    for index, item in enumerate(items):
        path = os.path.join(directory, item)
        connector = "└──" if index == len(items) - 1 else "├──"
        tree_lines.append(f"{prefix}{connector} {item}")

        # If it's a directory, recursively build its structure
        if os.path.isdir(path):
            tree_lines.extend(get_full_tree(path, prefix + "    ", ignore_patterns))
    
    return tree_lines

def is_readable_text_file(path):
    """Check if the file is a readable text file, including common dev file types."""
    mime_type, _ = mimetypes.guess_type(path)
    file_extension = os.path.splitext(path)[1].lower()
    file_name = os.path.basename(path)
    
    return (os.path.getsize(path) > 0 and 
            (mime_type and mime_type.startswith('text') or 
             file_extension in COMMON_DEV_EXTENSIONS or
             file_name in COMMON_DEV_EXTENSIONS))

def print_tree(directory, prefix="", ignore_patterns=None):
    """Recursively print the tree structure of a directory and file contents."""
    ignore_patterns = ignore_patterns or []

    # Get list of items in the directory, ignoring hidden files and folders
    items = sorted([item for item in os.listdir(directory) if not item.startswith('.')])

    # Filter items based on ignore patterns
    if ignore_patterns:
        items = [item for item in items if not any(
            pattern in item or item.endswith(pattern) for pattern in ignore_patterns)]

    # Iterate over items
    for index, item in enumerate(items):
        path = os.path.join(directory, item)
        connector = "└──" if index == len(items) - 1 else "├──"

        # Print the item
        print(f"{prefix}{connector} {item}")

        # Check if the item is a directory
        if os.path.isdir(path):
            # Recursively call print_tree with updated prefix
            print_tree(path, prefix + "    ", ignore_patterns)
        else:
            # Check if the file is a readable text file
            if is_readable_text_file(path):
                print(f"And this is what is inside {item}:\n")
                print('"""')
                try:
                    with open(path, 'r', encoding='utf-8') as file:
                        print(file.read())
                except Exception as e:
                    print(f"Unable to read file due to: {e}")
                print('"""')

def main():
    parser = argparse.ArgumentParser(
        description="Print a tree structure of a directory and display contents of text files."
    )
    parser.add_argument(
        "directory", nargs="?", default=".",
        help="Directory to print the tree for. Defaults to current directory."
    )
    parser.add_argument(
        "-I", "--ignore", default="", 
        help="Ignore files or directories matching the given pattern, e.g., '__pycache__|*.pyc'."
    )

    args = parser.parse_args()
    ignore_patterns = args.ignore.split("|") if args.ignore else []

    # Check if the directory exists
    if not os.path.isdir(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist.")
        return

    # Print the full tree structure first
    print("This is the full tree structure:")
    full_tree = get_full_tree(args.directory, ignore_patterns=ignore_patterns)
    for line in full_tree:
        print(line)

    print("\nProceeding to print the tree structure with file contents:\n")

    # Print the tree structure starting from the directory with file contents
    print_tree(args.directory, ignore_patterns=ignore_patterns)

if __name__ == "__main__":
    main()
