# Antigravity Instructions & Project Memory: Knesset 2026 Election Analysis System

## 1. Project Context & Purpose
This project is an automated, objective, evidence-based multi-agent analysis system evaluating political parties, party leaders, and realistic candidates for the **2026 Israeli Knesset Elections** (taking place late 2026).
It is implemented using dedicated **Antigravity Skills**:
1. **`run-election-round`** (`.agents/skills/run-election-round/SKILL.md`): Orchestrates the complete 4-phase multi-agent evaluation round across all active worldview profiles.
2. **`build-static-kb`** (`.agents/skills/build-static-kb/SKILL.md`): Gathers, structures, and validates static party rosters (1..30+ candidates), candidate CVs, achievements, voting records, and manifestos.
3. **`interview-worldview`** (`.agents/skills/interview-worldview/SKILL.md`): Interactively interviews the user via `ask_question` to configure custom voter profiles and weighting preferences.
4. **`election-analyst`** (`.agents/skills/election-analyst/SKILL.md`): Domain scoring methodology, rubric guidelines, and reference prompt templates.

> ⚠️ **STRICT MANDATE: NO MONOLITHIC SHORTCUTS & ZERO INLINE DATA**  
> 1. Running an election analysis round MUST NEVER be executed as a monolithic script or by copying past data. You MUST use Antigravity subagent tools (`define_subagent` and `invoke_subagent`).  
> 2. No political data (policy stances, candidate names, scores, evaluations) may appear in instructions or documentation files. All data resides exclusively in rebuildable artifacts under `data/` and `config/`.

## 2. Language & Communication Rules
- **Technical Discussion, Scripts, Code, Architecture, and Git**: English.
- **Content (Policy topics, stances, parties, candidate names, justifications, quotes, reports)**: Hebrew (עברית).

## 3. Core Evaluation Methodology
- **Scoring Range**: `-100.0` (Complete opposition / diametric conflict) to `+100.0` (Full alignment / flawless execution record). `0.0`: Neutrality or absence of stance.
- **6 Normalized Criteria**: Evaluated per topic based on `data/static/rubric/criteria.json` (Platform 15%, Leader Statements 15%, Leader Actions 30%, Candidate Statements 10%, Candidate Actions 20%, Designated Executive 20% - normalized from 110% to 100%).
- **Party Qualification**: Any party passing the electoral threshold (3.25% / 4 mandates) in at least one credible poll is included.
- **Realistic Candidates Cutoff**: Tracked dynamically in `config/polls.yaml` (`round(poll_average) + 1`).
- **Verifiable Citations**: Every score must cite real evidence, quotes, and direct clickable URLs.

---

## 4. Static vs. Dynamic Data Architecture

The system enforces a strict architectural boundary between static and dynamic data:

### Static Knowledge Base (`data/static/`)
Permanent, historical, and structural data managed via the `build-static-kb` skill:
- **`data/static/topics/catalog.json`**: Canonical definition of the 9 core policy topics.
- **`data/static/rubric/criteria.json`**: The 6 mathematical evaluation criteria and normalized weights.
- **`data/static/parties/<party_id>/`**:
  - `party.json`: Official party metadata, leadership titles, and verified URLs.
  - `candidates.json`: Complete candidate roster (1..30+), CVs, public service, key votes, achievements, and controversies.
  - `manifesto.md`: Official party manifestos and foundational platform documents.

### Dynamic Election Data
Transient and evolving data gathered weekly during the election cycle:
- **Polls & Mandates**: Latest polling averages and realistic candidate cutoffs (`config/polls.yaml`).
- **Dynamic Statements & Actions**: Recent speeches, media interviews, votes, and campaign promises gathered during Phase 1 (`data/staging/{DATE}/topics/`).
- **Worldview Profiles**: User-defined policy stances, priorities, and custom weights configured in `config/profiles/*.yaml` (created via `interview-worldview` skill).
- **Evaluations & Reports**: Multi-profile scored datasets (`data/evaluations/`), weekly Markdown reports (`reports/{DATE}/`), and the live responsive HTML dashboard (`docs/index.html`).

---

## 5. Multi-Agent Execution Lifecycle (`run-election-round`)

Whenever instructed to run an analysis round or weekly update, follow the **`run-election-round`** skill:

