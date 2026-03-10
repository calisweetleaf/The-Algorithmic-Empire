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
            'title': file_path.name,
            'description': 'No description available.',
            'path': str(file_path.relative_to(self.root_dir)).replace('\\', '/'),
            'type': file_path.suffix.lower()
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
                for line in lines:
                    if line.startswith('# '):
                        metadata['title'] = line[2:].strip()
                        break
                
                # Try to find first non-header text line for description
                for line in lines:
                    if line.strip() and not line.startswith('#') and not line.startswith('```') and not line.startswith('<!--'):
                        metadata['description'] = line.strip()[:200]
                        if len(line.strip()) > 200:
                            metadata['description'] += "..."
                        break
        except Exception:
            pass # Keep defaults on error

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
            lines.append(f"| File | Type | Description |")
            lines.append(f"|------|------|-------------|")
            
            # Sort files within category
            for item in sorted(self.index_data[category], key=lambda x: x['title']):
                # Create relative link
                link = f"[{item['title']}]({item['path']})"
                desc = item['description'].replace('|', '\|') # Escape pipes for table
                lines.append(f"| {link} | `{item['type']}` | {desc} |")
            
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
