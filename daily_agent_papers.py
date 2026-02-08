#!/usr/bin/env python3
"""
Daily Agent Papers Pipeline - Runs automatically at 6am
Scrapes yesterday's papers, filters for agents, generates Medium content, crops diagrams, pushes to GitHub
"""

import os
import sys
import json
import time
import base64
import shutil
import requests
import subprocess
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from PIL import Image
from pdf2image import convert_from_path
from openai import OpenAI

# Configuration
GITHUB_USERNAME = "dixonhuinVancouver"
GITHUB_REPO = "manus_research"
OUTPUT_BASE = "/home/ubuntu/hf-agent-scraper/output/agent-papers"

# Calculate yesterday's date
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
year, month, day = yesterday.split("-")

print("=" * 80)
print(f"DAILY AGENT PAPERS PIPELINE - {yesterday}")
print("=" * 80)

client = OpenAI()

# Create working directory
work_dir = f"/home/ubuntu/hf-agent-scraper/daily_{yesterday.replace('-', '')}"
os.makedirs(work_dir, exist_ok=True)
os.chdir(work_dir)

# STEP 1: Scrape HuggingFace
print("\n[STEP 1/7] Scraping HuggingFace papers...")
url = "https://huggingface.co/papers"
response = requests.get(url, timeout=30)
soup = BeautifulSoup(response.text, 'html.parser')

papers = []
for article in soup.find_all('article')[:50]:
    try:
        title_elem = article.find('h3')
        if not title_elem:
            continue
        title = title_elem.get_text(strip=True)
        
        link_elem = article.find('a', href=True)
        if not link_elem:
            continue
        hf_link = "https://huggingface.co" + link_elem['href']
        
        time_elem = article.find('time')
        if time_elem and 'datetime' in time_elem.attrs:
            paper_date = time_elem['datetime'][:10]
            if paper_date != yesterday:
                continue
        
        papers.append({'title': title, 'hf_link': hf_link})
    except:
        continue

print(f"✓ Found {len(papers)} papers from {yesterday}")

# STEP 2: Strict agent filtering
print("\n[STEP 2/7] Applying strict agent-only filtering...")
agent_papers = []

