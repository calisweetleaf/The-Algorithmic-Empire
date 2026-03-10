"""
Tool: entity_cleaner.py
========================================
Sovereign Entity Decontamination Pipeline
========================================

Reads per_document_stats.json and produces per_document_stats_clean.json with:
  - Off-topic documents excluded
  - Noise entities removed (generic phrases, metadata artifacts)
  - Entity types classified (PERSON, ORG, PROGRAM, CONCEPT, LOCATION)
  - Aliases merged (deduplicated references)
  - Document-title entities flagged and removed

This stage runs BEFORE synthesis_engine.py in the pipeline.
"""

import json
import argparse
import re
import logging
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Optional, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("entity_cleaner")

# ============================================================================
# CONFIGURATION — NOISE STOPLIST
# ============================================================================
# Generic phrases, metadata artifacts, and fragments that appear as "entities"
# in the NER extraction but carry zero intelligence signal.

NOISE_STOPLIST: Set[str] = {
    # --- Generic / Metadata ---
    "Actions Needed", "Case Study", "Factor Authentication", "Very High",
    "Open Question", "Source Snippet", "Source Snippet Context",
    "Reporting Tool", "Source Documentation", "Source Attribution",
    "Source Contract", "Provided Document", "Provided Documents",
    "Supporting Evidence", "Verification Analysis", "Risk Assessment",
    "Risk Profile", "Plausibility Verdict", "Penetration Confidence",
    "Red Flags", "Threat Category", "Violation Type", "Platform Analysis",
    "Technical Breakdown", "Technology Component", "Technology Validation Matrix",
    "Research Question", "Next Questions", "Official Recommendations",
    "Primary Function", "Operational Significance", "Operational Reality",
    "Strategic Value", "Strategic Function", "Strategic Effect",
    "Speculative Trail", "Strong Insider Claim", "None Found",
    "Oversight Body", "Oversight Mechanism", "Operational Authority",

    # --- Document/UI Artifacts ---
    "Part II", "Part III", "Section II", "Project Instructions",
    "Team Version Guide", "Reddit Context", "Reddit User Guide",
    "User Query", "User Recommendations", "User Showcase",
    "Profile Preferences", "Policies Terms", "Privacy Policy",
    "Usage Limits", "Usage Policies", "Service Credits",
    "Use Custom Instructions", "Use Privacy Policy Other",
    "Protocol File", "Protocol Buffers",

    # --- LLM/Tool Artifacts ---
    "The Custom GPT", "The Files API", "Messages API",
    "Science Latest Advancements GPT", "Our Research Research Index",
    "Research Overview Research Residency", "Super Assistant",
    "Vibe Coding",

    # --- Fragments / Nonsense ---
    "The June", "On September", "Improve Strategic Use",
    "Sending Power Bills Soaring", "Trillion AI Market With",
    "While Anthropic", "While ChatGPT", "Using AI", "Powerful AI",
    "The AI", "Publicly Traded", "Privately Held",
    "Private Tech Company", "Market Survey", "Marketing Posture",

    # --- Style/Routing System Leakage ---
    "Style Chaining", "Style Roulette", "This Style",
    "Slow Path", "Slow Thinking", "System Router", "System Name",
    "Protocol Router", "Protocol Architect", "Routing Entropy",
    "Routing Entropy Regularization", "Step Entropy",
    "Semantic Enhancement", "Semantic Signals",
    "Workspace Executor", "Replanning Tool",

    # --- Cybersecurity-specific (from password leak doc) ---
    "Credential Stuffing", "RedLine Stealer", "Continuous Authentication",
    "Malware Family", "Infostealer Malware", "Password Checkup",
    "Breached Password Protection", "Bot Detection", "Proactive Defense",
    "Business Email Compromise",

    # --- Math/ML theory leakage (from arne_mathematical_foundations, etc.) ---
    "Recursive Stability", "Reflexive Neural Entity", "Dimensional Manifold",
    "Quantum Measurement", "Dependent Computation", "Temporal Entanglement",
    "Dimensional Information Conservation", "Eigenvalue Stability",
    "Observer Complexity", "Spacetime Metric", "Mathematical Foundation",
    "Recursive Risk Score", "Sacred Ratio", "Prospective Folds",
    "Retrospective Folds", "Provenance Trace",

    # --- Generic tech terms that don't carry intelligence signal ---
    "Node Classification", "Random Forest", "Unsupervised Learning",
    "Reinforcement Learning", "Reinforcement Learning Systems",
    "Neural Networks", "Neural Turing Machine", "Sequence Learning",
    "State Space Models", "Memory Networks", "Memory Footprint",
    "Memory Usage", "Sparse Distributed Representations",
    "Relational Model", "Transformational Model", "Term Memory",
    "Python Implementation", "Unseen Data Detection",
    "Tape Paradigm",

    # --- Misc low-signal ---
    "Personal Data", "Public Safety", "Mental Health Care",
    "Workforce Optimization", "Senior Advisor", "Legal Framework",
    "Protection Framework", "Reward Reports", "Recovered Artifact",
    "Target Assessment", "Verified Sourcing", "Magnetic Field",
    "Magnetic System", "Plasma Beta", "Plasma Processes",
    "Thermal Management", "Quantum Dots",
    "REM REST", "SENTARI DICTIONARY",
    "THE VIDEOGRAPHER", "THE WITNESS",
    "TIME AND SPACE MANIPULATION",
}

