from utils.wiki_parsing import ContentProcessor
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List

load_dotenv()

# class SuggestedCorrection(BaseModel):
#     rationale: str = Field(description="rationale for verbiage used to correct the bias. Remember to not remove any factual content or proper nouns.")
#     text_added: str = Field(description="text added to the content to correct the bias")
#     text_removed: str = Field(description="text removed from the content to correct the bias")

class BiasInstance(BaseModel):
    rationale: str = Field(description="rationale for the bias instance")
    bias_type: str = Field(description="type of bias")
    biased_phrase: str = Field(description="content that is providing a biased perspective. Make sure to include entire phrase, do not abbreviate the phrase by using ellipses or removing any words.")
    affected_stakeholder: str = Field(description="stakeholder whose actions are distorted by the bias of the content")

class SemanticAnalysis(BaseModel):
    methodology: str = Field(description="methodologies used to detect bias")
    detected_biases: List[BiasInstance] = Field(description="list of instances of bias in the content")

class BiasInstanceWithMetadata(BaseModel):
    bias_id: int = Field(description="unique identifier for the bias instance")
    bias_instance: BiasInstance = Field(description="bias instance")

class BiasPhraseMetadata(BaseModel):
    index: int = Field(description="index of the bias phrase in the content")
    occurrence_count: int = Field(description="number of times the bias phrase occurs in the content")
    bias_phrase: str = Field(description="phrase that is biased")
    bias_instances: List[int] = Field(description="bias instance that the phrase is associated with")

class SemanticAnalyzer:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = """
            You are a semantic analyzer.
            You will be given a piece of content and asked to analyze it for bias.
            Make sure to only analyze the content for semantic biases such as:
                -Framing Bias
                    - Description: The way information is presented (e.g., word choice or tone) influences interpretation.
                    - Example: Calling a policy "tax relief" versus "government spending" shifts perceived intent.
                -Negation Bias
                    - Description: Uses negative language to describe a positive concept.
                    - Example: Calling a policy "anti-terrorism" instead of "counter-terrorism".
                -Affective Bias
                    - Description: Emotional language can distort meaning.
                    - Example: "devastating" instead of "significant" in a disaster context. 
        """

    def analyze_content(self, content: str, runs: int = 10) -> str:
        analyses = []
        # bias_heatmap: dict[int, int] = {}
        bias_instances: List[BiasInstanceWithMetadata] = []
        bias_phrase_heatmap: dict[str, BiasPhraseMetadata] = {}
        bias_index = 0
        for i in range(runs):
            response = self.openai_client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                response_format=SemanticAnalysis
            )
            analysis = response.choices[0].message.parsed
            analyses.append(analysis)

            # cycle through each BiasInstance and find index location of substring in the content 
            for bias in analysis.detected_biases:
                content_index = content.find(bias.biased_phrase)
                if content_index != -1:
                    bias_instance = BiasInstanceWithMetadata(
                        bias_instance=bias,
                        bias_id=bias_index
                    )
                    bias_instances.append(bias_instance)
                    if bias.biased_phrase.lower() not in bias_phrase_heatmap or bias_phrase_heatmap[bias.biased_phrase.lower()].index != content_index:
                        bias_phrase_heatmap[bias.biased_phrase.lower()] = BiasPhraseMetadata(
                            occurrence_count=1,
                            index=content_index,
                            bias_phrase=bias.biased_phrase,
                            bias_instances=[bias_index]
                        )
                    else:
                        bias_phrase_heatmap[bias.biased_phrase.lower()].occurrence_count += 1
                        bias_phrase_heatmap[bias.biased_phrase.lower()].bias_instances.append(bias_index)
                    bias_index += 1
                # for i in range(len(bias.biased_phrase)):
                    # # Initialize key with 0 if it doesn't exist
                    # if index + i not in bias_heatmap:
                    #     bias_heatmap[index + i] = 0
                    # bias_heatmap[index + i] += 1
                    
        # order bias_heatmap by value and group by occurrence count
        # occurrence_groups = {}
        # for index, count in bias_heatmap.items():
        #     if count not in occurrence_groups:
        #         occurrence_groups[count] = []
        #     occurrence_groups[count].append(index)
        
        # # Sort indices within each group
        # for count in occurrence_groups:
        #     occurrence_groups[count].sort()

        # # print content for each index in occurrence_groups
        # occurrence_groups_content = {}
        # for count in occurrence_groups:
        #     occurrence_groups_content[count] = []
        #     for index in occurrence_groups[count]:
        #         if index < len(content):
        #             occurrence_groups_content[count].append(content[index])
        
        return bias_instances, bias_phrase_heatmap
    
if __name__ == "__main__":
    content_processor = ContentProcessor()
    
    test_url = "https://en.wikipedia.org/wiki/Israeli-Palestinian_conflict"
    
    chunks = content_processor.get_and_process_content(test_url)
    if chunks:
        content_header = list(chunks.keys())[3]
        content_for_analysis = chunks[content_header]
        print(content_for_analysis)

        semantic_analyzer = SemanticAnalyzer()
        bias_instances, bias_phrase_heatmap = semantic_analyzer.analyze_content(content_for_analysis)

        print("----------------------------------")
        print("Semantic Analysis: ")
        for bias_instance in bias_instances:
            print("Bias: ", bias_instance.bias_instance.bias_type)
            print("Rationale: ", bias_instance.bias_instance.rationale)
            print("Affected Stakeholder: ", bias_instance.bias_instance.affected_stakeholder)
            print("Biased Phrase: ", bias_instance.bias_instance.biased_phrase)
            print("----------------------------------")
        # order bias_heatmap by value
        print("Bias Occurence Map: ")
        for phrase in bias_phrase_heatmap.keys():
            print("----------------------------------")
            print(f"{phrase}: {bias_phrase_heatmap[phrase].occurrence_count}", bias_phrase_heatmap[phrase].index)
            # for bias_instance_id in bias_phrase_heatmap[phrase].bias_instances:
            #     print(f"Bias Instance Rationale: {bias_instances[bias_instance_id].bias_instance.rationale}")
            #     print(f"Bias Instance Bias Type: {bias_instances[bias_instance_id].bias_instance.bias_type}")
            #     print(f"Bias Instance Biased Phrase: {bias_instances[bias_instance_id].bias_instance.biased_phrase}")
            #     print(f"Bias Instance Affected Stakeholder: {bias_instances[bias_instance_id].bias_instance.affected_stakeholder}")
            #     print("----------------------------------")
        print("----------------------------------")
