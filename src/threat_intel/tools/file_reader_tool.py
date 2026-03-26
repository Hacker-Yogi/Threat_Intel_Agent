from crewai.tools import BaseTool
from typing import Dict, Any
from pydantic import Field
import json
import os

class FileReaderTool(BaseTool):
    name: str = "file_reader"
    description: str = (
        "Reads JSON files from the output directory. "
        "Pass the filename (e.g., 'rss_data.json' or 'ioc_results.json') to read its contents."
    )
    
    # Declare output_dir as a Pydantic field
    output_dir: str = Field(description="The output directory path where files are stored")
    
    def _run(self, filename: str) -> str:
        """Read and return JSON file contents as a string"""
        filepath = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(filepath):
            return f"ERROR: File not found: {filepath}"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return json.dumps(data, indent=2)
        except Exception as e:
            return f"ERROR: Failed to read file: {str(e)}"