# ============================================================================
# OFF-TOPIC DOCUMENT EXCLUSION
# ============================================================================
# Documents whose content is not relevant to the core intelligence thesis
# (Thiel/Altman network, defense AI, sovereign tech stack).
# Identified by filename pattern or doc_id.

OFF_TOPIC_PATTERNS: List[str] = [
    r"(?i)password.leak",
    r"(?i)arne_mathematical_foundations",
    r"(?i)blueprint\.html",
    r"(?i)vivaldi.backup",
    r"(?i)ANARASIL_README",
    r"(?i)claude_styles_userguide",
    r"(?i)claude_styles_config",
    r"(?i)claude4_backend_arch",
    r"(?i)claude_gemini_comparison",
    r"(?i)First Dictionary",
    r"(?i)Pre-Transformer Neural Network Library",
]

# ============================================================================
# KNOWN ENTITY LISTS (seed data for type classification)
# ============================================================================

KNOWN_PERSONS: Dict[str, str] = {
    # Key figures — canonical names
    "Peter Thiel": "PERSON",
    "Sam Altman": "PERSON",
    "Sam Bankman": "PERSON",   # Sam Bankman-Fried fragment
    "Palmer Luckey": "PERSON",
    "Trae Stephens": "PERSON",
    "Marc Andreessen": "PERSON",
    "Reid Hoffman": "PERSON",
    "Elon Musk": "PERSON",
    "JD Vance": "PERSON",
    "Xi Jinping": "PERSON",
    "Mira Murati": "PERSON",
    "Ilya Sutskever": "PERSON",
    "Yoshua Bengio": "PERSON",
    "Tom Brown": "PERSON",
    "Paul Graham": "PERSON",
    "Nick Land": "PERSON",
    "Mencius Moldbug": "PERSON",
    "Reed Hastings": "PERSON",
    "Masayoshi Son": "PERSON",
    "Max Altman": "PERSON",
    "Maxwell Ramstead": "PERSON",
    "Robert Bigelow": "PERSON",
    "Salvatore Pais": "PERSON",
    "Nicolas Chaillan": "PERSON",
    "Richard Fontaine": "PERSON",
    "Scott Fouse": "PERSON",
    "Tasha McCauley": "PERSON",
    "Mike Gallagher": "PERSON",
    "Suchir Balaji": "PERSON",
    "Megan Milam": "PERSON",
    "Ranae Jabri": "PERSON",
    "Pinchas Buchris": "PERSON",
    "Poornima Rao": "PERSON",
    "Michael Obadal": "PERSON",
    "Viktor Vekselberg": "PERSON",
    "President Trump": "PERSON",
    "Suman Datta": "PERSON",
    "Tom Brown": "PERSON",
    "Zeju Li": "PERSON",
    "Qiang Xu": "PERSON",
    "Pattisapu Fox": "PERSON",
    "Sheikh Tahnoon": "PERSON",
    "Prime Minister": "PERSON",
}

