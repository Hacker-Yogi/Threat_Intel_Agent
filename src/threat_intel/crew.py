from typing import List
from crewai.project import CrewBase, agent, task, crew
from crewai import Agent, Task, Crew, Process, LLM
from crewai.agents.agent_builder.base_agent import BaseAgent
from threat_intel.tools.rss_tools import FetchNewArticles
from threat_intel.tools.ioc_extraction_tool import DeterministicIOCExtractor
from threat_intel.tools.file_reader_tool import FileReaderTool
from threat_intel.models.threat_actor_models import ThreatActorAttribution
from langchain_google_genai import ChatGoogleGenerativeAI 
import json
import os
from datetime import datetime


@CrewBase
class ThreatIntel:
    """ThreatIntel RSS crew"""
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    agents: List[BaseAgent]
    tasks: List[Task]
    
    def __init__(self):
        # Create output directory with timestamp
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"output/{self.run_id}"
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"\n📁 Run ID: {self.run_id}")
        print(f"📁 Output: {self.output_dir}\n")

        # Create Gemini LLM using CrewAI's LLM class
        self.gemini_llm = LLM(
            model="gemini/gemini-3-flash-preview",
            api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0
        )


    @agent
    def ioc_extractor(self) -> Agent:
        return Agent(
            role="IOC Data Collector",
            goal="Execute IOC extraction tools and confirm successful data processing",
            backstory="""You are a specialized data processing agent focused on executing extraction tools.
            Your job is simple: run the deterministic IOC extraction tool, verify the results
            are saved correctly, and confirm completion. You don't analyze, interpret, or make
            decisions - you execute tools reliably and report status.""",
            tools=[],
            reasoning=False,
            allow_delegation=False,
            verbose=True,
            llm=self.gemini_llm  # Use Gemini
        )
    
    @agent
    def threat_actor_analyst(self) -> Agent:
        return Agent(
            role="Threat Intelligence Data Analyst",
            goal="Read threat intelligence files and accurately map IOCs to threat actors without hallucination",
            backstory="""You are a meticulous data analyst who ALWAYS reads source files before making any conclusions.
            You never make assumptions or create fictional data. Every piece of information you provide
            must come directly from the files you read using the file_reader tool.
            
            Your process is strict:
            1. First, read rss_data.json using file_reader
            2. Second, read ioc_results.json using file_reader
            3. Only then analyze and map the data
            
            You understand that making up data or skipping file reading would compromise the entire
            threat intelligence operation. You are reliable, accurate, and tool-driven.""",
            tools=[FileReaderTool(output_dir=self.output_dir)],
            reasoning=False,
            allow_delegation=False,
            verbose=True,
            llm=self.gemini_llm  # Use Gemini
        )
    

    @task   
    def extract_iocs(self) -> Task:
        """Step 1 & 2: Fetch RSS and Extract IOCs (No LLM)"""
        # TESTING MODE: Always clear seen links
        seen_file = "seen_links.txt"
        if os.path.exists(seen_file):
            os.remove(seen_file)
            print("🔄 Cleared seen_links.txt for fresh run")

        print("[Step 1/3] Fetching RSS feeds...")
        rss_tool = FetchNewArticles()
        rss_data = rss_tool._run()
        
        # Save RSS data to file
        rss_file = f"{self.output_dir}/rss_data.json"
        with open(rss_file, 'w', encoding='utf-8') as f:
            json.dump(rss_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved {len(rss_data)} articles to {rss_file}")
        
        print("\n[Step 2/3] Extracting IOCs...")
        ioc_extractor = DeterministicIOCExtractor()
        ioc_results = ioc_extractor._run(rss_data)
        
        # Save IOC results to file
        ioc_file = f"{self.output_dir}/ioc_results.json"
        with open(ioc_file, 'w', encoding='utf-8') as f:
            json.dump(ioc_results, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved IOC results to {ioc_file}")
    
        # Use YAML config only
        return Task(
            config=self.tasks_config["extract_iocs"],
            agent=self.ioc_extractor()
        )
    
   
    
    @task
    def attribute_threat_actors(self) -> Task:
        """Step 3: Attribute IOCs to Threat Actors (Uses LLM)"""
        
        print("\n[Step 3/3] Preparing threat actor attribution task...")
        
        return Task(
            description="""You MUST use the file_reader tool to read both files before answering.

    MANDATORY STEPS:
    1. Call file_reader with filename='rss_data.json' - READ THIS FIRST
    2. Call file_reader with filename='ioc_results.json' - READ THIS SECOND
    3. For EACH article, identify any threat actor names explicitly mentioned (e.g., "UAT-9244", "APT28", "Qilin")
    4. Match the IOCs from ioc_results to those threat actors based on article context
    5. Extract TTPs, campaign names, and malware families from the text

    CRITICAL RULES:
    - Only include threat actors EXPLICITLY MENTIONED by name in the articles
    - Only include IOCs that are in the ioc_results.json file
    - Do NOT invent threat actor names
    - Do NOT make up IOCs
    - If an article doesn't mention a specific threat actor name, skip it
    - Use exact IOC values from ioc_results.json

    YOUR OUTPUT MUST BE VALID JSON IN THIS EXACT FORMAT:
    {
    "threat_actors": [
        {
        "name": "Threat Actor Name from Article",
        "aliases": ["any aliases mentioned"],
        "iocs": {
            "ips": ["IP addresses from ioc_results.json for this actor"],
            "domains": ["domains from ioc_results.json for this actor"],
            "hashes": ["hashes from ioc_results.json for this actor"],
            "urls": ["URLs from ioc_results.json for this actor"],
            "cves": ["CVEs from ioc_results.json for this actor"]
        },
        "ttps": ["tactics/techniques described in article"],
        "campaigns": ["campaign or malware names mentioned"],
        "source_articles": ["URL of the article"]
        }
    ]
    }

    If NO threat actors are explicitly named in any article, return:
    {
    "threat_actors": []
    }

    Read both files NOW and return the properly formatted JSON.""",
            expected_output="Valid JSON with threat_actors array containing all identified threat actors and their IOCs",
            agent=self.threat_actor_analyst(),
            context=[self.extract_iocs()],
            output_pydantic=ThreatActorAttribution
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.ioc_extractor(), self.threat_actor_analyst()],
            tasks=[self.extract_iocs(), self.attribute_threat_actors()],
            process=Process.sequential,
            verbose=True
        )