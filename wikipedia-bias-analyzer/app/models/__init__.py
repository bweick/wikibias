# This file marks the directory as a Python package 

# Import all models here to ensure they're registered with SQLAlchemy Base
from app.models.prompt import PromptTemplate
from app.models.wikipedia import WikipediaPage
from app.models.analysis import BiasAnalysis, AggregatedResult, BiasResult, BiasInstance
