import os
import argparse
import mimetypes

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
            # Check if the file is not empty and is a readable text file
            mime_type, _ = mimetypes.guess_type(path)
            if os.path.getsize(path) > 0 and mime_type and mime_type.startswith('text'):
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

    # Print the tree structure starting from the directory
    print_tree(args.directory, ignore_patterns=ignore_patterns)

if __name__ == "__main__":
    main()

