#!/usr/bin/env python3
"""
Narrative Generator - Intelligence Synthesis Module

This module employs Large Language Models (LLMs) to synthesize complex
analytical findings into structured, human-readable intelligence briefings
with confidence scores and evidence citations.

Author: REM-Core Development Team / Forseti Subsystem Team
Classification: Internal Development Use Only
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from enum import Enum

class BriefingType(Enum):
    """Types of intelligence briefings"""
    EXECUTIVE_SUMMARY = "executive_summary"
    TACTICAL_BRIEF = "tactical_brief"
    STRATEGIC_ASSESSMENT = "strategic_assessment"
    THREAT_ALERT = "threat_alert"
    TREND_ANALYSIS = "trend_analysis"

class ConfidenceLevel(Enum):
    """Confidence levels for narrative assertions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class EvidenceCitation:
    """Citation for evidence supporting narrative claims"""
    source_module: str
    data_type: str
    confidence_score: float
    timestamp: datetime
    description: str
    supporting_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NarrativeSection:
    """Section of intelligence narrative"""
    section_id: str
    title: str
    content: str
    confidence_level: ConfidenceLevel
    evidence_citations: List[EvidenceCitation] = field(default_factory=list)
    key_findings: List[str] = field(default_factory=list)
    implications: List[str] = field(default_factory=list)