KNOWN_ORGS: Dict[str, str] = {
    "Anduril Industries": "ORG",
    "Palantir Technologies": "ORG",
    "Palantir AIP": "ORG",
    "Palantir Foundation": "ORG",
    "Palantir Gotham": "ORG",
    "Palantir Metropolis": "ORG",
    "OpenAI LP": "ORG",
    "OPENAI OPCO": "ORG",
    "OpenAI OpCo": "ORG",
    "OpenAI API": "ORG",
    "OpenAI Assistant Swarm": "ORG",
    "OpenAI Startup Fund": "ORG",
    "OpenAI CEO": "ORG",
    "Meta Platforms": "ORG",
    "Scale AI": "ORG",
    "Scale Donovan": "ORG",
    "Shield AI": "ORG",
    "Shield AI Hivemind": "ORG",
    "Overland AI": "ORG",
    "Scout AI": "ORG",
    "Surge AI": "ORG",
    "VERSES AI": "ORG",
    "Noumenal Labs": "ORG",
    "NOUMENA DIGITAL AG": "ORG",
    "NSO Group": "ORG",
    "Northrop Grumman": "ORG",
    "Oracle Corporation": "ORG",
    "SoftBank Group": "ORG",
    "SOMPO Holdings": "ORG",
    "Thrive Capital": "ORG",
    "Valar Ventures": "ORG",
    "Mithril Capital": "ORG",
    "Mithril Capital Management": "ORG",
    "Thiel Capital Management": "ORG",
    "Thiel Foundation": "ORG",
    "Thiel Fellows": "ORG",
    "Thiel Fellowship": "ORG",
    "Open Philanthropy": "ORG",
    "Retro Biosciences": "ORG",
    "Skunk Works": "ORG",
    "Phantom Works": "ORG",
    "Portland General Electric": "ORG",
    "Skydweller Aero": "ORG",
    "Solar Impulse": "ORG",
    "Stargate LLC": "ORG",
    "Elbit Systems": "ORG",
    "Rafael Advanced Defense Systems": "ORG",
    "Milestone Systems": "ORG",
    "PIPER LLP": "ORG",
    "Premier Lexitas": "ORG",
    "Tsinghua University": "ORG",
    "Stanford University": "ORG",
    "Utah Valley University": "ORG",
    "National University": "ORG",
    "Monroe Institute": "ORG",
    "Machine Intelligence Research Institute": "ORG",
    "Seasteading Institute": "ORG",
    "Naval Institute": "ORG",
    "Public Benefit Corporation": "ORG",
    "Broadcasting Board": "ORG",
    "The Economic Times": "ORG",
    "The Guardian": "ORG",
    "The War Zone": "ORG",
    "The Intercept": "ORG",
    "The Information": "ORG",
}

KNOWN_PROGRAMS: Dict[str, str] = {
    "Project Maven": "PROGRAM",
    "Project Stargate": "PROGRAM",
    "Stargate Project": "PROGRAM",
    "Project Strawberry": "PROGRAM",
    "Project Recursion": "PROGRAM",
    "Project Orion": "PROGRAM",
    "Project Neptune": "PROGRAM",
    "Project Horizon": "PROGRAM",
    "Project Lobster": "PROGRAM",
    "Project ORACLE": "PROGRAM",
    "Project Vibe": "PROGRAM",
    "Project Winterhaven": "PROGRAM",
    "Operation Desert Storm": "PROGRAM",
    "Operation Igloo White": "PROGRAM",
    "Operation MHCHAOS": "PROGRAM",
    "Operation Rising Lion": "PROGRAM",
    "Open DAGIR": "PROGRAM",
    "Responsible Scaling Policy": "PROGRAM",
    "NAIRR Pilot": "PROGRAM",
    "National AI Research Resource": "PROGRAM",
    "National Artificial Intelligence Research": "PROGRAM",
    "Strategic Computing Initiative": "PROGRAM",
    "Targeted Neuroplasticity Training": "PROGRAM",
    "Pegasus Spyware": "PROGRAM",
    "Maven Smart System": "PROGRAM",
    "NIPR GPT": "PROGRAM",
    "Popeye Turbo": "PROGRAM",
    "Stone Soup": "PROGRAM",
    "OFFensive Swarm": "PROGRAM",
}

KNOWN_LOCATIONS: Dict[str, str] = {
    "Silicon Valley": "LOCATION",
    "San Francisco": "LOCATION",
    "New York": "LOCATION",
    "Tel Aviv": "LOCATION",
    "New Zealand": "LOCATION",
    "South Africa": "LOCATION",
    "Middle East": "LOCATION",
    "Red Sea": "LOCATION",
    "South China Sea": "LOCATION",
    "Northern Virginia": "LOCATION",
    "Yuma County": "LOCATION",
    "Maricopa County": "LOCATION",
    "United States": "LOCATION",
    "United Kingdom": "LOCATION",
    "United Arab Emirates": "LOCATION",
    "United Nations": "LOCATION",
    "Southwestern United States": "LOCATION",
    "The Dalles": "LOCATION",
    "St Andrews": "LOCATION",
    "West Point": "LOCATION",
    "Stennis International Airport": "LOCATION",
    "Skinwalker Ranch": "LOCATION",
    "South Pars": "LOCATION",
    "Zakarpattia Oblast": "LOCATION",
    "Sdot Micha Airbase": "LOCATION",
    "Yuma Proving Ground": "LOCATION",
}

