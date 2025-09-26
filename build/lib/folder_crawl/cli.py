#!/usr/bin/env python3
"""
folder-crawl: A CLI tool to display folder structure and contents with gitignore-style patterns.
"""

import os
import sys
import argparse
import mimetypes
from pathlib import Path
from typing import List, Optional, Set, Tuple

try:
    import pathspec
except ImportError:
    print("Error: pathspec is required. Install with: pip install pathspec", file=sys.stderr)
    sys.exit(1)

DEFAULT_IGNORE_PATTERNS = [
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".Python",
    "*.so",
    "*.dll",
    "*.dylib",
    ".git/",
    ".svn/",
    ".hg/",
    ".bzr/",
    ".idea/",
    ".vscode/",
    "*.swp",
    "*.swo",
    "*.swn",
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    "node_modules/",
    "venv/",
    "env/",
    ".venv/",
    ".env/",
    "*.egg-info/",
    "dist/",
    "build/",
    "*.log",
]

MAX_FILE_SIZE = 1_000_000  # 1MB default max file size
DEFAULT_MAX_BYTES = 50_000  # 50KB default max output per file


def is_text_file(file_path: Path) -> bool:
    """
    Determine if a file is likely text based on MIME type and content sampling.
    """
    if not file_path.is_file():
        return False

    # Check MIME type first
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type:
        if mime_type.startswith('text/'):
            return True
        if mime_type.startswith('application/'):
            # Common text-based application types
            text_app_types = [
                'application/json',
                'application/xml',
                'application/javascript',
                'application/typescript',
                'application/x-sh',
                'application/x-yaml',
                'application/toml',
            ]
            if mime_type in text_app_types:
                return True

    # Check by extension for common text files
    text_extensions = {
        '.txt', '.md', '.rst', '.log', '.csv', '.tsv',
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
        '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.r', '.m',
        '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
        '.html', '.htm', '.xml', '.css', '.scss', '.sass', '.less',
        '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.config',
        '.env', '.gitignore', '.dockerignore', '.editorconfig',
        '.sql', '.graphql', '.proto',
        'Dockerfile', 'Makefile', 'Rakefile', 'Gemfile', 'Pipfile',
        '.vue', '.svelte', '.astro',
    }

    if file_path.suffix.lower() in text_extensions:
        return True

    if file_path.name in ['Dockerfile', 'Makefile', 'Rakefile', 'Gemfile', 'Pipfile', 'LICENSE', 'README']:
        return True

    # Sample file content as last resort
    try:
        with open(file_path, 'rb') as f:
            sample = f.read(8192)  # Read first 8KB

        # Check for null bytes (binary indicator)
        if b'\x00' in sample:
            return False

        # Try to decode as UTF-8
        try:
            sample.decode('utf-8')
            return True
        except UnicodeDecodeError:
            pass

    except (OSError, IOError):
        pass

    return False


def load_ignore_patterns(
    ignore_patterns: List[str],
    ignore_files: List[Path],
    use_gitignore: bool,
    use_default_ignore: bool,
    root_path: Path
) -> pathspec.PathSpec:
    """
    Load and combine ignore patterns from various sources.
    """
    all_patterns = []

    # Add default patterns
    if use_default_ignore:
        # Check for .foldercrawlignore in root
        foldercrawl_ignore = root_path / '.foldercrawlignore'
        if foldercrawl_ignore.exists():
            try:
                with open(foldercrawl_ignore, 'r', encoding='utf-8') as f:
                    patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    all_patterns.extend(patterns)
            except (OSError, UnicodeDecodeError):
                pass

    # Add .gitignore patterns (only if explicitly requested)
    if use_gitignore:
        gitignore_path = root_path / '.gitignore'
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    all_patterns.extend(patterns)
            except (OSError, UnicodeDecodeError):
                pass

    # Add patterns from specified ignore files
    for ignore_file in ignore_files:
        if ignore_file.exists():
            try:
                with open(ignore_file, 'r', encoding='utf-8') as f:
                    patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    all_patterns.extend(patterns)
            except (OSError, UnicodeDecodeError):
                print(f"Warning: Could not read ignore file: {ignore_file}", file=sys.stderr)

    # Add command-line patterns
    for pattern in ignore_patterns:
        # Handle pipe-separated patterns
        if '|' in pattern:
            all_patterns.extend(p.strip() for p in pattern.split('|') if p.strip())
        else:
            all_patterns.append(pattern)

    # Add default ignore patterns if using defaults
    if use_default_ignore:
        all_patterns.extend(DEFAULT_IGNORE_PATTERNS)

    # Create PathSpec from all patterns
    if all_patterns:
        return pathspec.PathSpec.from_lines('gitwildmatch', all_patterns)
    else:
        return pathspec.PathSpec.from_lines('gitwildmatch', [])


