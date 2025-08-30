#!/usr/bin/env python3
"""
Animation Templates System
Provides structured templates for different types of CSS animations
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class AnimationType(Enum):
    KEYFRAMES = "keyframes"
    TRANSITION = "transition"
    TRANSFORM = "transform"
    HOVER_EFFECT = "hover_effect"
    LOADING_ANIMATION = "loading_animation"
    ENTRANCE_ANIMATION = "entrance_animation"
    EXIT_ANIMATION = "exit_animation"

@dataclass
class AnimationTemplate:
    name: str
    type: AnimationType
    css_code: str
    html_structure: str
    description: str
    use_cases: List[str]
    properties: Dict[str, str]
    complexity_level: str  # "beginner", "intermediate", "advanced"

class AnimationTemplateManager:
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, AnimationTemplate]:
        """Initialize all animation templates"""
        templates = {}
        
        # Keyframes Templates
        templates["fade_in"] = AnimationTemplate(
            name="Fade In",
            type=AnimationType.KEYFRAMES,
            css_code="""
@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

.fade-in {
    animation: fadeIn 0.5s ease-in-out;
}""",
            html_structure='<div class="fade-in">Content here</div>',
            description="Simple fade in animation using keyframes",
            use_cases=["Page load animations", "Modal appearances", "Content reveals"],
            properties={"duration": "0.5s", "timing-function": "ease-in-out", "fill-mode": "forwards"},
            complexity_level="beginner"
        )
        
        templates["slide_in_left"] = AnimationTemplate(
            name="Slide In Left",
            type=AnimationType.KEYFRAMES,
            css_code="""
