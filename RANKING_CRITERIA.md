# Top 5 Agent Papers - Ranking Criteria

## Overview

To provide a focused daily digest, we select the **top 5 most impactful agent papers** from all verified agent papers each day.

## Ranking Dimensions

### 1. Novelty & Innovation (40%)
**What it measures:** How new and original is the approach?

**Scoring criteria:**
- **High (8-10):** Introduces entirely new paradigm, architecture, or concept
- **Medium (5-7):** Significant improvement or novel combination of existing ideas
- **Low (1-4):** Incremental improvement or application of existing methods

**Examples:**
- High: First paper on intrinsic risk sensing for agents (Spider-Sense)
- Medium: New benchmark with novel evaluation metrics (CAR-bench)
- Low: Applying existing RL techniques to agent training

### 2. Technical Contribution (30%)
**What it measures:** Depth and rigor of the technical solution

**Scoring criteria:**
- **High (8-10):** Strong theoretical foundation, comprehensive experiments, clear methodology
- **Medium (5-7):** Solid technical approach with reasonable validation
- **Low (1-4):** Limited technical depth or weak experimental validation

**Examples:**
- High: Novel algorithm with mathematical proofs and extensive benchmarks
- Medium: Well-designed framework with ablation studies
- Low: Conceptual proposal without rigorous evaluation

### 3. Practical Impact (20%)
**What it measures:** Real-world applicability and usefulness

**Scoring criteria:**
- **High (8-10):** Addresses critical real-world problem, immediately applicable
- **Medium (5-7):** Useful for specific scenarios or research directions
- **Low (1-4):** Primarily theoretical or narrow application

**Examples:**
- High: Safety mechanism for deployed LLM agents
- Medium: Memory system for autonomous agents
- Low: Theoretical analysis of agent behavior

### 4. Relevance to Current Trends (10%)
**What it measures:** Alignment with hot topics and emerging directions

**Scoring criteria:**
- **High (8-10):** Directly addresses current major challenges (safety, reasoning, tool use)
- **Medium (5-7):** Related to active research areas
- **Low (1-4):** Niche topic or less active area

**Examples:**
- High: Agent safety, multi-agent coordination, tool use
- Medium: Agent memory, planning algorithms
- Low: Specific domain applications

## Scoring Process

### Step 1: Initial Scoring
For each paper, the LLM assigns scores (1-10) for each dimension based on the abstract and content.

### Step 2: Weighted Total Score
```
Total Score = (Novelty × 0.40) + (Technical × 0.30) + (Practical × 0.20) + (Relevance × 0.10)
```

### Step 3: Ranking
Papers are ranked by total score (highest to lowest).

### Step 4: Selection
Top 5 papers are selected for the daily digest.

## Additional Considerations

### Diversity
If top 5 are all from the same category (e.g., all Agent Evaluation), may swap one for the top paper from another category to ensure diversity.

### Tie-Breaking
If scores are tied:
1. Prefer papers with diagrams (better visual explanation)
2. Prefer papers from well-known institutions/authors
3. Prefer papers with more comprehensive abstracts

### Quality Threshold
Minimum score of 5.0 required to be included. If fewer than 5 papers meet this threshold, include all qualifying papers.

## Example Scoring

**Paper: Spider-Sense - Intrinsic Risk Sensing**
- Novelty: 9/10 (novel intrinsic risk sensing concept)
- Technical: 8/10 (hierarchical adaptive screening, solid experiments)
- Practical: 9/10 (critical for agent safety in production)
- Relevance: 10/10 (agent safety is top priority)
- **Total: 8.9/10**

**Paper: CAR-bench - Consistency and Limit-Awareness**
- Novelty: 7/10 (new benchmark, novel evaluation angle)
- Technical: 8/10 (comprehensive benchmark design)
- Practical: 7/10 (useful for evaluation but not deployment)
- Relevance: 8/10 (agent evaluation is important)
- **Total: 7.4/10**

**Paper: Incremental Agent Training Method**
- Novelty: 4/10 (applies existing RL to agents)
- Technical: 5/10 (standard experiments)
- Practical: 5/10 (limited real-world impact)
- Relevance: 5/10 (not addressing major challenges)
- **Total: 4.6/10** (below threshold)

## Output Format

The daily digest will show:
1. **Top 5 papers** with full Medium-style content
2. **Honorable mentions** section listing remaining papers (titles + links only)

This ensures readers get deep insights into the most important papers while still being aware of other relevant work.
