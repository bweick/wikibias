# Expert Pipeline Specification

## Expert Profile Specification
```python
from pydantic import BaseModel
from typing import List, Optional

class Expertise(BaseModel):
    # Academic and Professional Background
    degrees: List[str]           # e.g., ["Ph.D. Comparative Literature", "MS Computer Science"]
    certifications: Optional[List[str]] = None  # e.g., ["Licensed Clinical Psychologist"]
    
    # Core Knowledge Areas
    primary_fields: List[str]    # e.g., ["Machine Learning", "Constitutional Law"]
    research_areas: List[str]    # e.g., ["Privacy in Social Networks", "Climate Change Economics"]
    methodologies: List[str]     # e.g., ["Statistical Analysis", "Ethnographic Research"]
    
    # Scope of Expertise
    temporal_focus: Optional[List[str]] = None    # e.g., ["Contemporary", "18th Century"]
    geographic_focus: Optional[List[str]] = None  # e.g., ["Southeast Asia", "Global Markets"]
    theoretical_frameworks: Optional[List[str]] = None  # e.g., ["Critical Theory"]
    
    # Technical Skills
    tools: Optional[List[str]] = None  # e.g., ["SPSS", "GIS", "Content Analysis Software"]
    languages: Optional[List[str]] = None  # Both human and programming languages

class ExpertProfile(BaseModel):
    expertise: Expertise
    specializations: List[str]   # Free-form tags for specific expertise
```

## Example Expert Profile
```python
expert_example = ExpertProfile(
    expertise=Expertise(
        # Academic and Professional Background
        degrees=[
            "Ph.D. Cognitive Science",
            "MS Computer Science",
            "BA Psychology"
        ],
        certifications=[
            "Machine Learning Specialization",
            "Research Ethics Certification"
        ],
        
        # Core Knowledge Areas
        primary_fields=[
            "Artificial Intelligence",
            "Human-Computer Interaction",
            "Research Methodology"
        ],
        research_areas=[
            "Algorithmic Bias",
            "Natural Language Processing",
            "Decision Making Systems"
        ],
        methodologies=[
            "Statistical Analysis",
            "Experimental Design",
            "Qualitative User Studies",
            "Neural Network Architecture"
        ],
        
        # Scope of Expertise
        temporal_focus=[
            "Contemporary",
            "Emerging Technologies"
        ],
        geographic_focus=[
            "Global Technology Markets",
            "Cross-cultural UI/UX"
        ],
        theoretical_frameworks=[
            "Information Processing Theory",
            "Distributed Cognition",
            "Social Computing"
        ],
        
        # Technical Skills
        tools=[
            "PyTorch",
            "TensorFlow",
            "SPSS",
            "R",
            "Research Design Software"
        ],
        languages=[
            "Python",
            "R",
            "English",
            "Mandarin",
            "JavaScript"
        ]
    ),
    specializations=[
        "bias detection in ML systems",
        "ethical AI development",
        "cross-cultural technology adaptation",
        "human-centered AI design"
    ]
)
```

## Investigator System Prompt
```python
INVESTIGATOR_PROMPT = """You are an Investigator specialized in evaluating factual content for bias and accuracy. In this case you will be evaluating Wikipedia content. What makes you so good at this task is you have a vast rolodex of experts in all fields at your disposal, and you have a unique ability to identify the most relevant experts for any given topic.

Read the following Wikipedia content and identify the most relevant expert(s) to evaluate the content for bias and accuracy.

Wikipedia Content:
{wikipedia_content}
```

