#!/usr/bin/env python3
"""
SSDS OSINT Module - Sovereign Intelligence Gathering System
==========================================================
Production-grade Open Source Intelligence gathering with obfuscated
browser automation, local network analysis, and threat intelligence
aggregation. ROE Level 1 OBSERVE compliance.
"""

import asyncio
import aiohttp
import sqlite3
import json
import logging
import hashlib
import hmac
import time
import threading
import random
import os
import re
import base64
import gzip
from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from urllib.parse import urlparse, urljoin
import ssl
import certifi

import numpy as np
import onnxruntime as ort
from cryptography.fernet import Fernet
import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.l2 import ARP, Ether
import psutil
import netifaces
import dns.resolver
import whois
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from fake_useragent import UserAgent
import requests_html
from bs4 import BeautifulSoup
import feedparser

logger = logging.getLogger(__name__)


class IntelligenceType(Enum):
    """Types of intelligence gathered"""
    THREAT_INDICATORS = "threat_indicators"
    VULNERABILITY_DATA = "vulnerability_data"
    ATTRIBUTION_INTELLIGENCE = "attribution_intelligence"
    NETWORK_TELEMETRY = "network_telemetry"
    SYSTEM_BEHAVIORAL = "system_behavioral"
    RF_SPECTRUM = "rf_spectrum"
    THREAT_ACTOR_INTELLIGENCE = "threat_actor_intelligence"
    EXPLOIT_INTELLIGENCE = "exploit_intelligence"


class IntelligenceSource(Enum):
    """Sources of intelligence data"""
    BROWSER_AUTOMATION = "browser_automation"
    NETWORK_MONITORING = "network_monitoring"
    SYSTEM_MONITORING = "system_monitoring"
    RF_ANALYSIS = "rf_analysis"
    THREAT_FEEDS = "threat_feeds"
    DARK_WEB = "dark_web"
    SECURITY_FORUMS = "security_forums"
    VULNERABILITY_DATABASES = "vulnerability_databases"


@dataclass
class IntelligenceReport:
    """Structured intelligence report"""
    report_id: str
    intelligence_type: IntelligenceType
    source: IntelligenceSource
    collection_timestamp: datetime
    confidence_score: float
    threat_level: str
    raw_data: Dict[str, Any]
    processed_indicators: List[str]
    attribution_data: Dict[str, Any]
    correlation_markers: List[str]
    actionable_intelligence: List[str]
    metadata: Dict[str, Any]
    encrypted_payload: Optional[bytes] = None