for i, paper in enumerate(papers, 1):
    prompt = f"""Is this paper STRICTLY about AI agents?

Title: {paper['title']}

STRICT CRITERIA - Must be about:
- Autonomous agents, Multi-agent systems, Agent architectures
- Agent planning/reasoning, Agent tool use, Agent evaluation
- Agent memory/learning, Agent safety/robustness

REJECT: General LLM/VLLM, General reasoning, General RAG, General training

JSON: {{"is_agent_paper": boolean, "category": "agent_evaluation|agent_safety|agent_learning|agent_system|multi_agent|not_agent", "confidence": float}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=200
        )
        
        result_text = response.choices[0].message.content.strip()
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1].replace('json', '').strip()
        
        result = json.loads(result_text)
        
        if result['is_agent_paper'] and result['confidence'] >= 0.85:
            agent_papers.append({**paper, 'category': result['category'], 'confidence': result['confidence']})
    except:
        pass
    
    time.sleep(0.5)

print(f"✓ Filtered to {len(agent_papers)} verified agent papers")

if len(agent_papers) == 0:
    print("\n⚠️  No agent papers found for yesterday. Exiting.")
    sys.exit(0)

# STEP 3: Get arXiv IDs and download PDFs
print("\n[STEP 3/7] Downloading PDFs...")
os.makedirs('pdfs', exist_ok=True)
os.makedirs('diagrams', exist_ok=True)

for i, paper in enumerate(agent_papers, 1):
    try:
        response = requests.get(paper['hf_link'], timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a', href=True):
            if 'arxiv.org/abs/' in link['href']:
                arxiv_id = link['href'].split('/abs/')[-1].split('v')[0]
                paper['arxiv_id'] = arxiv_id
                
                # Download PDF
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                pdf_path = f"pdfs/{arxiv_id}.pdf"
                pdf_response = requests.get(pdf_url, timeout=60)
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_response.content)
                
                # Convert first 3 pages to images using pdf2image
                try:
                    images = convert_from_path(pdf_path, first_page=1, last_page=3, dpi=150)
                    diagram_paths = []
                    for j, img in enumerate(images, 1):
                        img_path = f"diagrams/{arxiv_id}_page{j}.png"
                        img.save(img_path, 'PNG')
                        diagram_paths.append(img_path)
                    paper['diagram_paths'] = diagram_paths
                except Exception as e:
                    print(f"  ⚠️  PDF conversion failed for {arxiv_id}: {e}")
                    paper['diagram_paths'] = []
                break
    except:
        pass
    
    time.sleep(1)

print(f"✓ Downloaded {sum(1 for p in agent_papers if p.get('arxiv_id'))} PDFs")

# STEP 4: Identify main diagrams
print("\n[STEP 4/7] Identifying main diagrams...")

def identify_main_diagram(paper):
    if not paper.get('diagram_paths'):
        return None
    
    for diagram_path in paper['diagram_paths'][:2]:
        try:
            with open(diagram_path, 'rb') as f:
                base64_image = base64.b64encode(f.read()).decode('utf-8')
            
            response = client.chat.completions.create(
                model="gemini-2.5-flash",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Does this page contain a MAIN ARCHITECTURE or FRAMEWORK DIAGRAM? JSON: {\"has_main_diagram\": boolean, \"confidence\": float}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                    ]
                }],
                temperature=0.2,
                max_tokens=100
            )
            
            result_text = response.choices[0].message.content.strip()
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1].replace('json', '').strip()
            
            result = json.loads(result_text)
            
            if result.get('has_main_diagram') and result.get('confidence', 0) >= 0.7:
                return diagram_path
        except:
            pass
    
    return None

for paper in agent_papers:
    paper['main_diagram'] = identify_main_diagram(paper)
    time.sleep(0.5)

print(f"✓ Found {sum(1 for p in agent_papers if p.get('main_diagram'))} main diagrams")

# STEP 5: Generate Medium content
print("\n[STEP 5/7] Generating Medium-style content...")

def generate_medium_content(paper):
    prompt = f"""Create Medium-style content for: {paper['title']}

Generate JSON with: subtitle (10-15 words), summary (2-3 sentences), intuition (2-3 simple sentences), problem (2-3 sentences), solution (2-3 sentences)"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=800
        )
        
        result_text = response.choices[0].message.content.strip()
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1].replace('json', '').strip()
        
        return json.loads(result_text)
    except:
        return None

for paper in agent_papers:
    paper['medium_content'] = generate_medium_content(paper)
    time.sleep(0.5)

print(f"✓ Generated content for {sum(1 for p in agent_papers if p.get('medium_content'))} papers")

# STEP 6: Smart crop diagrams
print("\n[STEP 6/7] Smart cropping diagrams...")
os.makedirs('cropped', exist_ok=True)

def smart_crop_diagram(image_path, arxiv_id):
    try:
        with open(image_path, 'rb') as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')
        
        img = Image.open(image_path)
        width, height = img.size
        
        prompt = f"""Locate the MAIN ARCHITECTURE/FRAMEWORK DIAGRAM (not tables/text).

Image: {width}x{height} pixels

JSON: {{"has_diagram": boolean, "top_percent": float, "left_percent": float, "width_percent": float, "height_percent": float}}"""

        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            }],
            temperature=0.1,
            max_tokens=200
        )
        
        result_text = response.choices[0].message.content.strip()
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1].replace('json', '').strip()
        
        result = json.loads(result_text)
        
        if result.get('has_diagram'):
            x = int(result['left_percent'] / 100 * width)
            y = int(result['top_percent'] / 100 * height)
            w = int(result['width_percent'] / 100 * width)
            h = int(result['height_percent'] / 100 * height)
            
            x, y = max(0, x - 10), max(0, y - 10)
            w, h = min(width - x, w + 20), min(height - y, h + 20)
            
            cropped = img.crop((x, y, x + w, y + h))
            output_path = f"cropped/{arxiv_id}_main.png"
            cropped.save(output_path, 'PNG', optimize=True, quality=95)
            return output_path
    except:
        pass
    
    return None