KNOWN_GOVT_MILITARY: Dict[str, str] = {
    "DARPA": "GOV_MIL",
    "Pentagon CDAO": "GOV_MIL",
    "NSA AI Security Center": "GOV_MIL",
    "National Cyber Security Centre": "GOV_MIL",
    "Senate Armed Services Committee": "GOV_MIL",
    "Senate Intelligence Committee": "GOV_MIL",
    "Space Force": "GOV_MIL",
    "Marine Corps": "GOV_MIL",
    "Pacific Fleet": "GOV_MIL",
    "The Pentagon": "GOV_MIL",
    "The DoD": "GOV_MIL",
    "The CIA": "GOV_MIL",
    "The IDF": "GOV_MIL",
    "The PLA": "GOV_MIL",
    "The White House": "GOV_MIL",
    "White House": "GOV_MIL",
    "The IAEA": "GOV_MIL",
    "The President": "GOV_MIL",
    "UK MOD": "GOV_MIL",
    "UK Ministry": "GOV_MIL",
    "UN Security Council": "GOV_MIL",
    "UN Charter": "GOV_MIL",
    "PLA Daily": "GOV_MIL",
    "Utah Department": "GOV_MIL",
    "Texas Secretary": "GOV_MIL",
    "The Utah DPS": "GOV_MIL",
    "The Census Bureau": "GOV_MIL",
    "Open Source Center": "GOV_MIL",
}

# ============================================================================
# ALIAS RESOLUTION TABLE
# ============================================================================
# Maps variant names → canonical entity name.
# Document titles that reference a person/org are merged here.

ALIAS_TABLE: Dict[str, str] = {
    # Peter Thiel aliases
    "Thiel Nexus": "Peter Thiel",
    "Theils Covert Ops": "Peter Thiel",
    "Thiel Capital Management": "Peter Thiel",
    "Thiel Foundation": "Peter Thiel",

    # Sam Altman aliases
    "Altmans Hidden Latus": "Sam Altman",
    "Altman Nexus": "Sam Altman",
    "Altman Control": "Sam Altman",
    "Altmans Influence": "Sam Altman",
    "OpenAI CEO": "Sam Altman",

    # Org aliases
    "OPENAI OPCO": "OpenAI LP",
    "OpenAI OpCo": "OpenAI LP",
    "Mithril Capital Management": "Mithril Capital",
    "Stargate Project": "Project Stargate",
    "Stargate LLC": "Project Stargate",
    "The Stargate": "Project Stargate",

    # Document-title entities that should map to concepts
    "Opaque Empire": "Sovereign Synthetic Empire",
    "The Sovereign Individual": "Sovereign Ideology",

    # Weapon system aliases
    "Shield AI Hivemind": "Shield AI",
    "Palantir AIP": "Palantir Technologies",
    "Palantir Gotham": "Palantir Technologies",
    "Palantir Metropolis": "Palantir Technologies",
    "Palantir Foundation": "Palantir Technologies",
    "Scale Donovan": "Scale AI",

    # Article fragments and partial references
    "The Epstein": "Epstein Network",
    "The Israeli": "Israel Defense",
    "The Assassination": "Assassination Event",
    "Roth IRA": "Financial Vehicle",
    "Term Benefit Trust": "Financial Vehicle",

    # Military system merges
    "USS Nimitz": "Nimitz Encounter",
    "The USS Princeton": "Nimitz Encounter",
    "Tic Tac": "Nimitz Encounter",
    "Tic Tac AAV": "Nimitz Encounter",
}

# ============================================================================
# ENTITY TYPE CLASSIFICATION PATTERNS
# ============================================================================
# Regex patterns for heuristic classification of unknown entities.

