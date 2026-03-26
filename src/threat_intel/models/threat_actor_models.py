from pydantic import BaseModel, Field
from typing import List

class ThreatActorIOCs(BaseModel):
    """IOCs (Indicators of Compromise) associated with a threat actor"""
    ips: List[str] = Field(
        default_factory=list, 
        description="IP addresses extracted from articles and attributed to this threat actor"
    )
    domains: List[str] = Field(
        default_factory=list, 
        description="Domain names extracted from articles and attributed to this threat actor"
    )
    hashes: List[str] = Field(
        default_factory=list, 
        description="File hashes (MD5, SHA256, etc.) extracted from articles and attributed to this threat actor"
    )
    urls: List[str] = Field(
        default_factory=list, 
        description="Malicious URLs extracted from articles and attributed to this threat actor"
    )
    cves: List[str] = Field(
        default_factory=list, 
        description="CVE identifiers extracted from articles and attributed to this threat actor"
    )

class ThreatActorProfile(BaseModel):
    """Complete profile of a single threat actor"""
    name: str = Field(
        description="Primary name of the threat actor as explicitly mentioned in the articles"
    )
    aliases: List[str] = Field(
        default_factory=list, 
        description="Alternative names or aliases for this threat actor mentioned in articles"
    )
    iocs: ThreatActorIOCs = Field(
        default=ThreatActorIOCs(),  # Provide default
        description="All indicators of compromise attributed to this threat actor"
    )
    ttps: List[str] = Field(
        default_factory=list, 
        description="Tactics, Techniques, and Procedures used by this threat actor as described in articles"
    )
    campaigns: List[str] = Field(
        default_factory=list, 
        description="Campaign names, operation names, or malware families associated with this threat actor"
    )
    source_articles: List[str] = Field(
        default_factory=list, 
        description="URLs of the articles where this threat actor was mentioned"
    )

class ThreatActorAttribution(BaseModel):
    """Complete threat actor attribution report - the final output format
    
    CRITICAL: The top-level key MUST be 'threat_actors' containing an array of threat actor profiles.
    """
    threat_actors: List[ThreatActorProfile] = Field(
        description="REQUIRED: List of all threat actors identified in the articles with their associated IOCs. If no threat actors are found, return an empty array []"
    )