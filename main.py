from typing import Optional, List
from pydantic import BaseModel, Field
import os
from openai import OpenAI
from dotenv import load_dotenv
from utils.wiki_parsing import ContentProcessor

load_dotenv()

# Expert Selection
class Expertise(BaseModel):
    # Academic and Professional Background
    degrees: List[str] = Field(description="degrees the expert should have")
    certifications: Optional[List[str]] = Field(description="certifications the expert should have")
    
    # Core Knowledge Areas
    primary_fields: List[str] = Field(description="primary fields the expert should have")
    research_areas: List[str] = Field(description="research areas the expert should have")
    methodologies: List[str] = Field(description="methodologies the expert should have")
    
    # Scope of Expertise
    temporal_focus: Optional[List[str]] = Field(description="temporal focus the expert should have")
    geographic_focus: Optional[List[str]] = Field(description="geographic focus the expert should have")
    theoretical_frameworks: Optional[List[str]] = Field(description="theoretical frameworks the expert should have")
    
    # Technical Skills
    tools: Optional[List[str]] = Field(description="tools the expert should have")
    programming_languages: Optional[List[str]] = Field(description="programming languages the expert should be fluent in")
    languages: Optional[List[str]] = Field(description="languages the expert should be fluent in")

class ExpertProfile(BaseModel):
    expert_name: str = Field(description="name of the expert")
    rationale: str = Field(description="Explanation for selecting the expert.")
    potential_bias: str = Field(description="Potential bias the expert may have")
    expertise: Expertise = Field(description="Qualifications and backgrounds the expert should have")

class ExpertsNeeded(BaseModel):
    experts: List[ExpertProfile] = Field(description="List of experts needed to evaluate the content")

# Expert Analysis
class SuggestedCorrection(BaseModel):
    rationale: str = Field(description="rationale for verbiage used to correct the bias")
    text_added: str = Field(description="text added to the content to correct the bias")
    text_removed: str = Field(description="text removed from the content to correct the bias")

class BiasInstance(BaseModel):
    rationale: str = Field(description="rationale for the bias instance")
    bias_type: str = Field(description="type of bias")
    affected_stakeholder: str = Field(description="stakeholder whose actions are distorted by the bias of the content")
    bias_example: str = Field(description="example of bias in content. Cite the source material and the specific text that is biased")
    suggested_correction: SuggestedCorrection = Field(description="suggested content correction for the bias")

class ExpertAnalysis(BaseModel):
    methodology: str = Field(description="methodologies used to detect bias")
    stakeholders: List[str] = Field(description="stakeholders whos actions may be distorted by bias in the content")
    detected_biases: List[BiasInstance] = Field(description="list of instances of bias in the content")

class ExpertAnalysisWithName(BaseModel):
    expert_name: str = Field(description="name of the expert")
    expert_analysis: ExpertAnalysis = Field(description="analysis of the content by the expert")

# Opinion Analysis
class PassageAnalysis(BaseModel):
    stakeholders: List[str] = Field(description="stakeholders who may be inclined to inject bias into the content taken from the expert analysis. Make sure there are no duplicates.")
    bias_instance: List[BiasInstance] = Field(description="instances of bias that need to be corrected taken from expert suggestions")
    # final_content: str = Field(description="apply corrections from bias_instance to the content")
    executive_summary: str = Field(description="summary of experts used, biases detected, who benefitted from the bias, and suggested corrections")

class FinalContent(BaseModel):
    final_content: str = Field(description="apply corrections from bias_instance to the content")
    