## Expert System Prompt Template
```python
EXPERT_PROMPT = """You are an expert with the following qualifications and background:

EXPERTISE BACKGROUND:
- Degrees: {{expertise.degrees}}
- Certifications: {{expertise.certifications}}

CORE KNOWLEDGE:
- Primary Fields: {{expertise.primary_fields}}
- Research Areas: {{expertise.research_areas}}
- Methodologies: {{expertise.methodologies}}

SCOPE OF EXPERTISE:
- Temporal Focus: {{expertise.temporal_focus}}
- Geographic Focus: {{expertise.geographic_focus}}
- Theoretical Frameworks: {{expertise.theoretical_frameworks}}

TECHNICAL SKILLS:
- Tools: {{expertise.tools}}
- Languages: {{expertise.languages}}

As an expert, your role is to provide balanced, well-reasoned analysis while:

1. MAINTAINING NEUTRALITY
- Acknowledge multiple perspectives on complex issues
- Identify your own potential biases and compensate for them
- Base analyses on verifiable evidence rather than personal views
- Consider alternative interpretations of evidence
- Maintain academic distance from emotional or political positions

2. APPLYING EXPERTISE
- Draw upon your research background in {{expertise.researchAreas}}
- Utilize your methodological training in {{expertise.methodologies}}
- Apply relevant theoretical frameworks from your field
- Reference established academic standards and practices
- Consider historical and cultural contexts within your areas of expertise

3. PROVIDING ANALYSIS
- Structure responses using academic reasoning
- Support claims with methodological justification
- Acknowledge limitations of available evidence
- Identify areas of uncertainty or debate
- Distinguish between fact, interpretation, and speculation

4. COMMUNICATION GUIDELINES
- Use precise, academic language
- Avoid emotional or politically charged terminology
- Clearly separate description from analysis
- Acknowledge complexity of issues
- Maintain professional tone and objectivity

Remember: Your role is to provide expert analysis while maintaining scholarly neutrality. Focus on evidence-based reasoning within your areas of expertise."""

```

## Investigator Process
```python
class BiasInvestigation(BaseModel):
    text_segment: str
    start_index: int
    end_index: int
    concern_description: str
    required_expert: ExpertProfile

class InvestigatorResult(BaseModel):
    investigations: List[BiasInvestigation]
    rationale: str

class Investigator:
    """
    The Investigator analyzes Wikipedia content to identify potential bias 
    and determines which experts should review specific segments.
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
        
    def analyze_content(self, wiki_content: WikipediaContent) -> InvestigatorResult:
        """
        Pseudocode for main investigation process:
        1. Process Wikipedia content
        2. Identify segments needing expert review
        3. Create expert profiles for each segment
        """
        
        # Convert content to format suitable for LLM
        formatted_content = self._prepare_content(wiki_content)
        
        # Create system message with investigator role
        system_message = INVESTIGATOR_PROMPT
        
        # Create user message with content and specific instructions
        user_message = f"""
        Analyze this Wikipedia content for potential bias:
        
        Title: {wiki_content.basic_info.title}
        Categories: {', '.join(wiki_content.links.categories)}
        
        Content:
        {formatted_content}
        
        For any segments that may contain bias:
        1. Identify the specific text
        2. Describe the potential bias concern
        3. Specify the expertise needed to evaluate it
        """
        
        # Get LLM response
        response = self.llm.analyze(
            system_message=system_message,
            user_message=user_message
        )
        
        # Parse LLM response into structured format
        investigations = self._parse_response(response)
        
        # Create expert profiles based on identified needs
        for investigation in investigations:
            expert_profile = self._create_expert_profile(
                investigation.concern_description
            )
            investigation.required_expert = expert_profile
            
        return InvestigatorResult(
            investigations=investigations,
            rationale=response.rationale
        )
    
    def _prepare_content(self, wiki_content: WikipediaContent) -> str:
        """Format Wikipedia content for LLM analysis"""
        # Clean and format content
        # Include relevant metadata
        # Return formatted string
        
    def _parse_response(self, llm_response) -> List[BiasInvestigation]:
        """Parse LLM response into structured investigations"""
        # Extract identified segments
        # Parse concern descriptions
        # Return list of BiasInvestigation objects
        
    def _create_expert_profile(self, concern_description: str) -> ExpertProfile:
        """Create expert profile based on bias concern"""
        # Use LLM to determine required expertise
        # Generate ExpertProfile with appropriate fields
        # Return ExpertProfile object

# Example usage:
investigator = Investigator(llm_client)
wiki_processor = WikipediaProcessor()

# Fetch Wikipedia content
content = wiki_processor.fetch_content(url)

# Analyze for bias and get expert requirements
result = investigator.analyze_content(content)

# Result contains segments needing review and expert profiles
for investigation in result.investigations:
    print(f"Segment: {investigation.text_segment}")
    print(f"Concern: {investigation.concern_description}")
    print(f"Required Expert: {investigation.required_expert}")
