"""
Tool 1: citation_recount.py
Multi-strategy citation counter that updates per_document_stats.json.
Strategies:
1. references_section_v2: Counts lines in ## References sections.
2. footnote_definitions: Counts [^label]: definitions.
3. url_references: Counts unique https:// domains.
4. inline_links_deduped: Counts [text](url) links (min 3).
5. numbered_list: Counts numbered lists after reference headers.
"""
import json
import re
import argparse
import sys
from pathlib import Path
from collections import defaultdict

def load_stats(stats_path):
    with open(stats_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_stats(stats, stats_path):
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

def count_references_section(content):
    # Find headers like ## References, ## Sources, etc.
    matches = re.finditer(r'^#{2,}\s+(References|Sources|Citations|Bibliography|Works Cited)', content, re.MULTILINE | re.IGNORECASE)
    max_count = 0
    for match in matches:
        start = match.end()
        remaining = content[start:]
        # Find next header to bound the section
        next_header = re.search(r'^#{2,}\s+', remaining, re.MULTILINE)
        section_text = remaining[:next_header.start()] if next_header else remaining
        
        # Count non-empty, non-header lines that look like citations
        lines = [line.strip() for line in section_text.split('\n') if line.strip()]
        # Filter out lines that are too short or look like headers/comments
        lines = [l for l in lines if len(l) > 5 and not l.startswith('#')]
        count = len(lines)
        if count > max_count:
            max_count = count
    return max_count

def count_footnotes(content):
    # Count [^label]: pattern
    return len(re.findall(r'^\[\^.+?\]:', content, re.MULTILINE))

def count_urls(content):
    # Count unique domains from http/https links
    urls = re.findall(r'https?://([\w\.-]+)', content)
    return len(set(urls))

def count_inline_links(content):
    # Count [text](url) pattern
    links = re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', content)
    unique = set(link[1] for link in links)
    count = len(unique)
    # Filter noise - if barely any links, might not be a "cited" doc via this method
    return count if count >= 3 else 0

def count_numbered_list(content):
    # Strictly count "1. ", "2. " after a reference header
    match = re.search(r'^#{2,}\s+(References|Sources|Citations|Bibliography)', content, re.MULTILINE | re.IGNORECASE)
    if not match: return 0
    remaining = content[match.end():]
    next_header = re.search(r'^#{2,}\s+', remaining, re.MULTILINE)
    text = remaining[:next_header.start()] if next_header else remaining
    return len(re.findall(r'^\d+\.\s+', text, re.MULTILINE))

def analyze_file(path):
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        # print(f"Error reading {path}: {e}")
        return {}
        
    return {
        "references_section_v2": count_references_section(text),
        "footnote_definitions": count_footnotes(text),
        "url_references": count_urls(text),
        "inline_links_deduped": count_inline_links(text),
        "numbered_list": count_numbered_list(text)
    }

def main():
    parser = argparse.ArgumentParser(description="Recount citations using multi-strategy heuristics.")
    parser.add_argument('--stats', default='docs/per_document_stats.json', help='Path to stats JSON')
    parser.add_argument('--root', default='.', help='Root corpus directory')
    parser.add_argument('--dry-run', action='store_true', help='Do not save changes to stats file')
    args = parser.parse_args()

    stats_path = Path(args.stats)
    root = Path(args.root)
    
    if not stats_path.exists():
        print(f"Stats file not found: {stats_path}")
        sys.exit(1)

    data = load_stats(stats_path)
    log = {}
    
    print(f"Analyzing {len(data)} documents...")
    
    updated_count = 0
    
    for doc in data:
        # Resolve file path
        rel = doc.get('relative_path')
        if not rel: continue
        
        fpath = root / rel
        if not fpath.exists():
             # Fallback: search by filename
             found = list(root.rglob(doc['filename']))
             if found: 
                 fpath = found[0]
             else:
                 log[doc['doc_id']] = {"error": "File not found"}
                 continue
        
        if fpath.exists():
            counts = analyze_file(fpath)
            # Take the maximum count found by any strategy
            best_count = max(counts.values()) if counts else 0
            # Identify which method yielded the max
            best_method = max(counts, key=counts.get) if counts and best_count > 0 else "none"
            
            # Preserve original count if not already backed up
            if 'citation_count_v1' not in doc:
                doc['citation_count_v1'] = doc.get('citation_count', 0)
            
            # Log changes
            old_count = doc.get('citation_count', 0)
            if best_count != old_count:
                updated_count += 1
                
            doc['citation_count'] = best_count
            doc['citation_count_method'] = best_method
            
            log[doc['doc_id']] = {
                "file": doc['filename'],
                "old_count": old_count,
                "new_count": best_count,
                "method": best_method,
                "breakdown": counts
            }

    # Save Log
    log_path = stats_path.parent / 'citation_recount_log.json'
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2)
    print(f"Log saved to {log_path}")

    # Save Stats
    if not args.dry_run:
        save_stats(data, stats_path)
        print(f"Updated {updated_count} documents. Stats saved to {stats_path}")
    else:
        print(f"Dry run complete. Would have updated {updated_count} documents.")

if __name__ == '__main__':
    main()
