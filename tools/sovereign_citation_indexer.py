"""
Sovereign Citation Indexer
==========================

A specialized tool for indexing and cataloging resources across strict directory structures.
Generates a clean, readable Markdown index of tools, documents, and code files.

Usage:
    python tools/sovereign_citation_indexer.py --config citation_config.yaml

Dependencies:
    pip install pyyaml
"""

import os
import yaml
import argparse
import fnmatch
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class CitationIndexer:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.root_dir = Path(self.config.get('root_dir', '.')).resolve()
        self.output_file = Path(self.config.get('output_file', 'CITATION_INDEX.md'))
        self.include_extensions = set(self.config.get('include_extensions', ['.md', '.py']))
        self.ignore_dirs = self.config.get('ignore_dirs', [])
        self.ignore_files = self.config.get('ignore_files', [])
        self.index_data = {}

        # Initialize logger
        self.logger = logging.getLogger('CitationIndexer')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def _is_ignored(self, path: Path) -> bool:
        """Check if a path should be ignored based on config."""
        # Check directories
        for part in path.parts:
            for ignore_pattern in self.ignore_dirs:
                if fnmatch.fnmatch(part, ignore_pattern):
                    return True
        
        # Check filename
        for ignore_pattern in self.ignore_files:
            if fnmatch.fnmatch(path.name, ignore_pattern):
                return True
                
        return False

    def _extract_metadata(self, file_path: Path) -> Dict[str, str]:
        """Extract title and description from file content."""
        metadata = {
            'title': file_path.stem.replace('_', ' '),
            'description': 'No description available.',
            'path': str(file_path.relative_to(self.root_dir)).replace('\\', '/'),
            'type': file_path.suffix.lower(),
            'date': 'Unknown'
        }

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()

            # Python: Look for docstrings
            if file_path.suffix == '.py':
                import ast
                try:
                    tree = ast.parse(content)
                    docstring = ast.get_docstring(tree)
                    if docstring:
                        # Use first line as title implication, rest as description
                        doc_lines = docstring.strip().split('\n')
                        if doc_lines:
                            metadata['description'] = doc_lines[0]
                            if len(doc_lines) > 1:
                                metadata['description'] += f" ... ({len(doc_lines)} lines)"
                except:
                    pass

            # Markdown: Look for H1 and text
            elif file_path.suffix == '.md':
                # Try to extract title from first H1
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                if title_match:
                    metadata["title"] = title_match.group(1).strip()
                
                # Crude date extraction (YYYY-MM-DD or Month YYYY)
                date_pattern = r'(20\d{2}-\d{2}-\d{2}|[A-Z][a-z]+ 20\d{2})'
                date_match = re.search(date_pattern, content)
                if date_match:
                    metadata["date"] = date_match.group(1)

                # Try to find first non-header, non-date text line for description
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line and not stripped_line.startswith('#') and not stripped_line.startswith('```') and not stripped_line.startswith('<!--'):
                        # Check if this line is just the date we already extracted
                        if re.search(date_pattern, stripped_line) and len(stripped_line) < 30:
                            continue

                        metadata['description'] = stripped_line[:200]
                        if len(stripped_line) > 200:
                            metadata['description'] += "..."
                        break
        except Exception as e:
            self.logger.warning(f"Failed to extract metadata from {file_path.name}: {e}")

        return metadata

    def scan(self):
        """Walk the directory tree and index files."""
        print(f"Starting scan of {self.root_dir}...")
        count = 0
        
        for root, dirs, files in os.walk(self.root_dir):
            root_path = Path(root)
            
            # Modify dirs in-place to skip ignored directories
            dirs[:] = [d for d in dirs if not self._is_ignored(root_path / d)]
            
            if self._is_ignored(root_path):
                continue

            for file in files:
                file_path = root_path / file
                
                if self._is_ignored(file_path):
                    continue
                
                if file_path.suffix.lower() in self.include_extensions:
                    relative_dir = str(root_path.relative_to(self.root_dir)).replace('\\', '/')
                    if relative_dir == '.':
                        relative_dir = 'Root'
                    
                    if relative_dir not in self.index_data:
                        self.index_data[relative_dir] = []
                    
                    self.index_data[relative_dir].append(self._extract_metadata(file_path))
                    count += 1
                    print(f"Indexed: {file_path.name}")

        print(f"Scan complete. Found {count} files.")

    def generate_markdown(self):
        """Generate the Markdown index file."""
        print(f"Generating {self.output_file}...")
        
        lines = [
            f"# Sovereign Citation Index",
            f"",
            f"> Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"**Root Directory:** `{self.root_dir}`",
            f"**Total Files Indexed:** {sum(len(items) for items in self.index_data.values())}",
            f"",
            f"---",
            f""
        ]

        # Sort directories
        for category in sorted(self.index_data.keys()):
            lines.append(f"## 📂 {category}")
            lines.append(f"")
            lines.append(f"| File | Type | Date | Description |")
            lines.append(f"|------|------|------|-------------|")
            
            # Sort files within category
            for item in sorted(self.index_data[category], key=lambda x: x['title']):
                # Create relative link
                link = f"[{item['title']}]({item['path']})"
                date = item.get('date', 'Unknown')
                desc = item['description'].replace('|', '\|') # Escape pipes for table
                lines.append(f"| {link} | `{item['type']}` | {date} | {desc} |")
            
            lines.append(f"")

        self.output_file.write_text('\n'.join(lines), encoding='utf-8')
        print(f"Success! Index saved to {self.output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sovereign Citation Indexer")
    parser.add_argument('--config', default='citation_config.yaml', help='Path to configuration file')
    args = parser.parse_args()

    if not Path(args.config).exists():
        print(f"Config file not found: {args.config}")
        print("Please create one or use the default template.")
        exit(1)

    indexer = CitationIndexer(args.config)
    indexer.scan()
    indexer.generate_markdown()