@keyframes slideInLeft {
    from {
        transform: translateX(-100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.slide-in-left {
    animation: slideInLeft 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}""",
            html_structure='<div class="slide-in-left">Content slides from left</div>',
            description="Element slides in from the left side",
            use_cases=["Navigation menus", "Sidebar content", "Card animations"],
            properties={"duration": "0.6s", "timing-function": "cubic-bezier(0.25, 0.46, 0.45, 0.94)"},
            complexity_level="intermediate"
        )
        
        templates["bounce"] = AnimationTemplate(
            name="Bounce",
            type=AnimationType.KEYFRAMES,
            css_code="""
@keyframes bounce {
    0%, 20%, 53%, 80%, 100% {
        animation-timing-function: cubic-bezier(0.215, 0.61, 0.355, 1);
        transform: translate3d(0, 0, 0);
    }
    40%, 43% {
        animation-timing-function: cubic-bezier(0.755, 0.05, 0.855, 0.06);
        transform: translate3d(0, -30px, 0);
    }
    70% {
        animation-timing-function: cubic-bezier(0.755, 0.05, 0.855, 0.06);
        transform: translate3d(0, -15px, 0);
    }
    90% {
        transform: translate3d(0, -4px, 0);
    }
}

.bounce {
    animation: bounce 1s;
}""",
            html_structure='<div class="bounce">Bouncing element</div>',
            description="Complex bounce animation with multiple keyframes",
            use_cases=["Button interactions", "Success notifications", "Attention grabbers"],
            properties={"duration": "1s", "timing-function": "variable", "transform": "translate3d"},
            complexity_level="advanced"
        )
        
        # Transition Templates
        templates["smooth_hover"] = AnimationTemplate(
            name="Smooth Hover",
            type=AnimationType.TRANSITION,
            css_code="""
.smooth-hover {
    background-color: #3498db;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    transition: all 0.3s ease;
    cursor: pointer;
}

.smooth-hover:hover {
    background-color: #2980b9;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}""",
            html_structure='<button class="smooth-hover">Hover me</button>',
            description="Smooth transition on hover with multiple properties",
            use_cases=["Buttons", "Cards", "Interactive elements"],
            properties={"duration": "0.3s", "timing-function": "ease", "properties": "all"},
            complexity_level="beginner"
        )
        
        templates["color_transition"] = AnimationTemplate(
            name="Color Transition",
            type=AnimationType.TRANSITION,
            css_code="""
.color-transition {
    background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
    background-size: 400% 400%;
    transition: background-position 0.5s ease;
    padding: 20px;
    color: white;
    text-align: center;
}

.color-transition:hover {
    background-position: 100% 0%;
}""",
            html_structure='<div class="color-transition">Gradient transition</div>',
            description="Animated gradient background transition",
            use_cases=["Hero sections", "Call-to-action buttons", "Background effects"],
            properties={"duration": "0.5s", "timing-function": "ease", "background-size": "400%"},
            complexity_level="intermediate"
        )
        
        # Transform Templates
        templates["scale_rotate"] = AnimationTemplate(
            name="Scale and Rotate",
            type=AnimationType.TRANSFORM,
            css_code="""
.scale-rotate {
    width: 100px;
    height: 100px;
    background-color: #e74c3c;
    margin: 50px;
    transition: transform 0.3s ease;
}

.scale-rotate:hover {
    transform: scale(1.2) rotate(15deg);
}""",
            html_structure='<div class="scale-rotate"></div>',
            description="Combined scale and rotation transform",
            use_cases=["Icons", "Images", "Interactive elements"],
            properties={"scale": "1.2", "rotation": "15deg", "duration": "0.3s"},
            complexity_level="beginner"
        )
        
        # Loading Animation Templates
        templates["spinner"] = AnimationTemplate(
            name="Loading Spinner",
            type=AnimationType.LOADING_ANIMATION,
            css_code="""
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
}""",
            html_structure='<div class="spinner"></div>',
            description="Classic loading spinner animation",
            use_cases=["Loading states", "Form submissions", "Data fetching"],
            properties={"duration": "1s", "timing-function": "linear", "iteration-count": "infinite"},
            complexity_level="beginner"
        )
        
        templates["pulse_dots"] = AnimationTemplate(
            name="Pulse Dots",
            type=AnimationType.LOADING_ANIMATION,
            css_code="""
@keyframes pulse {
    0%, 80%, 100% {
        transform: scale(0);
        opacity: 1;
    }
    40% {
        transform: scale(1);
        opacity: 0.5;
    }
}

.pulse-dots {
    display: flex;
    gap: 5px;
}

.pulse-dots div {
    width: 10px;
    height: 10px;
    background-color: #3498db;
    border-radius: 50%;
    animation: pulse 1.4s ease-in-out infinite both;
}

.pulse-dots div:nth-child(1) { animation-delay: -0.32s; }
.pulse-dots div:nth-child(2) { animation-delay: -0.16s; }
.pulse-dots div:nth-child(3) { animation-delay: 0s; }""",
            html_structure='<div class="pulse-dots"><div></div><div></div><div></div></div>',
            description="Three pulsing dots loading animation",
            use_cases=["Loading indicators", "Processing states", "Waiting animations"],
            properties={"duration": "1.4s", "timing-function": "ease-in-out", "stagger": "0.16s"},
            complexity_level="intermediate"
        )
        
        return templates
    
    def get_template(self, name: str) -> Optional[AnimationTemplate]:
        """Get a specific template by name"""
        return self.templates.get(name)
    
    def get_templates_by_type(self, animation_type: AnimationType) -> List[AnimationTemplate]:
        """Get all templates of a specific type"""
        return [template for template in self.templates.values() 
                if template.type == animation_type]
    
    def get_templates_by_complexity(self, complexity: str) -> List[AnimationTemplate]:
        """Get templates by complexity level"""
        return [template for template in self.templates.values() 
                if template.complexity_level == complexity]
    
    def search_templates(self, query: str) -> List[AnimationTemplate]:
        """Search templates by name, description, or use cases"""
        query_lower = query.lower()
        results = []
        
        for template in self.templates.values():
            if (query_lower in template.name.lower() or 
                query_lower in template.description.lower() or 
                any(query_lower in use_case.lower() for use_case in template.use_cases)):
                results.append(template)
        
        return results
    
    def get_all_templates(self) -> List[AnimationTemplate]:
        """Get all available templates"""
        return list(self.templates.values())
    
    def generate_template_response(self, template: AnimationTemplate) -> str:
        """Generate a formatted response for a template"""
        response = f"## {template.name}\n\n"
        response += f"**Type:** {template.type.value}\n"
        response += f"**Complexity:** {template.complexity_level}\n\n"
        response += f"**Description:** {template.description}\n\n"
        
        response += "**Use Cases:**\n"
        for use_case in template.use_cases:
            response += f"- {use_case}\n"
        response += "\n"
        
        response += "**CSS Code:**\n```css\n"
        response += template.css_code
        response += "\n```\n\n"
        
        response += "**HTML Structure:**\n```html\n"
        response += template.html_structure
        response += "\n```\n\n"
        
        if template.properties:
            response += "**Key Properties:**\n"
            for prop, value in template.properties.items():
                response += f"- **{prop}:** {value}\n"
        
        return response

# Global instance
animation_templates = AnimationTemplateManager()