@dataclass
class IntelligenceBriefing:
    """Complete intelligence briefing"""
    briefing_id: str
    briefing_type: BriefingType
    title: str
    executive_summary: str
    sections: List[NarrativeSection] = field(default_factory=list)
    key_findings: List[str] = field(default_factory=list)
    strategic_implications: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence_assessment: str = ""
    classification: str = "Internal Development Use Only"
    generated_timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class NarrativeGenerator:
    """
    Narrative Generator - Advanced text synthesis engine that transforms
    complex analytical data into structured intelligence narratives.
    
    This generator provides:
    - Multi-format intelligence briefing generation
    - Evidence-based narrative construction
    - Confidence scoring and citation tracking
    - Customizable briefing templates
    - Natural language synthesis
    """
    
    def __init__(self, config_path: str = "config/", mcp_manager=None):
        """
        Initialize the Narrative Generator.
        
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
        
        # Narrative generation configuration
        self.generation_config = {
            'max_briefing_length': 5000,  # words
            'min_confidence_for_inclusion': 0.6,
            'evidence_citation_threshold': 0.7,
            'key_findings_limit': 10,
            'implications_limit': 8,
            'recommendations_limit': 6
        }
        
        # Templates for different briefing types
        self.briefing_templates = self._load_briefing_templates()
        
        # Evidence weighting factors
        self.evidence_weights = {
            'PolicyImpactAnalyzer': 0.9,
            'TechTransferMonitor': 0.85,
            'GeopoliticalRiskModeler': 0.8,
            'SecondOrderLinker': 0.75,
            'ThreatAssessment': 0.95,
            'FinancialFlowAnalyzer': 0.8,
            'PersonnelMovementTracker': 0.7,
            'NetworkEntityMapper': 0.85
        }
        
        # Generated narratives cache
        self.briefing_history = []
        
        # Generation metrics
        self.generation_metrics = {
            'briefings_generated': 0,
            'average_confidence_score': 0.0,
            'evidence_citations_used': 0,
            'average_generation_time': 0.0,
            'last_generation': None
        }
        
        self.logger.info("Narrative Generator initialized")
    
    def _load_briefing_templates(self) -> Dict[BriefingType, Dict[str, Union[str, List[str]]]]:
        """Load briefing templates"""
        templates = {
            BriefingType.EXECUTIVE_SUMMARY: {
                'intro': "Based on comprehensive analysis of available intelligence sources, this executive summary presents key findings and strategic implications for monitored entities and networks.",
                'structure': [
                    'threat_landscape',
                    'key_developments',
                    'strategic_implications',
                    'recommendations'
                ]
            },
            BriefingType.TACTICAL_BRIEF: {
                'intro': "This tactical intelligence brief provides actionable insights and immediate threat assessments based on current analysis.",
                'structure': [
                    'immediate_threats',
                    'tactical_indicators',
                    'operational_recommendations'
                ]
            },
            BriefingType.STRATEGIC_ASSESSMENT: {
                'intro': "This strategic assessment examines long-term trends, emerging patterns, and potential future developments in monitored networks.",
                'structure': [
                    'strategic_trends',
                    'network_evolution',
                    'future_scenarios',
                    'strategic_recommendations'
                ]
            },
            BriefingType.THREAT_ALERT: {
                'intro': "THREAT ALERT: This briefing addresses emerging or escalating threats requiring immediate attention.",
                'structure': [
                    'threat_description',
                    'impact_assessment',
                    'immediate_actions'
                ]
            },
            BriefingType.TREND_ANALYSIS: {
                'intro': "This trend analysis report examines patterns and developments over time in monitored networks.",
                'structure': [
                    'trend_identification',
                    'pattern_analysis',
                    'future_projections'
                ]
            }
        }
        
        return templates
    
    async def generate_briefing(self, analysis_results: Optional[Dict[str, Any]] = None,
                              briefing_type: BriefingType = BriefingType.EXECUTIVE_SUMMARY,
                              target_entities: Optional[List[str]] = None) -> IntelligenceBriefing:
        """
        Generate intelligence briefing from analysis results.
        
        Args:
            analysis_results: Analysis data from correlation engines
            briefing_type: Type of briefing to generate
            target_entities: Specific entities to focus on
            
        Returns:
            Complete intelligence briefing
        """
        try:
            self.logger.info("Starting narrative generation for %s", briefing_type.value)
            start_time = datetime.now()
            
            # Phase 1: Gather and process analysis data
            if not analysis_results:
                analysis_results = await self._gather_analysis_data()
            
            # Phase 2: Extract evidence and citations
            evidence_base = await self._extract_evidence(analysis_results)
            
            # Phase 3: Synthesize key findings
            key_findings = await self._synthesize_key_findings(evidence_base, target_entities)
            
            # Phase 4: Generate narrative sections
            narrative_sections = await self._generate_narrative_sections(
                evidence_base, key_findings, briefing_type
            )
            
            # Phase 5: Create executive summary
            executive_summary = await self._generate_executive_summary(
                key_findings, narrative_sections
            )
            
            # Phase 6: Generate strategic implications and recommendations
            implications = await self._generate_implications(key_findings, evidence_base)
            recommendations = await self._generate_recommendations(implications, evidence_base)
            
            # Phase 7: Assess overall confidence
            confidence_assessment = await self._assess_briefing_confidence(
                narrative_sections, evidence_base
            )
            
            # Phase 8: Compile briefing
            briefing = IntelligenceBriefing(
                briefing_id=f"brief_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                briefing_type=briefing_type,
                title=self._generate_briefing_title(briefing_type, target_entities),
                executive_summary=executive_summary,
                sections=narrative_sections,
                key_findings=key_findings,
                strategic_implications=implications,
                recommendations=recommendations,
                confidence_assessment=confidence_assessment,
                metadata={
                    'generation_time': (datetime.now() - start_time).total_seconds(),
                    'evidence_sources': len(evidence_base),
                    'target_entities': target_entities or [],
                    'analysis_timestamp': analysis_results.get('timestamp', datetime.now().isoformat())
                }
            )
            
            # Phase 9: Update MCP memory if available
            if self.memory_client:
                await self._update_mcp_memory(briefing)
            
            # Update metrics
            generation_time = (datetime.now() - start_time).total_seconds()
            self._update_generation_metrics(briefing, generation_time)
            
            # Store in history
            self.briefing_history.append(briefing)
            
            self.logger.info("Narrative generation completed successfully")
            return briefing
            
        except Exception as e:
            self.logger.error("Narrative generation failed: %s", str(e))
            raise
    
    async def _gather_analysis_data(self) -> Dict[str, Any]:
        """Gather analysis data if not provided"""
        # Mock analysis data for demonstration
        mock_data = {
            'timestamp': datetime.now().isoformat(),
            'threat_scores': {
                'OpenAI': {'overall': 0.85, 'political': 0.9, 'regulatory': 0.8},
                'Palantir': {'overall': 0.78, 'political': 0.7, 'operational': 0.85}
            },
            'policy_analysis': {
                'significant_correlations': [
                    {
                        'entities': ['OpenAI', 'US Congress'],
                        'correlation_type': 'lobbying_influence',
                        'strength': 0.82,
                        'confidence': 0.9
                    }
                ]
            },
            'tech_transfer': {
                'significant_transfers': [
                    {
                        'source': 'Stanford AI Lab',
                        'target': 'OpenAI',
                        'technology': 'Large Language Models',
                        'risk_score': 0.75
                    }
                ]
            },
            'network_analysis': {
                'second_order_links': [
                    {
                        'entity_a': 'Sam Altman',
                        'entity_b': 'Peter Thiel',
                        'intermediary': 'Y Combinator Alumni Network',
                        'significance': 0.88
                    }
                ]
            }
        }
        
        return mock_data
    
    async def _extract_evidence(self, analysis_results: Dict[str, Any]) -> List[EvidenceCitation]:
        """Extract evidence citations from analysis results"""
        evidence_base = []
        
        # Extract from threat scores
        if 'threat_scores' in analysis_results:
            for entity, scores in analysis_results['threat_scores'].items():
                if scores.get('overall', 0) > 0.7:
                    citation = EvidenceCitation(
                        source_module='ThreatAssessment',
                        data_type='threat_score',
                        confidence_score=0.9,
                        timestamp=datetime.now(),
                        description=f"High threat score identified for {entity}",
                        supporting_data=scores
                    )
                    evidence_base.append(citation)
        
        # Extract from policy analysis
        if 'policy_analysis' in analysis_results:
            for correlation in analysis_results['policy_analysis'].get('significant_correlations', []):
                if correlation.get('confidence', 0) > self.generation_config['evidence_citation_threshold']:
                    citation = EvidenceCitation(
                        source_module='PolicyImpactAnalyzer',
                        data_type='correlation',
                        confidence_score=correlation['confidence'],
                        timestamp=datetime.now(),
                        description=f"Significant correlation: {correlation['correlation_type']}",
                        supporting_data=correlation
                    )
                    evidence_base.append(citation)
        
        # Extract from tech transfer analysis
        if 'tech_transfer' in analysis_results:
            for transfer in analysis_results['tech_transfer'].get('significant_transfers', []):
                if transfer.get('risk_score', 0) > 0.6:
                    citation = EvidenceCitation(
                        source_module='TechTransferMonitor',
                        data_type='technology_transfer',
                        confidence_score=0.8,
                        timestamp=datetime.now(),
                        description=f"Technology transfer: {transfer['source']} → {transfer['target']}",
                        supporting_data=transfer
                    )
                    evidence_base.append(citation)
        
        # Extract from network analysis
        if 'network_analysis' in analysis_results:
            for link in analysis_results['network_analysis'].get('second_order_links', []):
                if link.get('significance', 0) > 0.8:
                    citation = EvidenceCitation(
                        source_module='SecondOrderLinker',
                        data_type='network_connection',
                        confidence_score=link['significance'],
                        timestamp=datetime.now(),
                        description=f"Significant connection: {link['entity_a']} ↔ {link['entity_b']}",
                        supporting_data=link
                    )
                    evidence_base.append(citation)
        
        self.logger.info("Extracted %d evidence citations", len(evidence_base))
        return evidence_base
    
    async def _synthesize_key_findings(self, evidence_base: List[EvidenceCitation], 
                                     target_entities: Optional[List[str]]) -> List[str]:
        """Synthesize key findings from evidence"""
        findings = []
        
        # Group evidence by type and analyze patterns
        evidence_by_type = {}
        for citation in evidence_base:
            if citation.data_type not in evidence_by_type:
                evidence_by_type[citation.data_type] = []
            evidence_by_type[citation.data_type].append(citation)
        
        # Generate findings for threat scores
        if 'threat_score' in evidence_by_type:
            high_threat_entities = []
            for citation in evidence_by_type['threat_score']:
                entity = citation.description.split(' ')[-1]  # Extract entity name
                overall_score = citation.supporting_data.get('overall', 0)
                if overall_score > 0.8:
                    high_threat_entities.append((entity, overall_score))
            
            if high_threat_entities:
                high_threat_entities.sort(key=lambda x: x[1], reverse=True)
                top_entity = high_threat_entities[0]
                findings.append(
                    f"Critical threat level identified: {top_entity[0]} exhibits threat score of {top_entity[1]:.2f}, "
                    f"indicating significant risk factors across multiple domains."
                )
        
        # Generate findings for correlations
        if 'correlation' in evidence_by_type:
            strong_correlations = [
                c for c in evidence_by_type['correlation'] 
                if c.confidence_score > 0.85
            ]
            
            if strong_correlations:
                findings.append(
                    f"Strong influence correlations detected: {len(strong_correlations)} high-confidence "
                    f"patterns identified in policy and regulatory domains, suggesting coordinated influence operations."
                )
        
        # Generate findings for tech transfers
        if 'technology_transfer' in evidence_by_type:
            transfer_count = len(evidence_by_type['technology_transfer'])
            if transfer_count > 0:
                findings.append(
                    f"Technology transfer patterns: {transfer_count} significant transfers identified "
                    f"from academic institutions to private sector entities, indicating potential IP migration."
                )
        
        # Generate findings for network connections
        if 'network_connection' in evidence_by_type:
            significant_links = len(evidence_by_type['network_connection'])
            if significant_links > 0:
                findings.append(
                    f"Hidden network connections: {significant_links} second-order relationships discovered, "
                    f"revealing non-obvious influence pathways between key entities."
                )
        
        # Limit findings based on configuration
        findings = findings[:self.generation_config['key_findings_limit']]
        
        return findings
    
    async def _generate_narrative_sections(self, evidence_base: List[EvidenceCitation], 
                                         key_findings: List[str], 
                                         briefing_type: BriefingType) -> List[NarrativeSection]:
        """Generate narrative sections based on evidence and findings"""
        sections = []
        
        # Get template structure
        template = self.briefing_templates.get(briefing_type, {})
        structure = template.get('structure', ['threat_landscape', 'key_developments'])
        
        for section_name in structure:
            section = await self._generate_section(section_name, evidence_base, key_findings)
            if section:
                sections.append(section)
        
        return sections
    
    async def _generate_section(self, section_name: str, evidence_base: List[EvidenceCitation], 
                              key_findings: List[str]) -> Optional[NarrativeSection]:
        """Generate a specific narrative section"""
        
        if section_name == 'threat_landscape':
            return await self._generate_threat_landscape_section(evidence_base)
        elif section_name == 'key_developments':
            return await self._generate_developments_section(evidence_base)
        elif section_name == 'strategic_implications':
            return await self._generate_implications_section(evidence_base)
        elif section_name == 'immediate_threats':
            return await self._generate_immediate_threats_section(evidence_base)
        elif section_name == 'network_evolution':
            return await self._generate_network_evolution_section(evidence_base)
        else:
            # Generic section generation
            return await self._generate_generic_section(section_name, evidence_base)
    
    async def _generate_threat_landscape_section(self, evidence_base: List[EvidenceCitation]) -> NarrativeSection:
        """Generate threat landscape section"""
        threat_evidence = [e for e in evidence_base if e.source_module == 'ThreatAssessment']
        
        content_parts = [
            "Current threat landscape analysis reveals several concerning patterns across monitored entities."
        ]
        
        if threat_evidence:
            high_threat_count = len([e for e in threat_evidence if e.supporting_data.get('overall', 0) > 0.8])
            if high_threat_count > 0:
                content_parts.append(
                    f"Analysis identifies {high_threat_count} entities exhibiting critical threat indicators, "
                    f"with risk factors spanning political, regulatory, and operational domains."
                )
        
        policy_evidence = [e for e in evidence_base if e.source_module == 'PolicyImpactAnalyzer']
        if policy_evidence:
            content_parts.append(
                f"Policy influence analysis reveals {len(policy_evidence)} significant correlations, "
                f"indicating coordinated influence operations with potential regulatory capture implications."
            )
        
        content = " ".join(content_parts)
        
        # Determine confidence level
        avg_confidence = np.mean([e.confidence_score for e in threat_evidence + policy_evidence]) if (threat_evidence + policy_evidence) else 0.5
        confidence_level = self._determine_confidence_level(float(avg_confidence))
        
        section = NarrativeSection(
            section_id='threat_landscape',
            title='Current Threat Landscape',
            content=content,
            confidence_level=confidence_level,
            evidence_citations=threat_evidence + policy_evidence[:3],  # Top 3 policy citations
            key_findings=[
                "Multiple entities show critical threat indicators",
                "Coordinated influence operations detected",
                "Cross-domain risk factor correlation identified"
            ]
        )
        
        return section
    
    async def _generate_developments_section(self, evidence_base: List[EvidenceCitation]) -> NarrativeSection:
        """Generate key developments section"""
        recent_evidence = [
            e for e in evidence_base 
            if (datetime.now() - e.timestamp).days < 7
        ]
        
        content_parts = [
            "Recent intelligence analysis has identified several significant developments requiring attention."
        ]
        
        # Tech transfer developments
        tech_evidence = [e for e in recent_evidence if e.source_module == 'TechTransferMonitor']
        if tech_evidence:
            content_parts.append(
                f"Technology transfer monitoring reveals {len(tech_evidence)} new patterns of "
                f"intellectual property migration from academic institutions to private entities."
            )
        
        # Network developments
        network_evidence = [e for e in recent_evidence if e.source_module == 'SecondOrderLinker']
        if network_evidence:
            content_parts.append(
                f"Network analysis uncovers {len(network_evidence)} previously unknown connections "
                f"between key entities, suggesting coordinated activities."
            )
        
        content = " ".join(content_parts)
        
        avg_confidence = np.mean([e.confidence_score for e in recent_evidence]) if recent_evidence else 0.6
        confidence_level = self._determine_confidence_level(float(avg_confidence))
        
        section = NarrativeSection(
            section_id='key_developments',
            title='Key Recent Developments',
            content=content,
            confidence_level=confidence_level,
            evidence_citations=recent_evidence[:5],  # Top 5 recent citations
            key_findings=[
                "New technology transfer patterns identified",
                "Hidden network connections revealed",
                "Coordinated activities suggested"
            ]
        )
        
        return section
    
    async def _generate_implications_section(self, evidence_base: List[EvidenceCitation]) -> NarrativeSection:
        """Generate strategic implications section"""
        high_confidence_evidence = [e for e in evidence_base if e.confidence_score > 0.8]
        
        content_parts = [
            "Analysis of identified patterns reveals several strategic implications for ongoing monitoring operations."
        ]
        
        if high_confidence_evidence:
            content_parts.append(
                f"High-confidence intelligence indicates potential for systematic influence operations "
                f"across {len(set(e.source_module for e in high_confidence_evidence))} analytical domains."
            )
        
        content_parts.append(
            "These developments suggest the need for enhanced monitoring protocols and "
            "cross-domain correlation analysis to identify emerging threat patterns."
        )
        
        content = " ".join(content_parts)
        
        section = NarrativeSection(
            section_id='strategic_implications',
            title='Strategic Implications',
            content=content,
            confidence_level=ConfidenceLevel.HIGH,
            evidence_citations=high_confidence_evidence[:3],
            implications=[
                "Enhanced monitoring protocols required",
                "Cross-domain correlation analysis needed",
                "Systematic influence operations possible"
            ]
        )
        
        return section
    
    async def _generate_immediate_threats_section(self, evidence_base: List[EvidenceCitation]) -> NarrativeSection:
        """Generate immediate threats section"""
        critical_evidence = [
            e for e in evidence_base 
            if e.confidence_score > 0.85 and 
            e.supporting_data.get('overall', 0) > 0.8
        ]
        
        content = "IMMEDIATE ATTENTION REQUIRED: Critical threat indicators identified requiring urgent response."
        
        if critical_evidence:
            content += f" {len(critical_evidence)} high-confidence threats detected with immediate operational implications."
        
        section = NarrativeSection(
            section_id='immediate_threats',
            title='Immediate Threats',
            content=content,
            confidence_level=ConfidenceLevel.VERY_HIGH,
            evidence_citations=critical_evidence,
            key_findings=["Critical threats require immediate attention"]
        )
        
        return section
    
    async def _generate_network_evolution_section(self, evidence_base: List[EvidenceCitation]) -> NarrativeSection:
        """Generate network evolution section"""
        network_evidence = [e for e in evidence_base if e.source_module == 'SecondOrderLinker']
        
        content = "Network evolution analysis reveals dynamic changes in entity relationships and influence patterns."
        
        if network_evidence:
            significant_count = len([e for e in network_evidence if e.confidence_score > 0.8])
            content += f" {significant_count} significant relationship changes identified with strategic implications."
        
        avg_confidence = np.mean([e.confidence_score for e in network_evidence]) if network_evidence else 0.7
        confidence_level = self._determine_confidence_level(float(avg_confidence))
        
        section = NarrativeSection(
            section_id='network_evolution',
            title='Network Evolution Analysis',
            content=content,
            confidence_level=confidence_level,
            evidence_citations=network_evidence[:4]
        )
        
        return section
    
    async def _generate_generic_section(self, section_name: str, 
                                      evidence_base: List[EvidenceCitation]) -> NarrativeSection:
        """Generate generic section"""
        relevant_evidence = evidence_base[:3]  # Use first 3 pieces of evidence
        
        content = f"Analysis of {section_name.replace('_', ' ')} reveals patterns requiring further investigation."
        
        section = NarrativeSection(
            section_id=section_name,
            title=section_name.replace('_', ' ').title(),
            content=content,
            confidence_level=ConfidenceLevel.MEDIUM,
            evidence_citations=relevant_evidence
        )
        
        return section
    
    def _determine_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """Determine confidence level from numerical score"""
        if confidence_score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.75:
            return ConfidenceLevel.HIGH
        elif confidence_score >= 0.6:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    async def _generate_executive_summary(self, key_findings: List[str], 
                                        narrative_sections: List[NarrativeSection]) -> str:
        """Generate executive summary"""
        summary_parts = [
            "EXECUTIVE SUMMARY",
            "",
            "Comprehensive intelligence analysis reveals significant developments across monitored entities and networks."
        ]
        
        if key_findings:
            summary_parts.append(f"Key findings include: {'; '.join(key_findings[:3])}.")
        
        # High confidence sections
        high_conf_sections = [s for s in narrative_sections if s.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]]
        if high_conf_sections:
            summary_parts.append(f"High-confidence analysis across {len(high_conf_sections)} domains indicates coordinated patterns requiring immediate attention.")
        
        summary_parts.append("Continued monitoring and enhanced analytical focus recommended.")
        
        return " ".join(summary_parts)
    
    async def _generate_implications(self, key_findings: List[str], 
                                   evidence_base: List[EvidenceCitation]) -> List[str]:
        """Generate strategic implications"""
        implications = []
        
        # High threat implications
        threat_evidence = [e for e in evidence_base if e.source_module == 'ThreatAssessment']
        if threat_evidence:
            implications.append("Enhanced threat monitoring protocols required for critical entities")
        
        # Policy implications
        policy_evidence = [e for e in evidence_base if e.source_module == 'PolicyImpactAnalyzer']
        if policy_evidence:
            implications.append("Potential regulatory capture and influence operations detected")
        
        # Network implications
        network_evidence = [e for e in evidence_base if e.source_module == 'SecondOrderLinker']
        if network_evidence:
            implications.append("Hidden influence networks may facilitate coordinated activities")
        
        # Tech transfer implications
        tech_evidence = [e for e in evidence_base if e.source_module == 'TechTransferMonitor']
        if tech_evidence:
            implications.append("Intellectual property migration patterns suggest strategic technology acquisition")
        
        return implications[:self.generation_config['implications_limit']]
    
    async def _generate_recommendations(self, implications: List[str], 
                                      evidence_base: List[EvidenceCitation]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Monitoring recommendations
        high_conf_evidence = [e for e in evidence_base if e.confidence_score > 0.8]
        if len(high_conf_evidence) > 3:
            recommendations.append("Increase monitoring frequency for entities with critical threat indicators")
        
        # Analysis recommendations
        if len(set(e.source_module for e in evidence_base)) > 3:
            recommendations.append("Implement cross-domain correlation analysis to identify systematic patterns")
        
        # Response recommendations
        critical_evidence = [e for e in evidence_base if e.supporting_data.get('overall', 0) > 0.8]
        if critical_evidence:
            recommendations.append("Develop contingency response plans for highest-risk entities")
        
        # General recommendations
        recommendations.extend([
            "Maintain continuous intelligence collection across all monitored networks",
            "Enhance human analysis capabilities for complex pattern recognition",
            "Coordinate with relevant stakeholders on threat mitigation strategies"
        ])
        
        return recommendations[:self.generation_config['recommendations_limit']]
    
    async def _assess_briefing_confidence(self, narrative_sections: List[NarrativeSection], 
                                        evidence_base: List[EvidenceCitation]) -> str:
        """Assess overall briefing confidence"""
        # Calculate average confidence across sections
        section_confidences = [self._confidence_to_score(s.confidence_level) for s in narrative_sections]
        evidence_confidences = [e.confidence_score for e in evidence_base]
        
        overall_confidence = (np.mean(section_confidences) + np.mean(evidence_confidences)) / 2 if (section_confidences and evidence_confidences) else 0.5
        
        confidence_level = self._determine_confidence_level(float(overall_confidence))
        
        assessment = f"Overall briefing confidence: {confidence_level.value.upper()} ({overall_confidence:.2f}). "
        
        if confidence_level == ConfidenceLevel.VERY_HIGH:
            assessment += "Analysis supported by multiple high-confidence sources across domains."
        elif confidence_level == ConfidenceLevel.HIGH:
            assessment += "Analysis supported by reliable sources with strong correlation patterns."
        elif confidence_level == ConfidenceLevel.MEDIUM:
            assessment += "Analysis based on available evidence with moderate confidence levels."
        else:
            assessment += "Analysis preliminary; additional evidence collection recommended."
        
        return assessment
    
    def _confidence_to_score(self, confidence_level: ConfidenceLevel) -> float:
        """Convert confidence level to numerical score"""
        mapping = {
            ConfidenceLevel.LOW: 0.4,
            ConfidenceLevel.MEDIUM: 0.65,
            ConfidenceLevel.HIGH: 0.8,
            ConfidenceLevel.VERY_HIGH: 0.95
        }
        return mapping.get(confidence_level, 0.5)
    
    def _generate_briefing_title(self, briefing_type: BriefingType, 
                                target_entities: Optional[List[str]]) -> str:
        """Generate briefing title"""
        type_titles = {
            BriefingType.EXECUTIVE_SUMMARY: "Executive Intelligence Summary",
            BriefingType.TACTICAL_BRIEF: "Tactical Intelligence Brief",
            BriefingType.STRATEGIC_ASSESSMENT: "Strategic Assessment",
            BriefingType.THREAT_ALERT: "THREAT ALERT",
            BriefingType.TREND_ANALYSIS: "Trend Analysis Report"
        }
        
        base_title = type_titles.get(briefing_type, "Intelligence Report")
        
        if target_entities:
            entity_suffix = f" - {', '.join(target_entities[:2])}"
            if len(target_entities) > 2:
                entity_suffix += f" (+{len(target_entities)-2} others)"
            base_title += entity_suffix
        
        timestamp = datetime.now().strftime("%Y-%m-%d")
        return f"{base_title} ({timestamp})"
    
    def _update_generation_metrics(self, briefing: IntelligenceBriefing, generation_time: float):
        """Update generation metrics"""
        self.generation_metrics['briefings_generated'] += 1
        self.generation_metrics['evidence_citations_used'] += sum(len(s.evidence_citations) for s in briefing.sections)
        
        # Update average generation time
        total_briefings = self.generation_metrics['briefings_generated']
        current_avg = self.generation_metrics['average_generation_time']
        self.generation_metrics['average_generation_time'] = (current_avg * (total_briefings - 1) + generation_time) / total_briefings
        
        self.generation_metrics['last_generation'] = datetime.now()
    
    async def _update_mcp_memory(self, briefing: IntelligenceBriefing):
        """Update MCP memory with generated briefing"""
        if not self.memory_client:
            return
        
        try:
            # Create entity for the briefing
            entity = {
                'name': f"Intelligence Briefing: {briefing.title}",
                'entityType': 'intelligence_briefing',
                'observations': [
                    f"Briefing type: {briefing.briefing_type.value}",
                    f"Key findings: {len(briefing.key_findings)}",
                    f"Strategic implications: {len(briefing.strategic_implications)}",
                    f"Generated: {briefing.generated_timestamp.strftime('%Y-%m-%d %H:%M')}",
                    f"Confidence: {briefing.confidence_assessment[:100]}..."
                ]
            }
            
            await self.memory_client.create_entities([entity])
            
        except Exception as e:
            self.logger.error("Failed to update MCP memory: %s", str(e))
    
    def get_generation_summary(self) -> Dict[str, Any]:
        """Get generation summary for reporting"""
        return {
            'module': 'NarrativeGenerator',
            'status': 'operational',
            'metrics': self.generation_metrics,
            'last_update': datetime.now().isoformat()
        }

# Example usage
async def main():
    """Example usage of the Narrative Generator"""
    generator = NarrativeGenerator()
    
    # Generate briefing
    briefing = await generator.generate_briefing(
        briefing_type=BriefingType.EXECUTIVE_SUMMARY,
        target_entities=['OpenAI', 'Palantir']
    )
    
    print(f"Generated Briefing: {briefing.title}")
    print(f"Executive Summary: {briefing.executive_summary[:200]}...")
    print(f"Sections: {len(briefing.sections)}")
    print(f"Key Findings: {len(briefing.key_findings)}")
    print(f"Confidence: {briefing.confidence_assessment}")

if __name__ == "__main__":
    import numpy as np
    asyncio.run(main())
