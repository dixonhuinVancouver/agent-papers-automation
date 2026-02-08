# AI Agent Papers - Daily Automation

Automated pipeline to scrape, filter, and summarize cutting-edge AI agent research papers from HuggingFace daily.

## Features

- **Strict Agent-Only Filtering**: 85%+ confidence threshold
- **PDF Download**: Automatic arXiv PDF retrieval
- **Diagram Extraction**: Vision AI identifies main architecture diagrams
- **Smart Cropping**: Precise diagram boundaries using vision AI
- **Medium-Style Content**: Subtitle, summary, intuition, problem, solution
- **Auto GitHub Push**: Results pushed to manus_research repository

## Schedule

Runs daily at **6:00 AM** automatically.

## Output

- Repository: `dixonhuinVancouver/manus_research`
- Path: `YYYY/MM/YYYY-MM-DD.md`
- Format: Markdown with embedded diagrams

## Scripts

- `daily_agent_papers.py` - Main pipeline script
- `requirements.txt` - Python dependencies

## Setup

The scheduled task automatically:
1. Pulls latest scripts from this repository
2. Runs the daily pipeline
3. Pushes results to manus_research repository

## Manual Run

```bash
cd /home/ubuntu/agent-papers-automation
python3 daily_agent_papers.py
```