### Step 0: Ensure Subagents are Defined
Define the 4 subagent types using `define_subagent` if not already defined:
1. `topic_researcher`: Gathers dynamic topic evidence across qualifying parties (`references/researcher_prompt.md`).
2. `topic_validator`: Cross-validates dynamic findings against rubric and checks citations (`references/validator_prompt.md`).
3. `report_rebuilder`: Aggregates validated data, loads static candidate KB, evaluates all configured profiles, and rebuilds reports (`references/rebuilder_prompt.md`).
4. `ui_validator`: Enforces DOM validity, RTL layout, captures desktop/mobile snapshots, and gates deployment (`references/ui_validator_prompt.md`).

### Phase 1: Parallel Information Gathering (9 Concurrent Agents)
- Verify `config/polls.yaml` is up to date.
- Call `invoke_subagent` launching 9 parallel `topic_researcher` agents investigating the 9 canonical policy topics.
- Researchers save output to `data/staging/YYYY-MM-DD/topics/<topic_id>.json`.

### Phase 2: Two-Tier Cross-Validation & Feedback Loop
- Run Tier 1 automated link & schema validator (`scripts/validate_links.py`).
- Call `invoke_subagent` for `topic_validator` agents to cross-examine factual claims and rubric compliance.
- If defects or unverified links are found, send feedback via `send_message` (max 1 revision round).
- Validated files saved to `data/validated/YYYY-MM-DD/topics/<topic_id>.json`.

### Phase 3: Multi-Profile Aggregation & Report Rebuilding
- Call `invoke_subagent` for `report_rebuilder` agent.
- Merge topic files into `data/evaluations/YYYY-MM-DD.json` (`scripts/merge_topics.py`).
- Run `scripts/run_analysis.py --date YYYY-MM-DD`: evaluates all profiles in `config/profiles/`, integrates static candidate data, outputs per-profile Markdown reports and `docs/index.html` with interactive profile switcher.
- Prepare Hebrew Executive Synthesis.

### Phase 4: UI Validation & Deployment Gatekeeper
- Call `invoke_subagent` for `ui_validator` agent.
- Run `scripts/validate_ui.py --date YYYY-MM-DD --strict` capturing desktop and mobile snapshots.
- If defects found, send Reject payload back to `report_rebuilder` (max 2 revision rounds).
- If approved (`status: "APPROVED"` in `ui_validation.json`), commit and deploy (`git push origin main`).

---

## 6. Project Directory Structure
- `.agents/skills/`:
  - **`run-election-round/`**: Master execution skill orchestrating the 4-phase multi-agent round.
  - **`build-static-kb/`**: Static knowledge base builder and candidate roster profiler.
  - **`interview-worldview/`**: Interactive user worldview interview and profile generator.
  - **`election-analyst/`**: Scoring rubric, math, and agent prompt templates.
- `config/`:
  - `profiles/`: Worldview profiles (`default.yaml`, `liberal_economic.yaml`, custom user profiles).
  - `polls.yaml`: Polling benchmarks and realistic seat cutoffs.
  - `parties.yaml`: Party registry and official links.
- `scripts/`:
  - `build_static_kb.py`: Static knowledge base builder and `--verify` auditor.
  - `validate_links.py`: HTTP link and JSON schema validator.
  - `validate_ui.py`: Headless Chrome snapshot capturer and DOM validator.
  - `merge_topics.py`: Topic dataset merger & splitter.
  - `evaluator.py`: 6-criteria scoring engine with static KB integration.
  - `generate_report.py`: Markdown and multi-profile HTML dashboard generator.
  - `run_analysis.py`: Multi-profile analysis runner.
  - `orchestrate_analysis.py`: Pipeline CLI orchestrator.
- `data/`:
  - `static/`: Modular static KB (`topics/`, `rubric/`, `parties/<party_id>/`).
  - `staging/YYYY-MM-DD/topics/`: Raw dynamic research per topic.
  - `validated/YYYY-MM-DD/topics/`: Validated dynamic research per topic.
  - `validation_logs/YYYY-MM-DD/`: Tier 1 summaries, UI audit logs, and snapshots.
  - `evaluations/`: Scored evaluation datasets per date and profile.
- `reports/YYYY-MM-DD/`: Weekly Markdown reports per profile.
- `docs/index.html`: Responsive RTL HTML dashboard deployed to GitHub Pages.
