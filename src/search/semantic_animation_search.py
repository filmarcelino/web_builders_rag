#!/usr/bin/env python3
"""
Semantic Animation Search System
Specialized semantic search for animation-related queries
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import json

class AnimationConcept(Enum):
    MOVEMENT = "movement"
    TIMING = "timing"
    EASING = "easing"
    TRANSFORMATION = "transformation"
    INTERACTION = "interaction"
    VISUAL_EFFECT = "visual_effect"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"

@dataclass
class SemanticMatch:
    term: str
    concept: AnimationConcept
    confidence: float
    related_terms: List[str]
    css_properties: List[str]

class AnimationSemanticSearch:
    def __init__(self):
        self.semantic_mappings = self._initialize_semantic_mappings()
        self.animation_synonyms = self._initialize_synonyms()
        self.css_property_mappings = self._initialize_css_mappings()
        self.intent_patterns = self._initialize_intent_patterns()
    
    def _initialize_semantic_mappings(self) -> Dict[str, Dict]:
        """Initialize semantic mappings for animation concepts"""
        return {
            # Movement concepts
            "slide": {
                "concept": AnimationConcept.MOVEMENT,
                "confidence": 0.9,
                "related_terms": ["translate", "move", "glide", "shift", "pan"],
                "css_properties": ["transform", "translateX", "translateY", "left", "top"]
            },
            "fade": {
                "concept": AnimationConcept.VISUAL_EFFECT,
                "confidence": 0.95,
                "related_terms": ["opacity", "appear", "disappear", "transparent", "visible"],
                "css_properties": ["opacity", "visibility"]
            },
            "bounce": {
                "concept": AnimationConcept.MOVEMENT,
                "confidence": 0.85,
                "related_terms": ["spring", "elastic", "rebound", "jump"],
                "css_properties": ["transform", "translateY", "animation-timing-function"]
            },
            "rotate": {
                "concept": AnimationConcept.TRANSFORMATION,
                "confidence": 0.9,
                "related_terms": ["spin", "turn", "revolve", "twist"],
                "css_properties": ["transform", "rotate", "rotateX", "rotateY", "rotateZ"]
            },
            "scale": {
                "concept": AnimationConcept.TRANSFORMATION,
                "confidence": 0.9,
                "related_terms": ["zoom", "resize", "grow", "shrink", "expand"],
                "css_properties": ["transform", "scale", "scaleX", "scaleY"]
            },
            "hover": {
                "concept": AnimationConcept.INTERACTION,
                "confidence": 0.95,
                "related_terms": ["mouseover", "mouse enter", "on hover", "interactive"],
                "css_properties": [":hover", "transition", "transform"]
            },
            "smooth": {
                "concept": AnimationConcept.TIMING,
                "confidence": 0.8,
                "related_terms": ["fluid", "seamless", "gradual", "gentle"],
                "css_properties": ["transition", "ease", "ease-in-out"]
            },
            "fast": {
                "concept": AnimationConcept.TIMING,
                "confidence": 0.85,
                "related_terms": ["quick", "rapid", "speedy", "instant"],
                "css_properties": ["animation-duration", "transition-duration"]
            },
            "slow": {
                "concept": AnimationConcept.TIMING,
                "confidence": 0.85,
                "related_terms": ["gradual", "delayed", "leisurely"],
                "css_properties": ["animation-duration", "transition-duration", "animation-delay"]
            },
            "loading": {
                "concept": AnimationConcept.VISUAL_EFFECT,
                "confidence": 0.9,
                "related_terms": ["spinner", "progress", "waiting", "buffering"],
                "css_properties": ["animation", "keyframes", "animation-iteration-count"]
            },
            "keyframes": {
                "concept": AnimationConcept.TIMING,
                "confidence": 0.95,
                "related_terms": ["@keyframes", "animation steps", "timeline"],
                "css_properties": ["@keyframes", "animation-name", "animation-duration"]
            },
            "transition": {
                "concept": AnimationConcept.TIMING,
                "confidence": 0.95,
                "related_terms": ["change", "morph", "transform", "shift"],
                "css_properties": ["transition", "transition-property", "transition-duration"]
            },
            "elastic": {
                "concept": AnimationConcept.EASING,
                "confidence": 0.8,
                "related_terms": ["spring", "bounce", "rubber", "flexible"],
                "css_properties": ["cubic-bezier", "animation-timing-function"]
            },
            "ease": {
                "concept": AnimationConcept.EASING,
                "confidence": 0.9,
                "related_terms": ["smooth", "natural", "gradual"],
                "css_properties": ["ease", "ease-in", "ease-out", "ease-in-out"]
            },
            "performance": {
                "concept": AnimationConcept.PERFORMANCE,
                "confidence": 0.85,
                "related_terms": ["optimize", "smooth", "60fps", "gpu", "hardware acceleration"],
                "css_properties": ["transform", "opacity", "will-change", "transform3d"]
            },
            "accessible": {
                "concept": AnimationConcept.ACCESSIBILITY,
                "confidence": 0.8,
                "related_terms": ["reduced motion", "prefers-reduced-motion", "a11y"],
                "css_properties": ["@media (prefers-reduced-motion)", "animation-play-state"]
            }
        }
    
    def _initialize_synonyms(self) -> Dict[str, List[str]]:
        """Initialize synonym mappings for animation terms"""
        return {
            "animate": ["animation", "animated", "animating", "motion", "movement"],
            "move": ["movement", "moving", "translate", "shift", "slide"],
            "show": ["appear", "reveal", "display", "fade in", "enter"],
            "hide": ["disappear", "conceal", "fade out", "exit", "remove"],
            "button": ["btn", "click", "interactive", "clickable"],
            "card": ["panel", "container", "box", "component"],
            "menu": ["navigation", "nav", "dropdown", "sidebar"],
            "modal": ["popup", "dialog", "overlay", "lightbox"],
            "image": ["img", "picture", "photo", "graphic"],
            "text": ["typography", "font", "content", "copy"]
        }
    
    def _initialize_css_mappings(self) -> Dict[str, List[str]]:
        """Initialize CSS property to concept mappings"""
        return {
            "transform": ["translate", "rotate", "scale", "skew", "matrix"],
            "transition": ["property", "duration", "timing-function", "delay"],
            "animation": ["name", "duration", "timing-function", "delay", "iteration-count", "direction"],
            "opacity": ["fade", "transparent", "visible", "alpha"],
            "keyframes": ["from", "to", "percentage", "steps"]
        }
    
    def _initialize_intent_patterns(self) -> List[Dict]:
        """Initialize patterns for detecting user intent"""
        return [
            {
                "pattern": r"how to (make|create|add) (.*?) (animation|effect)",
                "intent": "tutorial",
                "confidence": 0.9
            },
            {
                "pattern": r"(.*?) on hover",
                "intent": "hover_effect",
                "confidence": 0.95
            },
            {
                "pattern": r"loading (.*?)",
                "intent": "loading_animation",
                "confidence": 0.9
            },
            {
                "pattern": r"smooth (.*?) transition",
                "intent": "smooth_transition",
                "confidence": 0.85
            },
            {
                "pattern": r"(fade|slide|bounce|rotate|scale) (in|out|up|down|left|right)",
                "intent": "directional_animation",
                "confidence": 0.9
            },
            {
                "pattern": r"(fast|slow|quick|gradual) (.*?)",
                "intent": "timing_control",
                "confidence": 0.8
            },
            {
                "pattern": r"(performance|optimize|smooth) (.*?) animation",
                "intent": "performance_optimization",
                "confidence": 0.85
            },
            {
                "pattern": r"accessible (.*?) animation",
                "intent": "accessibility",
                "confidence": 0.9
            }
        ]
    
    def analyze_query(self, query: str) -> Dict:
        """Analyze a query for animation-related semantic meaning"""
        query_lower = query.lower()
        
        # Extract semantic matches
        semantic_matches = self._extract_semantic_matches(query_lower)
        
        # Detect intent patterns
        intent_matches = self._detect_intent_patterns(query_lower)
        
        # Find synonyms and related terms
        expanded_terms = self._expand_with_synonyms(query_lower)
        
        # Extract CSS properties mentioned
        css_properties = self._extract_css_properties(query_lower)
        
        # Calculate overall animation relevance score
        animation_score = self._calculate_animation_score(semantic_matches, css_properties)
        
        return {
            "original_query": query,
            "semantic_matches": semantic_matches,
            "intent_matches": intent_matches,
            "expanded_terms": expanded_terms,
            "css_properties": css_properties,
            "animation_score": animation_score,
            "is_animation_query": animation_score > 0.3
        }
    
    def _extract_semantic_matches(self, query: str) -> List[SemanticMatch]:
        """Extract semantic matches from query"""
        matches = []
        
        for term, mapping in self.semantic_mappings.items():
            if term in query or any(related in query for related in mapping["related_terms"]):
                match = SemanticMatch(
                    term=term,
                    concept=mapping["concept"],
                    confidence=mapping["confidence"],
                    related_terms=mapping["related_terms"],
                    css_properties=mapping["css_properties"]
                )
                matches.append(match)
        
        return sorted(matches, key=lambda x: x.confidence, reverse=True)
    
    def _detect_intent_patterns(self, query: str) -> List[Dict]:
        """Detect intent patterns in query"""
        matches = []
        
        for pattern_info in self.intent_patterns:
            pattern = pattern_info["pattern"]
            match = re.search(pattern, query, re.IGNORECASE)
            
            if match:
                matches.append({
                    "intent": pattern_info["intent"],
                    "confidence": pattern_info["confidence"],
                    "matched_text": match.group(0),
                    "groups": match.groups()
                })
        
        return matches
    
    def _expand_with_synonyms(self, query: str) -> List[str]:
        """Expand query with synonyms"""
        expanded = set([query])
        
        for base_term, synonyms in self.animation_synonyms.items():
            if base_term in query:
                for synonym in synonyms:
                    expanded.add(query.replace(base_term, synonym))
            
            for synonym in synonyms:
                if synonym in query:
                    expanded.add(query.replace(synonym, base_term))
                    for other_synonym in synonyms:
                        if other_synonym != synonym:
                            expanded.add(query.replace(synonym, other_synonym))
        
        return list(expanded)
    
    def _extract_css_properties(self, query: str) -> List[str]:
        """Extract CSS properties mentioned in query"""
        properties = []
        
        # Direct CSS property mentions
        css_keywords = [
            "transform", "transition", "animation", "opacity", "keyframes",
            "translate", "rotate", "scale", "skew", "ease", "linear",
            "cubic-bezier", "steps", "hover", "active", "focus"
        ]
        
        for keyword in css_keywords:
            if keyword in query:
                properties.append(keyword)
        
        return properties
    
    def _calculate_animation_score(self, semantic_matches: List[SemanticMatch], css_properties: List[str]) -> float:
        """Calculate overall animation relevance score"""
        score = 0.0
        
        # Score from semantic matches
        for match in semantic_matches:
            score += match.confidence * 0.3
        
        # Score from CSS properties
        score += len(css_properties) * 0.2
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def generate_search_suggestions(self, query: str) -> List[str]:
        """Generate search suggestions based on semantic analysis"""
        analysis = self.analyze_query(query)
        suggestions = []
        
        # Add suggestions based on semantic matches
        for match in analysis["semantic_matches"][:3]:
            for related_term in match.related_terms[:2]:
                suggestion = query.replace(match.term, related_term)
                if suggestion != query and suggestion not in suggestions:
                    suggestions.append(suggestion)
        
        # Add CSS property-based suggestions
        for prop in analysis["css_properties"][:2]:
            suggestions.append(f"{query} {prop}")
            suggestions.append(f"{prop} {query}")
        
        return suggestions[:5]
    
    def get_related_concepts(self, query: str) -> List[AnimationConcept]:
        """Get related animation concepts for a query"""
        analysis = self.analyze_query(query)
        concepts = set()
        
        for match in analysis["semantic_matches"]:
            concepts.add(match.concept)
        
        return list(concepts)
    
    def enhance_search_terms(self, query: str) -> List[str]:
        """Enhance search terms with animation-specific vocabulary"""
        analysis = self.analyze_query(query)
        enhanced_terms = [query]
        
        # Add terms from semantic matches
        for match in analysis["semantic_matches"]:
            enhanced_terms.extend(match.related_terms)
            enhanced_terms.extend(match.css_properties)
        
        # Add expanded terms
        enhanced_terms.extend(analysis["expanded_terms"])
        
        # Remove duplicates and return
        return list(set(enhanced_terms))

# Global instance
semantic_search = AnimationSemanticSearch()