TYPE_PATTERNS: List[Tuple[str, str]] = [
    (r"^(Project|Operation|Program)\s", "PROGRAM"),
    (r"\b(Industries|Corp|Inc|LLC|Ltd|Group|Holdings|Technologies|Systems|Labs)\b", "ORG"),
    (r"\b(Institute|University|Foundation|Academy|Centre|Center)\b", "ORG"),
    (r"\b(Capital|Ventures|Fund|Partners)\b", "ORG"),
    (r"\b(Initiative|Strategy|Campaign|Mission|Protocol)\b", "PROGRAM"),
    (r"(^The\s\w+$)", "CONCEPT"),  # "The Gospel", "The Cathedral", etc.
    (r"\b(County|Oblast|City|Airbase|Airport|Base|Sea|Ocean)\b", "LOCATION"),
    (r"^(AI|UAV|UAS|ISR|RF|SIGINT)\s", "CONCEPT"),
]


def is_off_topic(doc: Dict[str, Any]) -> bool:
    """Check if a document should be excluded from the intelligence network."""
    fname = doc.get("filename", "")
    for pattern in OFF_TOPIC_PATTERNS:
        if re.search(pattern, fname):
            return True
    return False


def is_noise(entity: str) -> bool:
    """Check if an entity is in the noise stoplist."""
    return entity in NOISE_STOPLIST


def resolve_alias(entity: str) -> str:
    """Resolve an entity alias to its canonical name."""
    return ALIAS_TABLE.get(entity, entity)


def classify_entity(entity: str) -> str:
    """
    Classify an entity into a type.
    Priority: known lists → pattern matching → default CONCEPT.
    """
    if entity in KNOWN_PERSONS:
        return "PERSON"
    if entity in KNOWN_ORGS:
        return "ORG"
    if entity in KNOWN_PROGRAMS:
        return "PROGRAM"
    if entity in KNOWN_LOCATIONS:
        return "LOCATION"
    if entity in KNOWN_GOVT_MILITARY:
        return "GOV_MIL"

    # Pattern-based heuristic
    for pattern, etype in TYPE_PATTERNS:
        if re.search(pattern, entity):
            return etype

    return "CONCEPT"


def is_doc_title_entity(entity: str, all_filenames: Set[str]) -> bool:
    """
    Check if an entity is actually a document title leaking into entities.
    Uses fuzzy matching: strips common suffixes and checks containment.
    """
    entity_lower = entity.lower().replace(" ", "").replace("_", "")
    for fname in all_filenames:
        # Strip extension and normalize
        stem = Path(fname).stem.lower().replace(" ", "").replace("_", "").replace("-", "")
        if len(entity_lower) < 5:
            continue
        # Check if entity closely matches a document filename
        if entity_lower in stem or stem in entity_lower:
            # Only flag if match is strong (>60% of characters overlap)
            shorter = min(len(entity_lower), len(stem))
            if shorter >= 5 and (entity_lower[:shorter] == stem[:shorter]):
                return True
    return False