class Investigator:
    """Investigator class to determine the experts needed to evaluate the content"""

    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt =    f"""
                                    You are an Investigator specialized in evaluating factual content for bias and accuracy. In this case you will be evaluating Wikipedia content. What makes you so good at this task is you have a vast rolodex of experts in all fields at your disposal, and you have a unique ability to identify the most relevant experts for any given topic.
                                """
        self.chat_history: List[str] = []

    def get_experts_needed(self, topic: str, content: str) -> ExpertsNeeded:
        initial_message =    f"""
                                Read the following Wikipedia content on {topic} and identify a balanced panel of 3 experts to evaluate the content for bias and accuracy. It is important that the panel is able to evaluate all viewpoints on the subject matter.

                                Wikipedia Content:
                                ```
                                {content}
                                ```
                            """
        self.chat_history.append(initial_message)

        response = self.openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": initial_message
                }
            ],
            response_format=ExpertsNeeded
        )
        self.chat_history.append(response.choices[0].message.content)
        return response.choices[0].message.parsed
    
    def analyze_expert_opinions(self, expert_opinion: List[ExpertAnalysisWithName]) -> ExpertAnalysis:
        response = self.openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                *[
                    {
                        "role": "user",
                        "content": message
                    } for message in self.chat_history
                ],
                {
                    "role": "user",
                    "content":
                        f"""
                            The experts you selected have provided analysis of the content.
                            You can find their analysis in the dictionary below with expert name as the key:
                            {expert_opinion}
                    

                            It is up to you to decide what changes need to be made to the content to make it more accurate and unbiased. Remember the following:
                            - You are not obligated to make any changes, but if you do, you need to provide a rationale for the changes you made.
                            - You should consider the impact of bias on your expert's analysis.
                            - Changes should NOT remove any factual content or proper nouns, only add context and nuance.
                            - Make sure that any corrections you identify are accurately reflected in the content.
                            - You need to provide a summary of the experts used, biases detected, who benefitted from the bias, and suggested corrections.
                        """
                }
            ],
            response_format=PassageAnalysis
        )
        return response.choices[0].message.parsed
    
    def create_final_content(self, passage_analysis: PassageAnalysis, content: str) -> str:
        response = self.openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                *[
                    {
                        "role": "user",
                        "content": message
                    } for message in self.chat_history
                ],
                {
                    "role": "user",
                    "content":
                        f"""
                            Now that you have decided on the suggested corrections, please apply them to the content. When you apply the corrections be sure to apply them in the following way:

                            Example:
                            Original text: "The conflict began in 1948."
                            
                            SuggestedCorrection:
                            text_added: "following the UN partition plan"
                            text_removed: "in"
                            
                            Modified text: "The conflict began [following the UN partition plan]."

                            Apply all corrections to the content maintaining proper grammar and flow.

                            Here is a list of the suggested corrections:
                            {passage_analysis.bias_instance}

                            Here is the content:
                            {content}
                        """
                }
            ],
            response_format=FinalContent
        )
        return response.choices[0].message.parsed

class ExpertOpinion:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_expert_opinion(self, content: str, expert: ExpertProfile) -> ExpertAnalysisWithName:
        response = self.openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": 
                        f"""
                            You are, {expert.expert_name}, an expert with the following qualifications and background:

                            EXPERTISE BACKGROUND:
                            - Degrees: ```{expert.expertise.degrees}```
                            - Certifications: ```{expert.expertise.certifications}```

                            CORE KNOWLEDGE:
                            - Primary Fields: ```{expert.expertise.primary_fields}```
                            - Research Areas: ```{expert.expertise.research_areas}```
                            - Methodologies: ```{expert.expertise.methodologies}```

                            SCOPE OF EXPERTISE:
                            - Temporal Focus: ```{expert.expertise.temporal_focus}```
                            - Geographic Focus: ```{expert.expertise.geographic_focus}```
                            - Theoretical Frameworks: ```{expert.expertise.theoretical_frameworks}```

                            TECHNICAL SKILLS:
                            - Tools: ```{expert.expertise.tools}```
                            - Languages: ```{expert.expertise.languages}```
                        """
                },
                {
                    "role": "user",
                    "content":
                        f"""
                            As an expert, your role is to provide balanced, well-reasoned analysis of the following content while:

                            1. MAINTAINING NEUTRALITY
                            - Acknowledge multiple perspectives on complex issues
                            - Identify your own potential biases and compensate for them
                            - Base analyses on verifiable evidence rather than personal views
                            - Consider alternative interpretations of evidence
                            - Maintain academic distance from emotional or political positions

                            2. APPLYING EXPERTISE
                            - Draw upon your research background in ```{expert.expertise.research_areas}```
                            - Utilize your methodological training in ```{expert.expertise.methodologies}```
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

                            Remember: Your role is to provide expert analysis while maintaining scholarly neutrality. Focus on evidence-based reasoning within your areas of expertise.

                            Content:
                            ```
                            {content}
                            ```
                        """
                }
            ],
            response_format=ExpertAnalysis
        )
        return ExpertAnalysisWithName(
            expert_name=expert.expert_name,
            expert_analysis=response.choices[0].message.parsed
        )