class SovereignDataStore:
    """Encrypted data storage for intelligence"""
    
    def __init__(self, db_path: str, encryption_key: bytes):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.encryption_key = encryption_key
        self.cipher_suite = Fernet(encryption_key)
        self.db_lock = threading.Lock()
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize sovereign intelligence database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                PRAGMA journal_mode=WAL;
                PRAGMA synchronous=NORMAL;
                PRAGMA cache_size=20000;
                PRAGMA temp_store=memory;
                
                CREATE TABLE IF NOT EXISTS intelligence_reports (
                    report_id TEXT PRIMARY KEY,
                    intelligence_type TEXT,
                    source TEXT,
                    collection_timestamp TEXT,
                    confidence_score REAL,
                    threat_level TEXT,
                    raw_data_hash TEXT,
                    processed_indicators TEXT,
                    attribution_data TEXT,
                    correlation_markers TEXT,
                    actionable_intelligence TEXT,
                    metadata TEXT,
                    encrypted_payload BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS threat_indicators (
                    indicator_id TEXT PRIMARY KEY,
                    indicator_type TEXT,
                    indicator_value TEXT,
                    confidence_score REAL,
                    first_seen TEXT,
                    last_seen TEXT,
                    source_reports TEXT,
                    threat_level TEXT,
                    encrypted_context BLOB
                );
                
                CREATE TABLE IF NOT EXISTS attribution_data (
                    actor_id TEXT PRIMARY KEY,
                    actor_name TEXT,
                    actor_type TEXT,
                    confidence_score REAL,
                    ttps TEXT,
                    infrastructure TEXT,
                    campaigns TEXT,
                    last_activity TEXT,
                    encrypted_profile BLOB
                );
                
                CREATE TABLE IF NOT EXISTS network_telemetry (
                    telemetry_id TEXT PRIMARY KEY,
                    source_ip TEXT,
                    destination_ip TEXT,
                    protocol TEXT,
                    port INTEGER,
                    packet_size INTEGER,
                    flags TEXT,
                    payload_hash TEXT,
                    timestamp TEXT,
                    anomaly_score REAL,
                    encrypted_payload BLOB
                );
                
                CREATE TABLE IF NOT EXISTS system_metrics (
                    metric_id TEXT PRIMARY KEY,
                    metric_type TEXT,
                    metric_value REAL,
                    baseline_deviation REAL,
                    timestamp TEXT,
                    process_context TEXT,
                    anomaly_indicators TEXT,
                    encrypted_details BLOB
                );
                
                CREATE TABLE IF NOT EXISTS collection_status (
                    collector_id TEXT PRIMARY KEY,
                    collector_type TEXT,
                    status TEXT,
                    last_collection TEXT,
                    collection_count INTEGER,
                    error_count INTEGER,
                    performance_metrics TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_intelligence_timestamp 
                ON intelligence_reports(collection_timestamp);
                
                CREATE INDEX IF NOT EXISTS idx_intelligence_type 
                ON intelligence_reports(intelligence_type);
                
                CREATE INDEX IF NOT EXISTS idx_threat_indicators_type 
                ON threat_indicators(indicator_type);
                
                CREATE INDEX IF NOT EXISTS idx_network_timestamp 
                ON network_telemetry(timestamp);
                
                CREATE INDEX IF NOT EXISTS idx_system_timestamp 
                ON system_metrics(timestamp);
            ''')
    
    def store_intelligence_report(self, report: IntelligenceReport):
        """Store encrypted intelligence report"""
        with self.db_lock:
            # Encrypt sensitive payload
            encrypted_payload = self.cipher_suite.encrypt(
                json.dumps(report.raw_data).encode()
            )
            
            # Generate hash for deduplication
            raw_data_hash = hashlib.sha256(
                json.dumps(report.raw_data, sort_keys=True).encode()
            ).hexdigest()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO intelligence_reports VALUES 
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    report.report_id,
                    report.intelligence_type.value,
                    report.source.value,
                    report.collection_timestamp.isoformat(),
                    report.confidence_score,
                    report.threat_level,
                    raw_data_hash,
                    json.dumps(report.processed_indicators),
                    json.dumps(report.attribution_data),
                    json.dumps(report.correlation_markers),
                    json.dumps(report.actionable_intelligence),
                    json.dumps(report.metadata),
                    encrypted_payload
                ))
    
    def store_threat_indicator(self, indicator_type: str, indicator_value: str,
                             confidence: float, threat_level: str, context: Dict[str, Any]):
        """Store threat indicator with encryption"""
        with self.db_lock:
            indicator_id = f"{indicator_type}_{hashlib.md5(indicator_value.encode()).hexdigest()}"
            encrypted_context = self.cipher_suite.encrypt(json.dumps(context).encode())
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO threat_indicators VALUES 
                    (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    indicator_id,
                    indicator_type,
                    indicator_value,
                    confidence,
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat(),
                    json.dumps([]),
                    threat_level,
                    encrypted_context
                ))
    
    def get_recent_intelligence(self, hours: int = 24, 
                              intelligence_type: Optional[IntelligenceType] = None) -> List[IntelligenceReport]:
        """Retrieve recent intelligence reports"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        reports = []
        
        query = '''
            SELECT * FROM intelligence_reports 
            WHERE collection_timestamp > ?
        '''
        params = [cutoff_time.isoformat()]
        
        if intelligence_type:
            query += ' AND intelligence_type = ?'
            params.append(intelligence_type.value)
        
        query += ' ORDER BY collection_timestamp DESC'
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            
            for row in cursor.fetchall():
                try:
                    # Decrypt payload
                    decrypted_data = json.loads(
                        self.cipher_suite.decrypt(row[12]).decode()
                    )
                    
                    report = IntelligenceReport(
                        report_id=row[0],
                        intelligence_type=IntelligenceType(row[1]),
                        source=IntelligenceSource(row[2]),
                        collection_timestamp=datetime.fromisoformat(row[3]),
                        confidence_score=row[4],
                        threat_level=row[5],
                        raw_data=decrypted_data,
                        processed_indicators=json.loads(row[7]),
                        attribution_data=json.loads(row[8]),
                        correlation_markers=json.loads(row[9]),
                        actionable_intelligence=json.loads(row[10]),
                        metadata=json.loads(row[11])
                    )
                    reports.append(report)
                except Exception as e:
                    logger.error(f"Failed to decrypt intelligence report {row[0]}: {e}")
        
        return reports


class ObfuscatedBrowserEngine:
    """Advanced browser automation with attribution masking"""
    
    def __init__(self, data_store: SovereignDataStore):
        self.data_store = data_store
        self.user_agent_rotator = UserAgent()
        self.proxy_chains = self._initialize_proxy_chains()
        self.browser_profiles = self._generate_browser_profiles()
        self.active_sessions = {}
        self.collection_targets = self._load_collection_targets()
        self.request_delays = defaultdict(lambda: random.uniform(2.0, 8.0))
    
    def _initialize_proxy_chains(self) -> List[Dict[str, str]]:
        """Initialize proxy rotation for attribution masking"""
        # Production deployment would load from secure configuration
        return [
            {'http': 'socks5://127.0.0.1:9050', 'https': 'socks5://127.0.0.1:9050'},  # Tor
            # Additional proxy configurations loaded from secure storage
        ]
    
    def _generate_browser_profiles(self) -> List[Dict[str, Any]]:
        """Generate diverse browser fingerprint profiles"""
        profiles = []
        
        # Desktop profiles
        desktop_resolutions = [
            (1920, 1080), (1366, 768), (1440, 900), (1536, 864), (1280, 720)
        ]
        
        for resolution in desktop_resolutions:
            profile = {
                'user_agent': self.user_agent_rotator.chrome,
                'screen_resolution': resolution,
                'viewport_size': (resolution[0] - 20, resolution[1] - 100),
                'platform': random.choice(['Windows', 'Linux', 'macOS']),
                'languages': random.choice([['en-US'], ['en-GB'], ['en-CA']]),
                'timezone': random.choice(['America/New_York', 'Europe/London', 'America/Los_Angeles']),
                'webgl_vendor': random.choice(['Google Inc.', 'Mozilla', 'Apple Inc.']),
                'webgl_renderer': random.choice(['Chrome', 'Firefox', 'Safari'])
            }
            profiles.append(profile)
        
        return profiles
    
    def _load_collection_targets(self) -> Dict[str, Dict[str, Any]]:
        """Load intelligence collection targets"""
        return {
            'threat_feeds': {
                'sources': [
                    'https://feeds.feedburner.com/eset/blog',
                    'https://blog.malwarebytes.com/feed/',
                    'https://krebsonsecurity.com/feed/',
                    'https://threatpost.com/feed/',
                    'https://www.darkreading.com/rss_simple.asp',
                    'https://www.schneier.com/blog/atom.xml'
                ],
                'collection_interval': 1800,  # 30 minutes
                'processing_depth': 'full'
            },
            'vulnerability_databases': {
                'sources': [
                    'https://nvd.nist.gov/feeds/json/cve/1.1/',
                    'https://cve.mitre.org/data/downloads/',
                    'https://www.exploit-db.com/rss.xml'
                ],
                'collection_interval': 3600,  # 1 hour
                'processing_depth': 'metadata'
            },
            'security_forums': {
                'sources': [
                    'https://www.reddit.com/r/netsec/.rss',
                    'https://www.reddit.com/r/cybersecurity/.rss',
                    'https://forums.malwarebytes.com/forum/2-malware-removal-help/'
                ],
                'collection_interval': 7200,  # 2 hours
                'processing_depth': 'titles_and_links'
            },
            'threat_intelligence': {
                'sources': [
                    'https://otx.alienvault.com/api/v1/pulses/subscribed',
                    'https://www.circl.lu/doc/misp/feed-osint/',
                    'https://github.com/stamparm/ipsum'
                ],
                'collection_interval': 3600,  # 1 hour
                'processing_depth': 'full'
            }
        }
    
    async def start_collection_engines(self):
        """Start all browser-based collection engines"""
        logger.info("Starting obfuscated browser intelligence collection")
        
        collection_tasks = []
        
        for target_type, config in self.collection_targets.items():
            task = asyncio.create_task(
                self._collection_engine(target_type, config)
            )
            collection_tasks.append(task)
        
        # Additional specialized collection tasks
        collection_tasks.extend([
            asyncio.create_task(self._threat_actor_monitoring()),
            asyncio.create_task(self._vulnerability_monitoring()),
            asyncio.create_task(self._exploit_marketplace_monitoring())
        ])
        
        await asyncio.gather(*collection_tasks, return_exceptions=True)
    
    async def _collection_engine(self, target_type: str, config: Dict[str, Any]):
        """Generic collection engine for different target types"""
        while True:
            try:
                logger.info(f"Starting collection cycle for {target_type}")
                
                # Rotate browser profile
                profile = random.choice(self.browser_profiles)
                
                # Collect from all sources in target type
                for source_url in config['sources']:
                    try:
                        intelligence_data = await self._collect_from_source(
                            source_url, profile, config['processing_depth']
                        )
                        
                        if intelligence_data:
                            report = await self._process_collected_data(
                                intelligence_data, target_type, source_url
                            )
                            
                            if report:
                                self.data_store.store_intelligence_report(report)
                                logger.info(f"Stored intelligence report: {report.report_id}")
                        
                        # Randomized delay between sources
                        await asyncio.sleep(random.uniform(5.0, 15.0))
                        
                    except Exception as e:
                        logger.error(f"Collection failed for {source_url}: {e}")
                
                # Wait for next collection cycle
                await asyncio.sleep(config['collection_interval'])
                
            except Exception as e:
                logger.error(f"Collection engine error for {target_type}: {e}")
                await asyncio.sleep(300)  # 5 minute error backoff
    
    async def _collect_from_source(self, source_url: str, profile: Dict[str, Any], 
                                 processing_depth: str) -> Optional[Dict[str, Any]]:
        """Collect intelligence from specific source with obfuscation"""
        try:
            # Setup obfuscated session
            session = await self._create_obfuscated_session(profile)
            
            # Apply request delay
            domain = urlparse(source_url).netloc
            await asyncio.sleep(self.request_delays[domain])
            
            # Collect data based on source type
            if source_url.endswith('.rss') or source_url.endswith('.xml'):
                data = await self._collect_rss_feed(session, source_url)
            elif 'reddit.com' in source_url:
                data = await self._collect_reddit_data(session, source_url)
            elif 'github.com' in source_url:
                data = await self._collect_github_data(session, source_url)
            else:
                data = await self._collect_web_content(session, source_url, processing_depth)
            
            await session.close()
            
            # Update request delay
            self.request_delays[domain] = random.uniform(
                max(2.0, self.request_delays[domain] * 0.9),
                self.request_delays[domain] * 1.1
            )
            
            return data
            
        except Exception as e:
            logger.error(f"Collection from {source_url} failed: {e}")
            return None
    
    async def _create_obfuscated_session(self, profile: Dict[str, Any]) -> aiohttp.ClientSession:
        """Create obfuscated HTTP session with rotating attributes"""
        headers = {
            'User-Agent': profile['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': ','.join(profile['languages']),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Randomize additional headers
        if random.random() > 0.5:
            headers['Cache-Control'] = 'max-age=0'
        
        if random.random() > 0.3:
            headers['Sec-Fetch-Dest'] = random.choice(['document', 'empty'])
            headers['Sec-Fetch-Mode'] = random.choice(['navigate', 'cors'])
            headers['Sec-Fetch-Site'] = random.choice(['none', 'same-origin'])
        
        # SSL context
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create connector with proxy if available
        connector_kwargs = {
            'ssl': ssl_context,
            'limit': 10,
            'limit_per_host': 2,
            'enable_cleanup_closed': True
        }
        
        if self.proxy_chains:
            proxy = random.choice(self.proxy_chains)
            connector = aiohttp.ProxyConnector.from_url(
                proxy.get('http', proxy.get('https')), **connector_kwargs
            )
        else:
            connector = aiohttp.TCPConnector(**connector_kwargs)
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        return aiohttp.ClientSession(
            headers=headers,
            connector=connector,
            timeout=timeout
        )
    
    async def _collect_rss_feed(self, session: aiohttp.ClientSession, 
                              feed_url: str) -> Dict[str, Any]:
        """Collect and parse RSS/Atom feeds"""
        try:
            async with session.get(feed_url) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    entries = []
                    for entry in feed.entries[:20]:  # Limit to recent entries
                        entries.append({
                            'title': entry.get('title', ''),
                            'link': entry.get('link', ''),
                            'summary': entry.get('summary', ''),
                            'published': entry.get('published', ''),
                            'tags': [tag.term for tag in entry.get('tags', [])]
                        })
                    
                    return {
                        'feed_title': feed.feed.get('title', ''),
                        'feed_url': feed_url,
                        'entries': entries,
                        'collection_timestamp': datetime.utcnow().isoformat()
                    }
        except Exception as e:
            logger.error(f"RSS collection failed for {feed_url}: {e}")
        
        return {}
    
    async def _collect_reddit_data(self, session: aiohttp.ClientSession, 
                                 reddit_url: str) -> Dict[str, Any]:
        """Collect Reddit security discussions"""
        try:
            async with session.get(reddit_url) as response:
                if response.status == 200:
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    posts = []
                    for entry in feed.entries[:15]:
                        posts.append({
                            'title': entry.get('title', ''),
                            'link': entry.get('link', ''),
                            'author': entry.get('author', ''),
                            'published': entry.get('published', ''),
                            'content': entry.get('content', [{}])[0].get('value', '')
                        })
                    
                    return {
                        'source': 'reddit',
                        'subreddit': reddit_url.split('/')[-2],
                        'posts': posts,
                        'collection_timestamp': datetime.utcnow().isoformat()
                    }
        except Exception as e:
            logger.error(f"Reddit collection failed for {reddit_url}: {e}")
        
        return {}
    
    async def _collect_github_data(self, session: aiohttp.ClientSession, 
                                 github_url: str) -> Dict[str, Any]:
        """Collect GitHub security repositories and threat intelligence"""
        try:
            # Parse GitHub URL to determine collection strategy
            if 'github.com' in github_url:
                # Extract repository information
                parts = urlparse(github_url).path.strip('/').split('/')
                if len(parts) >= 2:
                    owner, repo = parts[0], parts[1]
                    
                    # Collect repository metadata
                    api_url = f"https://api.github.com/repos/{owner}/{repo}"
                    async with session.get(api_url) as response:
                        if response.status == 200:
                            repo_data = await response.json()
                            
                            # Collect recent commits
                            commits_url = f"https://api.github.com/repos/{owner}/{repo}/commits"
                            async with session.get(commits_url) as commits_response:
                                commits_data = []
                                if commits_response.status == 200:
                                    commits_data = await commits_response.json()
                            
                            return {
                                'source': 'github',
                                'repository': f"{owner}/{repo}",
                                'metadata': repo_data,
                                'recent_commits': commits_data[:10],
                                'collection_timestamp': datetime.utcnow().isoformat()
                            }
        except Exception as e:
            logger.error(f"GitHub collection failed for {github_url}: {e}")
        
        return {}
    
    async def _collect_web_content(self, session: aiohttp.ClientSession, 
                                 url: str, processing_depth: str) -> Dict[str, Any]:
        """Collect general web content with depth control"""
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Extract based on processing depth
                    if processing_depth == 'titles_and_links':
                        data = {
                            'title': soup.title.string if soup.title else '',
                            'links': [a.get('href') for a in soup.find_all('a', href=True)[:50]]
                        }
                    elif processing_depth == 'metadata':
                        data = {
                            'title': soup.title.string if soup.title else '',
                            'meta_description': '',
                            'meta_keywords': '',
                            'headings': [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])[:20]]
                        }
                        
                        # Extract meta tags
                        for meta in soup.find_all('meta'):
                            name = meta.get('name', '').lower()
                            if name == 'description':
                                data['meta_description'] = meta.get('content', '')
                            elif name == 'keywords':
                                data['meta_keywords'] = meta.get('content', '')
                    
                    else:  # full processing
                        data = {
                            'title': soup.title.string if soup.title else '',
                            'text_content': soup.get_text()[:10000],  # Limit content size
                            'links': [a.get('href') for a in soup.find_all('a', href=True)[:100]],
                            'images': [img.get('src') for img in soup.find_all('img', src=True)[:20]],
                            'headings': [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])]
                        }
                    
                    data.update({
                        'url': url,
                        'status_code': response.status,
                        'collection_timestamp': datetime.utcnow().isoformat()
                    })
                    
                    return data
                    
        except Exception as e:
            logger.error(f"Web content collection failed for {url}: {e}")
        
        return {}
    
    async def _process_collected_data(self, raw_data: Dict[str, Any], 
                                    target_type: str, source_url: str) -> Optional[IntelligenceReport]:
        """Process raw collected data into structured intelligence report"""
        try:
            report_id = f"osint_{int(time.time())}_{hashlib.md5(str(raw_data).encode()).hexdigest()[:8]}"
            
            # Extract threat indicators
            indicators = await self._extract_threat_indicators(raw_data)
            
            # Determine intelligence type
            intel_type = self._classify_intelligence_type(target_type, raw_data)
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(raw_data, indicators)
            
            # Extract attribution data
            attribution = await self._extract_attribution_data(raw_data)
            
            # Generate actionable intelligence
            actionable = await self._generate_actionable_intelligence(raw_data, indicators)
            
            # Determine threat level
            threat_level = self._assess_threat_level(indicators, confidence)
            
            report = IntelligenceReport(
                report_id=report_id,
                intelligence_type=intel_type,
                source=IntelligenceSource.BROWSER_AUTOMATION,
                collection_timestamp=datetime.utcnow(),
                confidence_score=confidence,
                threat_level=threat_level,
                raw_data=raw_data,
                processed_indicators=indicators,
                attribution_data=attribution,
                correlation_markers=self._extract_correlation_markers(raw_data),
                actionable_intelligence=actionable,
                metadata={
                    'target_type': target_type,
                    'source_url': source_url,
                    'processing_timestamp': datetime.utcnow().isoformat(),
                    'data_size': len(str(raw_data))
                }
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            return None
    
    async def _extract_threat_indicators(self, data: Dict[str, Any]) -> List[str]:
        """Extract threat indicators from collected data"""
        indicators = []
        
        # Text content to analyze
        text_content = ""
        if 'text_content' in data:
            text_content = data['text_content']
        elif 'entries' in data:
            text_content = ' '.join([
                f"{entry.get('title', '')} {entry.get('summary', '')}"
                for entry in data['entries']
            ])
        elif 'posts' in data:
            text_content = ' '.join([
                f"{post.get('title', '')} {post.get('content', '')}"
                for post in data['posts']
            ])
        
        # IP address indicators
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ip_addresses = re.findall(ip_pattern, text_content)
        indicators.extend([f"ip:{ip}" for ip in ip_addresses])
        
        # Domain indicators
        domain_pattern = r'\b[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+\b'
        domains = re.findall(domain_pattern, text_content)
        indicators.extend([f"domain:{domain[0]}{domain[1]}" for domain in domains])
        
        # Hash indicators (MD5, SHA1, SHA256)
        hash_patterns = [
            (r'\b[a-fA-F0-9]{32}\b', 'md5'),
            (r'\b[a-fA-F0-9]{40}\b', 'sha1'),
            (r'\b[a-fA-F0-9]{64}\b', 'sha256')
        ]
        
        for pattern, hash_type in hash_patterns:
            hashes = re.findall(pattern, text_content)
            indicators.extend([f"{hash_type}:{h}" for h in hashes])
        
        # CVE indicators
        cve_pattern = r'CVE-\d{4}-\d{4,7}'
        cves = re.findall(cve_pattern, text_content, re.IGNORECASE)
        indicators.extend([f"cve:{cve}" for cve in cves])
        
        # URL indicators
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text_content)
        indicators.extend([f"url:{url}" for url in urls])
        
        # Malware family indicators
        malware_keywords = [
            'ransomware', 'trojan', 'backdoor', 'rootkit', 'botnet',
            'spyware', 'adware', 'keylogger', 'worm', 'virus'
        ]
        
        for keyword in malware_keywords:
            if keyword.lower() in text_content.lower():
                indicators.append(f"malware_family:{keyword}")
        
        return list(set(indicators))  # Remove duplicates
    
    def _classify_intelligence_type(self, target_type: str, data: Dict[str, Any]) -> IntelligenceType:
        """Classify the type of intelligence based on content"""
        if target_type == 'vulnerability_databases':
            return IntelligenceType.VULNERABILITY_DATA
        elif target_type == 'threat_intelligence':
            return IntelligenceType.THREAT_INDICATORS
        elif 'actor' in str(data).lower() or 'apt' in str(data).lower():
            return IntelligenceType.THREAT_ACTOR_INTELLIGENCE
        elif 'exploit' in str(data).lower() or 'poc' in str(data).lower():
            return IntelligenceType.EXPLOIT_INTELLIGENCE
        else:
            return IntelligenceType.THREAT_INDICATORS
    
    def _calculate_confidence_score(self, data: Dict[str, Any], indicators: List[str]) -> float:
        """Calculate confidence score for collected intelligence"""
        base_confidence = 0.5
        
        # Boost confidence based on source reputation
        source_url = data.get('url', data.get('source_url', ''))
        trusted_sources = [
            'nist.gov', 'mitre.org', 'cert.org', 'us-cert.gov',
            'krebsonsecurity.com', 'schneier.com', 'malwarebytes.com'
        ]
        
        if any(domain in source_url for domain in trusted_sources):
            base_confidence += 0.3
        
        # Boost confidence based on indicator count
        if len(indicators) > 5:
            base_confidence += 0.2
        elif len(indicators) > 2:
            base_confidence += 0.1
        
        # Boost confidence for structured data
        if 'entries' in data or 'posts' in data:
            base_confidence += 0.1
        
        # Boost confidence for recent data
        timestamp_str = data.get('collection_timestamp', '')
        if timestamp_str:
            try:
                collection_time = datetime.fromisoformat(timestamp_str)
                age_hours = (datetime.utcnow() - collection_time).total_seconds() / 3600
                if age_hours < 24:
                    base_confidence += 0.1
            except:
                pass
        
        return min(base_confidence, 1.0)
    
    async def _extract_attribution_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract threat actor attribution data"""
        attribution = {
            'actor_names': [],
            'campaign_names': [],
            'ttps': [],
            'infrastructure': [],
            'confidence': 0.0
        }
        
        # Text content for analysis
        text_content = str(data).lower()
        
        # Known threat actor names
        actor_patterns = [
            r'apt\s*\d+', r'lazarus', r'cozy\s*bear', r'fancy\s*bear',
            r'carbanak', r'fin\d+', r'equation\s*group', r'dark\s*halo'
        ]
        
        for pattern in actor_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            attribution['actor_names'].extend(matches)
        
        # Campaign names
        campaign_patterns = [
            r'operation\s+\w+', r'campaign\s+\w+', r'\w+\s*panda',
            r'\w+\s*bear', r'\w+\s*kitten'
        ]
        
        for pattern in campaign_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            attribution['campaign_names'].extend(matches)
        
        # TTPs (simplified extraction)
        ttp_keywords = [
            'spear phishing', 'watering hole', 'supply chain',
            'lateral movement', 'privilege escalation', 'data exfiltration',
            'command and control', 'persistence mechanism'
        ]
        
        for keyword in ttp_keywords:
            if keyword in text_content:
                attribution['ttps'].append(keyword)
        
        # Calculate attribution confidence
        total_indicators = len(attribution['actor_names']) + len(attribution['campaign_names']) + len(attribution['ttps'])
        attribution['confidence'] = min(total_indicators * 0.2, 1.0)
        
        return attribution
    
    async def _generate_actionable_intelligence(self, data: Dict[str, Any], 
                                              indicators: List[str]) -> List[str]:
        """Generate actionable intelligence recommendations"""
        actionable = []
        
        # IOC-based actions
        if any(indicator.startswith('ip:') for indicator in indicators):
            actionable.append("Block identified IP addresses at network perimeter")
        
        if any(indicator.startswith('domain:') for indicator in indicators):
            actionable.append("Implement DNS blocking for identified malicious domains")
        
        if any(indicator.startswith('url:') for indicator in indicators):
            actionable.append("Add malicious URLs to web filtering blacklist")
        
        if any(indicator.startswith('cve:') for indicator in indicators):
            actionable.append("Prioritize patching for identified CVE vulnerabilities")
        
        # Content-based actions
        text_content = str(data).lower()
        
        if 'ransomware' in text_content:
            actionable.append("Enhance backup verification and offline storage procedures")
            actionable.append("Implement advanced endpoint detection for ransomware behaviors")
        
        if 'phishing' in text_content:
            actionable.append("Increase email security scanning and user awareness training")
        
        if 'zero-day' in text_content or '0-day' in text_content:
            actionable.append("Enable enhanced behavioral detection for unknown threats")
        
        if 'botnet' in text_content:
            actionable.append("Monitor for command and control communication patterns")
        
        return actionable
    
    def _assess_threat_level(self, indicators: List[str], confidence: float) -> str:
        """Assess overall threat level"""
        indicator_count = len(indicators)
        
        # High threat conditions
        if confidence > 0.8 and indicator_count > 10:
            return "CRITICAL"
        elif confidence > 0.7 and indicator_count > 5:
            return "HIGH"
        elif confidence > 0.5 and indicator_count > 2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _extract_correlation_markers(self, data: Dict[str, Any]) -> List[str]:
        """Extract markers for threat correlation"""
        markers = []
        
        # Extract timestamps
        if 'collection_timestamp' in data:
            markers.append(f"timestamp:{data['collection_timestamp'][:10]}")  # Date only
        
        # Extract source markers
        if 'url' in data:
            domain = urlparse(data['url']).netloc
            markers.append(f"source_domain:{domain}")
        
        # Extract content markers
        text_content = str(data).lower()
        
        # Malware family markers
        malware_families = ['emotet', 'trickbot', 'ryuk', 'maze', 'revil']
        for family in malware_families:
            if family in text_content:
                markers.append(f"malware_family:{family}")
        
        # Attack vector markers
        attack_vectors = ['email', 'web', 'usb', 'network', 'social']
        for vector in attack_vectors:
            if vector in text_content:
                markers.append(f"attack_vector:{vector}")
        
        return markers
    
    async def _threat_actor_monitoring(self):
        """Specialized threat actor intelligence monitoring"""
        while True:
            try:
                # Monitor threat actor specific sources
                actor_sources = [
                    'https://attack.mitre.org/groups/',
                    'https://malpedia.caad.fkie.fraunhofer.de/actors/',
                    'https://www.crowdstrike.com/blog/category/threat-intel/'
                ]
                
                for source in actor_sources:
                    try:
                        profile = random.choice(self.browser_profiles)
                        session = await self._create_obfuscated_session(profile)
                        
                        data = await self._collect_web_content(source, session, 'metadata')
                        
                        if data:
                            report = await self._process_collected_data(
                                data, 'threat_actor_intelligence', source
                            )
                            
                            if report:
                                self.data_store.store_intelligence_report(report)
                        
                        await session.close()
                        await asyncio.sleep(random.uniform(10.0, 30.0))
                        
                    except Exception as e:
                        logger.error(f"Threat actor monitoring failed for {source}: {e}")
                
                await asyncio.sleep(7200)  # 2 hours
                
            except Exception as e:
                logger.error(f"Threat actor monitoring error: {e}")
                await asyncio.sleep(600)
    
    async def _vulnerability_monitoring(self):
        """Specialized vulnerability intelligence monitoring"""
        while True:
            try:
                # Monitor vulnerability-specific sources
                vuln_sources = [
                    'https://www.exploit-db.com/rss.xml',
                    'https://packetstormsecurity.com/files/tags/exploit/',
                    'https://seclists.org/fulldisclosure/'
                ]
                
                for source in vuln_sources:
                    try:
                        profile = random.choice(self.browser_profiles)
                        session = await self._create_obfuscated_session(profile)
                        
                        if source.endswith('.xml'):
                            data = await self._collect_rss_feed(session, source)
                        else:
                            data = await self._collect_web_content(source, session, 'titles_and_links')
                        
                        if data:
                            report = await self._process_collected_data(
                                data, 'vulnerability_intelligence', source
                            )
                            
                            if report:
                                self.data_store.store_intelligence_report(report)
                        
                        await session.close()
                        await asyncio.sleep(random.uniform(15.0, 45.0))
                        
                    except Exception as e:
                        logger.error(f"Vulnerability monitoring failed for {source}: {e}")
                
                await asyncio.sleep(3600)  # 1 hour
                
            except Exception as e:
                logger.error(f"Vulnerability monitoring error: {e}")
                await asyncio.sleep(600)
    
    async def _exploit_marketplace_monitoring(self):
        """Monitor exploit marketplaces and underground forums"""
        while True:
            try:
                # Note: In production, this would monitor dark web sources through Tor
                # For this implementation, we monitor public exploit repositories
                
                exploit_sources = [
                    'https://github.com/topics/exploit',
                    'https://github.com/topics/vulnerability',
                    'https://github.com/topics/poc'
                ]
                
                for source in exploit_sources:
                    try:
                        profile = random.choice(self.browser_profiles)
                        session = await self._create_obfuscated_session(profile)
                        
                        data = await self._collect_github_data(session, source)
                        
                        if data:
                            report = await self._process_collected_data(
                                data, 'exploit_intelligence', source
                            )
                            
                            if report:
                                self.data_store.store_intelligence_report(report)
                        
                        await session.close()
                        await asyncio.sleep(random.uniform(20.0, 60.0))
                        
                    except Exception as e:
                        logger.error(f"Exploit monitoring failed for {source}: {e}")
                
                await asyncio.sleep(10800)  # 3 hours
                
            except Exception as e:
                logger.error(f"Exploit monitoring error: {e}")
                await asyncio.sleep(900)


class NetworkTelemetryEngine:
    """Local network monitoring and analysis"""
    
    def __init__(self, data_store: SovereignDataStore):
        self.data_store = data_store
        self.interfaces = self._get_network_interfaces()
        self.packet_buffer = deque(maxlen=10000)
        self.connection_tracker = defaultdict(dict)
        self.baseline_metrics = {}
        self.anomaly_threshold = 0.7
    
    def _get_network_interfaces(self) -> List[str]:
        """Get available network interfaces"""
        try:
            return [iface for iface in netifaces.interfaces() 
                   if not iface.startswith('lo') and netifaces.ifaddresses(iface)]
        except:
            return ['eth0', 'wlan0']  # Fallback
    
    async def start_network_monitoring(self):
        """Start comprehensive network monitoring"""
        logger.info("Starting sovereign network telemetry collection")
        
        monitoring_tasks = [
            asyncio.create_task(self._packet_capture_engine()),
            asyncio.create_task(self._connection_analysis_engine()),
            asyncio.create_task(self._baseline_monitoring_engine()),
            asyncio.create_task(self._anomaly_detection_engine())
        ]
        
        await asyncio.gather(*monitoring_tasks, return_exceptions=True)
    
    async def _packet_capture_engine(self):
        """Capture and analyze network packets"""
        while True:
            try:
                for interface in self.interfaces:
                    try:
                        # Use scapy for packet capture
                        packets = scapy.sniff(
                            iface=interface,
                            count=100,
                            timeout=30,
                            store=True,
                            filter="not arp"  # Exclude ARP traffic
                        )
                        
                        for packet in packets:
                            await self._process_packet(packet)
                        
                    except Exception as e:
                        logger.error(f"Packet capture failed on {interface}: {e}")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Packet capture engine error: {e}")
                await asyncio.sleep(30)
    
    async def _process_packet(self, packet):
        """Process individual network packet"""
        try:
            packet_data = {
                'timestamp': datetime.utcnow(),
                'protocol': 'unknown',
                'src_ip': None,
                'dst_ip': None,
                'src_port': None,
                'dst_port': None,
                'packet_size': len(packet),
                'flags': [],
                'payload_hash': None
            }
            
            # Extract IP layer information
            if IP in packet:
                packet_data['src_ip'] = packet[IP].src
                packet_data['dst_ip'] = packet[IP].dst
                packet_data['protocol'] = packet[IP].proto
            
            # Extract TCP information
            if TCP in packet:
                packet_data['src_port'] = packet[TCP].sport
                packet_data['dst_port'] = packet[TCP].dport
                packet_data['protocol'] = 'TCP'
                
                # Extract TCP flags
                flags = []
                if packet[TCP].flags.S: flags.append('SYN')
                if packet[TCP].flags.A: flags.append('ACK')
                if packet[TCP].flags.F: flags.append('FIN')
                if packet[TCP].flags.R: flags.append('RST')
                if packet[TCP].flags.P: flags.append('PSH')
                if packet[TCP].flags.U: flags.append('URG')
                packet_data['flags'] = flags
            
            # Extract UDP information
            elif UDP in packet:
                packet_data['src_port'] = packet[UDP].sport
                packet_data['dst_port'] = packet[UDP].dport
                packet_data['protocol'] = 'UDP'
            
            # Hash payload for analysis
            if packet.payload:
                payload_bytes = bytes(packet.payload)
                packet_data['payload_hash'] = hashlib.md5(payload_bytes).hexdigest()
            
            # Add to packet buffer
            self.packet_buffer.append(packet_data)
            
            # Analyze for anomalies
            anomaly_score = await self._calculate_packet_anomaly_score(packet_data)
            
            if anomaly_score > self.anomaly_threshold:
                await self._create_network_intelligence_report(packet_data, anomaly_score)
        
        except Exception as e:
            logger.error(f"Packet processing error: {e}")
    
    async def _calculate_packet_anomaly_score(self, packet_data: Dict[str, Any]) -> float:
        """Calculate anomaly score for network packet"""
        anomaly_score = 0.0
        
        # Check for unusual ports
        suspicious_ports = [1337, 31337, 4444, 5555, 6666, 7777, 8888, 9999]
        if packet_data.get('dst_port') in suspicious_ports:
            anomaly_score += 0.3
        
        # Check for unusual protocols
        if packet_data.get('protocol') not in ['TCP', 'UDP', 6, 17]:
            anomaly_score += 0.2
        
        # Check for unusual packet sizes
        packet_size = packet_data.get('packet_size', 0)
        if packet_size > 9000 or packet_size < 20:
            anomaly_score += 0.2
        
        # Check for suspicious IP ranges
        dst_ip = packet_data.get('dst_ip', '')
        if dst_ip:
            # Check for private IP communication with external hosts
            if self._is_private_ip(dst_ip) and not self._is_local_network(dst_ip):
                anomaly_score += 0.3
        
        # Check for unusual flag combinations
        flags = packet_data.get('flags', [])
        if 'RST' in flags and 'SYN' in flags:
            anomaly_score += 0.2
        
        return min(anomaly_score, 1.0)
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP address is in private range"""
        try:
            import ipaddress
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except:
            return False
    
    def _is_local_network(self, ip: str) -> bool:
        """Check if IP is in local network range"""
        local_ranges = ['192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.']
        return any(ip.startswith(range_prefix) for range_prefix in local_ranges)
    
    async def _create_network_intelligence_report(self, packet_data: Dict[str, Any], 
                                                anomaly_score: float):
        """Create intelligence report for network anomaly"""
        try:
            report_id = f"net_intel_{int(time.time())}_{os.urandom(4).hex()}"
            
            # Extract threat indicators
            indicators = []
            if packet_data.get('dst_ip'):
                indicators.append(f"ip:{packet_data['dst_ip']}")
            if packet_data.get('src_ip'):
                indicators.append(f"ip:{packet_data['src_ip']}")
            if packet_data.get('dst_port'):
                indicators.append(f"port:{packet_data['dst_port']}")
            
            # Determine threat level
            if anomaly_score > 0.8:
                threat_level = "HIGH"
            elif anomaly_score > 0.6:
                threat_level = "MEDIUM"
            else:
                threat_level = "LOW"
            
            report = IntelligenceReport(
                report_id=report_id,
                intelligence_type=IntelligenceType.NETWORK_TELEMETRY,
                source=IntelligenceSource.NETWORK_MONITORING,
                collection_timestamp=datetime.utcnow(),
                confidence_score=anomaly_score,
                threat_level=threat_level,
                raw_data=packet_data,
                processed_indicators=indicators,
                attribution_data={},
                correlation_markers=[f"network_anomaly:{anomaly_score:.2f}"],
                actionable_intelligence=[
                    f"Investigate network traffic to {packet_data.get('dst_ip', 'unknown')}",
                    f"Monitor for additional suspicious activity on port {packet_data.get('dst_port', 'unknown')}"
                ],
                metadata={
                    'anomaly_score': anomaly_score,
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            )
            
            self.data_store.store_intelligence_report(report)
            
        except Exception as e:
            logger.error(f"Failed to create network intelligence report: {e}")
    
    async def _connection_analysis_engine(self):
        """Analyze network connections for intelligence"""
        while True:
            try:
                # Get current network connections
                connections = psutil.net_connections(kind='inet')
                
                for conn in connections:
                    if conn.status == 'ESTABLISHED':
                        await self._analyze_connection(conn)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Connection analysis error: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_connection(self, connection):
        """Analyze individual network connection"""
        try:
            conn_key = f"{connection.laddr.ip}:{connection.laddr.port}-{connection.raddr.ip if connection.raddr else 'unknown'}:{connection.raddr.port if connection.raddr else 0}"
            
            # Store connection information
            self.connection_tracker[conn_key] = {
                'local_ip': connection.laddr.ip,
                'local_port': connection.laddr.port,
                'remote_ip': connection.raddr.ip if connection.raddr else None,
                'remote_port': connection.raddr.port if connection.raddr else None,
                'status': connection.status,
                'pid': connection.pid,
                'last_seen': datetime.utcnow()
            }
            
            # Analyze for suspicious patterns
            if connection.raddr:
                await self._check_suspicious_connection(connection)
        
        except Exception as e:
            logger.error(f"Connection analysis error: {e}")
    
    async def _check_suspicious_connection(self, connection):
        """Check connection for suspicious indicators"""
        try:
            remote_ip = connection.raddr.ip
            remote_port = connection.raddr.port
            
            # Check for connections to suspicious ports
            suspicious_ports = [1337, 4444, 5555, 6666, 31337]
            if remote_port in suspicious_ports:
                await self._create_suspicious_connection_report(connection, f"Connection to suspicious port {remote_port}")
            
            # Check for connections to non-standard HTTP/HTTPS ports
            if remote_port not in [80, 443, 8080, 8443] and remote_port > 1024:
                if not self._is_local_network(remote_ip):
                    await self._create_suspicious_connection_report(connection, f"Unusual external connection to port {remote_port}")
            
            # Check for connections to private IP ranges from external sources
            if self._is_private_ip(remote_ip) and not self._is_local_network(remote_ip):
                await self._create_suspicious_connection_report(connection, "Connection to external private IP range")
        
        except Exception as e:
            logger.error(f"Suspicious connection check error: {e}")
    
    async def _create_suspicious_connection_report(self, connection, reason: str):
        """Create intelligence report for suspicious connection"""
        try:
            report_id = f"conn_intel_{int(time.time())}_{os.urandom(4).hex()}"
            
            connection_data = {
                'local_ip': connection.laddr.ip,
                'local_port': connection.laddr.port,
                'remote_ip': connection.raddr.ip if connection.raddr else None,
                'remote_port': connection.raddr.port if connection.raddr else None,
                'status': connection.status,
                'pid': connection.pid,
                'reason': reason
            }
            
            indicators = []
            if connection.raddr:
                indicators.append(f"ip:{connection.raddr.ip}")
                indicators.append(f"port:{connection.raddr.port}")
            
            report = IntelligenceReport(
                report_id=report_id,
                intelligence_type=IntelligenceType.NETWORK_TELEMETRY,
                source=IntelligenceSource.NETWORK_MONITORING,
                collection_timestamp=datetime.utcnow(),
                confidence_score=0.7,
                threat_level="MEDIUM",
                raw_data=connection_data,
                processed_indicators=indicators,
                attribution_data={},
                correlation_markers=[f"suspicious_connection:{reason}"],
                actionable_intelligence=[
                    f"Investigate process PID {connection.pid} for malicious activity",
                    f"Monitor traffic to {connection.raddr.ip if connection.raddr else 'unknown'} for additional indicators"
                ],
                metadata={
                    'detection_reason': reason,
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            )
            
            self.data_store.store_intelligence_report(report)
            
        except Exception as e:
            logger.error(f"Failed to create suspicious connection report: {e}")
    
    async def _baseline_monitoring_engine(self):
        """Monitor and establish network baselines"""
        while True:
            try:
                # Collect baseline metrics
                current_metrics = await self._collect_network_metrics()
                
                # Update baseline
                await self._update_network_baseline(current_metrics)
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"Baseline monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _collect_network_metrics(self) -> Dict[str, Any]:
        """Collect current network metrics"""
        try:
            net_io = psutil.net_io_counters()
            connections = psutil.net_connections(kind='inet')
            
            metrics = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'active_connections': len([c for c in connections if c.status == 'ESTABLISHED']),
                'listening_ports': len([c for c in connections if c.status == 'LISTEN']),
                'timestamp': datetime.utcnow()
            }
            
            return metrics
        
        except Exception as e:
            logger.error(f"Network metrics collection error: {e}")
            return {}
    
    async def _update_network_baseline(self, current_metrics: Dict[str, Any]):
        """Update network baseline with current metrics"""
        try:
            if not self.baseline_metrics:
                self.baseline_metrics = current_metrics.copy()
                return
            
            # Update baseline with exponential moving average
            alpha = 0.1  # Smoothing factor
            
            for metric in ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv']:
                if metric in current_metrics and metric in self.baseline_metrics:
                    self.baseline_metrics[metric] = (
                        alpha * current_metrics[metric] + 
                        (1 - alpha) * self.baseline_metrics[metric]
                    )
            
            # Update discrete metrics
            self.baseline_metrics['active_connections'] = current_metrics.get('active_connections', 0)
            self.baseline_metrics['listening_ports'] = current_metrics.get('listening_ports', 0)
            self.baseline_metrics['last_updated'] = datetime.utcnow()
        
        except Exception as e:
            logger.error(f"Baseline update error: {e}")
    
    async def _anomaly_detection_engine(self):
        """Detect network anomalies based on baseline"""
        while True:
            try:
                if self.baseline_metrics:
                    current_metrics = await self._collect_network_metrics()
                    anomalies = await self._detect_network_anomalies(current_metrics)
                    
                    for anomaly in anomalies:
                        await self._create_network_anomaly_report(anomaly)
                
                await asyncio.sleep(120)  # Every 2 minutes
                
            except Exception as e:
                logger.error(f"Anomaly detection error: {e}")
                await asyncio.sleep(120)
    
    async def _detect_network_anomalies(self, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in network metrics"""
        anomalies = []
        
        try:
            for metric in ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv']:
                if metric in current_metrics and metric in self.baseline_metrics:
                    current_value = current_metrics[metric]
                    baseline_value = self.baseline_metrics[metric]
                    
                    if baseline_value > 0:
                        deviation = abs(current_value - baseline_value) / baseline_value
                        
                        if deviation > 2.0:  # 200% deviation threshold
                            anomalies.append({
                                'metric': metric,
                                'current_value': current_value,
                                'baseline_value': baseline_value,
                                'deviation': deviation,
                                'anomaly_type': 'statistical_deviation'
                            })
            
            # Check for connection anomalies
            current_connections = current_metrics.get('active_connections', 0)
            baseline_connections = self.baseline_metrics.get('active_connections', 0)
            
            if current_connections > baseline_connections * 3:
                anomalies.append({
                    'metric': 'active_connections',
                    'current_value': current_connections,
                    'baseline_value': baseline_connections,
                    'deviation': current_connections / max(baseline_connections, 1),
                    'anomaly_type': 'connection_spike'
                })
        
        except Exception as e:
            logger.error(f"Anomaly detection calculation error: {e}")
        
        return anomalies
    
    async def _create_network_anomaly_report(self, anomaly: Dict[str, Any]):
        """Create intelligence report for network anomaly"""
        try:
            report_id = f"net_anomaly_{int(time.time())}_{os.urandom(4).hex()}"
            
            # Determine threat level based on deviation
            deviation = anomaly.get('deviation', 0)
            if deviation > 5.0:
                threat_level = "HIGH"
                confidence = 0.8
            elif deviation > 3.0:
                threat_level = "MEDIUM"
                confidence = 0.6
            else:
                threat_level = "LOW"
                confidence = 0.4
            
            report = IntelligenceReport(
                report_id=report_id,
                intelligence_type=IntelligenceType.NETWORK_TELEMETRY,
                source=IntelligenceSource.NETWORK_MONITORING,
                collection_timestamp=datetime.utcnow(),
                confidence_score=confidence,
                threat_level=threat_level,
                raw_data=anomaly,
                processed_indicators=[f"network_anomaly:{anomaly['metric']}"],
                attribution_data={},
                correlation_markers=[f"baseline_deviation:{deviation:.2f}"],
                actionable_intelligence=[
                    f"Investigate cause of {anomaly['metric']} anomaly",
                    f"Monitor network activity for additional indicators"
                ],
                metadata={
                    'anomaly_type': anomaly.get('anomaly_type', 'unknown'),
                    'deviation_factor': deviation,
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            )
            
            self.data_store.store_intelligence_report(report)
            
        except Exception as e:
            logger.error(f"Failed to create network anomaly report: {e}")


class SystemBehaviorEngine:
    """System behavioral monitoring and analysis"""
    
    def __init__(self, data_store: SovereignDataStore):
        self.data_store = data_store
        self.process_tracker = {}
        self.system_baselines = {}
        self.behavioral_patterns = defaultdict(list)
        self.anomaly_threshold = 0.75
    
    async def start_system_monitoring(self):
        """Start comprehensive system behavior monitoring"""
        logger.info("Starting system behavioral intelligence collection")
        
        monitoring_tasks = [
            asyncio.create_task(self._process_monitoring_engine()),
            asyncio.create_task(self._system_metrics_engine()),
            asyncio.create_task(self._file_system_monitoring_engine()),
            asyncio.create_task(self._behavioral_analysis_engine())
        ]
        
        await asyncio.gather(*monitoring_tasks, return_exceptions=True)
    
    async def _process_monitoring_engine(self):
        """Monitor system processes for anomalies"""
        while True:
            try:
                current_processes = {}
                
                for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'cpu_percent', 'memory_percent']):
                    try:
                        proc_info = proc.info
                        if proc_info['pid'] != 0:  # Skip kernel process
                            current_processes[proc_info['pid']] = proc_info
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Analyze processes
                await self._analyze_processes(current_processes)
                
                # Update process tracker
                self.process_tracker = current_processes
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Process monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _analyze_processes(self, current_processes: Dict[int, Dict[str, Any]]):
        """Analyze processes for suspicious behavior"""
        try:
            for pid, proc_info in current_processes.items():
                # Check for suspicious process names
                proc_name = proc_info.get('name', '').lower()
                suspicious_names = [
                    'nc', 'netcat', 'ncat', 'socat', 'telnet', 'wget', 'curl',
                    'powershell', 'cmd', 'bash', 'sh', 'python', 'perl', 'ruby'
                ]
                
                if any(sus_name in proc_name for sus_name in suspicious_names):
                    await self._investigate_suspicious_process(pid, proc_info, "suspicious_process_name")
                
                # Check for high resource usage
                cpu_percent = proc_info.get('cpu_percent', 0)
                memory_percent = proc_info.get('memory_percent', 0)
                
                if cpu_percent > 80 or memory_percent > 50:
                    await self._investigate_suspicious_process(pid, proc_info, "high_resource_usage")
                
                # Check for processes with no executable path
                exe_path = proc_info.get('exe')
                if not exe_path and proc_name not in ['kernel', 'kthreadd']:
                    await self._investigate_suspicious_process(pid, proc_info, "no_executable_path")
                
                # Check for unusual command line arguments
                cmdline = proc_info.get('cmdline', [])
                if cmdline:
                    cmdline_str = ' '.join(cmdline).lower()
                    suspicious_patterns = [
                        'base64', 'powershell -enc', 'cmd /c', 'bash -c',
                        'wget http', 'curl http', 'nc -l', 'netcat -l'
                    ]
                    
                    if any(pattern in cmdline_str for pattern in suspicious_patterns):
                        await self._investigate_suspicious_process(pid, proc_info, "suspicious_command_line")
        
        except Exception as e:
            logger.error(f"Process analysis error: {e}")
    
    async def _investigate_suspicious_process(self, pid: int, proc_info: Dict[str, Any], 
                                           reason: str):
        """Investigate suspicious process and create intelligence report"""
        try:
            report_id = f"proc_intel_{int(time.time())}_{pid}"
            
            # Gather additional process information
            try:
                proc = psutil.Process(pid)
                additional_info = {
                    'parent_pid': proc.ppid(),
                    'create_time': proc.create_time(),
                    'status': proc.status(),
                    'num_threads': proc.num_threads(),
                    'connections': [conn._asdict() for conn in proc.connections()],
                    'open_files': [f._asdict() for f in proc.open_files()],
                    'cwd': proc.cwd() if proc.cwd() else 'unknown'
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                additional_info = {}
            
            # Combine process information
            full_proc_data = {**proc_info, **additional_info, 'investigation_reason': reason}
            
            # Extract indicators
            indicators = [f"process_name:{proc_info.get('name', 'unknown')}"]
            if proc_info.get('exe'):
                indicators.append(f"executable_path:{proc_info['exe']}")
            
            # Determine threat level
            threat_level = "MEDIUM"
            confidence = 0.6
            
            if reason in ['suspicious_command_line', 'no_executable_path']:
                threat_level = "HIGH"
                confidence = 0.8
            
            report = IntelligenceReport(
                report_id=report_id,
                intelligence_type=IntelligenceType.SYSTEM_BEHAVIORAL,
                source=IntelligenceSource.SYSTEM_MONITORING,
                collection_timestamp=datetime.utcnow(),
                confidence_score=confidence,
                threat_level=threat_level,
                raw_data=full_proc_data,
                processed_indicators=indicators,
                attribution_data={},
                correlation_markers=[f"suspicious_process:{reason}"],
                actionable_intelligence=[
                    f"Investigate process {proc_info.get('name', 'unknown')} (PID: {pid})",
                    f"Check parent process and process tree for additional indicators",
                    f"Monitor process network activity and file access"
                ],
                metadata={
                    'investigation_reason': reason,
                    'process_pid': pid,
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            )
            
            self.data_store.store_intelligence_report(report)
            
        except Exception as e:
            logger.error(f"Failed to investigate suspicious process {pid}: {e}")
    
    async def _system_metrics_engine(self):
        """Monitor system-wide metrics for anomalies"""
        while True:
            try:
                # Collect system metrics
                metrics = {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_usage': {disk.mountpoint: psutil.disk_usage(disk.mountpoint).percent 
                                 for disk in psutil.disk_partitions()},
                    'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
                    'boot_time': psutil.boot_time(),
                    'users': len(psutil.users()),
                    'timestamp': datetime.utcnow()
                }
                
                # Analyze metrics for anomalies
                await self._analyze_system_metrics(metrics)
                
                # Update baselines
                await self._update_system_baselines(metrics)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"System metrics monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_system_metrics(self, metrics: Dict[str, Any]):
        """Analyze system metrics for anomalies"""
        try:
            anomalies = []
            
            # Check CPU usage
            cpu_percent = metrics.get('cpu_percent', 0)
            if cpu_percent > 90:
                anomalies.append({
                    'metric': 'cpu_percent',
                    'value': cpu_percent,
                    'threshold': 90,
                    'severity': 'high' if cpu_percent > 95 else 'medium'
                })
            
            # Check memory usage
            memory_percent = metrics.get('memory_percent', 0)
            if memory_percent > 85:
                anomalies.append({
                    'metric': 'memory_percent',
                    'value': memory_percent,
                    'threshold': 85,
                    'severity': 'high' if memory_percent > 95 else 'medium'
                })
            
            # Check disk usage
            disk_usage = metrics.get('disk_usage', {})
            for mount_point, usage_percent in disk_usage.items():
                if usage_percent > 90:
                    anomalies.append({
                        'metric': f'disk_usage_{mount_point}',
                        'value': usage_percent,
                        'threshold': 90,
                        'severity': 'high' if usage_percent > 95 else 'medium'
                    })
            
            # Check load average
            load_avg = metrics.get('load_average', [0, 0, 0])
            cpu_count = psutil.cpu_count()
            if load_avg[0] > cpu_count * 2:  # Load > 2x CPU count
                anomalies.append({
                    'metric': 'load_average',
                    'value': load_avg[0],
                    'threshold': cpu_count * 2,
                    'severity': 'medium'
                })
            
            # Create reports for anomalies
            for anomaly in anomalies:
                await self._create_system_anomaly_report(anomaly, metrics)
        
        except Exception as e:
            logger.error(f"System metrics analysis error: {e}")
    
    async def _create_system_anomaly_report(self, anomaly: Dict[str, Any], 
                                          full_metrics: Dict[str, Any]):
        """Create intelligence report for system anomaly"""
        try:
            report_id = f"sys_anomaly_{int(time.time())}_{os.urandom(4).hex()}"
            
            # Determine threat level and confidence
            severity = anomaly.get('severity', 'medium')
            if severity == 'high':
                threat_level = "HIGH"
                confidence = 0.8
            else:
                threat_level = "MEDIUM"
                confidence = 0.6
            
            report = IntelligenceReport(
                report_id=report_id,
                intelligence_type=IntelligenceType.SYSTEM_BEHAVIORAL,
                source=IntelligenceSource.SYSTEM_MONITORING,
                collection_timestamp=datetime.utcnow(),
                confidence_score=confidence,
                threat_level=threat_level,
                raw_data=full_metrics,
                processed_indicators=[f"system_anomaly:{anomaly['metric']}"],
                attribution_data={},
                correlation_markers=[f"resource_anomaly:{anomaly['metric']}"],
                actionable_intelligence=[
                    f"Investigate cause of {anomaly['metric']} anomaly",
                    f"Check for resource-intensive processes",
                    f"Monitor for potential DoS or resource exhaustion attacks"
                ],
                metadata={
                    'anomaly_metric': anomaly['metric'],
                    'anomaly_value': anomaly['value'],
                    'threshold': anomaly['threshold'],
                    'severity': severity,
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            )
            
            self.data_store.store_intelligence_report(report)
            
        except Exception as e:
            logger.error(f"Failed to create system anomaly report: {e}")
    
    async def _update_system_baselines(self, metrics: Dict[str, Any]):
        """Update system performance baselines"""
        try:
            if not self.system_baselines:
                self.system_baselines = {
                    'cpu_percent': [],
                    'memory_percent': [],
                    'load_average': []
                }
            
            # Add current metrics to baseline (keep last 100 measurements)
            self.system_baselines['cpu_percent'].append(metrics.get('cpu_percent', 0))
            if len(self.system_baselines['cpu_percent']) > 100:
                self.system_baselines['cpu_percent'].pop(0)
            
            self.system_baselines['memory_percent'].append(metrics.get('memory_percent', 0))
            if len(self.system_baselines['memory_percent']) > 100:
                self.system_baselines['memory_percent'].pop(0)
            
            load_avg = metrics.get('load_average', [0, 0, 0])
            self.system_baselines['load_average'].append(load_avg[0])
            if len(self.system_baselines['load_average']) > 100:
                self.system_baselines['load_average'].pop(0)
        
        except Exception as e:
            logger.error(f"Baseline update error: {e}")
    
    async def _file_system_monitoring_engine(self):
        """Monitor file system for suspicious activity"""
        while True:
            try:
                # Monitor critical directories
                critical_dirs = ['/etc', '/bin', '/sbin', '/usr/bin', '/usr/sbin']
                
                for directory in critical_dirs:
                    if os.path.exists(directory):
                        await self._scan_directory_changes(directory)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"File system monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _scan_directory_changes(self, directory: str):
        """Scan directory for suspicious changes"""
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        stat_info = os.stat(file_path)
                        
                        # Check for recently modified critical files
                        modification_time = datetime.fromtimestamp(stat_info.st_mtime)
                        if (datetime.utcnow() - modification_time).total_seconds() < 3600:  # Modified in last hour
                            await self._investigate_file_change(file_path, stat_info)
                    
                    except (OSError, PermissionError):
                        continue
        
        except Exception as e:
            logger.error(f"Directory scan error for {directory}: {e}")
    
    async def _investigate_file_change(self, file_path: str, stat_info):
        """Investigate suspicious file changes"""
        try:
            report_id = f"file_intel_{int(time.time())}_{hashlib.md5(file_path.encode()).hexdigest()[:8]}"
            
            file_data = {
                'file_path': file_path,
                'size': stat_info.st_size,
                'modification_time': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'permissions': oct(stat_info.st_mode),
                'owner_uid': stat_info.st_uid,
                'owner_gid': stat_info.st_gid,
                'investigation_reason': 'recent_modification_critical_directory'
            }
            
            # Calculate file hash if possible and reasonable size
            if stat_info.st_size < 10 * 1024 * 1024:  # Less than 10MB
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                        file_data['file_hash'] = file_hash
                except (OSError, PermissionError):
                    pass
            
            indicators = [f"file_path:{file_path}"]
            if 'file_hash' in file_data:
                indicators.append(f"md5:{file_data['file_hash']}")
            
            report = IntelligenceReport(
                report_id=report_id,
                intelligence_type=IntelligenceType.SYSTEM_BEHAVIORAL,
                source=IntelligenceSource.SYSTEM_MONITORING,
                collection_timestamp=datetime.utcnow(),
                confidence_score=0.7,
                threat_level="MEDIUM",
                raw_data=file_data,
                processed_indicators=indicators,
                attribution_data={},
                correlation_markers=["file_system_change"],
                actionable_intelligence=[
                    f"Verify legitimacy of changes to {file_path}",
                    f"Check file integrity and compare against known good versions",
                    f"Investigate process responsible for file modification"
                ],
                metadata={
                    'file_size': stat_info.st_size,
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            )
            
            self.data_store.store_intelligence_report(report)
            
        except Exception as e:
            logger.error(f"Failed to investigate file change {file_path}: {e}")
    
    async def _behavioral_analysis_engine(self):
        """Analyze system behavior patterns"""
        while True:
            try:
                # Collect behavioral data
                behavior_data = await self._collect_behavioral_data()
                
                # Analyze patterns
                await self._analyze_behavioral_patterns(behavior_data)
                
                await asyncio.sleep(600)  # Analyze every 10 minutes
                
            except Exception as e:
                logger.error(f"Behavioral analysis error: {e}")
                await asyncio.sleep(600)
    
    async def _collect_behavioral_data(self) -> Dict[str, Any]:
        """Collect system behavioral data"""
        try:
            return {
                'active_processes': len([p for p in psutil.process_iter() if p.status() != 'zombie']),
                'network_connections': len(psutil.net_connections()),
                'logged_in_users': len(psutil.users()),
                'system_uptime': time.time() - psutil.boot_time(),
                'cpu_usage_pattern': [psutil.cpu_percent() for _ in range(5)],
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Behavioral data collection error: {e}")
            return {}
    
    async def _analyze_behavioral_patterns(self, behavior_data: Dict[str, Any]):
        """Analyze behavioral patterns for anomalies"""
        try:
            # Store behavior data for pattern analysis
            self.behavioral_patterns['recent'].append(behavior_data)
            
            # Keep only recent data (last 24 hours worth)
            if len(self.behavioral_patterns['recent']) > 144:  # 24 hours * 6 samples per hour
                self.behavioral_patterns['recent'].pop(0)
            
            # Analyze for patterns
            if len(self.behavioral_patterns['recent']) > 10:
                await self._detect_behavioral_anomalies()
        
        except Exception as e:
            logger.error(f"Behavioral pattern analysis error: {e}")
    
    async def _detect_behavioral_anomalies(self):
        """Detect anomalies in behavioral patterns"""
        try:
            recent_data = self.behavioral_patterns['recent']
            
            if len(recent_data) < 10:
                return
            
            # Analyze process count patterns
            process_counts = [data.get('active_processes', 0) for data in recent_data]
            process_mean = np.mean(process_counts)
            process_std = np.std(process_counts)
            
            current_processes = process_counts[-1]
            
            if abs(current_processes - process_mean) > 2 * process_std:
                await self._create_behavioral_anomaly_report(
                    'process_count_anomaly',
                    {
                        'current_value': current_processes,
                        'mean': process_mean,
                        'std_dev': process_std,
                        'deviation': abs(current_processes - process_mean) / process_std
                    }
                )
            
            # Analyze connection count patterns
            connection_counts = [data.get('network_connections', 0) for data in recent_data]
            connection_mean = np.mean(connection_counts)
            connection_std = np.std(connection_counts)
            
            current_connections = connection_counts[-1]
            
            if abs(current_connections - connection_mean) > 2 * connection_std:
                await self._create_behavioral_anomaly_report(
                    'connection_count_anomaly',
                    {
                        'current_value': current_connections,
                        'mean': connection_mean,
                        'std_dev': connection_std,
                        'deviation': abs(current_connections - connection_mean) / connection_std
                    }
                )
        
        except Exception as e:
            logger.error(f"Behavioral anomaly detection error: {e}")
    
    async def _create_behavioral_anomaly_report(self, anomaly_type: str, 
                                              anomaly_data: Dict[str, Any]):
        """Create intelligence report for behavioral anomaly"""
        try:
            report_id = f"behav_anomaly_{int(time.time())}_{os.urandom(4).hex()}"
            
            deviation = anomaly_data.get('deviation', 0)
            
            # Determine threat level
            if deviation > 4:
                threat_level = "HIGH"
                confidence = 0.8
            elif deviation > 3:
                threat_level = "MEDIUM"
                confidence = 0.6
            else:
                threat_level = "LOW"
                confidence = 0.4
            
            report = IntelligenceReport(
                report_id=report_id,
                intelligence_type=IntelligenceType.SYSTEM_BEHAVIORAL,
                source=IntelligenceSource.SYSTEM_MONITORING,
                collection_timestamp=datetime.utcnow(),
                confidence_score=confidence,
                threat_level=threat_level,
                raw_data=anomaly_data,
                processed_indicators=[f"behavioral_anomaly:{anomaly_type}"],
                attribution_data={},
                correlation_markers=[f"statistical_anomaly:{deviation:.2f}"],
                actionable_intelligence=[
                    f"Investigate cause of {anomaly_type}",
                    f"Check for unusual system activity or malware",
                    f"Monitor for additional behavioral changes"
                ],
                metadata={
                    'anomaly_type': anomaly_type,
                    'statistical_deviation': deviation,
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            )
            
            self.data_store.store_intelligence_report(report)
            
        except Exception as e:
            logger.error(f"Failed to create behavioral anomaly report: {e}")


class OSINTOrchestrator:
    """Main OSINT module orchestrator"""
    
    def __init__(self, config_path: str = "config/osint_config.json"):
        self.config = self._load_config(config_path)
        
        # Initialize encryption
        self.encryption_key = self._initialize_encryption()
        
        # Initialize data store
        self.data_store = SovereignDataStore(
            self.config['database_path'],
            self.encryption_key
        )
        
        # Initialize collection engines
        self.browser_engine = ObfuscatedBrowserEngine(self.data_store)
        self.network_engine = NetworkTelemetryEngine(self.data_store)
        self.system_engine = SystemBehaviorEngine(self.data_store)
        
        # Purple team interface
        self.purple_team_interface = None
        
        # Collection status
        self.collection_active = False
        self.collection_tasks: List[asyncio.Task] = []
        
        # Performance metrics
        self.metrics = {
            'reports_generated': 0,
            'indicators_extracted': 0,
            'collection_cycles': 0,
            'start_time': datetime.utcnow()
        }
        
        logger.info("OSINT Orchestrator initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load OSINT configuration"""
        default_config = {
            'database_path': 'data/osint_intelligence.db',
            'collection_interval': 1800,  # 30 minutes
            'max_concurrent_collections': 10,
            'browser_automation_enabled': True,
            'network_monitoring_enabled': True,
            'system_monitoring_enabled': True,
            'intelligence_retention_days': 90
        }
        
        try:
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
        except Exception as e:
            logger.warning(f"Could not load OSINT config from {config_path}: {e}")
        
        return default_config
    
    def _initialize_encryption(self) -> bytes:
        """Initialize encryption key for OSINT data"""
        key_path = Path('config/osint.key')
        
        if key_path.exists():
            with open(key_path, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            key_path.parent.mkdir(exist_ok=True)
            with open(key_path, 'wb') as f:
                f.write(key)
            return key
    
    def register_purple_team_interface(self, interface):
        """Register Purple Team interface for intelligence submission"""
        self.purple_team_interface = interface
        logger.info("Purple Team interface registered with OSINT module")
    
    async def start_intelligence_collection(self):
        """Start all intelligence collection engines"""
        if self.collection_active:
            logger.warning("Intelligence collection already active")
            return
        
        logger.info("Starting sovereign intelligence collection")
        
        # Start performance monitoring
        collection_engines.append(
            asyncio.create_task(self._performance_monitoring_loop())
        )
        
        # Start data maintenance
        collection_engines.append(
            asyncio.create_task(self._data_maintenance_loop())
        )
        
        self.collection_tasks = collection_engines
        self.collection_active = True
        
        try:
            await asyncio.gather(*collection_engines, return_exceptions=True)
        except Exception as e:
            logger.error(f"Intelligence collection error: {e}")
        finally:
            self.collection_active = False
    
    async def stop_intelligence_collection(self):
        """Stop all intelligence collection"""
        logger.info("Stopping sovereign intelligence collection")
        self.collection_active = False
        
        for task in self.collection_tasks:
            task.cancel()
        
        await asyncio.gather(*self.collection_tasks, return_exceptions=True)
        self.collection_tasks.clear()
    
    async def _intelligence_processing_loop(self):
        """Process and forward intelligence to Purple Team"""
        while self.collection_active:
            try:
                # Get recent intelligence reports
                recent_reports = self.data_store.get_recent_intelligence(hours=1)
                
                if recent_reports and self.purple_team_interface:
                    # Process intelligence for Purple Team
                    processed_intelligence = await self._process_intelligence_for_purple_team(recent_reports)
                    
                    # Forward to Purple Team
                    await self._forward_intelligence_to_purple_team(processed_intelligence)
                    
                    self.metrics['collection_cycles'] += 1
                
                await asyncio.sleep(300)  # Process every 5 minutes
                
            except Exception as e:
                logger.error(f"Intelligence processing loop error: {e}")
                await asyncio.sleep(300)
    
    async def _process_intelligence_for_purple_team(self, reports: List[IntelligenceReport]) -> Dict[str, Any]:
        """Process intelligence reports for Purple Team consumption"""
        try:
            processed_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'report_count': len(reports),
                'intelligence_summary': {},
                'threat_indicators': [],
                'actionable_intelligence': [],
                'attribution_data': {},
                'correlation_opportunities': [],
                'confidence_scores': [],
                'threat_levels': defaultdict(int)
            }
            
            # Process each report
            for report in reports:
                # Collect threat indicators
                processed_data['threat_indicators'].extend(report.processed_indicators)
                
                # Collect actionable intelligence
                processed_data['actionable_intelligence'].extend(report.actionable_intelligence)
                
                # Aggregate confidence scores
                processed_data['confidence_scores'].append(report.confidence_score)
                
                # Count threat levels
                processed_data['threat_levels'][report.threat_level] += 1
                
                # Collect attribution data
                if report.attribution_data:
                    for key, value in report.attribution_data.items():
                        if key not in processed_data['attribution_data']:
                            processed_data['attribution_data'][key] = []
                        if isinstance(value, list):
                            processed_data['attribution_data'][key].extend(value)
                        else:
                            processed_data['attribution_data'][key].append(value)
                
                # Collect correlation markers
                processed_data['correlation_opportunities'].extend(report.correlation_markers)
            
            # Generate intelligence summary by type
            intelligence_by_type = defaultdict(list)
            for report in reports:
                intelligence_by_type[report.intelligence_type.value].append(report)
            
            for intel_type, type_reports in intelligence_by_type.items():
                processed_data['intelligence_summary'][intel_type] = {
                    'count': len(type_reports),
                    'avg_confidence': np.mean([r.confidence_score for r in type_reports]),
                    'high_confidence_count': len([r for r in type_reports if r.confidence_score > 0.7]),
                    'critical_threat_count': len([r for r in type_reports if r.threat_level == 'CRITICAL'])
                }
            
            # Remove duplicates
            processed_data['threat_indicators'] = list(set(processed_data['threat_indicators']))
            processed_data['actionable_intelligence'] = list(set(processed_data['actionable_intelligence']))
            processed_data['correlation_opportunities'] = list(set(processed_data['correlation_opportunities']))
            
            # Calculate overall metrics
            processed_data['overall_confidence'] = np.mean(processed_data['confidence_scores']) if processed_data['confidence_scores'] else 0.0
            processed_data['high_confidence_percentage'] = len([c for c in processed_data['confidence_scores'] if c > 0.7]) / max(len(processed_data['confidence_scores']), 1) * 100
            
            self.metrics['reports_generated'] += len(reports)
            self.metrics['indicators_extracted'] += len(processed_data['threat_indicators'])
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Intelligence processing error: {e}")
            return {}
    
    async def _forward_intelligence_to_purple_team(self, intelligence_data: Dict[str, Any]):
        """Forward processed intelligence to Purple Team"""
        try:
            if not self.purple_team_interface:
                logger.warning("Purple Team interface not available for intelligence forwarding")
                return
            
            # Create Purple Team intelligence package
            purple_team_package = {
                'source': 'osint_module',
                'collection_timestamp': intelligence_data.get('timestamp'),
                'intelligence_type': 'comprehensive_osint',
                'confidence_score': intelligence_data.get('overall_confidence', 0.0),
                'threat_indicators': intelligence_data.get('threat_indicators', []),
                'actionable_intelligence': intelligence_data.get('actionable_intelligence', []),
                'attribution_data': intelligence_data.get('attribution_data', {}),
                'correlation_markers': intelligence_data.get('correlation_opportunities', []),
                'intelligence_summary': intelligence_data.get('intelligence_summary', {}),
                'threat_level_distribution': dict(intelligence_data.get('threat_levels', {})),
                'metadata': {
                    'report_count': intelligence_data.get('report_count', 0),
                    'high_confidence_percentage': intelligence_data.get('high_confidence_percentage', 0),
                    'osint_module_metrics': self.metrics.copy()
                }
            }
            
            # Forward to Purple Team
            await self.purple_team_interface.receive_osint_intelligence(purple_team_package)
            
            logger.info(f"Forwarded intelligence package with {len(intelligence_data.get('threat_indicators', []))} indicators to Purple Team")
            
        except Exception as e:
            logger.error(f"Intelligence forwarding error: {e}")
    
    async def _performance_monitoring_loop(self):
        """Monitor OSINT module performance"""
        while self.collection_active:
            try:
                # Update performance metrics
                uptime = (datetime.utcnow() - self.metrics['start_time']).total_seconds()
                
                # Calculate rates
                reports_per_hour = self.metrics['reports_generated'] / max(uptime / 3600, 1)
                indicators_per_hour = self.metrics['indicators_extracted'] / max(uptime / 3600, 1)
                
                # Log performance status
                logger.info(f"OSINT Performance - Reports: {self.metrics['reports_generated']}, "
                          f"Indicators: {self.metrics['indicators_extracted']}, "
                          f"Cycles: {self.metrics['collection_cycles']}, "
                          f"Rate: {reports_per_hour:.1f} reports/hour")
                
                # Check for performance issues
                if reports_per_hour < 1.0 and uptime > 3600:  # Less than 1 report per hour after 1 hour
                    logger.warning("Low intelligence collection rate detected")
                
                await asyncio.sleep(1800)  # Monitor every 30 minutes
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(1800)
    
    async def _data_maintenance_loop(self):
        """Maintain intelligence database and cleanup old data"""
        while self.collection_active:
            try:
                # Clean up old intelligence data
                await self._cleanup_old_intelligence()
                
                # Optimize database
                await self._optimize_database()
                
                # Backup critical data
                await self._backup_intelligence_data()
                
                await asyncio.sleep(86400)  # Daily maintenance
                
            except Exception as e:
                logger.error(f"Data maintenance error: {e}")
                await asyncio.sleep(86400)
    
    async def _cleanup_old_intelligence(self):
        """Clean up old intelligence data based on retention policy"""
        try:
            retention_days = self.config.get('intelligence_retention_days', 90)
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            with sqlite3.connect(self.data_store.db_path) as conn:
                # Clean up old reports
                cursor = conn.execute('''
                    DELETE FROM intelligence_reports 
                    WHERE collection_timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                deleted_reports = cursor.rowcount
                
                # Clean up old threat indicators
                cursor = conn.execute('''
                    DELETE FROM threat_indicators 
                    WHERE last_seen < ?
                ''', (cutoff_date.isoformat(),))
                
                deleted_indicators = cursor.rowcount
                
                # Clean up old network telemetry
                cursor = conn.execute('''
                    DELETE FROM network_telemetry 
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                deleted_telemetry = cursor.rowcount
                
                # Clean up old system metrics
                cursor = conn.execute('''
                    DELETE FROM system_metrics 
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                deleted_metrics = cursor.rowcount
                
                conn.commit()
                
                if deleted_reports > 0 or deleted_indicators > 0:
                    logger.info(f"Cleaned up old data: {deleted_reports} reports, "
                              f"{deleted_indicators} indicators, {deleted_telemetry} telemetry, "
                              f"{deleted_metrics} metrics")
        
        except Exception as e:
            logger.error(f"Data cleanup error: {e}")
    
    async def _optimize_database(self):
        """Optimize database performance"""
        try:
            with sqlite3.connect(self.data_store.db_path) as conn:
                # Vacuum database to reclaim space
                conn.execute('VACUUM')
                
                # Analyze tables for query optimization
                conn.execute('ANALYZE')
                
                # Update statistics
                conn.execute('PRAGMA optimize')
                
                logger.info("Database optimization completed")
        
        except Exception as e:
            logger.error(f"Database optimization error: {e}")
    
    async def _backup_intelligence_data(self):
        """Backup critical intelligence data"""
        try:
            backup_dir = Path('backups/osint')
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create backup filename with timestamp
            backup_filename = f"osint_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = backup_dir / backup_filename
            
            # Copy database file
            import shutil
            shutil.copy2(self.data_store.db_path, backup_path)
            
            # Compress backup
            import gzip
            with open(backup_path, 'rb') as f_in:
                with gzip.open(f"{backup_path}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed backup
            backup_path.unlink()
            
            # Keep only last 30 backups
            backup_files = sorted(backup_dir.glob('osint_backup_*.db.gz'))
            if len(backup_files) > 30:
                for old_backup in backup_files[:-30]:
                    old_backup.unlink()
            
            logger.info(f"Intelligence data backup created: {backup_filename}.gz")
        
        except Exception as e:
            logger.error(f"Data backup error: {e}")
    
    async def get_intelligence_status(self) -> Dict[str, Any]:
        """Get comprehensive OSINT module status"""
        try:
            # Get recent intelligence statistics
            recent_reports = self.data_store.get_recent_intelligence(hours=24)
            
            # Calculate statistics
            total_reports = len(recent_reports)
            high_confidence_reports = len([r for r in recent_reports if r.confidence_score > 0.7])
            critical_threats = len([r for r in recent_reports if r.threat_level == 'CRITICAL'])
            
            # Get threat indicator count
            with sqlite3.connect(self.data_store.db_path) as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM threat_indicators')
                total_indicators = cursor.fetchone()[0]
            
            # Calculate uptime
            uptime_seconds = (datetime.utcnow() - self.metrics['start_time']).total_seconds()
            
            status = {
                'collection_active': self.collection_active,
                'uptime_hours': uptime_seconds / 3600,
                'metrics': self.metrics.copy(),
                'recent_intelligence': {
                    'total_reports_24h': total_reports,
                    'high_confidence_reports_24h': high_confidence_reports,
                    'critical_threats_24h': critical_threats,
                    'confidence_rate': (high_confidence_reports / max(total_reports, 1)) * 100
                },
                'database_statistics': {
                    'total_threat_indicators': total_indicators,
                    'database_size_mb': self.data_store.db_path.stat().st_size / (1024 * 1024) if self.data_store.db_path.exists() else 0
                },
                'collection_engines': {
                    'browser_automation': self.config['browser_automation_enabled'],
                    'network_monitoring': self.config['network_monitoring_enabled'],
                    'system_monitoring': self.config['system_monitoring_enabled']
                },
                'purple_team_interface': self.purple_team_interface is not None,
                'active_tasks': len(self.collection_tasks),
                'configuration': {
                    'collection_interval': self.config['collection_interval'],
                    'retention_days': self.config['intelligence_retention_days'],
                    'max_concurrent': self.config['max_concurrent_collections']
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Status retrieval error: {e}")
            return {'error': str(e)}
    
    async def get_threat_indicators(self, hours: int = 24, 
                                  threat_level: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get threat indicators from recent intelligence"""
        try:
            recent_reports = self.data_store.get_recent_intelligence(hours=hours)
            
            if threat_level:
                recent_reports = [r for r in recent_reports if r.threat_level == threat_level]
            
            # Extract and deduplicate indicators
            all_indicators = []
            for report in recent_reports:
                for indicator in report.processed_indicators:
                    indicator_data = {
                        'indicator': indicator,
                        'source_report': report.report_id,
                        'confidence': report.confidence_score,
                        'threat_level': report.threat_level,
                        'timestamp': report.collection_timestamp.isoformat(),
                        'intelligence_type': report.intelligence_type.value,
                        'source': report.source.value
                    }
                    all_indicators.append(indicator_data)
            
            # Remove duplicates based on indicator value
            unique_indicators = {}
            for indicator_data in all_indicators:
                indicator_value = indicator_data['indicator']
                if indicator_value not in unique_indicators:
                    unique_indicators[indicator_value] = indicator_data
                else:
                    # Keep highest confidence version
                    if indicator_data['confidence'] > unique_indicators[indicator_value]['confidence']:
                        unique_indicators[indicator_value] = indicator_data
            
            return list(unique_indicators.values())
            
        except Exception as e:
            logger.error(f"Threat indicator retrieval error: {e}")
            return []
    
    async def query_intelligence(self, query_params: Dict[str, Any]) -> List[IntelligenceReport]:
        """Query intelligence data with filters"""
        try:
            intelligence_type = query_params.get('intelligence_type')
            source = query_params.get('source')
            min_confidence = query_params.get('min_confidence', 0.0)
            threat_level = query_params.get('threat_level')
            hours = query_params.get('hours', 24)
            
            # Get recent reports
            reports = self.data_store.get_recent_intelligence(hours=hours, intelligence_type=intelligence_type)
            
            # Apply filters
            filtered_reports = []
            for report in reports:
                if source and report.source.value != source:
                    continue
                if report.confidence_score < min_confidence:
                    continue
                if threat_level and report.threat_level != threat_level:
                    continue
                
                filtered_reports.append(report)
            
            return filtered_reports
            
        except Exception as e:
            logger.error(f"Intelligence query error: {e}")
            return []


# Purple Team Interface Classes
class PurpleTeamInterface:
    """Interface for Purple Team integration"""
    
    def __init__(self, purple_team_orchestrator):
        self.orchestrator = purple_team_orchestrator
    
    async def receive_osint_intelligence(self, intelligence_package: Dict[str, Any]):
        """Receive OSINT intelligence from OSINT module"""
        try:
            # Convert OSINT package to Purple Team threat event format
            threat_event_data = {
                'source': 'osint_module',
                'timestamp': intelligence_package.get('collection_timestamp'),
                'indicators': intelligence_package.get('threat_indicators', []),
                'confidence': intelligence_package.get('confidence_score', 0.0),
                'actionable_intelligence': intelligence_package.get('actionable_intelligence', []),
                'attribution_data': intelligence_package.get('attribution_data', {}),
                'correlation_markers': intelligence_package.get('correlation_markers', []),
                'threat_level_distribution': intelligence_package.get('threat_level_distribution', {}),
                'intelligence_summary': intelligence_package.get('intelligence_summary', {}),
                'metadata': intelligence_package.get('metadata', {})
            }
            
            # Process through Purple Team
            threat_assessment = await self.orchestrator.process_threat_event(threat_event_data)
            
            logger.info(f"OSINT intelligence processed by Purple Team: {threat_assessment.threat_id}")
            
        except Exception as e:
            logger.error(f"Purple Team OSINT integration error: {e}")


async def main():
    """Main execution function for OSINT module"""
    logger.info("SSDS OSINT Module - Sovereign Intelligence System Starting")
    
    try:
        # Initialize OSINT orchestrator
        osint_orchestrator = OSINTOrchestrator()
        
        # Start intelligence collection
        collection_task = asyncio.create_task(
            osint_orchestrator.start_intelligence_collection()
        )
        
        # Monitor status
        async def status_monitor():
            while True:
                await asyncio.sleep(600)  # Every 10 minutes
                status = await osint_orchestrator.get_intelligence_status()
                logger.info(f"OSINT Status - Active: {status['collection_active']}, "
                          f"Reports: {status['metrics']['reports_generated']}, "
                          f"Indicators: {status['metrics']['indicators_extracted']}")
        
        status_task = asyncio.create_task(status_monitor())
        
        # Run until interrupted
        await asyncio.gather(collection_task, status_task)
        
    except KeyboardInterrupt:
        logger.info("OSINT module shutdown requested")
        await osint_orchestrator.stop_intelligence_collection()
    except Exception as e:
        logger.error(f"OSINT module error: {e}")
        raise
    finally:
        logger.info("SSDS OSINT Module shutdown complete")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('osint_module.log'),
            logging.StreamHandler()
        ]
    )
    
    # Run OSINT module
    asyncio.run(main()) collection engines
        collection_engines = []
        
        if self.config['browser_automation_enabled']:
            collection_engines.append(
                asyncio.create_task(self.browser_engine.start_collection_engines())
            )
        
        if self.config['network_monitoring_enabled']:
            collection_engines.append(
                asyncio.create_task(self.network_engine.start_network_monitoring())
            )
        
        if self.config['system_monitoring_enabled']:
            collection_engines.append(
                asyncio.create_task(self.system_engine.start_system_monitoring())
            )
        
        # Start intelligence processing and forwarding
        collection_engines.append(
            asyncio.create_task(self._intelligence_processing_loop())
        )
        
        # Start