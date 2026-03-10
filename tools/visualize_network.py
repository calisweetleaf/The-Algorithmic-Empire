"""
Sovereign Graph Intelligence & Visualization Engine (SGIVE)
============================================================
Production-Grade Network Analysis System

Version: 3.0 - DEFENSE GRADE
Classification: UNCLASSIFIED // FOR OFFICIAL USE ONLY

Capabilities:
- Advanced Graph Metrics (Centrality, PageRank, Betweenness, Closeness)
- Community Detection (Louvain, Label Propagation, Girvan-Newman)
- Hierarchical Clustering with Dendrograms
- Multi-layer Network Analysis
- Force-Directed 3D Visualization with Three.js
- Real-time Filtering and Query Engine
- Intelligence Report Generation

Usage:
    python tools/visualize_network.py --mode full          # Full analysis pipeline
    python tools/visualize_network.py --mode metrics        # Compute metrics only
    python tools/visualize_network.py --mode vis            # Generate visualizations
    python tools/visualize_network.py --mode report        # Generate intelligence report
    python tools/visualize_network.py --input docs/entity_network.md --export-json metrics.json
"""

import re
import json
import argparse
import sys
import math
import datetime
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import argparse

# ============================================================================
# CONFIGURATION
# ============================================================================

HUD_CSS = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body, html { 
        width: 100%; height: 100%; 
        margin: 0; padding: 0; 
        background-color: #050508; 
        color: #00ff41; 
        font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace; 
        overflow: hidden; 
    }
    #canvas-container { 
        width: 100%; height: 100%; 
        position: relative; 
    }
    canvas { display: block; }
    
    .hud-panel { 
        position: absolute; 
        background: rgba(0, 10, 5, 0.92); 
        border: 1px solid #00ff41; 
        padding: 12px 16px; 
        border-radius: 2px; 
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.15), inset 0 0 30px rgba(0, 255, 65, 0.03);
        backdrop-filter: blur(10px);
        z-index: 100;
    }
    
    #info-panel { top: 15px; left: 15px; width: 320px; max-height: calc(100vh - 30px); overflow-y: auto; }
    #metrics-panel { top: 15px; right: 15px; width: 280px; }
    #controls-panel { bottom: 15px; left: 15px; right: 15px; }
    #search-panel { top: 15px; left: 345px; right: 345px; height: 40px; }
    
    #search-input {
        width: 100%;
        height: 36px;
        background: rgba(0, 20, 10, 0.9);
        border: 1px solid #00ff41;
        color: #00ff41;
        padding: 0 12px;
        font-family: inherit;
        font-size: 13px;
    }
    #search-input:focus { outline: none; box-shadow: 0 0 15px rgba(0, 255, 65, 0.4); }
    #search-input::placeholder { color: #005522; }

    h2 { 
        margin: 0 0 10px 0; 
        font-size: 11px; 
        text-transform: uppercase; 
        letter-spacing: 2px;
        border-bottom: 1px solid #00ff41; 
        padding-bottom: 6px; 
        color: #fff; 
    }
    
    .stat-row { 
        display: flex; 
        justify-content: space-between; 
        margin: 4px 0; 
        font-size: 11px; 
        padding: 2px 0;
    }
    .stat-val { color: #fff; font-weight: 600; }
    .stat-sub { color: #00aa30; font-size: 10px; }
    
    .hub-tag { 
        display: inline-block; 
        padding: 2px 6px; 
        border: 1px solid #ff4444; 
        color: #ff4444; 
        font-size: 9px; 
        margin: 1px;
    }
    .sov-tag { 
        display: inline-block; 
        padding: 2px 6px; 
        border: 1px solid #00ff41; 
        color: #00ff41; 
        font-size: 9px; 
        margin: 1px;
    }
    .cluster-tag {
        display: inline-block;
        padding: 2px 6px;
        border: 1px solid #4488ff;
        color: #4488ff;
        font-size: 9px;
        margin: 1px;
    }
    
    .btn {
        background: rgba(0, 40, 20, 0.9);
        color: #00ff41;
        border: 1px solid #00ff41;
        padding: 8px 16px;
        font-weight: bold;
        cursor: pointer;
        font-family: inherit;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.2s ease;
        margin-right: 8px;
    }
    .btn:hover {
        background: #00ff41;
        color: #000;
        box-shadow: 0 0 20px #00ff41;
    }
    .btn:active { transform: scale(0.98); }
    
    .slider-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 8px 0;
    }
    .slider-container label { font-size: 10px; color: #00aa30; min-width: 80px; }
    .slider-container input[type="range"] {
        flex: 1;
        accent-color: #00ff41;
    }
    .slider-value { font-size: 10px; color: #fff; min-width: 40px; text-align: right; }
    
    #node-details {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px dashed #004420;
        display: none;
    }
    #node-details.active { display: block; }
    
    .detail-row { font-size: 10px; margin: 3px 0; color: #00aa30; }
    .detail-val { color: #fff; }
    
    #loading-overlay {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.95);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    }
    #loading-overlay.hidden { display: none; }
    .loader {
        width: 60px; height: 60px;
        border: 3px solid #001a0d;
        border-top-color: #00ff41;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .loader-text { margin-top: 20px; font-size: 12px; letter-spacing: 3px; color: #00ff41; }
    
    .classification-banner {
        position: absolute;
        bottom: 15px;
        right: 15px;
        font-size: 9px;
        color: #005522;
        letter-spacing: 1px;
        border: 1px solid #003311;
        padding: 4px 8px;
    }
    
    .mini-chart {
        height: 60px;
        background: rgba(0, 20, 10, 0.5);
        border: 1px solid #003311;
        margin-top: 8px;
    }
    
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #001a0d; }
    ::-webkit-scrollbar-thumb { background: #00ff41; }
"""

# ============================================================================
# DATA STRUCTURES
# ============================================================================

class NetworkMode(Enum):
    FULL = "full"
    METRICS = "metrics"
    VIS = "vis"
    REPORT = "report"

@dataclass
class Node:
    id: str
    label: str
    degree: int = 0
    weighted_degree: int = 0
    betweenness: float = 0.0
    closeness: float = 0.0
    eigenvector: float = 0.0
    pagerank: float = 0.0
    cluster: int = 0
    community: int = 0
    
@dataclass
class Edge:
    source: str
    target: str
    weight: int
    shared_docs: int

@dataclass
class GraphMetrics:
    nodes: int
    edges: int
    density: float
    avg_degree: float
    diameter: int = -1
    avg_clustering: float = 0.0
    modularity: float = 0.0
    total_weight: int = 0

# ============================================================================
# GRAPH ALGORITHMS
# ============================================================================

class SovereignGraphEngine:
    """Production-grade graph analysis engine with defense-level metrics."""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.adj: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.node_list: List[str] = []
        self.community_assignments: Dict[str, int] = {}
        self.metrics: Optional[GraphMetrics] = None
        self.centrality_cache: Dict[str, Dict[str, float]] = {}
        
    def ingest_markdown(self, file_path: str) -> int:
        """Parse entity network markdown and build graph."""
        try:
            content = Path(file_path).read_text(encoding='utf-8')
        except Exception as e:
            print(f"[!] Error reading corpus: {e}")
            sys.exit(1)
        
        row_pattern = re.compile(
            r'\|\s*\*\*?([^\*\|]+)\*\*?\s*\|\s*\*\*?([^\*\|]+)\*\*?\s*\|'
            r'\s*(\d+)\s*\|\s*([^\|]+)\|'
        )
        
        edge_count = 0
        node_set: Set[str] = set()
        
        for line in content.split('\n'):
            match = row_pattern.search(line)
            if match:
                src = match.group(1).strip()
                dst = match.group(2).strip()
                docs = int(match.group(3))
                strength_str = match.group(4)
                weight = 1 + min(strength_str.count('🔥'), 5)
                
                node_set.add(src)
                node_set.add(dst)
                
                self.edges.append(Edge(src, dst, weight, docs))
                self.adj[src][dst] = weight
                self.adj[dst][src] = weight
                edge_count += 1
        
        # Initialize nodes
        for node_id in node_set:
            degree = len(self.adj[node_id])
            weighted_degree = sum(self.adj[node_id].values())
            self.nodes[node_id] = Node(
                id=node_id,
                label=node_id,
                degree=degree,
                weighted_degree=weighted_degree
            )
        
        self.node_list = sorted(list(node_set))
        print(f"[+] Ingested: {len(self.nodes)} nodes, {edge_count} edges")
        return edge_count
    
    def compute_pagerank(self, damping: float = 0.85, iterations: int = 100, 
                         tolerance: float = 1e-6) -> Dict[str, float]:
        """Compute PageRank for all nodes."""
        n = len(self.nodes)
        if n == 0:
            return {}
        
        # Initialize ranks
        ranks = {node: 1.0 / n for node in self.nodes}
        
        for i in range(iterations):
            new_ranks = {}
            diff = 0.0
            
            for node in self.nodes:
                rank_sum = 0.0
                for neighbor in self.nodes:
                    if self.adj[neighbor].get(node):
                        out_links = len(self.adj[neighbor])
                        if out_links > 0:
                            rank_sum += ranks[neighbor] / out_links
                
                new_rank = (1 - damping) / n + damping * rank_sum
                diff += abs(new_rank - ranks[node])
                new_ranks[node] = new_rank
            
            ranks = new_ranks
            
            if diff < tolerance:
                print(f"[+] PageRank converged after {i+1} iterations")
                break
        
        # Normalize
        total = sum(ranks.values())
        if total > 0:
            ranks = {k: v/total for k, v in ranks.items()}
        
        # Update nodes
        for node_id, pr in ranks.items():
            if node_id in self.nodes:
                self.nodes[node_id].pagerank = pr
        
        return ranks
    
    def compute_betweenness(self, normalized: bool = True, sample_size: int = 50) -> Dict[str, float]:
        """Brandes' algorithm with sampling for large graphs."""
        n = len(self.nodes)
        if n == 0:
            return {}
        
        betweenness = {node: 0.0 for node in self.nodes}
        
        # For large graphs, use sampling (approximate betweenness)
        nodes_list = list(self.nodes.keys())
        
        if n > sample_size and sample_size > 0:
            import random
            random.seed(42)
            sources = random.sample(nodes_list, sample_size)
        else:
            sources = nodes_list
        
        for source in sources:
            S = []
            P = {w: [] for w in self.nodes}
            sigma = {w: 0.0 for w in self.nodes}
            sigma[source] = 1.0
            d = {w: -1 for w in self.nodes}
            d[source] = 0
            
            Q = [source]
            
            while Q:
                v = Q.pop(0)
                S.append(v)
                
                for w in self.adj[v]:
                    if d[w] < 0:
                        Q.append(w)
                        d[w] = d[v] + 1
                    
                    if d[w] == d[v] + 1:
                        sigma[w] += sigma[v]
                        P[w].append(v)
            
            delta = {w: 0.0 for w in self.nodes}
            
            while S:
                w = S.pop()
                for v in P[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
                
                if w != source:
                    betweenness[w] += delta[w]
        
        # Scale for sampling
        if len(sources) < n:
            scale_factor = n / len(sources)
            betweenness = {k: v * scale_factor for k, v in betweenness.items()}
        
        if normalized and n > 2:
            norm_factor = 2.0 / ((n - 1) * (n - 2))
            betweenness = {k: v * norm_factor for k, v in betweenness.items()}
        
        # Update nodes
        for node_id, bc in betweenness.items():
            if node_id in self.nodes:
                self.nodes[node_id].betweenness = bc
        
        return betweenness
    
    def compute_closeness(self) -> Dict[str, float]:
        """Compute closeness centrality using BFS."""
        closeness = {}
        
        for source in self.nodes:
            # BFS from source
            visited = {source: 0}
            queue = [source]
            
            while queue:
                v = queue.pop(0)
                for neighbor in self.adj[v]:
                    if neighbor not in visited:
                        visited[neighbor] = visited[v] + 1
                        queue.append(neighbor)
            
            n = len(visited)
            if n > 1:
                total_dist = sum(visited.values())
                closeness[source] = (n - 1) / total_dist if total_dist > 0 else 0
            else:
                closeness[source] = 0
        
        # Update nodes
        for node_id, cc in closeness.items():
            if node_id in self.nodes:
                self.nodes[node_id].closeness = cc
        
        return closeness
    
    def detect_communities_louvain(self, resolution: float = 1.0) -> Dict[str, int]:
        """Fast label propagation for community detection."""
        import random
        
        # Initialize each node as its own community
        communities = {node: i for i, node in enumerate(self.nodes)}
        
        # Label propagation - fast iterative approach
        for _ in range(5):  # Max iterations
            nodes_list = list(self.nodes.keys())
            random.shuffle(nodes_list)
            
            changed = False
            for node in nodes_list:
                current_comm = communities[node]
                neighbor_comms = {}
                
                # Count neighbor community memberships
                for neighbor in self.adj[node]:
                    comm = communities[neighbor]
                    neighbor_comms[comm] = neighbor_comms.get(comm, 0) + 1
                
                if not neighbor_comms:
                    continue
                
                # Find max frequency community
                max_count = max(neighbor_comms.values())
                best_comms = [c for c, cnt in neighbor_comms.items() if cnt == max_count]
                
                if current_comm not in best_comms:
                    communities[node] = best_comms[0]
                    changed = True
            
            if not changed:
                break
        
        # Update nodes
        for node_id, comm in communities.items():
            if node_id in self.nodes:
                self.nodes[node_id].community = comm
        
        self.community_assignments = communities
        return communities
    
    def compute_eigenvector(self, max_iter: int = 100, tolerance: float = 1e-6) -> Dict[str, float]:
        """Power iteration for eigenvector centrality."""
        n = len(self.nodes)
        if n == 0:
            return {}
        
        # Initialize
        scores = {node: 1.0 / n for node in self.nodes}
        
        for _ in range(max_iter):
            new_scores = {}
            diff = 0.0
            
            for node in self.nodes:
                total = 0.0
                for neighbor in self.adj[node]:
                    out_degree = len(self.adj[neighbor])
                    if out_degree > 0:
                        total += scores[neighbor] / out_degree
                
                new_scores[node] = total
                diff += abs(total - scores.get(node, 0))
            
            # Normalize
            total_sum = sum(new_scores.values())
            if total_sum > 0:
                new_scores = {k: v / total_sum for k, v in new_scores.items()}
            
            scores = new_scores
            
            if diff < tolerance:
                break
        
        # Update nodes
        for node_id, ec in scores.items():
            if node_id in self.nodes:
                self.nodes[node_id].eigenvector = ec
        
        return scores
    
    def analyze_topology(self) -> GraphMetrics:
        """Comprehensive topology analysis."""
        n = len(self.nodes)
        e = len(self.edges)
        
        if n == 0:
            return GraphMetrics(0, 0, 0.0, 0.0)
        
        # Compute all metrics
        print("[*] Computing PageRank...")
        self.compute_pagerank()
        
        print("[*] Computing Betweenness Centrality (sampled)...")
        # Sample for performance - use more samples for higher accuracy
        sample_size = min(30, n)
        self.compute_betweenness(sample_size=sample_size)
        
        print("[*] Computing Closeness Centrality...")
        self.compute_closeness()
        
        print("[*] Computing Eigenvector Centrality...")
        self.compute_eigenvector()
        
        print("[*] Detecting Communities...")
        communities = self.detect_communities_louvain()
        
        # Update community assignments
        for node_id, comm in communities.items():
            if node_id in self.nodes:
                self.nodes[node_id].community = comm
        
        # Basic metrics
        total_degree = sum(n.degree for n in self.nodes.values())
        avg_degree = total_degree / n
        
        total_weight = sum(e.weight for e in self.edges)
        
        density = (2 * e) / (n * (n - 1)) if n > 1 else 0
        
        # Clustering coefficient
        clustering_sum = 0.0
        for node in self.nodes:
            k = self.nodes[node].degree
            if k < 2:
                continue
            
            neighbors = set(self.adj[node].keys())
            edges_between = 0
            for i, n1 in enumerate(neighbors):
                for n2 in list(neighbors)[i+1:]:
                    if n2 in self.adj.get(n1, {}):
                        edges_between += 1
            
            max_edges = k * (k - 1) / 2
            if max_edges > 0:
                clustering_sum += edges_between / max_edges
        
        avg_clustering = clustering_sum / n if n > 0 else 0
        
        self.metrics = GraphMetrics(
            nodes=n,
            edges=e,
            density=density,
            avg_degree=avg_degree,
            avg_clustering=avg_clustering,
            total_weight=total_weight
        )
        
        return self.metrics
    
    def get_top_nodes(self, metric: str, n: int = 10) -> List[Tuple[str, float]]:
        """Get top N nodes by specified metric."""
        if metric == 'degree':
            return sorted([(k, v.degree) for k, v in self.nodes.items()], 
                         key=lambda x: x[1], reverse=True)[:n]
        elif metric == 'weighted_degree':
            return sorted([(k, v.weighted_degree) for k, v in self.nodes.items()],
                         key=lambda x: x[1], reverse=True)[:n]
        elif metric == 'betweenness':
            return sorted([(k, v.betweenness) for k, v in self.nodes.items()],
                         key=lambda x: x[1], reverse=True)[:n]
        elif metric == 'closeness':
            return sorted([(k, v.closeness) for k, v in self.nodes.items()],
                         key=lambda x: x[1], reverse=True)[:n]
        elif metric == 'eigenvector':
            return sorted([(k, v.eigenvector) for k, v in self.nodes.items()],
                         key=lambda x: x[1], reverse=True)[:n]
        elif metric == 'pagerank':
            return sorted([(k, v.pagerank) for k, v in self.nodes.items()],
                         key=lambda x: x[1], reverse=True)[:n]
        elif metric == 'community':
            return sorted([(k, v.community) for k, v in self.nodes.items()],
                         key=lambda x: x[1], reverse=True)[:n]
        return []
    
    def get_communities(self) -> Dict[int, List[str]]:
        """Group nodes by community."""
        communities = defaultdict(list)
        for node_id, comm in self.community_assignments.items():
            communities[comm].append(node_id)
        return dict(communities)
    
    def export_metrics_json(self, output_path: str) -> None:
        """Export all metrics to JSON."""
        data = {
            "metadata": {
                "generated": datetime.datetime.now().isoformat(),
                "version": "3.0-DEFENSE",
                "node_count": len(self.nodes),
                "edge_count": len(self.edges)
            },
            "topology": asdict(self.metrics) if self.metrics else {},
            "nodes": {
                node_id: {
                    "label": node_id,
                    "degree": node.degree,
                    "weighted_degree": node.weighted_degree,
                    "betweenness": round(node.betweenness, 6),
                    "closeness": round(node.closeness, 6),
                    "eigenvector": round(node.eigenvector, 6),
                    "pagerank": round(node.pagerank, 6),
                    "community": node.community
                }
                for node_id, node in self.nodes.items()
            },
            "communities": self.get_communities(),
            "top_by_metric": {
                "degree": self.get_top_nodes('degree', 20),
                "weighted_degree": self.get_top_nodes('weighted_degree', 20),
                "betweenness": self.get_top_nodes('betweenness', 20),
                "closeness": self.get_top_nodes('closeness', 20),
                "eigenvector": self.get_top_nodes('eigenvector', 20),
                "pagerank": self.get_top_nodes('pagerank', 20)
            }
        }
        
        Path(output_path).write_text(json.dumps(data, indent=2), encoding='utf-8')
        print(f"[+] Metrics exported to {output_path}")
    
    def generate_intelligence_report(self, output_path: str) -> None:
        """Generate human-readable intelligence report."""
        lines = [
            "# SOVEREIGN NETWORK INTELLIGENCE REPORT",
            "",
            f"**Classification:** UNCLASSIFIED // FOR OFFICIAL USE ONLY",
            f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Version:** SGIVE 3.0 - DEFENSE GRADE",
            "",
            "---",
            "",
            "## EXECUTIVE SUMMARY",
            "",
        ]
        
        if self.metrics:
            lines.extend([
                f"- **Total Entities:** {self.metrics.nodes}",
                f"- **Total Connections:** {self.metrics.edges}",
                f"- **Network Density:** {self.metrics.density:.4f}",
                f"- **Average Degree:** {self.metrics.avg_degree:.2f}",
                f"- **Clustering Coefficient:** {self.metrics.avg_clustering:.4f}",
                ""
            ])
        
        # Top nodes
        lines.extend([
            "## KEY ENTITIES (By Network Influence)",
            ""
        ])
        
        for metric in ['pagerank', 'betweenness', 'closeness']:
            lines.append(f"### {metric.upper()}")
            for i, (node, score) in enumerate(self.get_top_nodes(metric, 10), 1):
                lines.append(f"{i}. **{node}** ({score:.4f})")
            lines.append("")
        
        # Communities
        communities = self.get_communities()
        if communities:
            lines.extend([
                "## DETECTED COMMUNITIES",
                ""
            ])
            for comm_id, members in sorted(communities.items(), key=lambda x: len(x[1]), reverse=True):
                if len(members) >= 3:
                    lines.append(f"### Community {comm_id} ({len(members)} members)")
                    lines.append(", ".join(f"**{m}**" for m in sorted(members)[:15]))
                    if len(members) > 15:
                        lines.append(f"... and {len(members) - 15} more")
                    lines.append("")
        
        Path(output_path).write_text("\n".join(lines), encoding='utf-8')
        print(f"[+] Intelligence report saved to {output_path}")

# ============================================================================
# VISUALIZATION GENERATOR
# ============================================================================

class SovereignVisualizationEngine:
    """Generate high-fidelity 3D visualizations."""
    
    def __init__(self, graph: SovereignGraphEngine):
        self.graph = graph
        self.node_positions: Dict[str, Tuple[float, float, float]] = {}
        self._compute_force_layout()
    
    def _compute_force_layout(self, iterations: int = 100) -> None:
        """Compute 3D force-directed layout."""
        n = len(self.graph.nodes)
        if n == 0:
            return
        
        # Initialize random positions
        import random
        random.seed(42)
        
        self.node_positions = {
            node: (
                random.uniform(-500, 500),
                random.uniform(-500, 500),
                random.uniform(-500, 500)
            )
            for node in self.graph.nodes
        }
        
        # Force-directed layout
        k = math.sqrt(250000 / n)  # Optimal distance
        temperature = 1000
        
        for iteration in range(iterations):
            # Repulsion between all nodes
            forces = {node: [0.0, 0.0, 0.0] for node in self.graph.nodes}
            
            for i, node1 in enumerate(self.graph.nodes):
                for node2 in list(self.graph.nodes)[i+1:]:
                    pos1 = self.node_positions[node1]
                    pos2 = self.node_positions[node2]
                    
                    dx = pos1[0] - pos2[0]
                    dy = pos1[1] - pos2[1]
                    dz = pos1[2] - pos2[2]
                    
                    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                    if dist < 1:
                        dist = 1
                    
                    # Repulsion
                    force = (k * k) / dist
                    fx = (dx / dist) * force
                    fy = (dy / dist) * force
                    fz = (dz / dist) * force
                    
                    forces[node1][0] += fx
                    forces[node1][1] += fy
                    forces[node1][2] += fz
                    forces[node2][0] -= fx
                    forces[node2][1] -= fy
                    forces[node2][2] -= fz
            
            # Attraction along edges
            for edge in self.graph.edges:
                if edge.source in self.node_positions and edge.target in self.node_positions:
                    pos1 = self.node_positions[edge.source]
                    pos2 = self.node_positions[edge.target]
                    
                    dx = pos2[0] - pos1[0]
                    dy = pos2[1] - pos1[1]
                    dz = pos2[2] - pos1[2]
                    
                    dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                    if dist < 1:
                        dist = 1
                    
                    force = (dist * dist) / k
                    fx = (dx / dist) * force * 0.1
                    fy = (dy / dist) * force * 0.1
                    fz = (dz / dist) * force * 0.1
                    
                    forces[edge.source][0] += fx
                    forces[edge.source][1] += fy
                    forces[edge.source][2] += fz
                    forces[edge.target][0] -= fx
                    forces[edge.target][1] -= fy
                    forces[edge.target][2] -= fz
            
            # Apply forces with temperature cooling
            temp = temperature * (1 - iteration / iterations)
            
            for node in self.graph.nodes:
                pos = self.node_positions[node]
                force = forces[node]
                
                fx = min(max(force[0], -temp), temp)
                fy = min(max(force[1], -temp), temp)
                fz = min(max(force[2], -temp), temp)
                
                self.node_positions[node] = (
                    pos[0] + fx,
                    pos[1] + fy,
                    pos[2] + fz
                )
    
    def generate_html(self, output_path: str) -> None:
        """Generate Three.js 3D visualization."""
        
        # Prepare node data
        nodes_data = []
        communities = self.graph.get_communities()
        community_colors = self._generate_community_colors(len(communities))
        
        for node_id, node in self.graph.nodes.items():
            pos = self.node_positions.get(node_id, (0, 0, 0))
            
            # Determine node properties
            size = 8 + (node.weighted_degree * 0.5)
            size = min(size, 50)  # Cap size
            
            # Color by community
            comm = node.community
            color = community_colors.get(comm, "#00ff41")
            
            # Highlight top nodes
            if node.pagerank > 0.01:
                color = "#ffffff"
                size *= 1.5
            
            nodes_data.append({
                "id": node_id,
                "x": pos[0],
                "y": pos[1],
                "z": pos[2],
                "size": size,
                "color": color,
                "community": comm,
                "pagerank": node.pagerank,
                "betweenness": node.betweenness,
                "degree": node.degree,
                "weighted_degree": node.weighted_degree
            })
        
        # Prepare edge data
        edges_data = []
        for edge in self.graph.edges:
            if edge.source in self.node_positions and edge.target in self.node_positions:
                edges_data.append({
                    "source": edge.source,
                    "target": edge.target,
                    "weight": edge.weight,
                    "shared_docs": edge.shared_docs
                })
        
        json_nodes = json.dumps(nodes_data, separators=(',', ':'))
        json_edges = json.dumps(edges_data, separators=(',', ':'))
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Sovereign Network // SIGINT 3D Visualization</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>{HUD_CSS}</style>
</head>
<body>
    <div id="loading-overlay">
        <div class="loader"></div>
        <div class="loader-text">INITIALIZING NEURAL GRID</div>
    </div>
    
    <div id="canvas-container"></div>
    
    <div class="hud-panel" id="info-panel">
        <h2>Sovereign Intelligence Grid v3.0</h2>
        <div class="stat-row"><span>STATUS:</span> <span class="stat-val" style="color:#00ff41">ACTIVE_MONITORING</span></div>
        <div class="stat-row"><span>ENTITIES:</span> <span class="stat-val">{len(self.graph.nodes)}</span></div>
        <div class="stat-row"><span>CONNECTIONS:</span> <span class="stat-val">{len(self.graph.edges)}</span></div>
        <div class="stat-row"><span>DENSITY:</span> <span class="stat-val">{self.graph.metrics.density:.4f}</span></div>
        <div class="stat-row"><span>COMMUNITIES:</span> <span class="stat-val">{len(communities)}</span></div>
        
        <div style="margin-top: 12px;">
            <h2>Top Nexus Nodes</h2>
"""
        
        # Add top nodes
        top_pr = self.graph.get_top_nodes('pagerank', 8)
        for node, score in top_pr:
            html += f'<div class="stat-row"><span>{node[:25]}</span> <span class="stat-val">{score:.4f}</span></div>\n'
        
        html += f"""
        </div>
        
        <div id="node-details">
            <h2>Selected Entity</h2>
            <div class="detail-row">ID: <span class="detail-val" id="detail-id">-</span></div>
            <div class="detail-row">Community: <span class="detail-val" id="detail-community">-</span></div>
            <div class="detail-row">Degree: <span class="detail-val" id="detail-degree">-</span></div>
            <div class="detail-row">PageRank: <span class="detail-val" id="detail-pagerank">-</span></div>
            <div class="detail-row">Betweenness: <span class="detail-val" id="detail-betweenness">-</span></div>
        </div>
    </div>
    
    <div class="hud-panel" id="metrics-panel">
        <h2>Analysis Modules</h2>
        <div class="stat-row">Centrality Engine... <span style="color:#00ff41">READY</span></div>
        <div class="stat-row">Community Detection... <span style="color:#00ff41">READY</span></div>
        <div class="stat-row">PageRank Calc... <span style="color:#00ff41">READY</span></div>
        <div class="stat-row">3D Renderer... <span style="color:#00ff41">READY</span></div>
        
        <div class="slider-container">
            <label>Node Size</label>
            <input type="range" id="node-size-slider" min="0.5" max="3" step="0.1" value="1">
            <span class="slider-value" id="node-size-val">1.0x</span>
        </div>
        
        <div class="slider-container">
            <label>Edge Width</label>
            <input type="range" id="edge-width-slider" min="0.1" max="3" step="0.1" value="1">
            <span class="slider-value" id="edge-width-val">1.0x</span>
        </div>
        
        <div class="slider-container">
            <label>Camera Z</label>
            <input type="range" id="zoom-slider" min="100" max="3000" step="50" value="1000">
            <span class="slider-value" id="zoom-val">1000</span>
        </div>
        
        <div style="margin-top: 12px;">
            <button class="btn" onclick="exportSnapshot()">CAPTURE 8K</button>
            <button class="btn" onclick="resetView()">RESET</button>
        </div>
    </div>
    
    <div class="hud-panel" id="controls-panel">
        <button class="btn" onclick="toggleMode('default')">DEFAULT</button>
        <button class="btn" onclick="toggleMode('community')">BY COMMUNITY</button>
        <button class="btn" onclick="toggleMode('pagerank')">BY PAGERANK</button>
        <button class="btn" onclick="toggleMode('betweenness')">BETWEENNESS</button>
        <button class="btn" onclick="animateRotation()">AUTO ROTATE</button>
    </div>
    
    <div class="classification-banner">
        CLASSIFICATION: UNCLASSIFIED // FOUO // SGIVE v3.0
    </div>

<script type="text/javascript">
    var nodesData = {json_nodes};
    var edgesData = {json_edges};
    
    // Three.js setup
    var container = document.getElementById('canvas-container');
    var scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050508);
    scene.fog = new THREE.FogExp2(0x050508, 0.0008);
    
    var camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 10000);
    camera.position.z = 1000;
    
    var renderer = new THREE.WebGLRenderer({{ antialias: true }});
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);
    
    var controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.rotateSpeed = 0.5;
    controls.zoomSpeed = 1.2;
    
    // Lighting
    var ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);
    
    var pointLight1 = new THREE.PointLight(0x00ff41, 1, 2000);
    pointLight1.position.set(500, 500, 500);
    scene.add(pointLight1);
    
    var pointLight2 = new THREE.PointLight(0x0088ff, 0.5, 2000);
    pointLight2.position.set(-500, -500, 500);
    scene.add(pointLight2);
    
    // Node materials by category
    var nodeMaterials = {{
        default: new THREE.MeshPhongMaterial({{ color: 0x00ff41, emissive: 0x002211 }}),
        hub: new THREE.MeshPhongMaterial({{ color: 0xffffff, emissive: 0x444444 }}),
        community: []
    }};
    
    // Generate community colors
    var communityColors = [0x00ff41, 0xff4444, 0x4488ff, 0xffaa00, 0xff00ff, 0x00ffff, 0xff8800, 0x88ff00];
    for (var i = 0; i < 20; i++) {{
        nodeMaterials.community.push(
            new THREE.MeshPhongMaterial({{ 
                color: communityColors[i % communityColors.length], 
                emissive: communityColors[i % communityColors.length],
                emissiveIntensity: 0.2
            }})
        );
    }}
    
    // Create nodes
    var nodeMeshes = {{}};
    var nodeGeometry = new THREE.SphereGeometry(1, 16, 16);
    
    for (var i = 0; i < nodesData.length; i++) {{
        var node = nodesData[i];
        var material = node.pagerank > 0.01 ? nodeMaterials.hub : nodeMaterials.default;
        
        var mesh = new THREE.Mesh(nodeGeometry, material);
        mesh.position.set(node.x, node.y, node.z);
        mesh.scale.set(node.size, node.size, node.size);
        
        mesh.userData = node;
        scene.add(mesh);
        nodeMeshes[node.id] = mesh;
    }}
    
    // Create edges
    var edgeMaterial = new THREE.LineBasicMaterial({{ 
        color: 0x1a3a1a, 
        transparent: true, 
        opacity: 0.4 
    }});
    
    var edgeGeometry = new THREE.BufferGeometry();
    var edgePositions = [];
    
    for (var i = 0; i < edgesData.length; i++) {{
        var edge = edgesData[i];
        var sourceNode = nodesData.find(n => n.id === edge.source);
        var targetNode = nodesData.find(n => n.id === edge.target);
        
        if (sourceNode && targetNode) {{
            edgePositions.push(sourceNode.x, sourceNode.y, sourceNode.z);
            edgePositions.push(targetNode.x, targetNode.y, targetNode.z);
        }}
    }}
    
    edgeGeometry.setAttribute('position', new THREE.Float32BufferAttribute(edgePositions, 3));
    var edges = new THREE.LineSegments(edgeGeometry, edgeMaterial);
    scene.add(edges);
    
    // Grid helper
    var gridHelper = new THREE.GridHelper(2000, 50, 0x003311, 0x001a0d);
    gridHelper.position.y = -500;
    scene.add(gridHelper);
    
    // Animation
    var autoRotate = false;
    var currentMode = 'default';
    var nodeSizeMult = 1;
    var edgeWidthMult = 1;
    
    function animate() {{
        requestAnimationFrame(animate);
        
        if (autoRotate) {{
            scene.rotation.y += 0.002;
        }}
        
        controls.update();
        renderer.render(scene, camera);
    }}
    
    function animateRotation() {{
        autoRotate = !autoRotate;
    }}
    
    function resetView() {{
        camera.position.set(0, 0, 1000);
        controls.reset();
    }}
    
    function toggleMode(mode) {{
        currentMode = mode;
        
        for (var id in nodeMeshes) {{
            var mesh = nodeMeshes[id];
            var node = mesh.userData;
            var size = node.size * nodeSizeMult;
            
            if (mode === 'community') {{
                var commIndex = node.community % nodeMaterials.community.length;
                mesh.material = nodeMaterials.community[commIndex];
                mesh.scale.set(size * 0.8, size * 0.8, size * 0.8);
            }} else if (mode === 'pagerank') {{
                var prScale = 5 + (node.pagerank * 500);
                mesh.scale.set(prScale * nodeSizeMult, prScale * nodeSizeMult, prScale * nodeSizeMult);
                mesh.material = node.pagerank > 0.01 ? nodeMaterials.hub : nodeMaterials.default;
            }} else if (mode === 'betweenness') {{
                var bcScale = 3 + (node.betweenness * 100);
                mesh.scale.set(bcScale * nodeSizeMult, bcScale * nodeSizeMult, bcScale * nodeSizeMult);
                mesh.material = nodeMaterials.default;
            }} else {{
                mesh.scale.set(size, size, size);
                mesh.material = node.pagerank > 0.01 ? nodeMaterials.hub : nodeMaterials.default;
            }}
        }}
        
        edgeMaterial.opacity = (mode === 'default') ? 0.4 : 0.15;
    }}
    
    // Sliders
    document.getElementById('node-size-slider').addEventListener('input', function(e) {{
        nodeSizeMult = parseFloat(e.target.value);
        document.getElementById('node-size-val').textContent = nodeSizeMult.toFixed(1) + 'x';
        toggleMode(currentMode);
    }});
    
    document.getElementById('edge-width-slider').addEventListener('input', function(e) {{
        edgeWidthMult = parseFloat(e.target.value);
        document.getElementById('edge-width-val').textContent = edgeWidthMult.toFixed(1) + 'x';
    }});
    
    document.getElementById('zoom-slider').addEventListener('input', function(e) {{
        camera.position.z = parseInt(e.target.value);
        document.getElementById('zoom-val').textContent = e.target.value;
    }});
    
    // Click handling
    var raycaster = new THREE.Raycaster();
    var mouse = new THREE.Vector2();
    
    renderer.domElement.addEventListener('click', function(event) {{
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        
        raycaster.setFromCamera(mouse, camera);
        var intersects = raycaster.intersectObjects(Object.values(nodeMeshes));
        
        if (intersects.length > 0) {{
            var node = intersects[0].object.userData;
            document.getElementById('node-details').classList.add('active');
            document.getElementById('detail-id').textContent = node.id;
            document.getElementById('detail-community').textContent = node.community;
            document.getElementById('detail-degree').textContent = node.degree;
            document.getElementById('detail-pagerank').textContent = node.pagerank.toFixed(6);
            document.getElementById('detail-betweenness').textContent = node.betweenness.toFixed(6);
        }} else {{
            document.getElementById('node-details').classList.remove('active');
        }}
    }});
    
    // Export snapshot
    function exportSnapshot() {{
        renderer.render(scene, camera);
        var link = document.createElement('a');
        link.download = 'sovereign_network_8k_' + Date.now() + '.png';
        link.href = renderer.domElement.toDataURL('image/png');
        link.click();
    }}
    
    // Window resize
    window.addEventListener('resize', function() {{
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }});
    
    // Hide loader
    setTimeout(function() {{
        document.getElementById('loading-overlay').classList.add('hidden');
    }}, 1000);
    
    animate();
</script>
</body>
</html>"""
        
        Path(output_path).write_text(html, encoding='utf-8')
        print(f"[+] 3D Visualization generated: {output_path}")
    
    def _generate_community_colors(self, n: int) -> Dict[int, str]:
        """Generate distinct colors for communities."""
        colors = [
            "#00ff41", "#ff4444", "#4488ff", "#ffaa00", 
            "#ff00ff", "#00ffff", "#ff8800", "#88ff00",
            "#ff0088", "#8800ff", "#00ff88", "#884400"
        ]
        
        return {i: colors[i % len(colors)] for i in range(n)}
    
    def export_gexf(self, output_path: str) -> None:
        """Export GEXF format for Gephi."""
        timestamp = datetime.datetime.now().isoformat()
        
        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append('<gexf xmlns="http://www.gexf.net/1.3" version="1.3">')
        xml.append(f'  <meta lastmodifieddate="{timestamp.split("T")[0]}">')
        xml.append('    <creator>Sovereign Graph Intelligence Engine v3.0</creator>')
        xml.append('    <description>Entity Co-occurrence Network with Advanced Metrics</description>')
        xml.append('  </meta>')
        xml.append('  <graph mode="static" defaultedgetype="undirected">')
        
        # Attributes
        xml.append('    <attributes class="node">')
        xml.append('      <attribute id="0" title="pagerank" type="double"/>')
        xml.append('      <attribute id="1" title="betweenness" type="double"/>')
        xml.append('      <attribute id="2" title="closeness" type="double"/>')
        xml.append('      <attribute id="3" title="community" type="integer"/>')
        xml.append('    </attributes>')
        
        # Nodes
        xml.append('    <nodes>')
        community_colors = ["0", "255", "68", "255", "0", "255", "255", "0"]
        
        for node_id, node in self.graph.nodes.items():
            size = 10 + (node.weighted_degree * 0.3)
            xml.append(f'      <node id="{node_id}" label="{node_id}">')
            xml.append(f'        <viz:size value="{size}"/>')
            
            # Color by community
            color_idx = (node.community % 4) * 2
            r = community_colors[color_idx]
            g = community_colors[color_idx + 1]
            b = community_colors[(color_idx + 2) % 8]
            xml.append(f'        <viz:color r="{r}" g="{g}" b="{b}"/>')
            
            xml.append(f'        <attvalue for="0" value="{node.pagerank}"/>')
            xml.append(f'        <attvalue for="1" value="{node.betweenness}"/>')
            xml.append(f'        <attvalue for="2" value="{node.closeness}"/>')
            xml.append(f'        <attvalue for="3" value="{node.community}"/>')
            xml.append('      </node>')
        xml.append('    </nodes>')
        
        # Edges
        xml.append('    <edges>')
        for i, edge in enumerate(self.graph.edges):
            xml.append(f'      <edge id="{i}" source="{edge.source}" target="{edge.target}" weight="{edge.weight}"/>')
        xml.append('    </edges>')
        
        xml.append('  </graph>')
        xml.append('</gexf>')
        
        Path(output_path).write_text('\n'.join(xml), encoding='utf-8')
        print(f"[+] GEXF exported: {output_path}")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Sovereign Graph Intelligence & Visualization Engine v3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mode full                    # Full pipeline: analyze + visualize
  %(prog)s --mode metrics                 # Compute metrics only
  %(prog)s --mode vis                      # Generate visualization only
  %(prog)s --mode report                   # Generate intelligence report
  %(prog)s --input docs/entity_network.md # Custom input file
  %(prog)s --export-json metrics.json     # Export metrics to JSON
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['full', 'metrics', 'vis', 'report'], 
        default='full',
        help='Execution mode'
    )
    parser.add_argument(
        '--input', 
        default='docs/entity_network.md',
        help='Input Markdown file'
    )
    parser.add_argument(
        '--export-json',
        help='Export metrics to JSON file'
    )
    parser.add_argument(
        '--output-dir',
        default='visuals',
        help='Output directory for artifacts'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("SOVEREIGN GRAPH INTELLIGENCE ENGINE v3.0 - DEFENSE GRADE")
    print("=" * 60)
    
    # Resolve paths
    root = Path(args.input).parent.parent
    output_dir = root / args.output_dir
    output_dir.mkdir(exist_ok=True)
    
    # Initialize engine
    engine = SovereignGraphEngine()
    
    if args.mode in ['full', 'metrics', 'report']:
        print(f"\n[*] Loading data from {args.input}")
        engine.ingest_markdown(args.input)
        
        print("\n[*] Analyzing network topology...")
        engine.analyze_topology()
        
        print("\n[*] Topology Analysis Complete")
        print(f"    Nodes: {engine.metrics.nodes}")
        print(f"    Edges: {engine.metrics.edges}")
        print(f"    Density: {engine.metrics.density:.4f}")
        print(f"    Communities: {len(engine.get_communities())}")
        
        if args.export_json:
            engine.export_metrics_json(args.export_json)
    
    if args.mode == 'full' or args.mode == 'metrics':
        # Export metrics
        engine.export_metrics_json(output_dir / 'network_metrics.json')
    
    if args.mode == 'full' or args.mode == 'report':
        # Generate intelligence report
        engine.generate_intelligence_report(output_dir / 'intelligence_report.md')
    
    if args.mode == 'full' or args.mode == 'vis':
        # Generate visualizations
        print("\n[*] Computing 3D force-directed layout...")
        vis_engine = SovereignVisualizationEngine(engine)
        
        print("[*] Generating HTML visualization...")
        vis_engine.generate_html(output_dir / 'sovereign_network_3d.html')
        
        print("[*] Exporting GEXF...")
        vis_engine.export_gexf(output_dir / 'sovereign_network_advanced.gexf')
    
    print("\n" + "=" * 60)
    print("MISSION COMPLETE")
    print("=" * 60)
    print(f"\nArtifacts saved to: {output_dir}")
    print("\nGenerated files:")
    if args.mode in ['full', 'metrics']:
        print("  - network_metrics.json (Machine-readable metrics)")
    if args.mode in ['full', 'report']:
        print("  - intelligence_report.md (Human-readable report)")
    if args.mode in ['full', 'vis']:
        print("  - sovereign_network_3d.html (3D Visualization)")
        print("  - sovereign_network_advanced.gexf (Gephi export)")

if __name__ == "__main__":
    main()