# Update the example usage to demonstrate the content processing
if __name__ == "__main__":
    content_processor = ContentProcessor()
    
    test_url = "https://wikipedia.org/wiki/Donald_Trump"
    
    chunks = content_processor.get_and_process_content(test_url)
    if chunks:
        # print(f"Content split into {len(chunks)} chunks")
        # print("\nFirst chunk preview:", list(chunks.keys())[2])
        content_header = list(chunks.keys())[3]
        content_for_analysis = chunks[content_header]
        print(content_for_analysis)

        investigator = Investigator()
        experts = investigator.get_experts_needed(content_header, content_for_analysis)
        expert_opinion = ExpertOpinion()
        opinions = {}
        for expert in experts.experts:
            print("Expert Name: ", expert.expert_name)
            print("Rationale: ", expert.rationale)
            print("Potential Bias: ", expert.potential_bias)
            print("Degrees: ", expert.expertise.degrees)
            print("Certifications: ", expert.expertise.certifications)
            print("Primary Fields: ", expert.expertise.primary_fields)
            print("Research Areas: ", expert.expertise.research_areas)
            print("Methodologies: ", expert.expertise.methodologies)
            print("Temporal Focus: ", expert.expertise.temporal_focus)
            print("Geographic Focus: ", expert.expertise.geographic_focus)
            print("Theoretical Frameworks: ", expert.expertise.theoretical_frameworks)
            print("----------------------------------")

            opinions[expert.expert_name] = expert_opinion.get_expert_opinion(content_for_analysis, expert)
            print("Expert Opinion by ", opinions[expert.expert_name].expert_name, ": ")
            print("Methodology: ", opinions[expert.expert_name].expert_analysis.methodology)
            print("Stakeholders: ", opinions[expert.expert_name].expert_analysis.stakeholders)
            for bias in opinions[expert.expert_name].expert_analysis.detected_biases:
                print("Bias: ", bias.bias_type)
                print("Rationale: ", bias.rationale)
                print("Bias Examples: ", bias.bias_example)
                print("Suggested Correction: ", "+", bias.suggested_correction.text_added, "-", bias.suggested_correction.text_removed)
                print("----------------------------------")
        
        analysis = investigator.analyze_expert_opinions(opinions)
        print("FINAL ANALYSIS: ", analysis.executive_summary)
        print("Stakeholders: ", analysis.stakeholders)
        print("----------------------------------")
        for bias in analysis.bias_instance:
            print("Bias: ", bias.bias_type)
            print("Rationale: ", bias.rationale)
            print("Victim: ", bias.affected_stakeholder)
            print("Bias Examples: ", bias.bias_example)
            print("Suggested Correction: ", "+", bias.suggested_correction.text_added, "-", bias.suggested_correction.text_removed)
            print("----------------------------------")

        final_content = investigator.create_final_content(analysis, content_for_analysis)
        print("Final Content: ", final_content.final_content)
    else:
        print("No content found")

    
