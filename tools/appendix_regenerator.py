"""
Tool 2: appendix_regenerator.py
Regenerates APPENDIX.md from per_document_stats.json.
Categorizes documents into Credibility Tiers:
- HIGH: >= 10 citations
- MEDIUM: 3-9 citations
- LOW: 1-2 citations
- UNCITED: 0 citations
Generates a sorted Markdown table.
"""
import json
import argparse
from pathlib import Path

def get_tier(count):
    if count >= 10: return "HIGH"
    if count >= 3: return "MEDIUM"
    if count >= 1: return "LOW"
    return "UNCITED"

def main():
    parser = argparse.ArgumentParser(description="Regenerate APPENDIX.md with credibility metrics.")
    parser.add_argument('--stats', default='docs/per_document_stats.json', help='Path to stats JSON')
    parser.add_argument('--out', default='docs/APPENDIX.md', help='Output Markdown file')
    args = parser.parse_args()
    
    path = Path(args.stats)
    if not path.exists():
        print(f"Stats file not found: {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Sort logic: 1. Tier Rank (Desc), 2. Citation Count (Desc), 3. Filename (Asc)
    tier_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNCITED": 0}
    data.sort(key=lambda x: (
        tier_rank[get_tier(x.get('citation_count', 0))], 
        x.get('citation_count', 0),
        x.get('filename', '')
    ), reverse=True)

    # Header
    lines = [
        "# SOVEREIGN INTELLIGENCE APPENDIX", 
        "", 
        "| ID | Title | TIER | Citations | Method | Major Topics |", 
        "|---|---|---|---|---|---|"
    ]
    
    # Stats Collection
    stats_summary = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNCITED": 0}
    total_citations = 0
    
    for doc in data:
        count = doc.get('citation_count', 0)
        tier = get_tier(count)
        stats_summary[tier] += 1
        total_citations += count
        
        topics = ", ".join(doc.get('topic_tags', [])) if doc.get('topic_tags') else ""
        # Truncate topics if too long
        if len(topics) > 50: topics = topics[:47] + "..."
        
        row = f"| {doc.get('doc_id', '?')} | {doc.get('filename', '?')} | **{tier}** | {count} | {doc.get('citation_count_method', 'N/A')} | {topics} |"
        lines.append(row)

    # Generate Summary Section
    summary = [
        "## Corpus Credibility Statistics",
        "",
        f"- **Total Documents**: {len(data)}",
        f"- **Total Signal Points (Citations)**: {total_citations}",
        ""
    ]
    for t in ["HIGH", "MEDIUM", "LOW", "UNCITED"]:
         summary.append(f"- **{t} CREDIBILITY**: {stats_summary[t]} docs")
    summary.append("")
    summary.append("---")
    
    # Assemble Output
    # Insert summary after Title (lines[0])
    output_content = lines[:1] + [""] + summary + lines[2:]
    
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write("\n".join(output_content))
        
    print(f"Generated {args.out} with {len(data)} entries.")

if __name__ == '__main__':
    main()