def clean_entities(
    stats: List[Dict[str, Any]],
    verbose: bool = False
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Main cleaning pipeline. Returns (cleaned_stats, cleaning_report).
    """
    # Collect all filenames for doc-title dedup
    all_filenames = {doc.get("filename", "") for doc in stats}

    # Tracking counters for the report
    docs_excluded = 0
    entities_removed_noise = 0
    entities_removed_doctitle = 0
    entities_aliased = 0
    entity_type_counts: Counter = Counter()
    total_entities_before = 0
    total_entities_after = 0

    cleaned_stats: List[Dict[str, Any]] = []

    for doc in stats:
        # --- Step 1: Exclude off-topic documents ---
        if is_off_topic(doc):
            docs_excluded += 1
            if verbose:
                log.info(f"EXCLUDED doc: {doc.get('doc_id')} ({doc.get('filename', '')[:60]})")
            continue

        raw_names = doc.get("major_names", [])
        total_entities_before += len(raw_names)

        cleaned_names: List[str] = []
        entity_types: Dict[str, str] = {}
        seen: Set[str] = set()  # Deduplicate within a document

        for name in raw_names:
            if not name or len(name) <= 2:
                continue

            # --- Step 2: Remove noise entities ---
            if is_noise(name):
                entities_removed_noise += 1
                if verbose:
                    log.debug(f"  NOISE: '{name}' in {doc.get('doc_id')}")
                continue

            # --- Step 3: Resolve aliases ---
            canonical = resolve_alias(name)
            if canonical != name:
                entities_aliased += 1
                if verbose:
                    log.debug(f"  ALIAS: '{name}' -> '{canonical}' in {doc.get('doc_id')}")

            # --- Step 4: Check doc-title leakage ---
            if is_doc_title_entity(canonical, all_filenames):
                # Only remove if it's NOT also a known entity
                if canonical not in KNOWN_PERSONS and canonical not in KNOWN_ORGS:
                    entities_removed_doctitle += 1
                    if verbose:
                        log.debug(f"  DOCTITLE: '{canonical}' in {doc.get('doc_id')}")
                    continue

            # --- Step 5: Classify type ---
            etype = classify_entity(canonical)
            entity_type_counts[etype] += 1

            # Deduplicate
            if canonical not in seen:
                seen.add(canonical)
                cleaned_names.append(canonical)
                entity_types[canonical] = etype

        total_entities_after += len(cleaned_names)

        # Build cleaned document record
        cleaned_doc = dict(doc)
        cleaned_doc["major_names"] = cleaned_names
        cleaned_doc["entity_types"] = entity_types
        cleaned_doc["entities_original_count"] = len(raw_names)
        cleaned_stats.append(cleaned_doc)

    # Build cleaning report
    report = {
        "pipeline": "entity_cleaner_v1",
        "docs_input": len(stats),
        "docs_output": len(cleaned_stats),
        "docs_excluded": docs_excluded,
        "total_entities_before": total_entities_before,
        "total_entities_after": total_entities_after,
        "entities_removed_noise": entities_removed_noise,
        "entities_removed_doctitle": entities_removed_doctitle,
        "entities_aliased": entities_aliased,
        "entity_type_distribution": dict(entity_type_counts),
        "noise_stoplist_size": len(NOISE_STOPLIST),
        "alias_table_size": len(ALIAS_TABLE),
    }

    return cleaned_stats, report


def detect_duplicate_docs(stats: List[Dict[str, Any]]) -> List[Tuple[str, str, str]]:
    """
    Detect duplicate documents by filename.
    Returns list of (doc_id, filename, duplicate_of_doc_id).
    """
    seen: Dict[str, str] = {}  # filename -> first doc_id
    duplicates: List[Tuple[str, str, str]] = []

    for doc in stats:
        fname = doc.get("filename", "")
        did = doc.get("doc_id", "")
        if fname in seen:
            duplicates.append((did, fname, seen[fname]))
        else:
            seen[fname] = did

    return duplicates


def main():
    parser = argparse.ArgumentParser(
        description="Sovereign Entity Decontamination Pipeline"
    )
    parser.add_argument(
        "--stats",
        default="docs/per_document_stats.json",
        help="Input stats JSON path"
    )
    parser.add_argument(
        "--out",
        default="docs/per_document_stats_clean.json",
        help="Output cleaned stats JSON path"
    )
    parser.add_argument(
        "--report",
        default="docs/cleaning_report.json",
        help="Output cleaning report JSON path"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--detect-dupes",
        action="store_true",
        help="Detect and log duplicate documents"
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    stats_path = Path(args.stats)
    if not stats_path.exists():
        log.error(f"Stats file not found: {stats_path}")
        return

    with open(stats_path, "r", encoding="utf-8") as f:
        stats = json.load(f)

    log.info(f"Loaded {len(stats)} documents from {stats_path}")

    # --- Detect duplicates ---
    if args.detect_dupes:
        dupes = detect_duplicate_docs(stats)
        if dupes:
            log.warning(f"Found {len(dupes)} duplicate documents:")
            for did, fname, orig_did in dupes:
                log.warning(f"  {did} duplicates {orig_did}: {fname[:60]}")
        else:
            log.info("No duplicate documents found.")

    # --- Run cleaning pipeline ---
    cleaned_stats, report = clean_entities(stats, verbose=args.verbose)

    # --- Save outputs ---
    out_path = Path(args.out)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_stats, f, indent=2, ensure_ascii=False)
    log.info(f"Cleaned stats saved to {out_path}")

    report_path = Path(args.report)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    log.info(f"Cleaning report saved to {report_path}")

    # --- Summary ---
    log.info("=" * 60)
    log.info("ENTITY CLEANING REPORT")
    log.info("=" * 60)
    log.info(f"Documents: {report['docs_input']} -> {report['docs_output']} ({report['docs_excluded']} excluded)")
    log.info(f"Entities:  {report['total_entities_before']} -> {report['total_entities_after']}")
    log.info(f"  Noise removed:     {report['entities_removed_noise']}")
    log.info(f"  Doc-title removed: {report['entities_removed_doctitle']}")
    log.info(f"  Aliases merged:    {report['entities_aliased']}")
    log.info(f"Entity type distribution:")
    for etype, count in sorted(report['entity_type_distribution'].items()):
        log.info(f"  {etype}: {count}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