for paper in agent_papers:
    if paper.get('main_diagram'):
        arxiv_id = paper.get('arxiv_id', 'unknown')
        paper['cropped_diagram'] = smart_crop_diagram(paper['main_diagram'], arxiv_id)

print(f"✓ Cropped {sum(1 for p in agent_papers if p.get('cropped_diagram'))} diagrams")

# STEP 7: Create markdown and push to GitHub
print("\n[STEP 7/7] Creating markdown and pushing to GitHub...")

output_dir = f"{OUTPUT_BASE}/{year}/{month}"
images_dir = f"{output_dir}/images"
os.makedirs(images_dir, exist_ok=True)

# Copy diagrams
for paper in agent_papers:
    if paper.get('cropped_diagram'):
        arxiv_id = paper.get('arxiv_id')
        shutil.copy(paper['cropped_diagram'], f"{images_dir}/{arxiv_id}_main.png")
        paper['diagram_path'] = f"images/{arxiv_id}_main.png"

# Generate markdown
md_file = f"{output_dir}/{yesterday}.md"
with open(md_file, 'w', encoding='utf-8') as f:
    f.write(f"# AI Agent Papers - {yesterday}\n\n")
    f.write("*Daily curated collection of cutting-edge research in AI agents*\n\n")
    f.write(f"**📊 {len(agent_papers)} verified agent papers** (strict filtering applied)\n\n")
    f.write("---\n\n")
    
    for i, paper in enumerate(agent_papers, 1):
        f.write(f"## {i}. {paper['title']}\n\n")
        
        if paper.get('medium_content'):
            mc = paper['medium_content']
            if mc.get('subtitle'):
                f.write(f"*{mc['subtitle']}*\n\n")
            if mc.get('summary'):
                f.write(f"**Summary**\n\n{mc['summary']}\n\n")
            if mc.get('intuition'):
                f.write(f"### 💡 Intuition\n\n{mc['intuition']}\n\n")
            if mc.get('problem'):
                f.write(f"### 🎯 Problem\n\n{mc['problem']}\n\n")
            if mc.get('solution'):
                f.write(f"### 🛠️ Solution\n\n{mc['solution']}\n\n")
        
        if paper.get('diagram_path'):
            f.write(f"### 📊 Architecture Diagram\n\n")
            f.write(f"![{paper['title']} - Main Diagram]({paper['diagram_path']})\n\n")
        
        f.write("**📄 Read More:**\n")
        f.write(f"- [HuggingFace Paper]({paper['hf_link']})\n")
        if paper.get('arxiv_id'):
            f.write(f"- [arXiv](https://arxiv.org/abs/{paper['arxiv_id']})\n")
        
        if paper.get('category'):
            cat = paper['category'].replace('_', ' ').title()
            f.write(f"\n**Category:** {cat}\n")
        
        f.write("\n---\n\n")

# Push to GitHub
subprocess.run([
    'bash', '-c',
    f"""
    cd /tmp && rm -rf manus_research_daily && \
    gh repo clone {GITHUB_USERNAME}/{GITHUB_REPO} manus_research_daily && \
    cd manus_research_daily && \
    mkdir -p {year}/{month}/images && \
    cp {md_file} {year}/{month}/ && \
    cp {images_dir}/*.png {year}/{month}/images/ 2>/dev/null || true && \
    git add {year}/ && \
    git commit -m "Add agent papers for {yesterday} ({len(agent_papers)} papers)

- {len(agent_papers)} verified agent papers with strict filtering
- Medium-style format with diagrams
- Auto-generated by daily pipeline" && \
    git push https://$(cat ~/.config/github/username):$(cat ~/.config/github/token)@github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git master
    """
])

print(f"\n✅ Pipeline complete!")
print(f"✅ Papers: {len(agent_papers)}")
print(f"✅ Pushed to: https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/master/{year}/{month}/{yesterday}.md")
