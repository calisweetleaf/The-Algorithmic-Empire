"""
Tool 3: synthesis_engine.py (Refactored)
Generates Entity Co-occurrence Matrix and Network Graph.
Leverages indexed 'major_names' in per_document_stats.json rather than raw text scanning.
Exports:
- docs/synthesis_matrix.json (Machine Readable)
- docs/entity_network.md (Human Readable)
"""
import json
import argparse
from pathlib import Path
from collections import defaultdict, Counter

def main():
    parser = argparse.ArgumentParser(description="Generate entity co-occurrence analysis.")
    parser.add_argument('--stats', default='docs/per_document_stats.json', help='Path to stats JSON')
    parser.add_argument('--corpus', default='.', help='Root directory (unused in stats-mode but kept for compat)')
    parser.add_argument('--out-json', default='docs/synthesis_matrix.json', help='Output Matrix JSON')
    parser.add_argument('--out-md', default='docs/entity_network.md', help='Output Network Markdown')
    args = parser.parse_args()

    stats_path = Path(args.stats)
    root = Path(args.corpus) # Used for output resolution usually
    
    if not stats_path.exists():
        print(f"Stats file not found: {stats_path}")
        return

    with open(stats_path, 'r', encoding='utf-8') as f:
        stats = json.load(f)
    
    # 1. Build Entity Map: Entity -> Set of DocIDs
    entity_map = defaultdict(set)
    doc_lookup = {}
    
    for doc in stats:
        did = doc.get('doc_id')
        doc_lookup[did] = doc.get('filename')
        
        # Use major_names from index
        names = doc.get('major_names', [])
        for name in names:
            # Normalize? Optional. For now, strict.
            if name and len(name) > 2:
                entity_map[name].add(did)

    # Filter singletons (Entities appearing in only 1 doc)
    # They don't create "bridges"
    bridging_entities = {k: v for k, v in entity_map.items() if len(v) > 1}
    
    print(f"Found {len(entity_map)} total entities. {len(bridging_entities)} are bridging entities.")

    # 2. Calculate Co-occurrence: (Entity A, Entity B) -> Overlap Count
    # Overlap = how many documents contain BOTH entities
    co_occurrence = defaultdict(int)
    
    # Optimization: Iterate interactions via Documents
    # For each doc, get all entities in it. Create pairs.
    # This is faster than N^2 entities.
    
    # Invert map for iteration: Doc -> Entities
    doc_entities = defaultdict(list)
    for ent, docs in bridging_entities.items():
        for d in docs:
            doc_entities[d].append(ent)
            
    # Count pairs
    for d, ents in doc_entities.items():
        # Sort to ensure A-B is same as B-A
        ents.sort()
        for i in range(len(ents)):
            for j in range(i + 1, len(ents)):
                pair = f"{ents[i]}|{ents[j]}"
                co_occurrence[pair] += 1
    
    # 3. Generate JSON Output
    output_data = {
        "metadata": {"source": "synthesis_engine_v2", "doc_count": len(stats)},
        "bridging_entities": {k: list(v) for k, v in bridging_entities.items()},
        "co_occurrence_matrix": dict(co_occurrence)
    }
    
    with open(args.out_json, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    print(f"Matrix saved to {args.out_json}")

    # 4. Generate Markdown Report
    lines = ["# Sovereign Entity Network Graph", "", "Top connected entities across the corpus.", ""]
    lines.append("| Entity A | Entity B | Shared Documents | Strength |")
    lines.append("|---|---|---|---|")
    
    # Sort by strength (shared doc count)
    sorted_pairs = sorted(co_occurrence.items(), key=lambda x: x[1], reverse=True)
    
    for pair, count in sorted_pairs:
        if count < 2: continue # Filter weak links
        e1, e2 = pair.split('|')
        lines.append(f"| **{e1}** | **{e2}** | {count} | {'🔥' * min(count, 5)} |")
        
    with open(args.out_md, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"Network graph saved to {args.out_md}")

if __name__ == '__main__':
    main()
