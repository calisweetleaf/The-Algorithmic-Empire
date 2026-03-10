#!/usr/bin/env python3
"""
Threat Assessment - Intelligence Synthesis Module

This module calculates quantitative threat scores for entities and networks
based on analysis results from all correlation engines and data sources.

Author: Daeron
Classification: Internal Development Use Only
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import numpy as np
from pathlib import Path
import json

@dataclass
class ThreatFactor:
    """Individual threat factor"""
    factor_id: str
    factor_type: str  # 'financial', 'political', 'regulatory', 'operational', 'reputational'
    severity: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    persistence: float  # 0.0 to 1.0 (how long-lasting is this threat)
    impact_scope: str  # 'local', 'regional', 'national', 'global'
    description: str
    data_sources: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
@dataclass
class EntityThreatProfile:
    """Comprehensive threat profile for an entity"""
    entity_id: str
    entity_name: str
    overall_threat_score: float
    threat_level: str  # 'minimal', 'low', 'moderate', 'high', 'critical'
    threat_factors: List[ThreatFactor] = field(default_factory=list)
    threat_breakdown: Dict[str, float] = field(default_factory=dict)
    trend_analysis: Dict[str, float] = field(default_factory=dict)
    risk_indicators: List[str] = field(default_factory=list)
    mitigation_recommendations: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
@dataclass
class NetworkThreatAssessment:
    """Network-level threat assessment"""
    network_id: str
    network_name: str
    network_threat_score: float
    systemic_risks: List[ThreatFactor] = field(default_factory=list)
    critical_nodes: List[str] = field(default_factory=list)
    vulnerability_chains: List[List[str]] = field(default_factory=list)
    cascade_potential: float = 0.0
    resilience_score: float = 0.0

class ThreatAssessment:
    """
    Threat Assessment - Advanced threat scoring and analysis engine that
    synthesizes intelligence from all correlation engines to generate
    comprehensive threat profiles and risk assessments.
    
    This engine provides:
    - Quantitative threat scoring for entities and networks
    - Multi-dimensional threat analysis
    - Trend analysis and threat evolution tracking
    - Risk mitigation recommendations
    - Network vulnerability assessment
    """
    
    def __init__(self, config_path: str = "config/", mcp_manager=None):
        """
        Initialize the Threat Assessment engine.
        
        Args:
            config_path: Path to configuration directory
            mcp_manager: MCP service manager for enhanced capabilities
        """
        self.config_path = Path(config_path)
        self.mcp_manager = mcp_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize MCP clients
        self.memory_client = None
        self.everything_client = None
        if mcp_manager:
            self.memory_client = mcp_manager.get_client('memory')
            self.everything_client = mcp_manager.get_client('everything')
        
        # Threat scoring configuration
        self.scoring_config = {
            'financial_weight': 0.25,
            'political_weight': 0.3,
            'regulatory_weight': 0.2,
            'operational_weight': 0.15,
            'reputational_weight': 0.1,
            'temporal_decay_factor': 0.95,
            'confidence_threshold': 0.6,
            'severity_amplifier': 1.2
        }
        
        # Threat level thresholds
        self.threat_thresholds = {
            'minimal': (0.0, 0.2),
            'low': (0.2, 0.4),
            'moderate': (0.4, 0.6),
            'high': (0.6, 0.8),
            'critical': (0.8, 1.0)
        }
        
        # Historical threat data for trend analysis
        self.historical_scores = {}
        self.threat_evolution = {}
        
        # Analysis results cache
        self.entity_profiles = {}
        self.network_assessments = {}
        
        # Metrics
        self.assessment_metrics = {
            'entities_assessed': 0,
            'networks_assessed': 0,
            'critical_threats_identified': 0,
            'average_threat_score': 0.0,
            'assessment_accuracy': 0.0,
            'last_assessment': None
        }
        
        self.logger.info("Threat Assessment engine initialized")
    
    async def calculate_scores(self, analysis_results: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive threat scores for all monitored entities.
        
        Args:
            analysis_results: Optional pre-computed analysis results
            
        Returns:
            Dict containing threat scores and assessments
        """
        try:
            self.logger.info("Starting threat score calculation")
            
            # Phase 1: Gather analysis data
            if not analysis_results:
                analysis_results = await self._gather_analysis_data()
            
            # Phase 2: Extract threat factors
            threat_factors = await self._extract_threat_factors(analysis_results)
            
            # Phase 3: Calculate entity threat profiles
            entity_profiles = await self._calculate_entity_profiles(threat_factors)
            
            # Phase 4: Perform network threat assessment
            network_assessments = await self._assess_network_threats(entity_profiles, threat_factors)
            
            # Phase 5: Analyze threat trends
            trend_analysis = await self._analyze_threat_trends(entity_profiles)
            
            # Phase 6: Generate mitigation recommendations
            recommendations = await self._generate_mitigation_recommendations(
                entity_profiles, network_assessments
            )
            
            # Phase 7: Update MCP memory if available
            if self.memory_client:
                await self._update_mcp_memory(entity_profiles, network_assessments)
            
            # Update metrics
            self.assessment_metrics.update({
                'entities_assessed': len(entity_profiles),
                'networks_assessed': len(network_assessments),
                'critical_threats_identified': len([p for p in entity_profiles.values() if p.overall_threat_score > 0.8]),
                'average_threat_score': np.mean([p.overall_threat_score for p in entity_profiles.values()]) if entity_profiles else 0.0,
                'last_assessment': datetime.now()
            })
            
            results = {
                'entity_profiles': entity_profiles,
                'network_assessments': network_assessments,
                'threat_factors': threat_factors,
                'trend_analysis': trend_analysis,
                'recommendations': recommendations,
                'metrics': self.assessment_metrics
            }
            
            self.logger.info("Threat score calculation completed successfully")
            return results
            
        except Exception as e:
            self.logger.error("Threat score calculation failed: %s", str(e))
            raise
    
    async def _gather_analysis_data(self) -> Dict[str, Any]:
        """Gather analysis data from all correlation engines"""
        analysis_data = {}
        
        try:
            # Import correlation engines
            from correlation_engines.policy_impact_analyzer import PolicyImpactAnalyzer
            from correlation_engines.tech_transfer_monitor import TechTransferMonitor  
            from correlation_engines.geopolitical_risk_modeler import GeopoliticalRiskModeler
            from correlation_engines.second_order_linker import SecondOrderLinker
            
            self.logger.info("Gathering analysis data from correlation engines...")
            
            # Policy Impact Analysis
            policy_analyzer = PolicyImpactAnalyzer()
            analysis_data['policy_impact'] = await policy_analyzer.correlate()
            self.logger.info("Policy impact analysis data gathered")
            
            # Technology Transfer Analysis
            tech_monitor = TechTransferMonitor()
            analysis_data['tech_transfer'] = await tech_monitor.correlate()
            self.logger.info("Technology transfer analysis data gathered")
            
            # Geopolitical Risk Analysis
            risk_modeler = GeopoliticalRiskModeler()
            analysis_data['geopolitical_risk'] = await risk_modeler.correlate()
            self.logger.info("Geopolitical risk analysis data gathered")
            
            # Second Order Link Analysis
            link_analyzer = SecondOrderLinker()
            analysis_data['second_order_links'] = await link_analyzer.correlate()
            self.logger.info("Second order link analysis data gathered")
            
            # Add summary metrics
            analysis_data['summary'] = {
                'total_entities': len(set(self._extract_all_entities(analysis_data))),
                'total_correlations': self._count_total_correlations(analysis_data),
                'data_quality_score': self._calculate_data_quality_score(analysis_data),
                'analysis_timestamp': datetime.now()
            }
            
            self.logger.info("Analysis data gathering completed successfully")
            return analysis_data
            
        except Exception as e:
            self.logger.error("Failed to gather analysis data: %s", str(e))
            # Return mock data as fallback
            return await self._get_mock_analysis_data()
        
        mock_analysis = {
            'policy_impact': {
                'entities': {
                    'OpenAI': {'influence_score': 0.9, 'policy_risk': 0.7},
                    'Palantir': {'influence_score': 0.85, 'policy_risk': 0.8}
                }
            },
            'tech_transfer': {
                'entities': {
                    'OpenAI': {'transfer_risk': 0.6, 'ip_vulnerability': 0.5},
                    'Palantir': {'transfer_risk': 0.7, 'ip_vulnerability': 0.8}
                }
            },
            'geopolitical_risk': {
                'entities': {
                    'OpenAI': {'geo_risk': 0.65, 'operational_exposure': 0.7},
                    'Palantir': {'geo_risk': 0.75, 'operational_exposure': 0.9}
                }
            },
            'second_order_links': {
                'entities': {
                    'OpenAI': {'hidden_connections': 5, 'influence_network_size': 12},
                    'Palantir': {'hidden_connections': 8, 'influence_network_size': 15}
                }
            },
            'financial_flows': {
                'entities': {
                    'OpenAI': {'financial_risk': 0.5, 'funding_concentration': 0.6},
                    'Palantir': {'financial_risk': 0.4, 'funding_concentration': 0.5}
                }
            }
        }
        
        return mock_analysis
    
    async def _extract_threat_factors(self, analysis_results: Dict[str, Any]) -> List[ThreatFactor]:
        """Extract threat factors from analysis results"""
        threat_factors = []
        
        try:
            # Extract from policy impact analysis
            if 'policy_impact' in analysis_results:
                policy_data = analysis_results['policy_impact']
                
                # Extract from correlation events
                for event in policy_data.get('events', []):
                    if hasattr(event, 'threat_level') and hasattr(event, 'correlation_strength'):
                        threat_severity = self._map_threat_level_to_severity(event.threat_level)
                        if threat_severity > 0.5:
                            factor = ThreatFactor(
                                factor_id=f"policy_event_{event.event_id}",
                                factor_type='political',
                                severity=threat_severity,
                                confidence=event.confidence_level,
                                persistence=0.7,
                                impact_scope='national',
                                description=f"Policy correlation threat: {event.event_type}",
                                data_sources=['policy_impact_analyzer']
                            )
                            threat_factors.append(factor)
                
                # Extract from ROI analysis
                roi_data = policy_data.get('roi_analysis', {})
                for sector, sector_info in roi_data.get('sector_analysis', {}).items():
                    if sector_info.get('campaigns', 0) > 5:  # High activity threshold
                        avg_roi = sector_info.get('returns', 0) / sector_info.get('investment', 1)
                        if avg_roi > 3.0:  # High ROI indicates potential influence
                            factor = ThreatFactor(
                                factor_id=f"influence_concentration_{sector}",
                                factor_type='regulatory',
                                severity=min(avg_roi / 5.0, 1.0),
                                confidence=0.75,
                                persistence=0.8,
                                impact_scope='regional',
                                description=f"High influence concentration in {sector} sector",
                                data_sources=['policy_impact_analyzer']
                            )
                            threat_factors.append(factor)
            
            # Extract from technology transfer analysis
            if 'tech_transfer' in analysis_results:
                tech_data = analysis_results['tech_transfer']
                
                # Extract from transfer events
                for event in tech_data.get('transfer_events', []):
                    if hasattr(event, 'strategic_importance') and event.strategic_importance > 0.7:
                        factor = ThreatFactor(
                            factor_id=f"tech_transfer_{event.event_id}",
                            factor_type='operational',
                            severity=event.strategic_importance,
                            confidence=event.confidence_score,
                            persistence=0.6,
                            impact_scope='global',
                            description=f"Critical technology transfer: {event.technology_domain}",
                            data_sources=['tech_transfer_monitor']
                        )
                        threat_factors.append(factor)
                
                # Extract from risk assessment
                risk_data = tech_data.get('risk_assessment', {})
                if risk_data.get('overall_risk_level') in ['high', 'critical']:
                    for risk_factor in risk_data.get('risk_factors', []):
                        factor = ThreatFactor(
                            factor_id=f"tech_risk_{risk_factor.get('factor')}",
                            factor_type='operational',
                            severity=risk_factor.get('severity', 0.5),
                            confidence=0.8,
                            persistence=0.7,
                            impact_scope='global',
                            description=risk_factor.get('factor', 'Technology transfer risk'),
                            data_sources=['tech_transfer_monitor']
                        )
                        threat_factors.append(factor)
            
            # Extract from geopolitical risk analysis
            if 'geopolitical_risk' in analysis_results:
                geo_data = analysis_results['geopolitical_risk']
                
                # Extract from risk factors
                for risk_factor in geo_data.get('risk_factors', []):
                    combined_risk = risk_factor.severity * risk_factor.probability
                    if combined_risk > 0.6:
                        factor = ThreatFactor(
                            factor_id=f"geo_risk_{risk_factor.factor_id}",
                            factor_type='political',
                            severity=combined_risk,
                            confidence=0.8,
                            persistence=0.9,
                            impact_scope=risk_factor.impact_scope,
                            description=risk_factor.description,
                            data_sources=['geopolitical_risk_modeler']
                        )
                        threat_factors.append(factor)
                
                # Extract from entity profiles
                for profile in geo_data.get('entity_profiles', []):
                    if profile.overall_risk_score > 0.7:
                        factor = ThreatFactor(
                            factor_id=f"entity_geo_risk_{profile.entity_id}",
                            factor_type='operational',
                            severity=profile.overall_risk_score,
                            confidence=0.7,
                            persistence=0.8,
                            impact_scope='regional',
                            description=f"High geopolitical risk for {profile.entity_name}",
                            data_sources=['geopolitical_risk_modeler']
                        )
                        threat_factors.append(factor)
            
            # Extract from second order links
            if 'second_order_links' in analysis_results:
                link_data = analysis_results['second_order_links']
                
                # Extract from high-significance links
                for link in link_data.get('second_order_links', []):
                    if link.significance_score > 0.7:
                        factor = ThreatFactor(
                            factor_id=f"hidden_link_{link.entity_a}_{link.entity_b}",
                            factor_type='reputational',
                            severity=link.significance_score,
                            confidence=link.link_strength,
                            persistence=0.6,
                            impact_scope='regional',
                            description=f"Hidden connection: {link.entity_a} -> {link.entity_b}",
                            data_sources=['second_order_linker']
                        )
                        threat_factors.append(factor)
                
                # Extract from power structures
                power_structures = link_data.get('power_structures', {})
                for structure_type, entities in power_structures.items():
                    if len(entities) > 3:  # Significant power concentration
                        factor = ThreatFactor(
                            factor_id=f"power_concentration_{structure_type}",
                            factor_type='political',
                            severity=min(len(entities) / 10.0, 1.0),
                            confidence=0.6,
                            persistence=0.8,
                            impact_scope='national',
                            description=f"Power concentration in {structure_type}",
                            data_sources=['second_order_linker']
                        )
                        threat_factors.append(factor)
            
            self.logger.info("Extracted %d threat factors from analysis results", len(threat_factors))
            return threat_factors
            
        except Exception as e:
            self.logger.error("Failed to extract threat factors: %s", str(e))
            # Return mock data as fallback
            return await self._get_mock_threat_factors()
        
        # Extract from geopolitical risk analysis
        if 'geopolitical_risk' in analysis_results:
            for entity, data in analysis_results['geopolitical_risk']['entities'].items():
                if data.get('geo_risk', 0) > 0.6:
                    factor = ThreatFactor(
                        factor_id=f"geo_risk_{entity}",
                        factor_type='operational',
                        severity=data['geo_risk'],
                        confidence=0.85,
                        persistence=0.8,
                        impact_scope='global',
                        description=f"Geopolitical operational risk for {entity}",
                        data_sources=['geopolitical_risk_modeler']
                    )
                    threat_factors.append(factor)
        
        # Extract from tech transfer analysis
        if 'tech_transfer' in analysis_results:
            for entity, data in analysis_results['tech_transfer']['entities'].items():
                if data.get('ip_vulnerability', 0) > 0.5:
                    factor = ThreatFactor(
                        factor_id=f"ip_vuln_{entity}",
                        factor_type='regulatory',
                        severity=data['ip_vulnerability'],
                        confidence=0.75,
                        persistence=0.6,
                        impact_scope='regional',
                        description=f"Intellectual property vulnerability for {entity}",
                        data_sources=['tech_transfer_monitor']
                    )
                    threat_factors.append(factor)
        
        # Extract from financial analysis
        if 'financial_flows' in analysis_results:
            for entity, data in analysis_results['financial_flows']['entities'].items():
                if data.get('financial_risk', 0) > 0.4:
                    factor = ThreatFactor(
                        factor_id=f"financial_risk_{entity}",
                        factor_type='financial',
                        severity=data['financial_risk'],
                        confidence=0.9,
                        persistence=0.5,
                        impact_scope='regional',
                        description=f"Financial stability risk for {entity}",
                        data_sources=['financial_flow_analyzer']
                    )
                    threat_factors.append(factor)
        
        self.logger.info("Extracted %d threat factors", len(threat_factors))
        return threat_factors
    
    async def _calculate_entity_profiles(self, threat_factors: List[ThreatFactor]) -> Dict[str, EntityThreatProfile]:
        """Calculate threat profiles for individual entities"""
        entity_profiles = {}
        
        # Group threat factors by entity
        entity_factors = {}
        for factor in threat_factors:
            # Extract entity name from factor_id (simplified approach)
            entity_name = factor.factor_id.split('_')[-1] if '_' in factor.factor_id else 'Unknown'
            
            if entity_name not in entity_factors:
                entity_factors[entity_name] = []
            entity_factors[entity_name].append(factor)
        
        # Calculate profile for each entity
        for entity_name, factors in entity_factors.items():
            profile = await self._calculate_single_entity_profile(entity_name, factors)
            entity_profiles[entity_name] = profile
        
        self.logger.info("Calculated threat profiles for %d entities", len(entity_profiles))
        return entity_profiles
    
    async def _calculate_single_entity_profile(self, entity_name: str, 
                                             factors: List[ThreatFactor]) -> EntityThreatProfile:
        """Calculate threat profile for a single entity"""
        # Calculate weighted threat score
        threat_breakdown = {
            'financial': 0.0,
            'political': 0.0,
            'regulatory': 0.0,
            'operational': 0.0,
            'reputational': 0.0
        }
        
        # Aggregate threat factors by type
        for factor in factors:
            if factor.factor_type in threat_breakdown:
                # Weight by confidence and apply temporal decay
                weighted_score = factor.severity * factor.confidence
                if factor.timestamp:
                    age_days = (datetime.now() - factor.timestamp).days
                    decay = self.scoring_config['temporal_decay_factor'] ** age_days
                    weighted_score *= decay
                
                threat_breakdown[factor.factor_type] = max(
                    threat_breakdown[factor.factor_type], 
                    weighted_score
                )
        
        # Calculate overall threat score
        overall_score = (
            threat_breakdown['financial'] * self.scoring_config['financial_weight'] +
            threat_breakdown['political'] * self.scoring_config['political_weight'] +
            threat_breakdown['regulatory'] * self.scoring_config['regulatory_weight'] +
            threat_breakdown['operational'] * self.scoring_config['operational_weight'] +
            threat_breakdown['reputational'] * self.scoring_config['reputational_weight']
        )
        
        # Apply severity amplifier for high-confidence threats
        high_confidence_factors = [f for f in factors if f.confidence > 0.8]
        if len(high_confidence_factors) > 2:
            overall_score *= self.scoring_config['severity_amplifier']
        
        overall_score = min(1.0, overall_score)  # Cap at 1.0
        
        # Determine threat level
        threat_level = self._determine_threat_level(overall_score)
        
        # Generate risk indicators
        risk_indicators = self._generate_risk_indicators(factors, threat_breakdown)
        
        # Generate mitigation recommendations
        mitigation_recommendations = self._generate_entity_recommendations(
            entity_name, factors, threat_breakdown
        )
        
        # Calculate trend analysis
        trend_analysis = self._calculate_entity_trends(entity_name, overall_score)
        
        profile = EntityThreatProfile(
            entity_id=f"entity_{entity_name.lower().replace(' ', '_')}",
            entity_name=entity_name,
            overall_threat_score=overall_score,
            threat_level=threat_level,
            threat_factors=factors,
            threat_breakdown=threat_breakdown,
            trend_analysis=trend_analysis,
            risk_indicators=risk_indicators,
            mitigation_recommendations=mitigation_recommendations
        )
        
        # Store for historical tracking
        self.entity_profiles[entity_name] = profile
        
        return profile
    
    def _determine_threat_level(self, score: float) -> str:
        """Determine threat level based on score"""
        for level, (min_score, max_score) in self.threat_thresholds.items():
            if min_score <= score < max_score:
                return level
        return 'critical'  # If score is 1.0 or above
    
    def _generate_risk_indicators(self, factors: List[ThreatFactor], 
                                 breakdown: Dict[str, float]) -> List[str]:
        """Generate risk indicators based on threat factors"""
        indicators = []
        
        # High-severity factors
        high_severity = [f for f in factors if f.severity > 0.8]
        if high_severity:
            indicators.append(f"High-severity threats identified: {len(high_severity)}")
        
        # Persistent threats
        persistent = [f for f in factors if f.persistence > 0.7]
        if persistent:
            indicators.append(f"Persistent threat patterns: {len(persistent)}")
        
        # Multi-domain threats
        active_domains = sum(1 for score in breakdown.values() if score > 0.5)
        if active_domains > 2:
            indicators.append(f"Multi-domain threat exposure: {active_domains} domains")
        
        # Global impact scope
        global_threats = [f for f in factors if f.impact_scope == 'global']
        if global_threats:
            indicators.append(f"Global impact threats: {len(global_threats)}")
        
        return indicators
    
    def _generate_entity_recommendations(self, entity_name: str, factors: List[ThreatFactor], 
                                       breakdown: Dict[str, float]) -> List[str]:
        """Generate mitigation recommendations for an entity"""
        recommendations = []
        
        # Political risk mitigation
        if breakdown['political'] > 0.6:
            recommendations.append("Enhance government relations and regulatory compliance programs")
            recommendations.append("Diversify political exposure across multiple jurisdictions")
        
        # Financial risk mitigation
        if breakdown['financial'] > 0.5:
            recommendations.append("Strengthen financial reserves and liquidity management")
            recommendations.append("Diversify funding sources and reduce concentration risk")
        
        # Operational risk mitigation
        if breakdown['operational'] > 0.6:
            recommendations.append("Implement business continuity and crisis management plans")
            recommendations.append("Diversify operational footprint across stable regions")
        
        # Regulatory risk mitigation
        if breakdown['regulatory'] > 0.5:
            recommendations.append("Strengthen compliance frameworks and legal risk management")
            recommendations.append("Engage proactively with regulatory authorities")
        
        # High-persistence threats
        persistent_threats = [f for f in factors if f.persistence > 0.8]
        if persistent_threats:
            recommendations.append("Develop long-term strategic risk mitigation plans")
        
        return recommendations
    
    def _calculate_entity_trends(self, entity_name: str, current_score: float) -> Dict[str, float]:
        """Calculate threat trend analysis for an entity"""
        trends = {
            'score_change_7d': 0.0,
            'score_change_30d': 0.0,
            'volatility': 0.0,
            'trend_direction': 0.0  # -1 improving, 0 stable, 1 deteriorating
        }
        
        # Update historical scores
        if entity_name not in self.historical_scores:
            self.historical_scores[entity_name] = []
        
        self.historical_scores[entity_name].append({
            'score': current_score,
            'timestamp': datetime.now()
        })
        
        # Keep only last 90 days
        cutoff = datetime.now() - timedelta(days=90)
        self.historical_scores[entity_name] = [
            entry for entry in self.historical_scores[entity_name]
            if entry['timestamp'] > cutoff
        ]
        
        history = self.historical_scores[entity_name]
        if len(history) > 1:
            # Calculate score changes
            week_ago = datetime.now() - timedelta(days=7)
            month_ago = datetime.now() - timedelta(days=30)
            
            week_scores = [e['score'] for e in history if e['timestamp'] > week_ago]
            month_scores = [e['score'] for e in history if e['timestamp'] > month_ago]
            
            if len(week_scores) > 1:
                trends['score_change_7d'] = current_score - week_scores[0]
            
            if len(month_scores) > 1:
                trends['score_change_30d'] = current_score - month_scores[0]
            
            # Calculate volatility
            scores = [e['score'] for e in history]
            if len(scores) > 2:
                trends['volatility'] = float(np.std(scores))
            
            # Trend direction
            if trends['score_change_30d'] > 0.1:
                trends['trend_direction'] = 1.0  # Deteriorating
            elif trends['score_change_30d'] < -0.1:
                trends['trend_direction'] = -1.0  # Improving
            else:
                trends['trend_direction'] = 0.0  # Stable
        
        return trends
    
    async def _assess_network_threats(self, entity_profiles: Dict[str, EntityThreatProfile], 
                                    threat_factors: List[ThreatFactor]) -> Dict[str, NetworkThreatAssessment]:
        """Assess network-level threats"""
        network_assessments = {}
        
        # For demonstration, create a sample network assessment
        if len(entity_profiles) > 1:
            entities = list(entity_profiles.keys())
            network_score = np.mean([p.overall_threat_score for p in entity_profiles.values()])
            
            # Identify critical nodes (entities with highest threat scores)
            critical_nodes = sorted(entities, 
                                  key=lambda e: entity_profiles[e].overall_threat_score, 
                                  reverse=True)[:3]
            
            # Identify systemic risks
            systemic_risks = []
            for factor in threat_factors:
                if factor.impact_scope == 'global' and factor.severity > 0.7:
                    systemic_risks.append(factor)
            
            assessment = NetworkThreatAssessment(
                network_id='primary_network',
                network_name='Primary Surveillance Network',
                network_threat_score=float(network_score),
                systemic_risks=systemic_risks,
                critical_nodes=critical_nodes,
                cascade_potential=min(1.0, network_score * 1.2),
                resilience_score=max(0.0, 1.0 - network_score)
            )
            
            network_assessments['primary_network'] = assessment
        
        return network_assessments
    
    async def _analyze_threat_trends(self, entity_profiles: Dict[str, EntityThreatProfile]) -> Dict[str, Any]:
        """Analyze threat trends across the network"""
        trend_analysis = {
            'overall_trend': 'stable',
            'emerging_threats': [],
            'declining_threats': [],
            'volatility_indicators': {},
            'forecast': {}
        }
        
        # Analyze overall trend
        threat_scores = [p.overall_threat_score for p in entity_profiles.values()]
        if threat_scores:
            avg_score = np.mean(threat_scores)
            
            # Simple trend analysis
            if avg_score > 0.7:
                trend_analysis['overall_trend'] = 'deteriorating'
            elif avg_score < 0.3:
                trend_analysis['overall_trend'] = 'improving'
            else:
                trend_analysis['overall_trend'] = 'stable'
        
        # Identify emerging threats
        for name, profile in entity_profiles.items():
            if profile.trend_analysis.get('trend_direction', 0) > 0.5:
                trend_analysis['emerging_threats'].append({
                    'entity': name,
                    'score_change': profile.trend_analysis.get('score_change_30d', 0),
                    'threat_score': profile.overall_threat_score
                })
        
        return trend_analysis
    
    async def _generate_mitigation_recommendations(self, entity_profiles: Dict[str, EntityThreatProfile], 
                                                 network_assessments: Dict[str, NetworkThreatAssessment]) -> List[str]:
        """Generate network-level mitigation recommendations"""
        recommendations = []
        
        # High-threat entities
        high_threat_entities = [
            name for name, profile in entity_profiles.items() 
            if profile.overall_threat_score > 0.7
        ]
        
        if high_threat_entities:
            recommendations.append(
                f"Priority monitoring required for {len(high_threat_entities)} high-threat entities"
            )
        
        # Systemic risks
        systemic_risk_count = sum(
            len(assessment.systemic_risks) 
            for assessment in network_assessments.values()
        )
        
        if systemic_risk_count > 0:
            recommendations.append(
                "Implement network-wide risk mitigation for systemic threats"
            )
        
        # Network resilience
        low_resilience_networks = [
            name for name, assessment in network_assessments.items()
            if assessment.resilience_score < 0.3
        ]
        
        if low_resilience_networks:
            recommendations.append(
                "Strengthen network resilience and redundancy measures"
            )
        
        return recommendations
    
    async def _update_mcp_memory(self, entity_profiles: Dict[str, EntityThreatProfile], 
                               network_assessments: Dict[str, NetworkThreatAssessment]):
        """Update MCP memory with threat assessment results"""
        if not self.memory_client:
            return
        
        try:
            # Create entities for high-threat profiles
            entities = []
            for name, profile in entity_profiles.items():
                if profile.overall_threat_score > 0.6:  # Only high-threat entities
                    entities.append({
                        'name': f"Threat Profile: {profile.entity_name}",
                        'entityType': 'threat_profile',
                        'observations': [
                            f"Overall threat score: {profile.overall_threat_score:.2f}",
                            f"Threat level: {profile.threat_level}",
                            f"Primary risk factors: {', '.join(profile.risk_indicators[:3])}",
                            f"Trend direction: {profile.trend_analysis.get('trend_direction', 0)}"
                        ]
                    })
            
            if entities:
                await self.memory_client.create_entities(entities)
            
            # Create relationships between high-threat entities
            relations = []
            high_threat_entities = [
                name for name, profile in entity_profiles.items() 
                if profile.overall_threat_score > 0.7
            ]
            
            for i, entity1 in enumerate(high_threat_entities):
                for entity2 in high_threat_entities[i+1:]:
                    relations.append({
                        'from': entity1,
                        'to': entity2,
                        'relationType': 'shared_high_threat_classification'
                    })
            
            if relations:
                await self.memory_client.create_relations(relations)
            
            self.logger.info("Updated MCP memory with %d threat entities and %d relations", 
                           len(entities), len(relations))
            
        except Exception as e:
            self.logger.error("Failed to update MCP memory: %s", str(e))
    
    def get_assessment_summary(self) -> Dict[str, Any]:
        """Get assessment summary for reporting"""
        return {
            'module': 'ThreatAssessment',
            'status': 'operational',
            'metrics': self.assessment_metrics,
            'last_update': datetime.now().isoformat()
        }
    
    # Helper methods for real data processing
    def _extract_all_entities(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Extract all unique entities from analysis data."""
        entities = set()
        
        # Extract from policy impact
        if 'policy_impact' in analysis_data:
            for event in analysis_data['policy_impact'].get('events', []):
                if hasattr(event, 'entities_involved'):
                    entities.update(event.entities_involved)
        
        # Extract from tech transfer
        if 'tech_transfer' in analysis_data:
            for event in analysis_data['tech_transfer'].get('transfer_events', []):
                if hasattr(event, 'source_entity'):
                    entities.add(event.source_entity)
                if hasattr(event, 'target_entity'):
                    entities.add(event.target_entity)
        
        # Extract from geopolitical risk
        if 'geopolitical_risk' in analysis_data:
            for profile in analysis_data['geopolitical_risk'].get('entity_profiles', []):
                entities.add(profile.entity_name)
        
        # Extract from second order links
        if 'second_order_links' in analysis_data:
            for link in analysis_data['second_order_links'].get('second_order_links', []):
                entities.add(link.entity_a)
                entities.add(link.entity_b)
        
        return list(entities)
    
    def _count_total_correlations(self, analysis_data: Dict[str, Any]) -> int:
        """Count total correlations across all analysis results."""
        total = 0
        
        if 'policy_impact' in analysis_data:
            total += len(analysis_data['policy_impact'].get('correlations', []))
        if 'tech_transfer' in analysis_data:
            total += len(analysis_data['tech_transfer'].get('transfer_events', []))
        if 'geopolitical_risk' in analysis_data:
            total += len(analysis_data['geopolitical_risk'].get('risk_factors', []))
        if 'second_order_links' in analysis_data:
            total += len(analysis_data['second_order_links'].get('second_order_links', []))
        
        return total
    
    def _calculate_data_quality_score(self, analysis_data: Dict[str, Any]) -> float:
        """Calculate overall data quality score."""
        quality_scores = []
        
        for domain, data in analysis_data.items():
            if domain == 'summary':
                continue
            
            # Basic quality metrics
            has_data = len(data) > 0
            has_metrics = 'metrics' in data
            has_results = any(key in data for key in ['events', 'correlations', 'risk_factors', 'second_order_links'])
            
            domain_score = (has_data + has_metrics + has_results) / 3.0
            quality_scores.append(domain_score)
        
        return np.mean(quality_scores) if quality_scores else 0.0
    
    def _map_threat_level_to_severity(self, threat_level) -> float:
        """Map threat level enum to severity score."""
        if hasattr(threat_level, 'value'):
            threat_level = threat_level.value
        
        threat_level_str = str(threat_level).lower()
        
        severity_map = {
            'benign': 0.1,
            'monitoring': 0.3,
            'noteworthy': 0.5,
            'concerning': 0.7,
            'high_risk': 0.8,
            'critical': 0.9,
            'critical_expansion': 0.95,
            'synthetic_sovereignty': 1.0
        }
        
        return severity_map.get(threat_level_str, 0.5)
    
    async def _get_mock_analysis_data(self) -> Dict[str, Any]:
        """Fallback mock analysis data."""
        return {
            'policy_impact': {
                'events': [],
                'correlations': [],
                'roi_analysis': {'sector_analysis': {}},
                'metrics': {}
            },
            'tech_transfer': {
                'transfer_events': [],
                'risk_assessment': {'overall_risk_level': 'low', 'risk_factors': []},
                'metrics': {}
            },
            'geopolitical_risk': {
                'risk_factors': [],
                'entity_profiles': [],
                'metrics': {}
            },
            'second_order_links': {
                'second_order_links': [],
                'power_structures': {},
                'metrics': {}
            },
            'summary': {
                'total_entities': 0,
                'total_correlations': 0,
                'data_quality_score': 0.5,
                'analysis_timestamp': datetime.now()
            }
        }
    
    async def _get_mock_threat_factors(self) -> List[ThreatFactor]:
        """Fallback mock threat factors."""
        return [
            ThreatFactor(
                factor_id='mock_threat_001',
                factor_type='operational',
                severity=0.6,
                confidence=0.7,
                persistence=0.5,
                impact_scope='regional',
                description='Mock threat factor for testing',
                data_sources=['mock_fallback']
            )
        ]

# Example usage
async def main():
    """Example usage of the Threat Assessment engine"""
    assessment = ThreatAssessment()
    
    # Calculate threat scores
    results = await assessment.calculate_scores()
    
    print(f"Threat Assessment Results:")
    print(f"- Entities assessed: {results['metrics']['entities_assessed']}")
    print(f"- Critical threats: {results['metrics']['critical_threats_identified']}")
    print(f"- Average threat score: {results['metrics']['average_threat_score']:.2f}")
    
    # Display entity profiles
    for name, profile in results['entity_profiles'].items():
        print(f"\n{name}:")
        print(f"  Threat Score: {profile.overall_threat_score:.2f}")
        print(f"  Threat Level: {profile.threat_level}")
        print(f"  Key Risks: {', '.join(profile.risk_indicators[:2])}")

if __name__ == "__main__":
    asyncio.run(main())
