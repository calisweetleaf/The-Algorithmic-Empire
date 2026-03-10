(.venv) PS C:\Users\treyr\Documents\algorithmic_empire> & c:/Users/treyr/Documents/algorithmic_empire/.venv/Scripts/python.exe c:/Users/treyr/Documents/algorithmic_empire/file-proccessor/semantic_chunking_rewrite.py
Loading weights: 100%|█████████████████████████████████████████████████████████████████████| 103/103 [00:00<00:00, 813.27it/s, Materializing param=pooler.dense.weight]
BertModel LOAD REPORT from: sentence-transformers/all-MiniLM-L6-v2
Key                     | Status     |  |
------------------------+------------+--+-
embeddings.position_ids | UNEXPECTED |  |

Notes:
- UNEXPECTED    :can be ignored when loading from different task/architecture; not ok if you expect identical arch.
🚀 Advanced Semantic Chunking Results
==================================================
Success: True
Total chunks: 5
High quality chunks: 0
Average quality score: 0.535
Average coherence: 0.505
Processing time: 2.96s
Chunks per second: 1.7

📊 Extracted Content Preview:
------------------------------
Advanced Semantic Chunking Results
==========================================

Document Analysis:
- Content Type: Markdown
- Total Chunks: 5
- Safe Chunks: 5 (100.0%)
- High Quality Chunks: 0 (0.0%)

Quality Metrics:
- Average Quality Score: 0.535
- Average Semantic Coherence: 0.505
- Average Information Density: 0.615
- Average Readability: 0.274

Size Distribution:
- Average Chunk Size: 37 words
- Size Range: 11-111 words
- Size Consistency: -0.021

Content Analysis:
- Unique Key Phrases: 81
- Named Entities: 17

Sample High-Quality Chunks:
==========================

Chunk 1 (Quality: 0.620, Coherence: 1.000):
# Advanced Machine Learning Techniques

 ## Introduction

 Machine learning has revolutionized the way we approach complex problems in various domains.
Key Phrases: # advanced machine learning techniques

 ## introduction

 machine learning, the way, complex problems, various domains, machine

Chunk 2 (Quality: 0.600, Coherence: 0.209):
The attention mechanism allows models to...
(.venv) PS C:\Users\treyr\Documents\algorithmic_empire> 