# 🛡️ Threat Intelligence Automation Agent

An advanced multi-agent threat intelligence system that automates the collection, analysis, and attribution of cyber threat data from RSS feeds. It combines LLM-driven insights with deterministic IOC extraction to deliver structured and actionable intelligence. Built using the CrewAI framework.

Modern threat intelligence workflows often depend on proprietary platforms, creating blind spots and limiting adaptability. This project introduces a multi-agent system that decentralizes threat intelligence collection by aggregating RSS feeds from blogs, news, and security research sources. It combines LLM-powered analysis with deterministic IOC extraction to transform unstructured content into actionable intelligence. Built using the CrewAI framework.

![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-Latest-orange.svg)
![Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-blue.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Output Structure](#output-structure)
- [Dependencies](#dependencies)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This threat intelligence automation system combines deterministic pattern matching with advanced LLM capabilities to:

1. **Fetch** threat intelligence articles from configured RSS feeds
2. **Extract** Indicators of Compromise (IOCs) using regex-based tools
3. **Attribute** threats to specific threat actors using AI-powered analysis
4. **Organize** results in structured JSON format for easy integration

The system runs autonomously, deduplicates content using a rolling 7-day window, and accumulates daily intelligence in organized folders.

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────────────────────┐
│                    THREAT INTEL AUTOMATION PIPELINE                  │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   RSS SOURCES    │  Configuration: config/rss_sources.yaml
│  (Threat Intel   │
│     Feeds)       │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         STEP 1: RSS FETCHING                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Tool: FetchNewArticles (Deterministic)                      │   │
│  │  • Fetches articles from RSS feeds                           │   │
│  │  • 7-day rolling window deduplication                        │   │
│  │  • Stores seen links in seen_links.json                      │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ▼                                        │
│                    output/daily_data/YYYY-MM-DD/                     │
│                         rss_data.json                                 │
└──────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      STEP 2: IOC EXTRACTION                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Tool: DeterministicIOCExtractor (Regex-based)               │   │
│  │  Agent: IOC Data Collector                                   │   │
│  │  • Extracts IPs, domains, hashes, URLs, CVEs                 │   │
│  │  • No LLM - Pure pattern matching                            │   │
│  │  • Prevents hallucination in data extraction                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ▼                                        │
│                    output/daily_data/YYYY-MM-DD/                     │
│                        ioc_results.json                               │
└──────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                 STEP 3: THREAT ACTOR ATTRIBUTION                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Agent: Threat Intelligence Data Analyst                     │   │
│  │  LLM: Google Gemini 1.5 Pro / 3.0 Flash Preview              │   │
│  │  Tools: FileReaderTool                                       │   │
│  │  • Reads rss_data.json and ioc_results.json                  │   │
│  │  • Maps IOCs to threat actors                                │   │
│  │  • Extracts TTPs, campaigns, aliases                         │   │
│  │  • Enforces Pydantic schema for structured output            │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ▼                                        │
│              output/final_results/YYYYMMDD_HHMMSS/                   │
│                   threat_attribution.json                             │
└──────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW SUMMARY                           │
│                                                                      │
│  Deterministic Steps (No LLM):                                      │
│    • RSS Fetching                                                   │
│    • IOC Extraction                                                 │
│                                                                      │
│  Semantic/LLM-Powered Steps:                                        │
│    • Threat Actor Attribution                                       │
│    • TTP Extraction                                                 │
│    • Campaign Identification                                        │
│                                                                      │
│  Storage:                                                            │
│    • Daily Data: Cumulative per day                                 │
│    • Final Results: Timestamped per run                             │
│    • Deduplication: Rolling 7-day window                            │
└─────────────────────────────────────────────────────────────────────┘
```

### Agent Roles

| Agent | Type | Purpose | LLM Usage |
|-------|------|---------|-----------|
| **RSS Fetcher** | Tool | Fetches articles from RSS feeds | ❌ None |
| **IOC Data Collector** | Agent | Orchestrates deterministic IOC extraction | ❌ None (confirms completion only) |
| **Threat Intelligence Analyst** | Agent | Maps IOCs to threat actors, extracts TTPs | ✅ Gemini (Semantic Analysis) |

### Design Philosophy

- **Deterministic Where Possible**: IOC extraction uses regex to prevent hallucination
- **LLM Where Needed**: Semantic analysis for threat actor attribution and context
- **File-Based Flow**: Enables restart from any step and easy debugging
- **Pydantic Validation**: Ensures structured, type-safe output

---

## ✨ Features

- 🔄 **Automated RSS Feed Processing**: Fetch threat intel from multiple sources
- 🎯 **Smart Deduplication**: 7-day rolling window prevents reprocessing
- 🔍 **Multi-IOC Support**: IPs, domains, file hashes, URLs, CVEs
- 🤖 **AI-Powered Attribution**: Maps IOCs to threat actors with high accuracy
- 📊 **Structured Output**: Clean JSON format for easy integration
- 🗂️ **Daily Accumulation**: Merges multiple runs per day seamlessly
- ⚡ **Production-Ready**: Error handling, retry logic, and scalable design

---

## 📦 Installation

### Prerequisites

- **Python 3.12** (required for IOCextract library compatibility)
- **uv** package manager (recommended) or pip
- **Google Gemini API Key** ([Get one here](https://aistudio.google.com/app/apikey))

### Setup Steps

1. **Clone the repository**
```bash
   git clone https://github.com/yourusername/threat-intel-agent.git
   cd threat-intel-agent
```

2. **Create virtual environment**
```bash
   # Using Python 3.12
   python3.12 -m venv .venv
   
   # Or on Windows
   python -m venv .venv
```

3. **Activate virtual environment**
```bash
   # Linux/Mac
   source .venv/bin/activate
   
   # Windows
   .venv\Scripts\activate
```

4. **Install CrewAI**
```bash
   uv tool install crewai --upgrade
```

5. **Install dependencies**
```bash
   uv pip install iocextract feedparser newspaper3k requests lxml_html_clean fastapi-sso
   uv pip install 'litellm[proxy]' "pydantic[email]"
```

6. **Configure environment**
```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env and add your API key
   GOOGLE_API_KEY=your-gemini-api-key-here
```

---

## ⚙️ Configuration

### RSS Sources

Edit `config/rss_sources.yaml`:
```yaml
rss_feeds:
  - https://blog.talosintelligence.com/rss/
  - https://www.cisa.gov/cybersecurity-advisories/rss.xml
  - https://www.bleepingcomputer.com/feed/
  # Add your feeds here
```

### Agent Configuration

Edit `config/agents.yaml` to customize agent behavior:
```yaml
ioc_extractor:
  role: IOC Data Collector
  goal: Execute IOC extraction tools and confirm successful data processing
  backstory: >
    You are a specialized data processing agent...

threat_actor_analyst:
  role: Threat Intelligence Data Analyst
  goal: Read threat intelligence files and accurately map IOCs to threat actors
  backstory: >
    You are a meticulous data analyst...
```

### Task Configuration

Edit `config/tasks.yaml` to modify task prompts and outputs.

---

## 🚀 Usage

### Run the Pipeline
```bash
crewai run
```

### First Run (8:00 AM)
```
📁 Run Date: 20260329
🕐 Run Time: 08:00:00
📁 Daily Data: output/daily_data/2026-03-29

[Step 1/3] Fetching RSS feeds...
✅ Found 15 new articles
✓ Saved 15 total articles

[Step 2/3] Extracting IOCs...
✓ Saved 15 IOC entries

[Step 3/3] Threat actor attribution...
💾 Final result saved: output/final_results/20260329_080000/threat_attribution.json
```

### Second Run Same Day (8:00 PM)
```
📁 Run Date: 20260329
🕐 Run Time: 20:00:00
📁 Daily Data: output/daily_data/2026-03-29

[Step 1/3] Fetching RSS feeds...
✅ Found 5 new articles
📂 Found existing rss_data.json with 15 articles
✓ Saved 20 total articles (5 new)

[Step 2/3] Extracting IOCs...
✓ Saved 20 IOC entries

[Step 3/3] Threat actor attribution...
💾 Final result saved: output/final_results/20260329_200000/threat_attribution.json
```

---

## 📁 Output Structure
```
threat-intel-agent/
├── output/
│   ├── daily_data/
│   │   └── 2026-03-29/
│   │       ├── rss_data.json          # Raw articles (cumulative per day)
│   │       └── ioc_results.json       # Extracted IOCs (cumulative per day)
│   └── final_results/
│       └── 20260329_080000/
│           └── threat_attribution.json # Threat actor attribution (per run)
├── seen_links.json                     # 7-day rolling deduplication window
├── config/
│   ├── rss_sources.yaml
│   ├── agents.yaml
│   └── tasks.yaml
└── .env
```

### Sample Output: `threat_attribution.json`
```json
{
  "threat_actors": [
    {
      "name": "UAT-9244",
      "aliases": ["Famous Sparrow", "Tropic Trooper"],
      "iocs": {
        "ips": ["154.205.154.82", "207.148.121.95"],
        "domains": ["xtibh.com", "xcit76.com"],
        "hashes": ["711d9427ee43bc2186b9124f31cba2db..."],
        "urls": [],
        "cves": []
      },
      "ttps": [
        "DLL side-loading",
        "BitTorrent protocol for C2",
        "Scheduled tasks for persistence"
      ],
      "campaigns": ["TernDoor", "SparrowDoor"],
      "source_articles": ["https://blog.talosintelligence.com/uat-9244/"]
    }
  ]
}
```

---

## 🔧 Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| **Python** | 3.12 | Runtime (IOCextract requirement) |
| **CrewAI** | Latest | Multi-agent orchestration |
| **iocextract** | Latest | IOC pattern extraction |
| **feedparser** | Latest | RSS feed parsing |
| **newspaper3k** | Latest | Article content extraction |
| **litellm** | Latest | LLM abstraction layer |
| **pydantic** | Latest | Data validation and schema enforcement |

### LLM Provider

- **Google Gemini** (1.5 Pro or 3.0 Flash Preview)
- Free tier: 1,500 requests/day
- [Get API Key](https://aistudio.google.com/app/apikey)

---

## 🐛 Troubleshooting

### 503 Error: "Model experiencing high demand"

**Cause**: Gemini server overload (temporary)

**Solutions**:
1. Wait 10-30 minutes and retry
2. Switch to Gemini 1.5 Pro (more stable):
```python
   # In crew.py
   model="gemini/gemini-1.5-pro"
```

### No New Articles Found

**Cause**: All articles already processed within 7-day window

**Expected**: System will use existing data and proceed to attribution step

### IOCextract Import Error

**Cause**: Python version mismatch

**Solution**: Ensure Python 3.12 is being used:
```bash
python --version  # Should show 3.12.x
```

### Empty threat_actors Array

**Cause**: Articles don't explicitly mention threat actor names

**Expected Behavior**: System returns valid JSON with empty array

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **CrewAI** - Multi-agent orchestration framework
- **Google Gemini** - Advanced LLM capabilities
- **Cisco Talos**, **CISA**, **BleepingComputer** - Threat intelligence sources
- **iocextract** - Robust IOC pattern matching

---

## 📧 Contact

For questions or support, please open an issue or contact [your-email@example.com]

---

**⚡ Built with CrewAI and powered by Google Gemini**