def should_ignore(path: Path, root: Path, spec: pathspec.PathSpec, include_hidden: bool) -> bool:
    """
    Check if a path should be ignored based on patterns and settings.
    """
    # Get relative path for pattern matching
    try:
        rel_path = path.relative_to(root)
    except ValueError:
        return True

    # Check hidden files
    if not include_hidden:
        for part in rel_path.parts:
            if part.startswith('.') and part not in ['.', '..']:
                return True

    # Check against pathspec
    if spec.match_file(str(rel_path)):
        return True

    # For directories, also check with trailing slash
    if path.is_dir():
        if spec.match_file(str(rel_path) + '/'):
            return True

    return False


def format_size(size: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}TB"


def get_tree_structure(
    root: Path,
    spec: pathspec.PathSpec,
    include_hidden: bool,
    prefix: str = "",
    is_last: bool = True,
    current_depth: int = 0,
    max_depth: Optional[int] = None
) -> List[str]:
    """
    Generate tree structure lines for a directory.
    """
    if max_depth is not None and current_depth >= max_depth:
        return []

    lines = []

    try:
        items = sorted(root.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        return [f"{prefix}[Permission Denied]"]

    # Filter items
    items = [item for item in items if not should_ignore(item, root, spec, include_hidden)]

    for i, item in enumerate(items):
        is_last_item = (i == len(items) - 1)

        # Tree characters
        if current_depth == 0:
            connector = ""
            extension = ""
        else:
            connector = "└── " if is_last_item else "├── "
            extension = "    " if is_last_item else "│   "

        # Add current item
        if item.is_dir():
            lines.append(f"{prefix}{connector}{item.name}/")
            # Recursively add subdirectory contents
            sub_lines = get_tree_structure(
                item, spec, include_hidden,
                prefix + extension,
                is_last_item,
                current_depth + 1,
                max_depth
            )
            lines.extend(sub_lines)
        else:
            try:
                size = item.stat().st_size
                size_str = f" ({format_size(size)})"
            except OSError:
                size_str = ""
            lines.append(f"{prefix}{connector}{item.name}{size_str}")

    return lines


def process_directory(
    root: Path,
    spec: pathspec.PathSpec,
    include_hidden: bool,
    show_contents: bool,
    max_bytes: int,
    max_file_size: int,
    max_depth: Optional[int] = None
) -> None:
    """
    Process and display a directory's structure and contents.
    """
    print(f"\n📁 {root.absolute()}")
    print("=" * 60)

    # Print tree structure
    print("\n## Structure:\n")
    tree_lines = get_tree_structure(root, spec, include_hidden, max_depth=max_depth)
    if tree_lines:
        for line in tree_lines:
            print(line)
    else:
        print("[Empty or all files ignored]")

    # Print file contents if requested
    if show_contents:
        print("\n## File Contents:\n")
        process_contents(root, spec, include_hidden, max_bytes, max_file_size)


def process_contents(
    root: Path,
    spec: pathspec.PathSpec,
    include_hidden: bool,
    max_bytes: int,
    max_file_size: int,
    current_path: Optional[Path] = None
) -> None:
    """
    Recursively process and display file contents.
    """
    if current_path is None:
        current_path = root

    try:
        items = sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        return

    for item in items:
        if should_ignore(item, root, spec, include_hidden):
            continue

        if item.is_dir():
            process_contents(root, spec, include_hidden, max_bytes, max_file_size, item)
        elif item.is_file():
            # Check if file is text and within size limits
            try:
                size = item.stat().st_size
                if size > max_file_size:
                    continue

                if is_text_file(item):
                    print(f"\n### {item.relative_to(root)}")
                    print("```")

                    try:
                        with open(item, 'r', encoding='utf-8', errors='replace') as f:
                            content = f.read(max_bytes)
                            print(content)
                            if size > max_bytes:
                                print(f"\n[... truncated {format_size(size - max_bytes)} ...]")
                    except (OSError, UnicodeDecodeError) as e:
                        print(f"[Error reading file: {e}]")

                    print("```")
            except OSError:
                pass


def main():
    parser = argparse.ArgumentParser(
        description='Display folder structure and contents with gitignore-style filtering',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  folder-crawl .                           # Current directory with default ignores
  folder-crawl /path/to/project            # Specific directory
  folder-crawl . -I "*.log|*.tmp|cache/"   # Ignore patterns (pipe or multiple -I)
  folder-crawl . --ignore-file .myignore   # Use custom ignore file
  folder-crawl . --gitignore               # Also use .gitignore patterns
  folder-crawl . --hidden                  # Include hidden files
  folder-crawl . --no-contents             # Structure only, no file contents
  folder-crawl . --max-bytes 10000         # Limit content output per file
  folder-crawl . --max-depth 2             # Limit tree depth
        """
    )

    parser.add_argument(
        'path',
        type=str,
        nargs='?',
        default='.',
        help='Directory path to crawl (default: current directory)'
    )

    parser.add_argument(
        '-I', '--ignore',
        action='append',
        default=[],
        dest='ignore_patterns',
        help='Gitignore-style patterns (can use | separator or repeat flag)'
    )

    parser.add_argument(
        '--ignore-file',
        action='append',
        default=[],
        type=Path,
        dest='ignore_files',
        help='Path to ignore file with patterns (can be repeated)'
    )

    parser.add_argument(
        '--gitignore',
        action='store_true',
        dest='use_gitignore',
        help="Also read .gitignore patterns (opt-in)"
    )

    parser.add_argument(
        '--no-default-ignore',
        action='store_false',
        dest='use_default_ignore',
        help="Don't use default ignore patterns and .foldercrawlignore"
    )

    parser.add_argument(
        '--hidden',
        action='store_true',
        help='Include hidden files and directories'
    )

    parser.add_argument(
        '--no-contents',
        action='store_false',
        dest='show_contents',
        help='Only show structure, not file contents'
    )

    parser.add_argument(
        '--max-bytes',
        type=int,
        default=DEFAULT_MAX_BYTES,
        help=f'Maximum bytes to display per file (default: {DEFAULT_MAX_BYTES})'
    )

    parser.add_argument(
        '--max-file-size',
        type=int,
        default=MAX_FILE_SIZE,
        help=f'Maximum file size to process (default: {MAX_FILE_SIZE})'
    )

    parser.add_argument(
        '--max-depth',
        type=int,
        default=None,
        help='Maximum directory depth to traverse'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 0.2.0'
    )

    args = parser.parse_args()

    # Resolve the root path
    root_path = Path(args.path).resolve()

    if not root_path.exists():
        print(f"Error: Path does not exist: {root_path}", file=sys.stderr)
        sys.exit(1)

    if not root_path.is_dir():
        print(f"Error: Path is not a directory: {root_path}", file=sys.stderr)
        sys.exit(1)

    # Load ignore patterns
    spec = load_ignore_patterns(
        args.ignore_patterns,
        args.ignore_files,
        args.use_gitignore,
        args.use_default_ignore,
        root_path
    )

    # Process the directory
    try:
        process_directory(
            root_path,
            spec,
            args.hidden,
            args.show_contents,
            args.max_bytes,
            args.max_file_size,
            args.max_depth
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()