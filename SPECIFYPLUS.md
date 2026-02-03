-   [](/)
-   [Part 3: SDD-RI Fundamentals](/docs/SDD-RI-Fundamentals)
-   [Chapter 13: Master Spec-Kit Plus](/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on)
-   Constitution Phase — Project-Wide Quality Standards

# Constitution Phase — Project-Wide Quality Standards

You've installed Spec-Kit Plus and initialized your project. Now it's time to create the foundational rules that will guide every part of your research paper project.

The Constitution answers a critical question: **What standards apply to every piece of work you do?** Not just for this paper, but for all papers. Not just this deadline, but for your professional reputation.

Think of it like team rules before building a big LEGO project:

-   What if you want all towers square, but your helper builds round ones?
-   What if you decide the roof must be blue, but your helper builds red?

The Constitution is your team's **Rulebook**. It lists the most important rules that both you and your AI companion MUST follow, no matter what.

* * *

## What Is a Constitution?

### Constitution: Global Rules, One Per Project

A **Constitution** defines **immutable standards** applying to **all work** in a project. It's distinct from a **Specification**, which applies to **one feature**.

**Constitution applies to (research paper project)**:

-   Citation standards for ALL papers (APA format, source verification)
-   Writing clarity for ALL papers (Flesch-Kincaid grade level)
-   Academic integrity for ALL papers (plagiarism checking)
-   Source requirements for ALL papers (peer-reviewed minimum)

**Specification applies to (one specific paper)**:

-   THIS paper's thesis statement
-   THIS paper's specific research questions
-   THIS paper's word count and deadline
-   THIS paper's acceptance criteria

**Example**:

```
CONSTITUTION (applies to ALL papers):  ✅ "All papers must cite primary sources"  ✅ "All claims must be verified against sources"  ✅ "APA citation format required"  ✅ "Zero plagiarism tolerance"SPECIFICATION (applies only to THIS paper):  ✅ "Thesis: AI-native development requires spec-first thinking"  ✅ "Target length: 5,000 words"  ✅ "Minimum 12 peer-reviewed sources"  ✅ "Due date: December 15"
```

### Why Constitution Matters: The Cascade

The Constitution is the **starting point of the cascade**:

```
Clear Constitution    ↓(ensures every spec respects quality standards)    ↓Clear Specification    ↓(ensures planning accounts for quality gates)    ↓Clear Plan    ↓(ensures tasks include verification)    ↓Clear Tasks    ↓(enables AI to generate properly cited writing)    ↓Published Research Paper
```

**Weak Constitution** produces:

-   Specs that don't specify citation requirements
-   Plans that skip plagiarism checking
-   Writing with uncited claims
-   Papers that fail fact-checking

**Strong Constitution** produces:

-   Specs that automatically include source quality requirements
-   Plans with built-in verification steps
-   Writing that's properly cited
-   Papers that pass publication standards

### Constitution is One-Time, Feature Work is Repetitive

You write the Constitution **once per project**. Then, for each paper:

```
1. Initialize project2. Write Constitution (quality standards for ALL papers)3. Commit Constitution to git4. FOR EACH PAPER:   - Run /sp.specify (new specification for this paper)   - Run /sp.clarify (refine specification)   - Run /sp.plan (new plan for this paper)   - Run /sp.tasks (new tasks for this paper)   - Run /sp.implement (write paper with AI)   - Commit paper to git
```

* * *

## Part A: Reading the Base Constitution

Before writing your own, look at the base Constitution file that `specifyplus init` created:

```
# Open the constitution filecat .specify/memory/constitution.md
```

**What you'll see**: A starter template with placeholder sections for principles, standards, and constraints.

**The Key Insight**: Constitutions are project-specific. Your research paper Constitution would never mention "type hints" because that's for code. A software project Constitution wouldn't need "citation format" because that's for papers.

* * *

## Part B: Writing Your Research Paper Constitution

Now let's write YOUR Constitution for the research paper project.

### Step 1: Run `/sp.constitution`

Open your AI tool and run the constitution command with your project requirements:

```
/sp.constitutionProject: Research paper on AI-native software developmentCore principles:- Accuracy through primary source verification- Clarity for academic audience (computer science background)- Reproducibility (all claims cited and traceable)- Rigor (peer-reviewed sources preferred)Key standards:- All factual claims must be traceable to sources- Citation format: APA style- Source types: minimum 50% peer-reviewed articles- Plagiarism check: 0% tolerance before submission- Writing clarity: Flesch-Kincaid grade 10-12Constraints:- Word count: 5,000-7,000 words- Minimum 15 sources- Format: PDF with embedded citationsSuccess criteria:- All claims verified against sources- Zero plagiarism detected- Passes fact-checking review
```

**What the agent does**:

-   Creates a comprehensive Constitution file at `.specify/memory/constitution.md`
-   Defines testable quality standards
-   Documents all constraints and success criteria
-   Shows you the generated Constitution

### Step 2: Review Your Constitution

After the agent generates your Constitution, **review it carefully**.

**Your Prompt**:

```
Show me the generated constitution file and explain what it contains.
```

**Agent shows**:

-   **Core Principles** — Your research philosophy
-   **Quality Standards** — Testable criteria for all papers
-   **Source Requirements** — Citation and verification rules
-   **Constraints** — Length, format, deadlines
-   **Success Criteria** — How to know if standards are met

### Step 3: Improve Your Constitution

Think about what "good research" means for YOUR project. Ask the agent:

```
Review my Constitution at .specify/memory/constitution.md and improve it:1. Are all standards testable (not vague)?   - ❌ Vague: "Papers should be well-written"   - ✅ Testable: "Flesch-Kincaid grade 10-12; active voice 75%+ of time"2. Did I cover essential categories?   - Citation accuracy   - Source verification   - Writing clarity   - Plagiarism checking   - Review process3. Are any standards unrealistic?Suggest 2-3 concrete improvements.
```

**What the agent does**:

-   Identifies vague standards and makes them testable
-   Suggests missing categories
-   Flags unrealistic constraints
-   Updates the Constitution file

* * *

## Part C: Commit Constitution to Git

Here's a critical best practice: **Always commit the Constitution before starting feature work.**

### Why Commit First?

1.  **Immutability**: Constitution is foundational; committing signals "this is our standard"
2.  **Clarity**: Everyone (including your AI) sees Constitution as the baseline
3.  **Traceability**: Git history shows when and why Constitution was created
4.  **Reversibility**: You can revert if needed (rare, but important)

### Commit Steps

**Your Prompt**:

```
/sp.git.commit_pr Commit the constitution to a feature branch
```

**Agent Does**:

-   Creates a conventional commit for the constitution
-   Pushes to a new feature branch
-   Creates a draft PR (or shares compare URL)

The Constitution is now the foundation for all your paper work. Every specification you write, every plan you generate—they all work within the Constitution's constraints.

* * *

## How Constitution Guides Downstream Phases

Now that you've created a Constitution, let's see how it cascades through every other phase.

### Constitution → Specification Phase

**Your Constitution says**:

```
- All papers must cite primary sources- Minimum 50% peer-reviewed sources- APA citation format- Zero plagiarism tolerance
```

**Your Specification for Paper #1 must respect this**:

```
This specification inherits Constitution standards:- Thesis: "AI-native development requires spec-first thinking"- Length: 5,000 words- Sources: minimum 15 total, minimum 8 peer-reviewed- Format: APA style (inherited from Constitution)- Success criteria: All claims cited, Flesch-Kincaid 10-12
```

Notice: You DON'T re-specify citation format or plagiarism checking. The Constitution already requires it.

### Constitution → Plan Phase

**Your Constitution says**:

```
- All claims must be verified against sources- Plagiarism check required before submission
```

**Your Plan must account for this**:

```
Phase 1: Research and source identificationPhase 2: Detailed outline with source assignmentsPhase 3: Draft writing with inline citationsPhase 4: Fact-checking pass (verify all claims)Phase 5: Plagiarism scanning (0% tolerance)Phase 6: Final review and submission
```

The plan INCLUDES verification steps because Constitution REQUIRES them.

### Constitution → Implementation

When you write the paper with AI, Constitution standards guide every interaction:

```
You: "Write the Introduction section. Use these sources: [list].Follow the Constitution: APA citations, verify all claims."AI: "I'll write the introduction with:- In-text APA citations for each claim- Plain language targeting grade 10-12 reading level- Verification of claims against provided sources"[AI writes introduction with citations]You: "The third claim needs a primary source, not secondary.Constitution requires 50% primary sources."AI: "You're right. Let me find the primary research on that topicand revise the citation."[AI revises with primary source]
```

Constitution REQUIREMENTS shape every interaction.

* * *

## Common Mistakes

### Mistake 1: Copying Constitution Without Customization

**The Error**: "I'll use the example Constitution as-is."

**Why It's Wrong**: Constitutions are project-specific. A code project Constitution mentions "type hints"—irrelevant for papers.

**The Fix**: Read examples for structure, but write rules specific to YOUR project.

### Mistake 2: Vague Quality Standards

**The Error**: "Papers must be good quality" or "Sources should be credible"

**Why It's Wrong**: "Good" and "credible" are subjective. No one can verify these.

**The Fix**: Use testable criteria:

-   ❌ Vague: "Good writing quality"
-   ✅ Testable: "Flesch-Kincaid grade 10-12; all claims cited; zero plagiarism"

### Mistake 3: Forgetting to Commit Constitution

**The Error**: Create Constitution, then start spec without committing.

**Why It's Wrong**: Constitution becomes "whatever I remember" instead of "documented standard."

**The Fix**: Always commit Constitution BEFORE starting `/sp.specify`.

* * *

## Try With AI

Validate your Constitution and understand how quality rules cascade:

**Test Constitution Completeness:**

> "Review my Constitution at `.specify/memory/constitution.md`. Check: (1) Are all standards testable and specific? (2) Did I cover citation, source verification, writing clarity, plagiarism checking? (3) Are any standards unrealistic? Suggest 2-3 improvements."

**Explore Cascade Effect:**

> "I wrote a Constitution with standards for APA citations, source verification, and zero plagiarism tolerance. Explain how these rules cascade: How do they affect my Specification? My Plan? My Implementation? Give me a concrete example."

**Test Specification Alignment:**

> "Based on my Constitution rules, what constraints MUST a specification for my first paper section include? Walk through: citation requirements, source types, verification steps, and quality standards."

# Constitution Phase — Project-Wide Quality Standards

This lesson teaches students how to create a Constitution using `/sp.constitution`—a document that defines project-wide quality standards applying to ALL work in a project. Students run the command, review the generated constitution, improve it with testable criteria, then commit it to git. The key distinction: Constitution applies to ALL papers (global rules), Specification applies to ONE paper (feature-specific requirements). Students learn that weak constitutions produce vague downstream work, while strong constitutions cascade quality through every phase.

### Mental Models

-   **Constitution vs Specification**: Constitution = global rules for ALL features ("all papers must cite primary sources, APA format, zero plagiarism"). Specification = rules for ONE feature ("this paper's thesis is X, due December 15"). Constitution written once; Specification written per feature.
    
-   **The Cascade Effect**: Clear Constitution → Clear Specification → Clear Plan → Clear Tasks → Quality Implementation. Each phase respects Constitution constraints without re-specifying them. Weak Constitution produces specs without citation requirements, plans without verification steps, papers with uncited claims.
    
-   **Testability Principle**: Standards must be measurable, not subjective. ❌ Vague: "Papers should be well-written." ✅ Testable: "Flesch-Kincaid grade 10-12; active voice 75%+ of time; all claims cited."
    

### Key Patterns

-   **Run `/sp.constitution` with project requirements**: Provide core principles, key standards, constraints, and success criteria. Agent generates comprehensive constitution file at `.specify/memory/constitution.md`.
    
-   **Review for testability**: After generation, check: Are all standards testable (not vague)? Are essential categories covered (citation, verification, clarity, plagiarism)? Are any standards unrealistic?
    
-   **Commit before feature work**: Always `git commit` the Constitution BEFORE running `/sp.specify`. This establishes Constitution as documented standard with full traceability.
    
-   **Constitution-First Workflow**: Initialize project → Write Constitution (once) → Commit to git → FOR EACH PAPER: `/sp.specify` → `/sp.clarify` → `/sp.plan` → `/sp.tasks` → `/sp.implement` → commit.
    

### Common Mistakes

-   **Copying Constitution without customization**: Using example Constitution as-is. A code project Constitution mentions "type hints"—irrelevant for papers. Read examples for structure, write rules specific to YOUR project.
    
-   **Vague quality standards**: "Papers must be good quality" or "Sources should be credible." These are subjective and unverifiable. Use testable criteria: "Flesch-Kincaid grade 10-12; all claims cited; zero plagiarism."
    
-   **Forgetting to commit Constitution**: Creating Constitution then starting `/sp.specify` without committing. Constitution becomes "whatever I remember" instead of documented standard. Always commit BEFORE starting feature work.
    

### Progression Context

-   **Builds on**: Lesson 2 (Installation and Setup) where students installed Spec-Kit Plus and initialized their project. The constitution file from `specifyplus init` is a starter template—this lesson expands it.
    
-   **Leads to**: Lesson 4 (Specification Phase) where students run `/sp.specify` to write requirements for their first paper. The Specification must respect Constitution standards without re-specifying them.
    

## Study Mode

Teaching by Socratic Method (OpenAI Study Mode & Google Extended Learning)

📚Socratic Teaching - AI guides you with questions

### Ready to Learn

Click the Teach button to get a guided explanation of this lesson from the book.

---
Source: https://agentfactory.panaversity.org/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on/constitution-phase


-   [](/)
-   [Part 3: SDD-RI Fundamentals](/docs/SDD-RI-Fundamentals)
-   [Chapter 13: Master Spec-Kit Plus](/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on)
-   Specify Phase — Writing Complete Specifications

# Specify Phase — Writing Complete Specifications

Welcome to the most important phase: Specification. This is where you translate your vague ideas ("I want to write a research paper") into crystal-clear requirements that AI can build from.

Here's the paradigm shift: **In AI-native development, your ability to write a clear specification is more valuable than your ability to write code.** Bad code can be refactored—but a bad spec breaks everything downstream. In this lesson, you'll learn how to collaborate with AI to define success and turn it into a complete, testable specification.

* * *

## Thinking About What Success Looks Like

Before writing a specification, define criteria for evaluating whether the solution succeeds. This is NOT a formal phase; it's an informal human-AI conversation that clarifies intent.

Not "does it compile?" or "do tests pass?" (those are technical validation). Real evals are business/user criteria that define success:

**For a research paper:**

-   ✅ "Paper defines 3+ concrete AI applications in K-12 classrooms"
-   ✅ "All claims supported by peer-reviewed sources"
-   ✅ "Reader can explain ROI of classroom AI after reading"
-   ✅ "Paper passes plagiarism check with 0% match"

**For any document:**

-   ✅ "Audience can complete the intended action after reading"
-   ✅ "All factual claims are traceable to sources"
-   ✅ "Structure follows the established format requirements"

* * *

## Part A: Pre-Specification Conversation

Here's how professionals work: **YOU drive the exploration through questions.** The AI doesn't interview you; you use the AI to think through requirements.

### Step 1: Start the Conversation

Open your AI tool in your `my-research-paper` directory:

```
I want to write a research paper on AI's impact on K-12 classroom efficiency.Before I write the formal spec, help me think through:1. What aspects of "AI in education" should I focus on?2. Who is my target audience?3. What does success look like for this paper?4. What edge cases or constraints should I consider?
```

**Example conversation:**

```
You: "I want to write a research paper on AI in K-12 education.      What aspects should I focus on?"AI: "Key focus areas for K-12 AI research:     - Teacher workload reduction (grading, planning automation)     - Student engagement improvements (adaptive learning)     - Administrative efficiency (scheduling, resource allocation)     - Learning outcome measurement (assessment analytics)     Which resonates with your goals?"You: "I'm interested in teacher workload and student outcomes.      What would success look like for this paper?"AI: "For a paper on those topics, success criteria might be:     - Identifies 3+ specific AI applications with evidence     - Cites peer-reviewed sources (8+ minimum for academic credibility)     - Reader understands economic ROI (time saved, outcomes improved)     - Clear enough that school administrators could act on recommendations"You: "What constraints should I consider?"AI: "Key constraints for academic papers:     - Word count: 3000-5000 words is standard for this scope     - Citation style: APA is common for education research     - Source quality: Peer-reviewed journals, recent publications (past 10 years)     - Scope boundaries: What you're NOT covering (ethics, specific products)"
```

### Step 2: Summarize What You Learned

From the conversation, you now know:

-   **Focus**: Teacher workload reduction + student outcomes
-   **Audience**: Education administrators and technology decision-makers
-   **Success**: 3+ AI applications, 8+ sources, clear ROI explanation
-   **Constraints**: 3000-5000 words, APA format, peer-reviewed sources
-   **Not covering**: Ethics debates, specific product comparisons

This becomes your specification.

* * *

## Part B: Write Your Specification

Now formalize the conversation into a specification using `/sp.specify`.

### Step 1: Run `/sp.specify`

```
/sp.specify Research paper on AI's impact on K-12 classroom efficiencyTarget audience: Education administrators evaluating AI adoptionFocus: Teacher workload reduction and student outcome improvementsSuccess criteria:- Identifies 3+ concrete AI applications with evidence- Cites 8+ peer-reviewed academic sources- Reader can explain ROI of classroom AI after reading- All claims supported by evidenceConstraints:- Word count: 3000-5000 words- Format: Markdown source, APA citations- Sources: Peer-reviewed journals, published within past 10 years- Timeline: Complete within 2 weeksNot building:- Comprehensive literature review of entire AI field- Comparison of specific AI products/vendors- Discussion of ethical concerns (separate paper)- Implementation guide or code examples
```

**What the agent does:**

-   Creates a new feature branch automatically
-   Generates comprehensive spec file at `specs/[feature-name]/spec.md`
-   Defines user scenarios and edge cases
-   Establishes acceptance criteria
-   Sets up testing requirements

### Step 2: Review the Generated Specification

After the agent creates your spec, review it:

```
Show me the generated specification and explain what each section contains.
```

**Agent shows:**

-   **Intent** — What you're building and why
-   **Constraints** — Boundaries and requirements
-   **Success Evals** — Measurable acceptance criteria
-   **Non-Goals** — What you're explicitly NOT building

### Step 3: Verify Completeness

Check that your specification has:

```
Specification Checklist:[ ] Intent is clear (someone unfamiliar can understand the goal)[ ] Constraints are specific and testable (not vague "do good work")[ ] Success Evals are SMART (Specific, Measurable, Achievable, Relevant, Time-bound)[ ] Non-Goals are explicit (prevents scope creep)[ ] No "how" leaked in (describes what, not how to build)[ ] Written clearly enough that another person could write from it
```

* * *

## Part C: The SMART Test

Success Evals must be **SMART**: Specific, Measurable, Achievable, Relevant, Time-bound.

### Test Your Success Criteria

**❌ Vague (NOT SMART):**

```
- Paper is high-quality- Sources are credible- Writing is clear- Reader finds it valuable
```

**✅ SMART:**

```
- Paper is between 3000-5000 words- Paper cites 8+ peer-reviewed academic sources- Each major claim is supported by evidence- Reader can explain 3 concrete AI use cases after reading- Paper completed within 2-week timeframe
```

### Ask AI to Review

```
Review my specification at specs/[feature-name]/spec.md.For each success criterion, check if it's SMART:- Specific (not vague)?- Measurable (can verify objectively)?- Achievable (realistic)?- Relevant (matters for this paper)?- Time-bound (has deadline)?Identify any vague criteria and suggest specific alternatives.
```

* * *

## Common Mistakes

### Mistake 1: Leaking Implementation Into Specification

**The Error:**

```
## Specification: Research PaperThe paper will be written using Claude AI to:1. Research the topic2. Outline the structure3. Generate each section based on the outline4. Ask Claude to review and refine
```

**Why It's Wrong:** This is IMPLEMENTATION (HOW). Specification is WHAT.

**The Fix:** Keep specification focused on outcomes, not process:

```
## Intent3000-5000 word research paper on AI in K-12 education.## Success Evals- Paper identifies 3+ concrete AI applications- At least 8 citations from peer-reviewed sources- Each claim supported by evidence
```

### Mistake 2: Vague Success Criteria

**The Error:** "Paper should be well-written" or "Sources should be credible"

**Why It's Wrong:** "Well-written" and "credible" are subjective. No one can verify these.

**The Fix:** Use testable criteria:

-   ❌ Vague: "Paper should be well-researched"
-   ✅ SMART: "Paper cites 8+ peer-reviewed sources; average publication date within past 10 years"

### Mistake 3: Missing Non-Goals

**The Error:** Only specifying what you ARE building, not what you're NOT building.

**Why It's Wrong:** Scope creep happens. AI might add "helpful" sections you didn't want.

**The Fix:** Explicitly state boundaries:

```
## Non-Goals- Not a comprehensive literature review (focused analysis only)- Not a comparison of specific AI products- Not an implementation guide- No discussion of ethical concerns (separate paper)
```

* * *

## Validation: The Cascade Effect

Now test your specification's quality by asking: **Will this spec produce a good plan?**

**A good spec has:**

-   ✅ Crystal-clear intent (no ambiguity)
-   ✅ Explicit constraints (no surprises during planning)
-   ✅ Measurable success criteria (AI can build acceptance tests from them)
-   ✅ Constitution alignment (specification respects Constitution standards)

**A bad spec has:**

-   ❌ Vague intent ("should work correctly"—what's "correct"?)
-   ❌ Missing constraints (surprises emerge during implementation)
-   ❌ Ambiguous criteria ("handle errors"—how?)
-   ❌ Ignores Constitution (specification asks for things Constitution forbids)

**Action:** Read your specification aloud. Does it sound clear? Would someone else understand exactly what to write?

* * *

## Try With AI

Ready to write your specification? Practice with your AI companion:

**Explore Success Criteria:**

> "I want to write a research paper on \[your topic\]. Before I write the formal spec, help me define success: What does 'good' mean for this paper? What would prove it's valuable? Don't let me write vague requirements like 'well-researched'—push me toward specific, measurable criteria."

**Practice SMART Criteria:**

> "Review my specification at specs/\[feature-name\]/spec.md. For each success criterion, check if it's SMART (Specific, Measurable, Achievable, Relevant, Time-bound). Identify vague criteria like 'good quality' and suggest specific alternatives."

**Test Specification Completeness:**

> "Looking at my spec, identify what's missing: (1) Are constraints explicit? (2) Are non-goals defined? (3) Could someone else write this paper from just the spec? (4) Does it respect my Constitution standards? Generate a list of improvements."

**Apply to Your Paper:**

> "Help me write a specification for my research paper on \[topic\]. Walk me through: (1) What exactly am I building? (2) Who is the audience? (3) What does success look like—specifically? (4) What constraints apply? (5) What am I NOT covering? Then run /sp.specify with everything we discussed."

# Specify Phase — Writing Complete Specifications

This lesson teaches students how to transform vague project ideas into clear, measurable specifications through a two-part workflow: (1) Pre-specification conversation where YOU drive exploration through questions with AI, then (2) Formalize into specification using `/sp.specify`. Students learn that specification answers "What are we building?" with Intent, Constraints, Success Evals, and Non-Goals—not "How" (that's planning). The key paradigm shift: your ability to write a clear specification is more valuable than your ability to write code.

### Mental Models

-   **Pre-Specification Conversation**: Before writing formal specs, have an informal conversation with AI to clarify intent. YOU drive the exploration through questions ("What aspects should I focus on? Who is my audience? What does success look like?"). The AI doesn't interview you; you use AI to think through requirements.
    
-   **SMART Criteria Filter**: Success Evals must be Specific, Measurable, Achievable, Relevant, Time-bound. "Paper is high-quality" fails (subjective). "Paper cites 8+ peer-reviewed sources within past 10 years" passes (verifiable).
    
-   **What vs How Boundary**: Specifications describe WHAT (outcomes). Plans describe HOW (process). If you're writing about steps, sequence, or tools—you're in planning, not specification.
    
-   **Cascade Effect**: Clear spec → clear plan → clear tasks → quality output. Vague spec breaks everything downstream. Test your spec by asking: "Will this produce a good plan?"
    

### Key Patterns

-   **Two-Part Workflow**: (1) Pre-specification conversation to explore requirements, then (2) `/sp.specify` to formalize into structured document. Never skip the conversation—it surfaces constraints and edge cases.
    
-   **Four-Section Structure**: Intent (what problem, why, audience) → Constraints (limits, format, scope) → Success Evals (measurable done-ness) → Non-Goals (explicit out-of-scope). This structure works for any project type.
    
-   **Specification Checklist**: After generating spec, verify: Intent clear? Constraints specific? Success Evals SMART? Non-Goals explicit? No HOW leaked? Could someone else build from this?
    
-   **Ask AI to Review**: After `/sp.specify`, prompt: "For each success criterion, check if it's SMART. Identify vague criteria and suggest specific alternatives."
    

### Common Mistakes

-   **Leaking Implementation**: Writing "Use Claude AI to research, outline, generate sections" in spec. This is HOW, not WHAT. Keep spec focused on outcomes: "5000-word paper with 8+ sources."
    
-   **Vague Success Criteria**: "Paper is high-quality" or "sources are credible" can't be verified objectively. Use testable criteria: "8+ peer-reviewed sources; APA formatting; 3000-5000 words."
    
-   **Missing Non-Goals**: Not specifying what you're NOT building causes scope creep. Explicitly state: "Not a comprehensive literature review; not a product comparison; no ethical discussion."
    
-   **Skipping Pre-Specification Conversation**: Jumping straight to `/sp.specify` without clarifying intent, audience, and success criteria. The conversation surfaces requirements you'd otherwise miss.
    

### Progression Context

-   **Builds on**: Lesson 3 (Constitution Phase) established global rules. Lesson 4 applies those rules to a specific feature specification.
    
-   **Leads to**: Lesson 5 (Clarify Phase) uses `/sp.clarify` to identify gaps and ambiguities in the specification. Lesson 6 (Plan Phase) takes the clarified specification and designs HOW to build it.
    

## Study Mode

Teaching by Socratic Method (OpenAI Study Mode & Google Extended Learning)

📚Socratic Teaching - AI guides you with questions

### Ready to Learn

Click the Teach button to get a guided explanation of this lesson from the book.

---
Source: https://agentfactory.panaversity.org/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on/specify-phase


-   [](/)
-   [Part 3: SDD-RI Fundamentals](/docs/SDD-RI-Fundamentals)
-   [Chapter 13: Master Spec-Kit Plus](/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on)
-   Clarify Phase

# Clarify Phase

In Lesson 04, you wrote a specification for your research paper. It looked complete. But there are always gaps you didn't catch—ambiguities that seemed clear in your head but are actually vague on paper. Assumptions about scope, audience, or success that you didn't state explicitly.

This is where the `/sp.clarify` command helps. **Clarify is a quick check** that your specification is complete before moving to planning.

Think of `/sp.clarify` as your AI companion putting on a "detail detective" hat and asking: "Wait, who exactly is your audience? What counts as a 'well-researched' paper? How many sources is enough? What format should this follow?" It finds gaps you might have missed, then you decide whether to update your spec.

The goal: Make your specification **so clear** that the planning phase can generate a perfect implementation plan.

* * *

## What Does /sp.clarify Do?

### The Clarify Command

`/sp.clarify` analyzes your specification and reports:

1.  **Ambiguous Terms** - Words that could mean multiple things
    
    -   Example: "well-researched paper" (5 sources? 50 sources? What counts as credible?)
    -   Example: "professional format" (APA? MLA? Chicago? Single-spaced? Double-spaced?)
2.  **Missing Assumptions** - Things you assumed but didn't state
    
    -   Example: You assumed academic paper but didn't specify citation style
    -   Example: You assumed 3,000-word length but didn't state minimum or maximum
    -   Example: You assumed English but didn't specify if other languages acceptable
3.  **Incomplete Requirements** - Scenarios or cases you didn't cover
    
    -   Example: You specified content but didn't specify editing or revision process
    -   Example: You specified research but didn't specify how to handle conflicting sources
    -   Example: You specified "introduce topic" but didn't define what introduction contains
4.  **Scope Conflicts** - Places where scope is unclear or inconsistent
    
    -   Example: "Comprehensive research" on what exactly? All historical context or just recent developments?
    -   Example: "Clear structure" using what organization method? Chronological? Thematic?
    -   Example: "Compelling conclusion" appealing to whom? Academic audience? General readers?

### Why Clarify Matters Before Planning

A vague specification creates a vague plan. When the planning phase can't understand exactly what you want, it generates ambiguous design decisions. Then you spend time during implementation realizing your actual intention wasn't captured.

**Without clarification** (vague spec):

```
Intent: Write research paper on climate changeSuccess Criteria: Paper is well-researched and professionally written
```

Planning phase has questions:

-   What specific aspect of climate change? Global warming trends? Policy solutions? Historical development?
-   How many sources? Academic only or include journalistic sources?
-   What length? 2 pages? 10 pages? 50 pages?
-   What citation style? Who's the audience?

**With clarification** (precise spec):

```
Intent: Write research paper on climate policy solutions adopted since 2015Success Criteria:- Minimum 5 peer-reviewed sources (journals, not news)- APA format, 3,000-4,000 words- Three policy solutions compared (effectiveness, adoption barriers, future outlook)- Audience: undergraduate economics students- Conclusion: assessment of which policy approach shows most promise
```

Planning phase now has clear requirements and generates specific implementation tasks.

* * *

## The Clarify Workflow

### Step 1: Run /sp.clarify

In Claude Code, from your research-paper directory:

```
/sp.clarifyMy research paper specification is at specs/paper/spec.mdPlease analyze it for:1. Ambiguous terms (what does "well-researched" mean? How many sources? What type?)2. Missing assumptions (citation style? audience? paper length? structure?)3. Incomplete requirements (what does "introduce topic" contain? how to handle conflicting sources? revision process?)4. Scope conflicts (is this historical overview or current policy analysis? broad or narrowly focused?)What gaps should I address before planning the paper structure?
```

Your AI companion will analyze your specification, identify gaps or ambiguities, and ask clarifying questions. Review its findings and consider which gaps are critical versus nice-to-have.

### Step 2: Update Your Specification

For each clarifying question, decide: **Do I need to answer this before planning?**

-   **Critical gaps** (planning can't work without this): Update spec immediately
    
    -   Example: Citation style is critical (affects all references)
    -   Example: Paper length is critical (determines research scope)
    -   Example: Audience is critical (determines tone and complexity)
-   **Nice-to-have clarifications** (planning can proceed): Update spec or defer
    
    -   Example: Specific revision timeline
    -   Example: Preferred formatting tools
    -   Example: Aesthetic preferences

### Step 3: Re-Run /sp.clarify (Optional)

If you made significant changes, run `/sp.clarify` again:

```
I've updated my research paper specification based on your feedback.Please analyze it again for remaining gaps.Is this specification clear enough to proceed to the planning phase?
```

Most specifications need 1-2 clarification rounds. After that, they're ready for planning.

* * *

## Clarifying Your Paper Specification

Now let's clarify YOUR research paper specification—the one you wrote in Lesson 04.

### Step 1: Run /sp.clarify on Your Specification

In Claude Code, from your research-paper directory, run:

```
/sp.clarifyMy research paper specification is at specs/paper/spec.mdPlease analyze it for:1. AMBIGUOUS TERMS   - What does "well-researched" mean in my spec? (how many sources? which types?)   - What does "professional format" mean? (which citation style? spacing? margins?)   - What does "clear structure" mean? (how many sections? what should each contain?)2. MISSING ASSUMPTIONS   - What citation style should I use? (APA, MLA, Chicago, Harvard?)   - What's the target audience? (academic, general readers, specific field?)   - What's the paper length? (minimum and maximum word count?)   - How recent should sources be? (published in last 5 years? 10 years?)3. INCOMPLETE REQUIREMENTS   - What should the introduction contain? (background? thesis statement? scope?)   - How do I handle conflicting sources? (which viewpoints to include?)   - What constitutes a "credible" source? (peer-reviewed only? news acceptable?)   - How should I structure the paper? (chronological? thematic? by source?)4. SCOPE CONFLICTS   - Is this narrowly focused on one aspect or broadly covering the topic?   - Is this historical overview or current-state analysis?   - Are there sub-questions I should address or exclude?List any gaps or questions. Which ones are CRITICAL (planning won't work without them) vs NICE-TO-HAVE (improve quality but not blocking)?
```

### Step 2: Evaluate Feedback

Review the clarifying questions your AI companion identified. For each one, ask:

-   Is this critical to planning the paper structure?
-   Can planning proceed without this answer, or does it affect section design?
-   Should I resolve this now or defer it?

### Step 3: Update Your Specification

Update your spec.md with the clarifications you decide are critical. You might add:

```
Audience: Undergraduate economics students (not specialized researchers)Citation Style: APA format, 7th editionLength: 3,000-3,500 wordsSource Types: Peer-reviewed journals (80%), reputable news sources (20%)Structure: Introduction → Problem Analysis → Three Solutions → Comparison → Conclusion
```

### Step 4: Verify Readiness

Ask your AI companion:

```
Based on the clarifications I've made, is my research paper specification now ready for the planning phase?Can you explain the paper structure and success criteria back to me to confirm we're aligned?
```

* * *

## Why Clarification Prevents Implementation Problems

Skipping clarification creates cascading problems during implementation:

**Missing specification clarity** → **Vague planning decisions** → **Confused implementation tasks** → **Rework and frustration**

Here's how clarification breaks this chain:

1.  You run `/sp.clarify` and discover ambiguity: "What's the minimum number of sources?"
2.  You update spec: "Minimum 6 peer-reviewed sources"
3.  Planning phase generates clear implementation task: "Research and select 6+ peer-reviewed sources on \[topic\]"
4.  Implementation proceeds smoothly because the requirement is explicit

* * *

## Common Mistakes

### Mistake 1: Skipping /sp.clarify Because "Spec Looks Good to Me"

**The Error**: "I wrote a detailed spec. I don't need clarification."

**Why It's Wrong**: Every specification has ambiguities you didn't notice. Clarify surfaces them now (5 minutes) instead of during implementation (5 hours).

**The Fix**: Always run `/sp.clarify`. You'll be surprised what gaps emerge. Most specs need 1-2 clarification rounds.

### Mistake 2: Ignoring Critical Clarifications

**The Error**: "AI asked about citation style but I'll just figure that out later."

**Why It's Wrong**: Citation style affects every source reference. Deferring this decision means planning the paper structure without knowing how citations work, then discovering mid-implementation you chose wrong.

**The Fix**: Address critical gaps upfront. Test: "If planning didn't know this, would they make a different choice?" If yes, it's critical.

### Mistake 3: Accepting All AI Suggestions Without Thinking

**The Error**: AI suggests adding source diversity requirements → immediately adding without evaluating necessity

**Why It's Wrong**: Not all suggestions improve your spec. Some add unnecessary complexity.

**The Fix**: Evaluate each suggestion:

-   Is this critical to paper quality or nice-to-have?
-   Does this affect planning or just implementation?
-   Can I defer this to revision?

Then decide: Accept, Reject, or Modify.

* * *

## Try With AI

Ready to clarify your research paper specification? Test these prompts:

**Explore Specification Gaps:**

> "I'm ready to run /sp.clarify on my research paper specification. Before I do, what are the most common gaps in paper specifications? What questions should I expect the clarification process to surface?"

**Interpret Clarification Feedback:**

> "Here are the clarifying questions my AI identified about my paper spec: \[paste the questions\]. Help me categorize them: (1) Which are CRITICAL (planning won't work without this)? (2) Which are NICE-TO-HAVE (improve quality but not blocking)? (3) Which can I defer? Explain how each critical gap affects the planning phase."

**Validate Clarity:**

> "I've updated my research paper specification based on clarification feedback. Read my updated spec and tell me: (1) Is the paper scope clear? (2) Would a planner know what paper structure to design? (3) Are there any remaining ambiguities? (4) Is this specification ready for the planning phase?"

**Practice Decision-Making:**

> "My clarification feedback included suggestions about \[topic\]. Help me decide whether to address each suggestion now: Is it critical for planning? Does it affect success criteria? Can I defer it to revision? Walk me through your decision framework."

* * *

# Clarify Phase

The `/sp.clarify` command systematically identifies gaps, ambiguities, and missing assumptions in specifications before the planning phase. Students learn to recognize specification weaknesses (vague terms, unstated assumptions, incomplete requirements, scope conflicts) and iteratively refine specs through AI feedback, preventing cascading problems during implementation and planning.

## Mental Models

-   **Detail Detective Pattern**: `/sp.clarify` acts as a critical reader that identifies gaps you didn't catch—ambiguities that seemed clear in your head but are vague on paper (assumptions about scope, audience, success, terminology, requirements, scenarios).
    
-   **Specification Clarity ↔ Plan Quality**: Vague specifications produce vague plans; precise specifications enable specific implementation tasks. Clarification is the bridge between intent and actionable design.
    
-   **Critical vs. Nice-to-Have**: Distinguish gaps that block planning (audience, citation style, length requirements) from improvements that enhance quality (formatting preferences, timeline details). Prioritize critical gaps upfront; defer nice-to-have clarifications.
    
-   **Iterative Specification Refinement**: Most specifications require 1-2 clarification rounds. Each round surfaces remaining gaps, iteratively improving clarity until the spec is ready for planning.
    

## Key Patterns

-   **Four Gap Categories** (identified by `/sp.clarify`):
    
    -   Ambiguous Terms (undefined concepts like "well-researched," "professional format")
    -   Missing Assumptions (unstated scope: citation style, audience, word count, source recency)
    -   Incomplete Requirements (unspecified scenarios: how to handle conflicts, what sections contain, revision process)
    -   Scope Conflicts (unclear focus: historical vs. current, broad vs. narrow, what's in/out)
-   **Critical Gap Recognition**: Test whether planning can proceed without this answer—if planning would make different choices without it, it's critical and should be addressed upfront.
    
-   **Ambiguity Prevention Chain**: Specification clarity → Planning precision → Implementation clarity → Smooth execution. Skipping clarification creates cascading problems: vague planning → confused tasks → rework.
    
-   **AI-Driven Gap Discovery**: `/sp.clarify` systematically analyzes specs and returns categorized feedback; students evaluate each finding and decide to accept, reject, or modify the suggestion.
    

## Common Mistakes

-   **Skipping clarification because "spec looks good"**: Every specification has ambiguities you didn't notice. Clarify surfaces them in minutes rather than hours during implementation rework.
    
-   **Ignoring critical clarifications for later**: Deferring decisions that affect all downstream work (citation style, paper length, audience) means planning proceeds without understanding critical constraints, requiring rework mid-implementation.
    
-   **Accepting all AI suggestions without evaluation**: Not all clarification suggestions improve the spec; some add unnecessary complexity. Evaluate each suggestion before accepting: Is it critical? Does it affect planning? Can it be deferred?
    
-   **Over-clarifying (nice-to-have details)**: Treating every suggestion as critical blocks progress. Some details (formatting tools, aesthetic preferences) don't affect planning and can be deferred or omitted.
    

## Progression Context

-   **Builds on**: Lesson 04 (Specify Phase) — Students have written initial specifications. Clarify phase validates specification quality before moving to planning.
    
-   **Leads to**: Lesson 06 (Plan Phase) — Clear, gap-free specifications enable planning phase to generate precise implementation tasks. Clarification ensures planning has all information needed for design decisions.
    

## Study Mode

Teaching by Socratic Method (OpenAI Study Mode & Google Extended Learning)

📚Socratic Teaching - AI guides you with questions

### Ready to Learn

Click the Teach button to get a guided explanation of this lesson from the book.

---
Source: https://agentfactory.panaversity.org/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on/clarify-phase

-   [](/)
-   [Part 3: SDD-RI Fundamentals](/docs/SDD-RI-Fundamentals)
-   [Chapter 13: Master Spec-Kit Plus](/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on)
-   Plan Phase — Architecture Decisions and ADRs

# Plan Phase — Architecture Decisions and ADRs

With your specification complete and clarified, you now face a new question: **How will you actually build it?** This is the essence of the Plan Phase—transforming the "What" of your specification into the "How" of architecture and implementation strategy.

`/sp.plan` generates an implementation plan that breaks your specification into:

-   **Architectural components** (sections, research management, quality validation)
-   **Implementation phases** (research first, then writing, then polish)
-   **Dependencies** (what must be completed before what)
-   **Design decisions** (which ones matter enough to document)

This lesson teaches you how to work with generated plans and how to capture important architectural decisions using **ADRs (Architectural Decision Records)**.

* * *

## Understanding the `/sp.plan` Command

`/sp.plan` analyzes your specification and generates a detailed implementation plan by:

1.  **Breaking spec into components** — Which parts of your spec need separate phases?
2.  **Ordering dependencies** — What must be built first?
3.  **Identifying design decisions** — Where are there multiple valid approaches?
4.  **Proposing architecture** — How should work be organized?

**Input**: Your specification (what the paper must accomplish)

**Output**: Implementation plan with:

-   Architecture overview
-   Implementation phases
-   Component breakdown
-   Dependencies and sequencing
-   Design decisions highlighted

**The Cascade Effect**: Detailed spec → detailed plan. Vague spec → vague plan.

* * *

## Part A: Generating Your Implementation Plan

Let's generate the plan for your research paper.

### Step 1: Run `/sp.plan`

In your AI tool, from your `my-research-paper` directory:

```
/sp.planCreate: architecture sketch, section structure, research approach, quality validation.Decisions needing documentation: list important choices with options and tradeoffs.Testing strategy: validation checks based on acceptance criteria.Technical details:- Use research-concurrent approach (research while writing, not all upfront)- Follow APA citation style from Constitution- Organize by phases: Research → Foundation → Analysis → Synthesis
```

**What the agent does:**

-   Creates technical implementation plan
-   Defines section structure and dependencies
-   Establishes validation strategy
-   Identifies architectural decisions
-   Generates `plan.md` file in your specs directory

**Why This Matters**: The plan defines architecture for ALL sections at once. This ensures consistency—same research approach, same citation handling, same quality validation. Much more efficient than planning each section separately!

### Step 2: Review Generated Plan

The generated plan should include:

**Architecture Overview:** How work will be organized (phases, dependencies)

**Implementation Phases:** 3-5 phases building from research to polish

**Component Breakdown:** Research management, thesis development, evidence integration, writing phases, quality gates

**Sequencing:** Research before findings? Outline before detailed writing?

**Design Decisions:** Where are there choices? (Research-first vs research-concurrent? Section order?)

### Step 3: Verify Plan Completeness

After the agent generates your plan, review it:

```
Show me the generated plan and explain:1. How does it break down the work into phases?2. What dependencies does it identify?3. What design decisions are highlighted?4. Does it account for all specification requirements?
```

**Agent shows:**

-   **Technical Approach** — Overall strategy for building the paper
-   **Major Components** — Logical parts that need to be built
-   **Dependencies** — What blocks what
-   **Phases** — Milestones with deliverables
-   **Success Criteria** — How you'll know each phase is complete

* * *

## Part B: Understanding ADRs (Architectural Decision Records)

Planning exposes architectural decisions—choices about HOW to build that have long-term consequences.

### What Is an ADR?

An ADR documents:

-   **The Decision**: What choice did you make?
-   **The Context**: Why did you need to make this choice?
-   **The Alternatives**: What other options existed?
-   **The Rationale**: Why did you choose this over alternatives?
-   **The Consequences**: What are the long-term impacts?

### When Should You Create an ADR?

**Create an ADR when:**

-   The decision has long-term impact (affects paper structure, not just word choice)
-   Multiple valid alternatives existed (not an obvious choice)
-   Future readers/collaborators will question the decision
-   The decision constrains future choices (e.g., choosing research approach)

**Don't create ADRs for:**

-   Style choices (formatting preferences)
-   Obvious choices (of course we use APA—Constitution requires it!)
-   Temporary decisions (will revisit before submission)
-   Out-of-scope decisions (already decided by Constitution)

### Example ADR Decisions for Research Paper

Decision

ADR Needed?

Why?

Research-concurrent vs research-first approach

✅ YES

Affects entire writing workflow

Section ordering (Lit Review before Methodology?)

✅ YES

Affects logical flow and dependencies

APA citation style

❌ NO

Constitution already decided this

Font choice

❌ NO

Trivial, no long-term impact

Whether to include ethics discussion

✅ YES

Scope decision with tradeoffs

* * *

## Part C: Creating ADRs for Your Plan

Now let's identify and document the architectural decisions from your plan.

### Step 1: Run `/sp.adr`

```
/sp.adr Review the generated plan and record key Architectural Decisions.Focus on decisions that:1. Affect multiple sections or phases2. Had alternatives we considered3. Will shape how we write the paper4. Someone might question later
```

**What the agent does:**

-   Reviews your plan.md
-   Identifies architecturally significant decisions
-   Creates ADR files in `history/adr/` directory
-   Documents context, alternatives, rationale, and consequences

### Step 2: Review Generated ADRs

After the agent creates your ADRs, examine them:

```
Show me the ADRs created. For each one, explain:1. What decision was documented?2. What alternatives were considered?3. Why was this choice made over alternatives?4. What are the consequences (both positive and negative)?
```

**Example ADR Structure:**

```
# ADR-001: Research-Concurrent Writing Approach## StatusAccepted## ContextWe need to decide when research happens relative to writing.Two approaches exist: research-first (gather all sources, then write)vs research-concurrent (research while writing each section).## DecisionWe will use research-concurrent approach.## Alternatives Considered1. **Research-first**: Gather all 8+ sources before writing anything   - Pro: Complete knowledge before writing   - Con: Delays writing, may gather irrelevant sources2. **Research-concurrent**: Research each section as we write it   - Pro: Research stays focused and relevant   - Con: May discover knowledge gaps mid-writing## RationaleResearch-concurrent keeps engagement with material high and ensuressources are directly relevant to sections being written. Risk ofknowledge gaps is mitigated by outline phase identifying key topics.## Consequences- Positive: More focused research, faster initial writing- Negative: May need additional research passes for cross-section references- Constraint: Must complete detailed outline before starting section writing
```

### Step 3: Verify ADR Completeness

Check that your ADRs:

```
ADR Completeness Checklist:[ ] Each ADR has clear context (why this decision was needed)[ ] Alternatives are documented (not just the chosen option)[ ] Rationale explains WHY this choice over others[ ] Consequences include both positives and negatives[ ] Decision is architecturally significant (not trivial)[ ] ADR would help future collaborator understand the choice
```

* * *

## Common Mistakes

### Mistake 1: Documenting Every Small Decision as ADR

**The Error**: Creating ADRs for trivial choices like "Use headings for sections" or "Put references at the end"

**Why It's Wrong**: ADRs are for architecturally significant decisions (long-term impact, multiple alternatives, future questioning). Trivial choices clutter your ADR history.

**The Fix**: Apply the three-part test:

1.  Does this have long-term consequences?
2.  Are there multiple viable alternatives?
3.  Will someone ask "why did we choose this" in 6 months?

If not all three → Skip the ADR.

### Mistake 2: Vague ADR Consequences

**The Error**: ADR says "This approach is better" without explaining tradeoffs

**Why It's Wrong**: Future developers need to understand WHY you chose this and WHAT you gave up.

**The Fix**: Document both positives and negatives:

-   ✅ "Pros: More focused research. Cons: May need additional passes."
-   ✅ "Alternatives considered: Research-first (rejected: delays writing)"

### Mistake 3: Skipping the Plan Phase

**The Error**: Going straight from specification to task writing, skipping planning.

**Why It's Wrong**: You lose sight of overall architecture. Tasks become disconnected. You discover structural problems late.

**The Fix**: Always plan. The `/sp.plan` command makes this quick and automatic.

* * *

## Connecting Spec → Plan → Tasks

This is important: your specification, plan, and tasks form a clear chain.

**Specification says**: "Write a 3000-5000 word research paper on AI in K-12 education, APA format, 8+ sources, define 3+ concrete applications"

**Plan says**: "Structure: Research Phase → Foundation Writing → Analysis Writing → Synthesis. Phases in order, dependencies mapped. Key decision: research-concurrent approach."

**Tasks** (next lesson) will say: "Task 1: Define thesis (15 min), Task 2: Outline all sections (30 min), Task 3: Research for Lit Review (45 min)..." etc.

Each level adds specificity:

-   **Spec**: What is success? (Measurable criteria)
-   **Plan**: How will we organize the work? (Architecture + ADRs)
-   **Tasks**: What are the 15-30 minute units? (Atomic work)

* * *

## Try With AI

Ready to generate your implementation plan and document architectural decisions?

**Generate Your Plan:**

> "I have a research paper specification. Run `/sp.plan` to generate an implementation plan. Show me: (1) The technical approach for structuring the paper, (2) Major components and phases, (3) Dependencies between components, (4) Design decisions that need documenting. Create the plan.md file."

**Analyze Plan Quality:**

> "Review my generated plan at specs/\[feature-name\]/plan.md. Does it: (1) Match the specification's requirements? (2) Show clear dependencies? (3) Break work into logical phases? (4) Identify parallel work opportunities? Where could the plan be clearer?"

**Create ADRs:**

> "Run `/sp.adr` to review my plan and record key Architectural Decisions. Focus on decisions that: (1) Affect multiple sections, (2) Had alternatives we considered, (3) Will shape how we write the paper. For each ADR, document context, alternatives, rationale, and consequences."

**Test Plan-to-Tasks Readiness:**

> "Based on my plan, simulate breaking it into tasks. For each implementation phase, can you create 3-5 atomic tasks? If you struggle to create clear tasks, identify which parts of my plan are too vague and need more detail. This tests if my plan is detailed enough for the Tasks phase."

# Plan Phase — Architecture Decisions and ADRs

This lesson teaches students to transform specifications into implementation plans using `/sp.plan`, then document key architectural decisions using `/sp.adr`. Students run the plan command, review the generated architecture (components, phases, dependencies), and create ADRs for decisions that have long-term impact, multiple alternatives, and will be questioned later. The lesson emphasizes the cascade effect: clear spec → clear plan. Plans answer HOW we'll build what the spec defines, bridging intent to executable tasks.

### Mental Models

-   **Cascade Effect**: Specification quality determines plan quality. Detailed spec → clear plan with well-defined components. Vague spec → vague plan that exposes missing requirements. Plans act as quality checkpoint.
    
-   **Three-Layer Hierarchy**: Spec defines WHAT (success criteria), Plan defines HOW (architecture), Tasks define WORK UNITS (15-30 min pieces). Each layer adds specificity. Plans prevent jumping from abstract requirements to granular tasks.
    
-   **ADR as Decision Documentation**: Architectural Decision Records capture WHY choices were made, not just WHAT was decided. Include context, alternatives considered, rationale, and consequences (both positive and negative).
    
-   **ADR Significance Test**: Create ADR only if: (1) long-term consequences, (2) multiple viable alternatives existed, (3) someone will question it later. If not all three → skip the ADR.
    

### Key Patterns

-   **Run `/sp.plan` with context**: Provide architecture sketch, section structure, research approach, quality validation strategy. Agent generates plan.md with components, dependencies, phases.
    
-   **Review generated plan**: Check that plan maps to all spec requirements, shows clear dependencies, breaks work into logical phases, identifies parallel opportunities.
    
-   **Run `/sp.adr` to document decisions**: Focus on decisions affecting multiple sections, with considered alternatives, that shape how work proceeds. Agent creates ADRs in `history/adr/`.
    
-   **ADR Structure**: Status → Context (why decision needed) → Decision → Alternatives Considered (with pros/cons) → Rationale (why this over others) → Consequences (positives AND negatives).
    
-   **Spec → Plan → Tasks chain**: Each level adds specificity. Spec: measurable success criteria. Plan: architecture + ADRs. Tasks: 15-30 minute atomic units.
    

### Common Mistakes

-   **Documenting trivial decisions as ADRs**: Creating ADRs for "use headings for sections" or style choices. Apply three-part test: long-term consequences? multiple alternatives? future questioning?
    
-   **Vague ADR consequences**: "This approach is better" without tradeoffs. Document both positives AND negatives. Show what you gave up.
    
-   **Skipping plan phase**: Jumping from spec to tasks loses architecture visibility. Tasks become disconnected, structural problems emerge late.
    

### Progression Context

-   **Builds on**: Lesson 5 (Clarify Phase) where students refined specifications. Students now have complete, detailed specs ready for planning.
    
-   **Leads to**: Lesson 7 (Tasks Phase) where students break the plan into atomic 15-30 minute work units. Plan's components and phases structure the task breakdown.
    

## Study Mode

Teaching by Socratic Method (OpenAI Study Mode & Google Extended Learning)

📚Socratic Teaching - AI guides you with questions

### Ready to Learn

Click the Teach button to get a guided explanation of this lesson from the book.

---
Source: https://agentfactory.panaversity.org/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on/plan-phase


-   [](/)
-   [Part 3: SDD-RI Fundamentals](/docs/SDD-RI-Fundamentals)
-   [Chapter 13: Master Spec-Kit Plus](/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on)
-   Tasks Phase - Atomic Work Units and Checkpoints

# Tasks Phase - Atomic Work Units and Checkpoints

You now have:

-   ✅ A clear research paper specification (intent, success criteria, scope)
-   ✅ A detailed implementation plan (research approach, structure, timeline)
-   ✅ Documented architecture decisions (citation style, source strategy, outline format)

Next: Break the plan into **atomic work units** (tasks) that you'll execute. Each task is 15-30 minutes, has one acceptance criterion, and produces a verifiable output.

This lesson teaches the **checkpoint pattern**—the critical workflow practice that keeps YOU in control. The pattern is:

```
Agent: "Here's Section 1 research complete"You: "Review... sources are credible!"You: "Commit to git"You: "Tell me what's next"Agent: "Section 2 outline refinement starting"
```

NOT:

```
Agent: "Here's everything at once" (no human control)
```

The difference is huge. Checkpoints keep you in control and catch issues early before wasting time on downstream tasks.

* * *

## What Are Tasks?

A **task** is a unit of work that:

-   Takes 15-30 minutes to complete
-   Has a single, clear acceptance criterion
-   Depends on specific other tasks
-   Produces one verifiable output (file, section, validated state)

### Task Properties

**Size**: 15-30 minutes

-   Too small (under 10 minutes) = too many micro-tasks, checkpoint overhead
-   Too large (over 45 minutes) = hard to review, hard to fix if wrong
-   Just right (15-30) = meaningful progress, reviewable scope

**Criterion**: Single, testable

-   "Research section 1 sources and verify credibility" ✅
-   "Research section 1 AND outline section 1 AND find images" ❌ (three things)
-   "Work on research stuff" ❌ (untestable)

**Independence**: Can be reviewed individually

-   Doesn't require other tasks to be done first
-   Or clearly depends on specific other tasks

**Clarity**: Defines exact acceptance criterion that signals completion

-   ✅ "Section 1 has 5+ credible sources (peer-reviewed or authoritative), each with full citation"
-   ❌ "Section 1 is researched"

* * *

## The Checkpoint Pattern (CRITICAL)

This is **the most important concept** in this lesson. The checkpoint pattern is how you maintain control of the workflow.

### Pattern Definition

```
Loop:  1. Agent: "I've completed Phase X (description of output)"  2. Human: "Review the work (output visible and testable)"  3. Human: "APPROVE" → Commit to git  4. Human: "Tell me next phase"
```

### Why Checkpoints Matter

**Without Checkpoints** (dangerous):

```
You: "Write my research paper"Agent: "Done! I've completed 15 tasks, researched all sections,        synthesized 50 sources, written full paper, formatted        everything. All automated. You're welcome."You: "Wait, which sources did you use? Is section 3 accurate?      How do I verify what you wrote?"Agent: "Already committed. Sorry! Check it now?"
```

**With Checkpoints** (controlled):

```
You: "Start research paper workflow"Agent: "Phase 1 (Section 1 Research) complete:        ✓ 5 credible sources identified        ✓ Notes summarizing key points        ✓ Citations formatted        Ready for review."You: "Read sources... all high-quality. Commit. What's next?"Agent: "Phase 2 (Section 1 Outline) - Key points ordered..."You: "Found issue with point sequence. Fixing..."Agent: "Phase 3 (Section 2 Research) - Starting literature review..."You: "Paper structure looks good so far. Paper complete!"
```

### Your Role in Each Checkpoint

**Step 1: Human Reviews**

-   See the actual output (written section, bibliography, research notes)
-   Ask: "Does this match the plan?"
-   Ask: "Are there accuracy issues I should fix before continuing?"
-   Ask: "Is this ready for the next phase?"

**Step 2: Human Decides**

-   Approve ("Looks good, commit")
-   Reject ("Fix this issue before continuing")
-   Request clarification ("Where did you get this source?")

**Step 3: Human Directs**

-   "What's the next phase?"
-   You initiate next phase
-   Agent doesn't autonomously continue

* * *

## Task Structure for Research Paper

Your research paper project breaks into **4 phases with 10 atomic tasks**. Here's the breakdown:

### Phase 1: Research Foundation (3 tasks, 45-60 minutes)

These tasks establish credible sources and research notes BEFORE writing.

**Task 1.1: Research Section 1 - Find Credible Sources**

-   **Duration**: 20 minutes
-   **Depends on**: Nothing
-   **What to do**: Identify 5+ credible sources for Section 1 (topic introduction)
-   **Acceptance**: "5+ sources identified; each is peer-reviewed OR from authoritative domain expert; full citations recorded"
-   **Output**: Bibliography file with 5+ sources and notes on why each is credible

**Task 1.2: Research Section 1 - Synthesize Key Points**

-   **Duration**: 15 minutes
-   **Depends on**: Task 1.1
-   **What to do**: Read sources and extract key points for Section 1
-   **Acceptance**: "3-5 key points documented; each has source attribution; points relate directly to introduction goal"
-   **Output**: Research notes file with key points and source citations

**Task 1.3: Create Outline Structure**

-   **Duration**: 15 minutes
-   **Depends on**: Task 1.2
-   **What to do**: Draft outline for all sections with main points and sub-points
-   **Acceptance**: "Outline has all 4+ sections; each section has 2-3 main points; structure flows logically"
-   **Output**: Markdown outline file showing section hierarchy

### Phase 2: Content Research and Organization (4 tasks, 60-90 minutes)

These tasks research remaining sections and organize findings.

**Task 2.1: Research Section 2 - Find Credible Sources**

-   **Duration**: 20 minutes
-   **Depends on**: Task 1.3
-   **What to do**: Identify 5+ credible sources for Section 2 (main topic)
-   **Acceptance**: "5+ sources identified; each is peer-reviewed OR from domain expert; full citations recorded"
-   **Output**: Bibliography update with Section 2 sources and credibility notes

**Task 2.2: Research Section 2 - Synthesize Key Points**

-   **Duration**: 15 minutes
-   **Depends on**: Task 2.1
-   **What to do**: Read sources and extract key points for Section 2
-   **Acceptance**: "4-6 key points documented; source attributed; points advance main argument"
-   **Output**: Research notes update with Section 2 key points

**Task 2.3: Research Section 3 and Beyond - Find Sources**

-   **Duration**: 20 minutes
-   **Depends on**: Task 2.2
-   **What to do**: Research remaining sections (conclusion, implications) and gather sources
-   **Acceptance**: "All remaining sections have 3+ credible sources each; citations recorded"
-   **Output**: Complete bibliography with all sections covered

**Task 2.4: Organize All Research Notes by Section**

-   **Duration**: 15 minutes
-   **Depends on**: Task 2.3
-   **What to do**: Consolidate all research notes; organize by section; verify coverage
-   **Acceptance**: "All sections have research notes; notes are organized by topic; no gaps identified"
-   **Output**: Organized research notes file; verified coverage checklist

### Phase 3: Writing and Synthesis (2 tasks, 60-90 minutes)

These tasks transform research into written paper.

**Task 3.1: Write and Synthesize Content**

-   **Duration**: 45 minutes
-   **Depends on**: Task 2.4
-   **What to do**: Write paper sections using research notes; synthesize findings
-   **Acceptance**: "All sections written; each section 300+ words; citations embedded; argument flows"
-   **Output**: Complete draft paper with citations

**Task 3.2: Format and Verify Citations**

-   **Duration**: 20 minutes
-   **Depends on**: Task 3.1
-   **What to do**: Apply citation style; verify all sources cited; check bibliography completeness
-   **Acceptance**: "All citations follow APA format; bibliography complete; in-text citations present"
-   **Output**: Formatted paper with verified citations; complete bibliography

### Phase 4: Review and Finalization (1 task, 30 minutes)

These tasks validate final paper quality.

**Task 4.1: Review Paper Quality and Finalize**

-   **Duration**: 30 minutes
-   **Depends on**: Task 3.2
-   **What to do**: Read complete paper; verify accuracy, clarity, argument coherence; finalize
-   **Acceptance**: "Paper reads smoothly; argument is clear; sources are credible; no typos; ready to submit"
-   **Output**: Final paper ready for submission; quality checklist completed

* * *

## Checkpoint Sequence

Here's how the workflow actually progresses with human checkpoints:

### Checkpoint 1: After Phase 1 (Research Foundation)

```
AGENT: "Research foundation complete:        ✓ Section 1 sources identified (5 peer-reviewed articles)        ✓ Key points synthesized from sources        ✓ Outline structure created (4 sections, logical flow)        Ready for Phase 2: Content Research"YOU: "Review sources... all high-quality academic journals.      Read outline... structure makes sense.      Looks good! Committing Phase 1."YOU: (git commit)YOU: "Proceed to Phase 2"
```

### Checkpoint 2: After Phase 2 (Content Research)

```
AGENT: "Content research complete:        ✓ Sections 2-4 sources identified (15+ total sources)        ✓ Key points extracted and organized by section        ✓ Research notes consolidated and verified for gaps        Ready for Phase 3: Writing"YOU: "Review research notes... coverage is comprehensive.      Check bibliography... all sources have full citations.      Committing Phase 2."YOU: (git commit)YOU: "Proceed to Phase 3"
```

### Checkpoint 3: After Phase 3 (Writing)

```
AGENT: "Writing complete:        ✓ All sections written (2,500+ words total)        ✓ Research synthesized into narrative        ✓ Citations formatted in APA style        ✓ Bibliography complete        Ready for Phase 4: Finalization"YOU: "Read draft... argument is clear and well-supported.      Check citations... all formatted correctly.      Committing Phase 3."YOU: (git commit)YOU: "Proceed to Phase 4"
```

### Checkpoint 4: After Phase 4 (Finalization)

```
AGENT: "Review and finalization complete:        ✓ Paper reads smoothly, no formatting issues        ✓ All sources properly cited        ✓ Argument coherent from introduction to conclusion        ✓ Quality gates: All pass        PROJECT COMPLETE: Paper ready for submission"YOU: "Final read-through... excellent quality.      All requirements met. Committing final version.      Project complete!"YOU: (final git commit)
```

* * *

## Task Dependency Graph

Here's how your tasks depend on each other:

```
Phase 1 (Research Foundation): Sequential path (each depends on previous)┌────────────────────────────────────────────────────────────┐│  Task 1.1: Research Section 1 Sources                      ││      ↓                                                      ││  Task 1.2: Synthesize Section 1 Key Points                 ││      ↓                                                      ││  Task 1.3: Create Outline Structure                        ││      ↓ [CHECKPOINT 1]                                      │└────────────────────────────────────────────────────────────┘Phase 2 (Content Research): Sequential path (each depends on previous)┌────────────────────────────────────────────────────────────┐│  Task 2.1: Research Sections 2+ Sources (depends on 1.3)   ││      ↓                                                      ││  Task 2.2: Synthesize Sections 2+ Key Points               ││      ↓                                                      ││  Task 2.3: Research Final Sections Sources                 ││      ↓                                                      ││  Task 2.4: Organize All Research by Section                ││      ↓ [CHECKPOINT 2]                                      │└────────────────────────────────────────────────────────────┘Phase 3 (Writing): Linear path (each depends on previous)┌────────────────────────────────────────────────────────────┐│  Task 3.1: Write and Synthesize Content (depends on 2.4)   ││      ↓                                                      ││  Task 3.2: Format and Verify Citations                     ││      ↓ [CHECKPOINT 3]                                      │└────────────────────────────────────────────────────────────┘Phase 4 (Finalization): Final review (depends on Phase 3)┌────────────────────────────────────────────────────────────┐│  Task 4.1: Review and Finalize (depends on 3.2)            ││      ↓ [CHECKPOINT 4 - PROJECT COMPLETE]                   │└────────────────────────────────────────────────────────────┘Legend: Each task must complete before next starts (strict dependency)        Checkpoints occur after each phase group
```

* * *

## Lineage Traceability

Can you trace a task back to specification? Try this one:

```
Specification: "Write 2,500+ word research paper on AI in education               with academic rigor and clear argument structure"  ↓Plan: "Phase 1: Establish research foundation with credible sources;       Phase 2: Organize research by section;       Phase 3: Synthesize into written paper;       Phase 4: Verify quality and finalize"  ↓Task 2.1: "Research Section 2 - Find Credible Sources"  ↓Acceptance Criterion: "5+ sources identified; each peer-reviewed OR                       from domain expert; full citations recorded"
```

If you can trace this lineage for each task, your task breakdown is well-connected to your specification.

* * *

## Common Mistakes

### Mistake 1: Tasks Too Large (45+ Minutes)

**The Error**: "Task: Complete entire section research and writing (2+ hours)"

**Why It's Wrong**: Large tasks hide complexity, delay feedback, and make checkpoints meaningless. You can't validate progress until the entire section completes.

**The Fix**: Break into atomic units (15-30 minutes each):

-   ❌ Large: "Research and write section 1"
-   ✅ Atomic: "Find sources" (20 min), "Synthesize points" (15 min), "Outline structure" (15 min), "Write section" (45 min)

### Mistake 2: Combining Research and Writing

**The Error**: Task includes "research section, synthesize findings, write content, format citations" all as one task

**Why It's Wrong**: If you find issues with source credibility mid-task, you can't easily restart research without redoing writing. Mixing research + writing confuses where quality issues originate.

**The Fix**: Separate research from writing:

-   Task 2.1: "Research Section 2 Sources" (automation/research)
-   Task 2.2: "Synthesize Section 2 Points" (analysis)
-   **CHECKPOINT**: Human reviews research quality before continuing
-   Task 3.1: "Write and Synthesize Content" (composition)

### Mistake 3: Vague Acceptance Criteria

**The Error**: "Task: Section 1 is researched" (what does "researched" mean?)

**Why It's Wrong**: You won't know if the task is done or if there's a hidden gap.

**The Fix**: Make acceptance criteria specific and testable:

-   ✅ "Section 1 has 5+ peer-reviewed sources AND each source has full citation AND notes summarize key points"
-   ✅ "Paper has 2,500+ words AND all sources cited AND bibliography complete AND no formatting errors"

* * *

## What Makes /sp.tasks Powerful

The `/sp.tasks` command analyzes your specification and plan, then **generates a complete task breakdown** that includes:

1.  **Atomic Unit Definition** - Each task is 15-30 minutes with one acceptance criterion
2.  **Dependency Ordering** - Tasks ordered so dependencies are clear
3.  **Checkpoint Placement** - Human review points between phases
4.  **Lineage Traceability** - You can trace each task back to specification
5.  **Acceptance Criteria** - Each task has specific, testable completion condition

You don't write tasks from scratch. **`/sp.tasks` writes them for you** based on your specification and plan. Your job is to **understand the task structure, validate it's atomic, and execute it with checkpoints**.

* * *

## Try With AI

Ready to validate your task breakdown and understand how `/sp.tasks` works? Test your understanding:

**Explore Task Atomicity:**

> "I'm using `/sp.tasks` to break my research paper into atomic work units. Review my task list: (1) Is each task atomic (does ONE thing with ONE acceptance criterion)? (2) Are they sized right (15-30 minutes, not hours or minutes)? (3) Can each be reviewed independently? (4) Identify any tasks that should be split further or combined. (5) Which tasks would you add or remove?"

**Practice Checkpoint Validation:**

> "Walk me through the checkpoint pattern for my research paper workflow. For each checkpoint (after Phases 1, 2, 3, 4): (1) What should I review for? (2) What makes a 'good' output at this checkpoint? (3) What issues could arise that I should catch before continuing? (4) Create a checklist I can use at each checkpoint to decide 'ready to proceed'."

**Analyze Dependencies:**

> "Examine my task dependencies: (1) Are they logically correct? (2) Which tasks could theoretically run in parallel? (3) What's the critical path (minimum sequence to completion)? (4) If one task failed (e.g., couldn't find enough credible sources), which downstream tasks would be affected? (5) How would I recover and restart?"

**Understanding /sp.tasks Command:**

> "Explain what `/sp.tasks` does: (1) What INPUT does it take (spec + plan)? (2) What OUTPUT does it generate (task list structure)? (3) How does it ensure tasks are atomic? (4) How does it order tasks by dependency? (5) When would you run `/sp.tasks` in a Spec-Kit Plus workflow?"

* * *

## Tasks Phase - Atomic Work Units and Checkpoints

The `/sp.tasks` command transforms a specification and plan into a structured breakdown of atomic work units (15-30 minute tasks) with explicit dependencies and human-controlled checkpoints. This lesson teaches task atomicity (single acceptance criterion per task), the four-phase checkpoint pattern (Agent Complete → Human Review → Human Approve → Continue), and how to maintain human control throughout execution by requiring explicit approval at each phase boundary before proceeding to the next phase.

### Mental Models

-   **Atomic Task Unit**: A 15-30 minute unit of work with a single, testable acceptance criterion that produces one verifiable output. Size constraint prevents tasks too small (micro-management) or too large (hidden complexity, delayed feedback, hard to fix mid-stream).
    
-   **Checkpoint Pattern**: Agent → Review → Approve → Continue loop that keeps humans in control. Without checkpoints, agents can complete all tasks autonomously and you lose visibility. With checkpoints, you see each phase output, validate quality, catch issues early, and explicitly authorize the next phase before proceeding.
    
-   **Dependency Graph**: Visual representation of task ordering showing which tasks must complete before others can start (strict sequential path for research paper: Phase 1 → Phase 2 → Phase 3 → Phase 4, with sub-task dependencies within each phase).
    
-   **Lineage Traceability**: Ability to trace any task backward through the chain: Specification → Plan → Task → Acceptance Criterion. If traceability breaks, the task may be solving the wrong problem or may not be needed for specification fulfillment.
    

### Key Patterns

-   **Four-Phase Task Structure**: Research Foundation (sources + outline) → Content Research (gather all materials) → Writing and Synthesis (transform research into prose) → Review and Finalization (quality validation). Each phase ends with human checkpoint.
    
-   **Separation of Concerns**: Research tasks (find sources, extract key points) separate from writing tasks. This prevents quality issues in research from cascading through written content without human review between phases.
    
-   **Sequential Dependency within Phase**: Each task in a phase depends on the previous task completing first. Task 1.1 (find sources) → Task 1.2 (synthesize points) → Task 1.3 (create outline), enabling strict checkpoints at phase boundaries.
    
-   **Clear Acceptance Criteria**: "5+ sources identified; each peer-reviewed OR from domain expert; full citations recorded" (testable) vs. "Section 1 is researched" (untestable). Testable criteria are measurable and allow human validation.
    
-   **Checkpoint Sequence**: Four explicit human approval points (after Phase 1, Phase 2, Phase 3, and Phase 4 completion) where human reviews output, validates against plan, and explicitly authorizes progression to next phase.
    

### Common Mistakes

-   **Tasks Too Large (45+ minutes)**: Hiding complexity behind overly large tasks defeats the checkpoint pattern. Task "Research and write Section 1" (2+ hours) prevents human feedback until too much work has been done. Fix: Split into atomic units (find sources, synthesize points, outline, write content).
    
-   **Combining Research and Writing**: Including "research section, synthesize findings, write content, format citations" in a single task prevents early quality validation of sources. If sources are poor, human discovers this too late (after writing has already started). Fix: Separate research tasks from writing tasks with a checkpoint between phases.
    
-   **Vague Acceptance Criteria**: Criteria like "Section 1 is researched" leave hidden ambiguity about when task truly completes. Does "researched" mean 3 sources? 5? Peer-reviewed? Full citations? Fix: Make criteria specific and measurable: "5+ peer-reviewed sources, full citations, notes summarizing key points."
    
-   **Missing Dependencies**: Treating all tasks as independent or assuming parallel execution when tasks actually have strict sequence requirements. Correct understanding of dependencies prevents attempting Task 2.1 before Task 1.3 completes, which would invalidate the outline structure needed for targeted research.
    
-   **Skipping Checkpoints**: Letting agent autonomously complete multiple phases without human review ("Tell me everything") removes human control and prevents early issue detection. The checkpoint pattern explicitly requires human approval between phases.
    

### Progression Context

-   **Builds on**: Lesson 6 (Plan Phase) taught how to structure implementation approach through phases, timelines, and strategies. This lesson decomposes that plan into executable atomic work units with clear sequencing and human approval gates.
    
-   **Leads to**: Lesson 8 (Execution Phase) teaches how to actually execute the tasks with the `/sp.implement` command, monitoring progress through the checkpoint pattern, and handling task failures or refinements discovered during human review.
    
-   **Within SDD-RI Workflow**: `/sp.tasks` is the bridge between planning (intent, approach) and execution (atomic work units, checkpoints). Spec → Plan → Tasks → Implement → Validate forms the complete workflow.
    
-   **Requires**:
    
    -   Understanding of specification structure (Chapter 12, Lesson 1)
    -   Understanding of plan structure and phases (Lesson 6)
    -   Ability to trace lineage from specification through plan to tasks (validation skill)
    -   Familiarity with acceptance criteria as measurable completion signals (Lesson 6)
-   **Prepares for**:
    
    -   Executing tasks using `/sp.implement` with checkpoint validation (Lesson 8)
    -   Creating skills and subagents that orchestrate task sequences autonomously (Chapter 16+)
    -   Recognizing when tasks are too large or unclear and requesting refinement from `/sp.tasks`

## Study Mode

Teaching by Socratic Method (OpenAI Study Mode & Google Extended Learning)

📚Socratic Teaching - AI guides you with questions

### Ready to Learn

Click the Teach button to get a guided explanation of this lesson from the book.

---
Source: https://agentfactory.panaversity.org/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on/tasks-phase


-   [](/)
-   [Part 3: SDD-RI Fundamentals](/docs/SDD-RI-Fundamentals)
-   [Chapter 13: Master Spec-Kit Plus](/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on)
-   Implement Phase - Execute Tasks with AI Collaboration

# Implement Phase — Execute Tasks with AI Collaboration

You have a specification that defines what you're building, a plan that outlines the strategy, and tasks that break the work into atomic units. Now comes the execution phase: actually doing the work with your AI companion.

This lesson focuses on **control and validation**. Implementation isn't just "run tasks autonomously." It's you and AI working together—you deciding direction, AI handling execution, both of you validating results against the specification.

* * *

## What Implementation Means in SDD-RI

**Implementation = executing your tasks.md to fulfill your specification.**

This is fundamentally different from ad-hoc coding. Consider the difference:

**Without specification (ad-hoc)**:

```
You: "Generate text for a research paper introduction"AI: [Produces 500 words]You: "Good enough?" (You have no objective standard)
```

**With specification (SDD-RI)**:

```
You: "Execute Task 1.1: Write research paper introduction (500-700 words,      academic tone, establish context for three key claims from spec)"AI: [Produces text]You: Check against spec:  ✓ 650 words (within 500-700)  ✓ Academic tone maintained  ✓ All three key claims established  ✓ Task complete
```

The difference: **Objective acceptance criteria from your spec**.

Implementation executes against these criteria. When a task is done, you know it's done because it meets the spec's success criteria.

* * *

## The /sp.implement Command

When you run `/sp.implement` in Claude Code, the command reads your tasks.md and orchestrates their execution with your AI companion.

**Basic usage**:

```
/sp.implement
```

The agent will:

1.  Read your tasks.md
2.  Begin executing tasks in dependency order
3.  Show outputs and intermediate results
4.  Wait for your review at checkpoint boundaries
5.  Continue on your approval

**You maintain control.** The agent doesn't proceed autonomously; it presents work and waits for your decision.

* * *

## Checkpoint Pattern: The Core Control Mechanism

Implementation uses checkpoints to maintain human decision-making at critical boundaries.

**The pattern:**

```
Task 1 → Task 2 → Task 3 → CHECKPOINT 1                            (You review)                            (You approve or iterate)                                ↓                            Task 4 → Task 5 → CHECKPOINT 2                                            (You review)
```

**At each checkpoint**, you answer one question: **"Does the output meet the specification?"**

If yes: Commit and move forward. If no: Work with AI to refine until it meets spec.

### Example Checkpoint Review

**Your tasks.md specifies:**

```
Task 1.1: Write research paper introduction- Success criteria: 500-700 words, academic tone, introduces three main arguments- Dependencies: None
```

**Agent completes Task 1.1, shows output:**

```
[Introduction text, 623 words]
```

**Your checkpoint review (2 minutes)**:

-   Count words? 623 (within 500-700) ✓
-   Academic tone? Yes, peer-reviewed style ✓
-   Three arguments introduced? Argument 1, 2, 3 all present ✓
-   Ready for next task? Yes ✓

**Your decision**: "Task 1.1 meets spec. Committing. Proceed to Task 1.2."

This prevents cascading problems. If Task 1.1 had missed an argument, you'd catch it before Task 2 builds on faulty foundation.

* * *

## The Four Concepts You're Learning

### Concept 1: Implementation ≠ Autonomous Execution

Many students assume implementation means "Tell AI to build it and walk away."

**Reality**: Implementation is orchestrated execution with human judgment at every phase.

You direct. AI executes. You validate. You iterate if needed. This cycle repeats for each phase.

### Concept 2: Spec Success Criteria Are Your Acceptance Standard

Before running /sp.implement, your spec already defines what "done" means.

**In your spec:**

-   Introduction section: 500-700 words, academic tone, three arguments
-   Literature review: 800-1000 words, 10+ sources, critical analysis
-   Methodology: Clear procedure, reproducible, 300-400 words

**During implementation:**

-   Task completes
-   You check: "Does it meet success criteria from spec?"
-   Not yet? "AI, adjust X aspect and try again"
-   Meets spec? "Commit. Next task"

This objective standard prevents scope creep and "almost good enough" mediocrity.

### Concept 3: Iteration Loops Accelerate Problem-Solving

When a task doesn't meet spec, iteration (not abandonment) is the solution.

**Failure scenario**: You request introduction. AI produces 1200 words (exceeds 700-word spec).

**Without iteration (wrong)**:

```
You: "That's too long. Project failed."
```

**With iteration (correct)**:

```
You: "This exceeds the 700-word spec limit. Can you condense to 500-700      while keeping all three arguments?"AI: [Revises to 680 words]You: [Validates against spec]Done.
```

Iteration transforms failures into learning. The spec guides refinement.

### Concept 4: AI Collaboration During Execution

AI doesn't just execute—it collaborates during execution.

**Example iteration dialogue:**

You: "Task 2.3: Write methodology section (300-400 words, reproducible procedure)"

AI proposes approach: "I'll structure this with (1) research population, (2) data collection method, (3) analysis approach. Does this align with what you're aiming for?"

You refine: "Add one more: (4) validity checks. Want to ensure readers can replicate this."

AI adjusts proposal: "Perfect. Here's revised structure with validity checks integrated..."

AI executes revised version: \[Produces 385-word methodology\]

You validate against spec: ✓ 385 words (within 300-400), ✓ Reproducible, ✓ Validity checks present

**This is AI collaboration in implementation.** Not "execute blindly," but "suggest → refine → execute → validate."

* * *

## Example: Implementing Your Research Paper

Let's walk through what happens when you execute `/sp.implement` for your paper project.

### Setup Before Running /sp.implement

You have:

-   **spec.md**: Paper specification with success evals (5-7 sections, 3000-4000 total words, academic sources, coherent argument)
-   **plan.md**: Implementation plan (write intro → lit review → methodology → analysis → conclusion, each section builds on previous)
-   **tasks.md**: Atomic tasks (Task 1.1, 1.2, 1.3... Task 5.4, 5.5)

### Running the Command

```
/sp.implement
```

Agent reads tasks.md, recognizes structure:

```
Phase 1: Introduction & Literature Foundation├─ Task 1.1: Research paper introduction (500-700 words)├─ Task 1.2: Literature review outline (sources identified, 10+ required)└─ CHECKPOINT 1: Validate intro + outline against specPhase 2: Methodology & Analysis├─ Task 2.1: Methodology section (300-400 words, reproducible)├─ Task 2.2: Analysis section (800-1000 words, critical synthesis)└─ CHECKPOINT 2: Validate sections meet quality criteriaPhase 3: Integration & Refinement├─ Task 3.1: Conclusion synthesizing all sections├─ Task 3.2: Final review and adjustment└─ CHECKPOINT 3: Full document validation against spec
```

### CHECKPOINT 1 Review

**Agent reports:**

```
Task 1.1: Introduction (623 words)- Opening hook explaining research context- Three main arguments clearly stated- Transition to literature review preparedTask 1.2: Literature outline- 12 sources identified (exceeds 10-source requirement)- Categories: foundational (3), recent empirical (5), contrasting (4)- Annotations show critical analysis planned
```

**Your 3-minute review**:

-   ✓ Introduction 623 words (within 500-700)
-   ✓ Three arguments present and clear
-   ✓ Outline has 12 sources (meets 10+ requirement)
-   ✓ Sources span theoretical, empirical, and contrasting perspectives

**Your checkpoint decision**: "Both tasks meet spec criteria. Committing Phase 1. Ready for Phase 2."

### CHECKPOINT 2 Review

**Agent reports:**

```
Task 2.1: Methodology (385 words)- Clear procedure described- Population/sample specified- Data collection method documented- Analysis approach outlined- Reproducibility criteria metTask 2.2: Analysis (920 words)- Synthesizes all 12 sources- Identifies patterns across sources- Addresses contradictions- Connects to research questions
```

**Your 5-minute review**:

-   Methodology: 385 words (within 300-400) ✓
-   All steps reproducible ✓
-   Analysis: 920 words (within 800-1000) ✓
-   Critical synthesis visible ✓
-   Connects back to spec's three main arguments ✓

**Your checkpoint decision**: "Both tasks meet spec. Committing Phase 2. Proceed to Phase 3."

### CHECKPOINT 3: Final Validation

**Agent reports:**

```
Complete document assembled:- Introduction: 623 words ✓- Literature Review: 1050 words (from outline + full section)- Methodology: 385 words ✓- Analysis: 920 words ✓- Conclusion: 450 words ✓Total: 3,428 words (within 3000-4000 spec requirement)Final checks:✓ All sections present✓ Academic tone throughout✓ 12 sources integrated✓ Argument coherence verified✓ Meets specification success criteria
```

**Your validation**:

-   Word count: 3,428 (within 3000-4000) ✓
-   All required sections ✓
-   Sources properly cited ✓
-   Argument is coherent and supported ✓

**Your final decision**: "Document meets specification. Implementation complete. Ready for next project phase."

* * *

## What Happens When Tasks Don't Meet Spec

**Real scenario**: Agent completes Task 1.1 (introduction) with 450 words. Your spec requires 500-700.

**At Checkpoint 1**:

```
Agent: "Task 1.1 complete: 450 words"You: "This is below the 500-700 word spec requirement.      Missing depth on which aspect?"Agent: "The second argument needs more context. I can expand       that section to add 75-100 words."You: "Yes, expand the second argument while keeping tone consistent."Agent: [Revises to 520 words]You: [Validates]Result: Task 1.1 now meets spec. Move forward.
```

**The key**: You used the spec to identify the gap, guided the refinement, and validated the fix. This is iterative implementation—normal, expected, productive.

* * *

## Common Implementation Patterns

### Pattern 1: Serial Task Execution (Most Common)

Tasks execute in order. Each builds on previous.

```
Task 1 → Task 2 → Task 3 → CHECKPOINT → Task 4 → Task 5 → CHECKPOINT
```

**When to use**: Linear projects (writing, sequential analysis)

**Your role**: Validate after each task block, ensure quality before next block uses output

### Pattern 2: Parallel Task Execution (When Possible)

Some tasks don't depend on others. Execute simultaneously.

```
Task 1.1 ─┐Task 1.2 ─┼─→ CHECKPOINT 1Task 1.3 ─┘           Task 2.1 → Task 2.2 → CHECKPOINT 2
```

**When to use**: Independent sections (research paper: intro, methodology, analysis can draft in parallel)

**Your role**: Ensure parallel tasks don't create integration conflicts at checkpoint

### Pattern 3: Iterative Refinement (When First Pass Insufficient)

Task executes, checkpoint review shows gap, task re-executes with refinement.

```
Task 1 → Review → Gap Identified → Task 1 (refined) → Review → Approved
```

**When to use**: Complex tasks, creative work (good first draft exists, needs polish)

**Your role**: Provide specific feedback ("expand argument 2," "add example," "tighten analysis")

* * *

## Validation Against Specification

At each checkpoint, validation answers: **"Does this meet our specification?"**

### Validation Checklist Structure

**For each task completion:**

1.  **Success Criteria Met?**
    
    -   Does output match explicit criteria from task definition?
    -   Word count? Format? Tone? Completeness?
2.  **Specification Requirements Fulfilled?**
    
    -   Does this task's output advance toward spec's overall success evals?
    -   Are we building the right thing?
3.  **Quality Standards?**
    
    -   Does output meet your constitutional standards (from Lesson 3)?
    -   Academic rigor? Clarity? Coherence?
4.  **Ready for Next Task?**
    
    -   Can the next task safely build on this output?
    -   Any risks or dependencies that aren't met?

**Example checklist for Task 1.1 (Introduction)**:

```
Success Criteria:  ☐ 500-700 words  ☐ Academic tone  ☐ Introduces three main arguments  ☐ Smooth transition to literature reviewSpecification Requirements:  ☐ Advances toward "coherent research argument" eval  ☐ Establishes context for paper  ☐ Reader understands what paper will argueQuality Standards:  ☐ Engaging opening hook  ☐ Clear language (no jargon without definition)  ☐ Proper grammar and citation formatReady for Next Task:  ☐ Literature review can build on these arguments  ☐ No placeholder text or unresolved questions
```

If all checkboxes checked: Commit and continue. If any unchecked: Iterate.

* * *

## The AI Collaboration Dynamic

Implementation isn't you alone or AI alone. It's **collaboration with clear structure**.

### Your Responsibilities

-   **Direction**: "Here's what we're building (spec). Here's the next task."
-   **Judgment**: "Does this meet our spec? If not, what's missing?"
-   **Decision**: "Commit this task. Iterate on that task. Move forward."

### AI's Responsibilities

-   **Execution**: "I'll complete this task to your specification."
-   **Suggestion**: "I notice this approach might work better..." (AI as Teacher)
-   **Adaptation**: "You want to add X requirement. Adjusting..." (AI as Student)
-   **Refinement**: "Re-executing with your feedback..." (AI as Co-Worker)

### The Cycle

```
You specify task → AI proposes approach → You refine → AI executes                    ↑                                     ↓                    ←←← You validate ←←←←←←←←←←←←←←←←
```

This cycle repeats for each task. It's predictable, controlled, and produces measurable results.

* * *

## Checkpoint Decisions

At each checkpoint, you make one of three decisions:

### Decision 1: "Commit and Proceed"

**When**: All tasks meet spec requirements.

**Your statement**: "Phase X complete. All success criteria met. Committing. Proceed to Phase Y."

**What happens**: Agent records completion, moves to next phase.

### Decision 2: "Iterate on This Task"

**When**: A specific task doesn't meet spec.

**Your statement**: "Task 2.1 needs adjustment. It's 450 words but spec requires 500-700. Expand the analysis section by 75-100 words while keeping tone consistent."

**What happens**: Agent refines that task, re-executes, shows updated output.

**You review again**: Does it meet spec now? If yes → commit. If no → iterate again.

### Decision 3: "Revise the Plan"

**When**: A task completed reveals a planning problem.

**Your statement**: "Task 1.2 showed that the literature review is larger than planned (1050 vs 1000 words budgeted). We need to adjust the conclusion (reduce by 100 words) to keep total under 4000. AI, adjust plan and re-execute Task 1.3 accordingly."

**What happens**: Agent updates plan, adjusts downstream tasks, re-executes.

**When to use**: Infrequent. Reserve for when checkpoint review reveals structural issues, not just tweaks.

* * *

## Anti-Patterns: What Not to Do

### Anti-Pattern 1: Approving Without Review

```
❌ WRONG:Agent: "Task complete"You: "Looks good" (without checking against spec)✓ RIGHT:Agent: "Task complete"You: [Spend 2-5 minutes validating against spec]
```

Skipping review defeats the purpose. Specs guide validation; validation ensures quality.

### Anti-Pattern 2: Accepting "Close Enough"

```
❌ WRONG:Spec says: 500-700 wordsTask delivers: 780 wordsYou: "Close enough, let's move on"✓ RIGHT:Spec says: 500-700 wordsTask delivers: 780 wordsYou: "Over spec limit. AI, condense to 500-700 while keeping key points."
```

"Close enough" is how requirements creep. Specs exist to prevent this.

### Anti-Pattern 3: Not Iterating When First Pass Fails

```
❌ WRONG:Agent: "Task 2.1 complete"You: "This doesn't meet spec"Agent: "Too bad. Moving on."You: "Okay, I guess project is compromised now"✓ RIGHT:Agent: "Task 2.1 complete"You: "This doesn't meet spec. Here's the gap: [specific feedback]"Agent: "Understood. Adjusting and re-executing..."Agent: [Shows revised output]You: [Validates again]Result: Task now meets spec
```

Iteration is normal. It's how you converge on specification compliance.

* * *

## Try With AI

Ready to understand `/sp.implement` deeply? Explore these prompts with your AI companion:

**Explore the Command Structure:**

> "I'm about to use `/sp.implement` to execute a research paper project. Walk me through what happens: (1) What does the agent read first (spec, plan, or tasks)? (2) How does it decide execution order? (3) How are checkpoints triggered? (4) What happens if I say 'iterate on Task 2' at a checkpoint? (5) When is implementation truly 'done'?"

**Practice Checkpoint Review:**

> "I just completed Task 1.2 of my research paper (literature review outline). The spec says 'identify 10+ academic sources, span theoretical and empirical work, show critical perspective.' The outline has 12 sources. How do I validate this meets spec in 3 minutes? What questions should I ask? What would make me say 'iterate' vs 'commit'?"

**Handle Iteration:**

> "My research paper introduction is 450 words, but spec requires 500-700. Rather than just asking to 'add 50-250 words,' how should I direct the AI? What specific aspect should expand? How do I ensure iteration improves the introduction rather than padding it with fluff?"

**Reflect on Specification Alignment:**

> "During implementation, I notice the research paper's conclusion feels disconnected from the introduction's three main arguments. This is a checkpoint review moment. Should I (a) iterate on the conclusion, (b) revise the plan to reconnect pieces, (c) go back and adjust the specification? What's the right decision and why?"

**Design Your First Checkpoint:**

> "For my next project, I'll write a technical spec document (not a research paper). Based on `/sp.implement` patterns, design what my first checkpoint should look like: What tasks go into Phase 1? What success criteria matter? What 3-5 questions should I answer during Phase 1 review?"

* * *

# Implement Phase — Execute Tasks with AI Collaboration

Implementation transforms your specification and plan into reality by executing tasks with measurable validation. This lesson teaches that implementation is orchestrated execution with human decision-making at checkpoints—not autonomous code generation. The core skill is validating task completion against specification success criteria at critical phase boundaries, using the `/sp.implement` command to coordinate AI execution with your judgment.

### Mental Models

-   **Implementation ≠ Autonomous Execution**: Implementation is you directing strategy, AI handling execution, both validating results. You maintain control through checkpoints, not by walking away and hoping the AI completes the project autonomously.
    
-   **Specification as Acceptance Standard**: Your spec defines "done" before implementation begins. Success criteria (word counts, requirements, quality measures) become objective measures of task completion. A task meets spec when its output satisfies all predefined criteria; iteration refines tasks that don't meet criteria.
    
-   **Checkpoint Pattern (Control Mechanism)**: Work executes in phases separated by checkpoints. At each checkpoint, you answer one question—"Does this meet the specification?"—then decide: commit and proceed, iterate the current task, or revise the plan if checkpoint reveals structural issues. Checkpoints prevent cascading failures from undetected task deficiencies.
    
-   **Iteration as Solution Pattern**: When tasks don't meet spec, iteration (not abandonment) solves the problem. AI refines output based on your feedback guided by the spec. Iteration transforms task failures into productive learning—spec shows what's missing, you guide adjustment, AI re-executes, you re-validate.
    

### Key Patterns

-   **Spec→Prompt→Execute→Validate Cycle**: Tasks execute within a structured cycle where you specify requirements from tasks.md, AI proposes execution approach, you refine direction, AI executes, you validate against spec success criteria, cycle repeats or proceeds based on checkpoint decision.
    
-   **Checkpoint Decisions (Three Options)**: At each checkpoint you choose: (1) "Commit and Proceed"—all tasks meet spec, move to next phase; (2) "Iterate on This Task"—specific task needs refinement, provide targeted feedback based on spec gaps; (3) "Revise the Plan"—checkpoint revealed structural issue requiring plan adjustment (rare, reserved for systematic problems).
    
-   **Serial Task Execution**: Tasks execute in dependency order (Task 1 → Task 2 → Task 3 → Checkpoint). Each task builds on previous output. You validate after each task block to ensure quality before next block uses output as foundation.
    
-   **Parallel Task Execution**: Independent tasks execute simultaneously (Task 1.1, 1.2, 1.3 in parallel → Checkpoint). Reduces time when tasks have no dependencies. Requires checkpoint validation to ensure parallel outputs don't create integration conflicts.
    
-   **Iterative Refinement Pattern**: Task executes, checkpoint review identifies gap, task re-executes with refinement, review validates against spec, process repeats until specification met. Used for complex work where polished first draft exists but needs targeted improvement.
    
-   **AI Collaboration During Execution**: AI doesn't just execute blindly—it collaborates with suggestion→refinement→execution→validation cycle. AI proposes approach (suggesting pattern you might not discover), you refine based on project constraints, AI adapts and executes revised version, you validate outcome.
    

### Common Mistakes

-   **Approving Without Review**: Checkpoint appears and you say "Looks good" without validating against specification success criteria. Skipping review defeats checkpoint purpose—specs guide validation; validation ensures spec-aligned quality. Always spend 2-5 minutes validating each checkpoint.
    
-   **Accepting "Close Enough"**: Spec requires 500-700 words, task delivers 780 words. You move on without iteration because it's "close enough." This is how requirements creep occurs. Specs exist to prevent creep—enforce them at checkpoints through iteration when tasks exceed or fall short of criteria.
    
-   **Not Iterating When First Pass Fails**: Task doesn't meet spec, and you either give up or accept the failed output. Iteration is normal and productive. When a task misses spec, identify the specific gap using specification criteria, provide targeted feedback to AI, re-execute with refinement, validate again. This convergence is how implementation works.
    
-   **Attempting Autonomous Execution**: You run `/sp.implement` and let the agent execute all tasks without checkpoint review. This eliminates human judgment and risks cascading failures. Instead, wait at each checkpoint, validate against spec, make informed decision, then proceed.
    
-   **Missing Dependencies in Validation**: Checkpoint review checks individual task quality but doesn't verify that downstream tasks can safely build on this output. Always ask: "Can the next task safely use this output? Are there integration risks?" This prevents downstream failures.
    
-   **Conflating Iteration with Plan Revision**: When a task doesn't meet spec, iteration refines that task. When checkpoint reveals a systematic planning problem (word budget overflow, structural mismatch), plan revision adjusts downstream tasks. Confusing these patterns leads to excessive plan changes instead of targeted task refinement.
    

### Progression Context

-   **Builds on**: Lesson 7 (Plan Phase) where you created atomic tasks with dependencies and success criteria. That plan becomes the roadmap `/sp.implement` executes. You needed clear task definitions and dependencies before implementation can proceed efficiently.
    
-   **Leads to**: Validation and completion workflows where you systematically verify that final implementation meets specification success evals (Lesson 9, Validation Phase). Implementation executes tasks; validation verifies that accumulated task outputs fulfill the original specification intent.
    

## Study Mode

Teaching by Socratic Method (OpenAI Study Mode & Google Extended Learning)

📚Socratic Teaching - AI guides you with questions

### Ready to Learn

Click the Teach button to get a guided explanation of this lesson from the book.

---
Source: https://agentfactory.panaversity.org/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on/implement-phase


-   [](/)
-   [Part 3: SDD-RI Fundamentals](/docs/SDD-RI-Fundamentals)
-   [Chapter 13: Master Spec-Kit Plus](/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on)
-   Designing Reusable Intelligence

# Designing Reusable Intelligence

You've completed the SDD workflow (Lessons 01-08): Constitution → Specify → Clarify → Plan → Tasks → Implement. You wrote specifications, refined requirements, planned architecture, and executed implementation with AI collaboration.

But here's what separates AI-native developers from AI-assisted developers: **The ability to transform good sessions into reusable skills.**

With Skills, you teach your AI specific workflows, tools, and processes. By creating a skill, you're giving your AI a playbook it can reference whenever you need that particular type of help—whether that's writing research sections, validating sources, or refining outlines.

* * *

## When to Create a Skill

Not every workflow deserves a skill. Create one when you notice:

**After a good session, ask yourself:**

1.  **Will I do this again?** (Frequency: 3+ times across projects)
2.  **Did it involve multiple decisions?** (Complexity: 5+ decision points)
3.  **Would I want the same quality next time?** (Value: consistent results matter)

If 2+ answers are YES → Create a skill.

**Examples from your research paper project:**

Pattern

Frequency

Complexity

Value

Create Skill?

Writing quality sections

✅ Every paper

✅ 6+ decisions

✅ Consistency

**YES**

Validating research sources

✅ Every source

✅ 5+ decisions

✅ Accuracy

**YES**

Refining outlines

✅ Every draft

✅ 5+ decisions

✅ Structure

**YES**

Formatting citations

✅ Every source

❌ 2-3 decisions

❌ Tool handles

NO

Spell checking

✅ Every draft

❌ 1 decision

❌ Automated

NO

* * *

## Part A: Creating a Skill Through Conversation

Creating a skill with AI means having a conversation where you explain your approach and share any materials you want included. AI translates this into a properly formatted skill.

### Step 1: Start the Conversation

After a good session (like writing a great section), start a new conversation:

```
I want to create a skill for writing research paper sections.During our last session, I noticed my best sections had:- Clear opening that establishes what the section explains- Evidence integrated naturally, not tacked on- Logical flow from one paragraph to the next- Conclusions that connect back to thesisCan you help me turn this into a reusable skill?
```

**What happens:**

-   AI asks clarifying questions about your process
-   You explain what makes your approach work
-   AI structures this into a skill file

### Step 2: Answer AI's Questions

AI will ask about your process. Provide enough detail that someone capable but unfamiliar could follow your approach.

**Example conversation:**

```
AI: "What makes a section 'good' in your view? How do you know when     a section is ready vs needs more work?"You: "A good section has three things:     1. Every claim is supported by evidence or citation     2. The opening hooks interest and the ending connects to thesis     3. Someone unfamiliar with the topic could follow the logic     It needs more work if I have to re-read sentences to understand them,     or if claims feel unsupported."AI: "What's your process for writing a section? Do you outline first,     write linearly, or iterate?"You: "I start with a rough outline of key points. Then I write the opening     paragraph to establish context. Then I fill in evidence for each point.     Finally I write transitions and the closing. I always read it aloud     to check flow."AI: "What quality checks do you apply before considering a section done?"You: "I check:     - Does every paragraph have a clear topic sentence?     - Is every factual claim cited?     - Does it read smoothly without stopping?     - Does it connect to the thesis?"
```

### Step 3: AI Builds the Skill File

Based on your conversation, AI creates a complete SKILL.md file. Ask:

```
Create the skill file with:- YAML frontmatter (name, description, version)- When to use this skill- Process steps from our conversation- Output format- Example with input and outputFormat it as a SKILL.md file I can save.
```

**AI generates:**

```
---name: "section-writer"description: "Write clear, evidence-supported research paper sections with proper citations and logical flow. Use when user asks to write a section, needs help with academic writing, or wants to structure research content."version: "1.0.0"---# Section Writing Skill## When to Use This Skill- User asks to "write a section" or "draft content" for a research paper- User mentions thesis, evidence integration, or academic writing- User needs help structuring research content with citations## How This Skill Works1. **Outline key points**: Identify 3-5 main points the section must make2. **Write opening paragraph**: Establish context, hook interest, connect to thesis3. **Develop each point**: Topic sentence → evidence/citation → significance → transition4. **Write closing**: Summarize insights, connect to thesis, set up next section5. **Quality check**: Verify claims cited, flow smooth, thesis connected## Output FormatProvide:- **Opening Paragraph**: Hook + context + thesis connection- **Body Segments**: For each key point: topic sentence, evidence, significance- **Transitions**: Smooth connections between paragraphs- **Closing Paragraph**: Summary + thesis connection + setup for next section## Quality CriteriaA section is ready when:- Someone unfamiliar with topic can follow the logic- All claims supported by evidence- No sentences require re-reading to understand- Opening hooks interest, closing connects to thesis## Example**Input**: "Write the Literature Review section on AI in K-12 education. Key points: (1) Current state of AI in K-12, (2) Teacher workload research, (3) Student outcome studies. Thesis: AI tools can measurably improve K-12 classroom efficiency."**Output**:- **Opening**: "The integration of artificial intelligence into K-12 classrooms represents one of the most significant shifts in educational technology since the introduction of personal computers. As schools face mounting pressure to improve outcomes while managing limited resources, AI tools offer promising solutions—but what does the research actually show?"- **Body**: [3 segments with topic sentences, evidence from studies, significance explained]- **Closing**: "The evidence suggests AI tools can meaningfully reduce teacher workload while improving student engagement. However, implementation challenges and equity concerns require careful attention as districts consider adoption."
```

### Step 4: Save the Skill File

Skills use a specific directory structure. Create the skill directory and save:

```
# Create skill directory (skill-name/SKILL.md structure)mkdir -p .claude/skills/section-writer
```

Then tell AI:

```
Save this skill to .claude/skills/section-writer/SKILL.md
```

Your directory structure now includes:

```
my-research-paper/├── .claude/│   ├── commands/              # Slash commands from specifyplus init│   └── skills/                # YOUR reusable intelligence│       └── section-writer/    # Skill directory│           └── SKILL.md       # Main skill file├── .specify/│   └── memory/│       └── constitution.md├── specs/│   └── [your-paper]/│       ├── spec.md│       ├── plan.md│       └── tasks.md└── ...
```

**Note**: Skills can also include supporting files (scripts, reference docs) in the skill directory. For now, SKILL.md is all you need.

### Step 5: Test the Skill

**Test on a real task:**

```
I need to write the Discussion section for my paper.Use the section-writer skill to guide me.Key points:1. How AI applications address teacher workload2. Evidence of student outcome improvements3. Limitations and areas needing more researchThesis: AI tools can measurably improve K-12 classroom efficiency.
```

**Evaluate the result:**

-   Did AI follow the skill's process (outline → opening → evidence → closing)?
-   Did output meet the quality criteria (claims cited, flows smoothly)?
-   What's missing or needs adjustment?

### Step 6: Iterate Until It Works

If something's off, ask AI to update the skill:

```
The section-writer skill worked well, but I noticed:- It didn't emphasize checking source credibility- The quality checklist could be more specificUpdate the skill to:1. Add source credibility check in Step 32. Add "minimum 3 sources per major point" to quality criteriaThen save the updated version to .claude/skills/section-writer.md
```

Repeat testing until your skill produces consistent, high-quality results.

* * *

## Part B: Skill vs Subagent — When to Create Which

As you identify more patterns, you'll wonder: **Should I create a skill or a subagent?**

### Decision Framework

**Create a SKILL (2-6 decision points)** when:

-   Human guides the process, AI assists
-   You apply the framework, AI helps execute
-   Examples: section-writer, outline-refiner, citation-formatter

**Create a SUBAGENT (7+ decision points)** when:

-   AI should work autonomously with minimal guidance
-   AI makes judgments and returns verdicts
-   Pattern requires complex, multi-step reasoning
-   Examples: research-validator (evaluates source credibility), fact-checker (verifies claims)

**From your research paper project:**

Component

Decision Points

Human Involvement

Create

Section writing

6

Human guides, AI assists

**SKILL**

Outline refinement

5

Collaborative iteration

**SKILL**

Research validation

8+

AI judges credibility

**SUBAGENT**

Fact checking

7+

AI verifies autonomously

**SUBAGENT**

### What Makes Subagents Different

A subagent adds three things beyond a skill:

**1\. Role Definition** (autonomous identity):

```
**Name**: source-validator**Autonomy Level**: High (makes accept/reject decisions)**Invocation**: Automatic (after adding source) or manual
```

**2\. Decision Authority** (what it can decide vs escalate):

```
**Can ACCEPT**: Peer-reviewed sources from past 10 years**Can REJECT**: Non-peer-reviewed sources, outdated sources**Must ESCALATE**: Borderline cases, conflicting information
```

**3\. Reporting Format** (structured output):

```
=== SOURCE VALIDATION ===Source: [title]Verdict: [ACCEPT | REJECT | ESCALATE]Reasoning: [specific criteria applied]Required Actions: [if any]
```

### Creating a Subagent (Preview)

Subagents follow a similar conversation-based creation process:

```
I want to create a subagent for validating research sources.The subagent should autonomously:1. Check if sources are peer-reviewed2. Evaluate publication date (prefer recent)3. Assess author credibility4. Flag potential bias5. Verify source actually supports the claim being madeIt should return a verdict (accept/reject/escalate) with reasoning.Help me design this subagent with:- Role definition- Decision authority (what it can decide vs escalate)- Reporting format
```

You'll learn more about subagents in later chapters. For now, focus on skills.

* * *

## Part C: Validating Your Skill Works

Good skills trigger **reasoning mode** (context-specific analysis). Bad skills trigger **prediction mode** (generic responses).

### Test Your Skill's Effectiveness

Ask your AI to apply your skill to a challenging case:

```
Apply the section-writer skill to this vague request:"Write about AI in education"Walk me through how you're applying each step of the skill.Show your reasoning for each quality check.
```

**Good response (reasoning mode):**

```
Applying section-writer skill:STEP 1 - OUTLINE KEY POINTS:The request is too vague. Before outlining, I need:- What specific aspect of AI in education?- What thesis should this connect to?- What audience level?[Skill triggers clarification before proceeding]STEP 2-4 - [Would proceed after clarification]QUALITY CHECK:- Cannot verify "connects to thesis" without knowing thesis- Cannot ensure "someone unfamiliar can follow" without knowing audienceSKILL VERDICT: Request needs refinement before skill can be applied effectively.
```

**Bad response (prediction mode):**

```
Here's a section about AI in education:AI is transforming education in many ways. It helps teachersand students learn better. Many schools are using AI tools...[Generic content that ignores skill process]
```

If you get prediction mode responses, your skill needs strengthening. Revise with more specific criteria and quality checks.

* * *

## Part D: Building Your Intelligence Library

### Organizing Your Skills

Standard directory structure (each skill gets its own folder):

```
my-research-paper/├── .claude/│   ├── commands/                    # Slash commands (from specifyplus)│   └── skills/                      # YOUR accumulated intelligence│       ├── section-writer/          # Skill directory│       │   └── SKILL.md             # Main skill file│       ├── outline-refiner/         # Future skill│       │   └── SKILL.md│       └── source-evaluator/        # Future skill│           ├── SKILL.md│           └── scripts/             # Optional supporting files│               └── verify_source.py├── .specify/│   └── memory/│       └── constitution.md├── specs/└── ...
```

### Intelligence Reuse Strategy

**Skill reuse** (apply to new contexts):

```
# Project 2: Different research paperI'm writing a section on climate policy impacts.Use the section-writer skill.Context: This is for a policy paper, not education research.Key points: (1) Current policy landscape, (2) Economic impacts, (3) Implementation challengesThesis: Carbon pricing is the most efficient policy mechanism.
```

**Intelligence composition** (combine multiple skills):

```
# Project 3: Comprehensive paperApply these skills in sequence:1. outline-refiner → improve paper structure2. section-writer → write each section3. source-evaluator → validate all citationsStart with outline-refiner on my current outline.
```

* * *

## Common Mistakes

### Mistake 1: Creating Skills for Trivial Patterns

**The Error**: Creating a skill for "How to format headings"

**Why It's Wrong**: 1-2 decision points don't justify a skill. Save skills for complex, recurring workflows.

**The Fix**: Only create skills for patterns with 5+ decisions that recur across 3+ projects.

### Mistake 2: Skipping the Testing Phase

**The Error**: Saving a skill and assuming it works

**Why It's Wrong**: Skills need iteration. Your first version probably misses edge cases.

**The Fix**: Always test skills on real tasks. Update based on what's missing.

### Mistake 3: Over-Specific Skills

**The Error**: Creating "AI-Education-Literature-Review-Writer" that only works for one topic

**Why It's Wrong**: Intelligence should be reusable. Over-specificity limits value.

**The Fix**: Generalize patterns:

-   ❌ "AI-Education-Literature-Review-Writer"
-   ✅ "Section-Writer" (works for any research paper section)

### Mistake 4: No Quality Criteria

**The Error**: Skill describes process but not what "good" looks like

**Why It's Wrong**: Without quality criteria, you can't verify output or improve skill.

**The Fix**: Every skill needs explicit quality criteria:

-   What makes output "ready"?
-   What makes output "needs work"?
-   How do you check?

* * *

## Skill Reuse in Practice

### Project 1: Research Paper (Lessons 04-08)

You execute the complete workflow from scratch:

-   Write specification, plan, tasks
-   Write sections through trial and error
-   Learn what works through iteration
-   **Total**: 8-10 hours

### Project 2: New Paper (With `section-writer` Skill)

With your skill, dramatically faster:

1.  Write paper specification (30 min)
2.  Plan sections (30 min)
3.  Write sections using skill guidance (3 hours—skill provides structure)
4.  **Total**: 4 hours (50% faster)

### Project 3: Multi-Paper Work (With Multiple Skills)

With accumulated skills:

1.  Use `section-writer` skill to write (2 hours)
2.  Use `source-evaluator` skill to check citations (1 hour)
3.  Use `outline-refiner` skill to improve structure (30 min)
4.  **Total**: 3.5 hours

**Intelligence compounds**: Each skill accelerates future work.

* * *

## Try With AI

Ready to create your first reusable skill? Practice conversation-based skill creation:

**Start Skill Creation:**

> "I want to create a skill for writing research paper sections. During my work on this paper, I noticed my best sections had clear openings, evidence integrated naturally, logical flow, and conclusions connecting to thesis. Help me turn this into a reusable skill. Ask me questions about my process."

**Generate Complete Skill File:**

> "Based on our conversation, create a complete SKILL.md file with: YAML frontmatter (name, description, version), when to use, process steps, output format, and example. Format it so I can save to .claude/skills/section-writer/SKILL.md"

**Test Your Skill:**

> "Apply the section-writer skill to write my Discussion section. Key points: (1) How AI applications address teacher workload, (2) Evidence of student outcome improvements, (3) Limitations. Walk me through each step of the skill as you apply it."

**Iterate Based on Results:**

> "The skill worked, but I noticed \[specific issue\]. Update the skill to address this. Save the updated version."

**Decide Skill vs Subagent:**

> "I'm thinking about creating reusable intelligence for validating research sources. Help me decide: (1) How many decision points does this involve? (2) Should human guide or AI work autonomously? (3) Based on that, should this be a skill or subagent? (4) Start the creation process."

# Designing Reusable Intelligence

This lesson teaches students to create reusable skills through conversation with AI after good sessions. Students identify patterns worth encoding (frequency + complexity + value), have a conversation where they explain their approach, and AI structures it into a complete skill file with metadata, process steps, quality criteria, usage example, and self-check validation. Students save skills to `.claude/skills/`, test them on real tasks, and iterate until they work. The lesson also distinguishes skills (2-6 decision points, human-guided) from subagents (7+ decisions, AI autonomous).

### Mental Models

-   **Skills from Good Sessions**: After a session that went well, ask: Will I do this again? Did it involve multiple decisions? Would I want the same quality next time? If 2+ YES → create a skill.
    
-   **Conversation-Based Creation**: You describe your process naturally, AI asks clarifying questions (what makes output good? what's your process? what quality checks?), AI structures it into a complete skill file.
    
-   **Test and Iterate Loop**: Skills need iteration. Save skill → test on real task → evaluate results → update skill → repeat until consistent results.
    
-   **Reasoning vs Prediction Mode**: Good skills trigger reasoning mode (AI asks for clarification, applies each step explicitly). Bad skills trigger prediction mode (AI produces generic content ignoring the skill process).
    
-   **Intelligence Compounds**: Project 1: 8-10 hours (from scratch). Project 2 with skill: 4 hours (50% faster). Project 3 with multiple skills: 3.5 hours. Each skill accelerates future work.
    

### Key Patterns

-   **Start skill conversation**: After good session, say "I want to create a skill for \[workflow\]. During my work, I noticed my best \[outputs\] had \[specific qualities\]. Help me turn this into a reusable skill."
    
-   **Complete skill file structure**: YAML frontmatter (`name`, `description`, `version`) → When to use → Process steps → Output format → Quality criteria → Example.
    
-   **Save to `.claude/skills/<skill-name>/SKILL.md`**: Create skill directory with `mkdir -p .claude/skills/section-writer`, then save SKILL.md inside. Skills use directory structure (skill-name/SKILL.md), not flat files.
    
-   **Test skill on real task**: Apply skill to actual work, evaluate: Did AI follow the process? Did output meet criteria? What's missing?
    
-   **Iterate with specific feedback**: "The skill worked but \[specific issue\]. Update skill to \[fix\]. Save updated version."
    
-   **Validate skill triggers reasoning**: Apply skill to vague request. Good skill asks for clarification and shows step-by-step reasoning. Bad skill produces generic content.
    

### Common Mistakes

-   **Creating skills for trivial patterns**: "How to format headings" (1-2 decisions) doesn't justify a skill. Save skills for 5+ decision workflows.
    
-   **Skipping testing**: Saving skill and assuming it works. Skills need iteration—first version misses edge cases.
    
-   **Over-specific skills**: "AI-Education-Literature-Review-Writer" only works for one topic. Generalize to "Section-Writer" (any paper).
    
-   **No quality criteria**: Skill describes process but not what "good" looks like. Every skill needs explicit ready/needs-work criteria.
    

### Progression Context

-   **Builds on**: Lessons 04-08 (complete SDD workflow). Students have executed one full project cycle and understand where patterns recur.
    
-   **Leads to**: Lesson 11 (Capstone) where students invoke created skills to accelerate new work, demonstrating intelligence compounding across projects.
    

## Study Mode

Teaching by Socratic Method (OpenAI Study Mode & Google Extended Learning)

📚Socratic Teaching - AI guides you with questions

### Ready to Learn

Click the Teach button to get a guided explanation of this lesson from the book.

---
Source: https://agentfactory.panaversity.org/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on/designing-reusable-intelligence


-   [](/)
-   [Part 3: SDD-RI Fundamentals](/docs/SDD-RI-Fundamentals)
-   [Chapter 13: Master Spec-Kit Plus](/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on)
-   Brownfield Adoption

# Brownfield Adoption

Most of what you've learned in Chapter 13 applies to **greenfield projects**—new codebases where you start from scratch and control the entire structure. But real work is different. You'll inherit existing projects with months or years of accumulated code, decisions, and team knowledge.

**Brownfield adoption** is the process of bringing Spec-Kit Plus into an existing project. The challenge isn't technical—it's strategic. How do you add a structured workflow framework without losing the institutional knowledge your team has already captured? How do you protect against data loss when the framework overwrites key files like `CLAUDE.md`?

This lesson teaches you a safe, proven workflow for brownfield adoption that preserves existing knowledge, prevents accidental data loss, and integrates Spec-Kit Plus incrementally.

* * *

## Foundation — Greenfield vs Brownfield

### What's the Difference?

**Greenfield Project**: You start with an empty directory. You have no existing:

-   Code to protect
-   Team conventions to preserve
-   Architectural decisions made
-   Custom tools or workflows

Running `specifyplus init` in a greenfield project is straightforward—you're building from scratch.

**Brownfield Project**: You inherit an existing codebase with:

-   Working code in `src/`, `lib/`, or equivalent directories
-   Custom `CLAUDE.md` with team knowledge (coding standards, architecture principles, collaboration patterns)
-   Custom slash commands in `.claude/commands/` (project-specific workflows)
-   Git history containing architectural decisions and design rationale
-   Team members relying on existing conventions

Running `specifyplus init --here` (the brownfield command) in this context requires careful strategy to avoid data loss.

### The Core Problem

When you run `specifyplus init --here`, the command initializes Spec-Kit Plus in your **existing directory**. Here's what happens:

**Files that get OVERWRITTEN** (complete replacement):

-   `CLAUDE.md` — Your custom AI instructions get replaced with the Spec-Kit Plus template (~240 lines)
-   Any existing `.specify/` directory (if present) gets reset

**Files that are PRESERVED** (completely safe):

-   All custom slash commands in `.claude/commands/` are preserved
-   All source code (`src/`, `lib/`, etc.) remains untouched
-   All tests, configuration files, and project artifacts survive intact
-   Your git history is unaffected

**The Risk**: Your `CLAUDE.md` contains months or years of team knowledge. Without a backup before running init, that content is permanently lost—no recovery mechanism exists.

### Example: Three Real Project Types

Let's see how brownfield adoption affects different project types:

**Scenario 1: Existing Blog/Website Project**

```
blog-project/├── CLAUDE.md          (200 lines of team conventions)├── src/│   ├── pages/│   ├── components/│   └── styles/├── README.md└── .claude/commands/    └── deploy-netlify.md   (custom deployment workflow)
```

After `init --here`:

-   CLAUDE.md (200 → 240 lines) — Your content replaced with template
-   `.specify/` directory created
-   `deploy-netlify.md` preserved and working
-   Source code completely untouched

**Scenario 2: Existing API Project**

```
api-project/├── CLAUDE.md          (150 lines of coding standards)├── src/│   ├── routes/│   ├── models/│   └── middleware/├── tests/└── .claude/commands/    ├── run-tests.md    └── format-code.md
```

After `init --here`:

-   CLAUDE.md replaced (your standards lost without backup)
-   `.specify/` created with constitution template
-   Both custom commands preserved
-   Code and tests completely safe

**Scenario 3: Documentation Project**

```
docs-project/├── CLAUDE.md          (100 lines of documentation standards)├── docs/│   ├── guides/│   ├── api/│   └── tutorials/└── .claude/commands/    └── publish-docs.md
```

After `init --here`:

-   CLAUDE.md replaced
-   `.specify/` created
-   Custom publish command preserved
-   Documentation source intact

* * *

## Collaboration — Safe Brownfield Testing Workflow

The key to safe brownfield adoption is **redundant safety measures**: git branches + manual backups + clear inspection of what actually changed.

### Designing the Workflow

**Your situation**: You have an existing project with a custom `CLAUDE.md` that your team values. You want to test `specifyplus init --here` but can't afford to lose the content.

**AI's response**:

> "The solution is creating multiple recovery points before testing. Here's the proven workflow:
> 
> ```
> # STEP 1: Create experimental branch (isolates risk from main)git checkout -b experiment/specifykit# STEP 2: Create backup copies (manual recovery option)cp CLAUDE.md CLAUDE.md.backupcp -r .claude .claude.backup# STEP 3: Commit current state (git recovery option)git add -Agit commit -m 'backup: preserve team knowledge before Spec-Kit Plus init'# STEP 4: NOW test safely (you have multiple recovery paths)specifyplus init --here
> ```
> 
> **Why this approach works**:
> 
> -   **Experiment branch**: Your `main` branch stays completely untouched
> -   **Backup files**: If you need your original content, `.backup` files have it
> -   **Git commit**: Historical recovery via `git show HEAD~1:CLAUDE.md`
> -   **Multiple recovery paths**: If one method fails, you have alternatives
> 
> Want me to walk through exactly what changes, and how to merge your content afterward?"

### Understanding What Actually Changed

After running init, you inspect the results:

```
# Check what changedgit diff --name-only# Output:# CLAUDE.md# .specify/memory/constitution.md# .specify/memory/context-quality-memory.md# .specify/templates/spec-template.md# .specify/templates/plan-template.md# .specify/templates/tasks-template.md# [... more .specify/ files ...]
```

Your `CLAUDE.md.backup` still has the original content. Now you can make an informed decision about merging:

**Option 1: Content goes to Constitution** (Recommended for standards and architecture decisions)

Your team's coding standards, architecture principles, and development conventions belong in `.specify/memory/constitution.md`—the project-specific principles file that AI agents read alongside `CLAUDE.md`.

**Option 2: Content appends to CLAUDE.md** (For behavioral collaboration patterns)

Your team's AI collaboration patterns (like "test-first development" or "review AI output critically") belong appended to the end of `CLAUDE.md`, since they're instructions for HOW AI should work with your team.

### Merging Strategy

**For a real project**, here's how you'd merge (using example content):

1.  **Read your backup**: `cat CLAUDE.md.backup`
2.  **Identify content categories**:
    -   Coding standards → Move to `constitution.md`
    -   Architecture principles → Move to `constitution.md`
    -   AI collaboration patterns → Append to new `CLAUDE.md`
3.  **Execute the merge**:
    
    ```
    # Add standards to constitutionecho "## Project Development Standards[paste your coding standards here]" >> .specify/memory/constitution.md# Append patterns to CLAUDE.mdecho "## Team AI Collaboration Patterns[paste your collaboration patterns here]" >> CLAUDE.md
    ```
    
4.  **Verify nothing was lost**:
    
    ```
    # Compare old vs new (backup has all your content)diff CLAUDE.md.backup CLAUDE.md.backup.recovered
    ```
    

* * *

## Practice — Identifying Your Project's Content

Before you adopt Spec-Kit Plus on a real project, understand what you'd need to preserve.

### Self-Check: Content Categories

For each category, decide where your team's content would go:

**Category 1: Development Standards**

-   Type hints requirements (Python)
-   Line length limits (80, 100, 120 chars)
-   Import ordering conventions
-   Naming conventions

**Decision**: These are project rules → Move to `constitution.md`

**Category 2: Architecture Principles**

-   Technology choices (Flask vs FastAPI, PostgreSQL vs MongoDB)
-   Design patterns (microservices, monolith, serverless)
-   Deployment strategy (Docker, Kubernetes, serverless)

**Decision**: These are project constraints → Move to `constitution.md`

**Category 3: AI Collaboration Patterns**

-   "Specification first, then code"
-   "Review AI output before merging"
-   "Test coverage minimum 80%"
-   Preferred AI tools and models

**Decision**: These are behavioral instructions → Append to `CLAUDE.md`

### Planning Your Adoption

Write down your actual content before running init:

**What's in your current CLAUDE.md?** (Estimate line counts and categories)

-   Development standards: \_\_\_ lines
-   Architecture principles: \_\_\_ lines
-   AI collaboration patterns: \_\_\_ lines
-   Custom workflow notes: \_\_\_ lines

**What custom commands do you rely on?** (These are safe)

-   `/deploy` or `/deploy-staging`?
-   `/test` or `/test-coverage`?
-   `/format` or `/lint`?
-   Others: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**What would break if CLAUDE.md disappeared?**

-   Team coding standard consensus lost?
-   Architecture decisions undocumented?
-   AI collaboration practices forgotten?

* * *

## Try With AI

You're evaluating whether to adopt Spec-Kit Plus on a real project. Let's plan the actual adoption strategy.

**Setup**: Open your project directory with Spec-Kit Plus ready.

**Prompt Set**:

```
Prompt 1 (Understanding your current state):"My project already has a custom CLAUDE.md with our team's coding standards andarchitecture principles. I want to use Spec-Kit Plus but can't lose this content.What's my safe adoption strategy? Should I back up first? What will actually get overwritten?"Prompt 2 (Planning the workflow):"Here's what's in our CLAUDE.md:[paste your actual content or describe it]Walk me through the exact steps to:1. Create a safe testing environment2. Run specifyplus init --here3. Merge my team's knowledge with the Spec-Kit Plus template"Prompt 3 (Merging strategy for your content):"After running init, how do I decide what content goes to constitution.md vsappends to CLAUDE.md? Give me specific examples based on [your project type: blog, API, docs]"
```

**Expected Outcomes**:

-   Clear understanding of what's safe to overwrite (you know in advance)
-   Concrete backup and recovery plan before running init
-   Decision framework for where your team's knowledge belongs in Spec-Kit Plus structure

**Safety Note**: Always create both a git branch AND manual backup files before running experimental commands. One backup method is good; two is better; three is gold standard.

* * *

## Checkpoint: Reflect on Your Adoption Path

Before moving to the capstone, consider:

-   **Greenfield vs Brownfield**: Which applies to your next project? (You'll use different workflows)
-   **Content Preservation**: What team knowledge would you need to preserve before adopting Spec-Kit Plus?
-   **Recovery Readiness**: Could you recover your CLAUDE.md if it got overwritten accidentally? (Git history? Manual backup?)
-   **Incremental Adoption**: Would you adopt Spec-Kit Plus all at once, or incrementally? Why?

## Lesson Title

Brownfield adoption teaches the safe, strategic process of integrating Spec-Kit Plus into existing projects while preserving team knowledge. Unlike greenfield projects where you control the entire structure from the start, brownfield work requires protecting accumulated institutional knowledge (custom CLAUDE.md, slash commands, team conventions) while avoiding data loss from framework-driven overwrites. The lesson establishes a three-layer safety workflow (git branches + manual backups + git commit history) before running `specifyplus init --here`, then shows students how to classify and merge their existing knowledge into the appropriate Spec-Kit Plus locations (constitution.md for standards, CLAUDE.md for collaboration patterns).

### Mental Models

-   **Greenfield vs Brownfield**: Greenfield means starting from scratch with no existing code, conventions, or institutional knowledge. Brownfield means inheriting an existing codebase with months/years of accumulated decisions, team knowledge, and working code that must be protected during framework adoption.
    
-   **File Preservation Profile**: Not all files are equally at risk during init. Understanding exactly what gets overwritten (CLAUDE.md, .specify/), what gets created (constitution.md, templates), and what stays completely safe (source code, git history, custom slash commands) lets students make informed decisions about backup strategy.
    
-   **Content Classification**: Team knowledge stored in a single CLAUDE.md file must be sorted by destination after adoption—coding standards and architecture principles belong in constitution.md (project-specific rules), while AI collaboration patterns and behavioral instructions belong appended to CLAUDE.md (instructions for AI working with the team).
    
-   **Redundant Safety Strategy**: Multiple recovery paths (git branch isolation, manual backup files, git commit history, diffs) provide overlapping protection. If one recovery method fails, others can restore content—eliminating single points of failure.
    

### Key Patterns

-   **Three-Layer Safety Workflow**: Create experiment branch (isolates main branch from risk) + create backup files (manual recovery) + commit current state (git recovery history) BEFORE running init. This produces three independent ways to recover if needed.
    
-   **Diff-Based Verification**: After running init, inspect actual changes via `git diff --name-only` to confirm only expected files changed. This prevents surprising overwrites and builds confidence in the safety of the process.
    
-   **Content Routing Decision Matrix**: Establish clear classification rules before merging—coding standards/architecture/design patterns go to constitution.md (project constraints), collaboration behaviors/AI interaction patterns go to CLAUDE.md (behavioral instructions). This prevents mixing concerns and maintains clean separation.
    
-   **Incremental Adoption Strategy**: Teams don't have to adopt Spec-Kit Plus all at once. Testing safely on a branch, merging selectively, and keeping both systems coexisting temporarily lets teams transition gradually without disrupting existing workflows.
    

### Common Mistakes

-   **No Backup Before Init**: Running `specifyplus init --here` without backing up CLAUDE.md first. If the init overwrites your team knowledge and you don't have backups or git history, the content is permanently lost—no recovery mechanism exists.
    
-   **Single Point of Failure**: Relying on only one recovery method (like git commit) and ignoring the others. If you used git and the git history gets corrupted or accidentally reset, you have no fallback. Multiple overlapping recovery methods prevent total loss.
    
-   **Wrong Content Destination**: Putting coding standards into CLAUDE.md instead of constitution.md, or putting behavioral AI instructions into constitution.md instead of CLAUDE.md. This confuses concerns—constitution defines project rules, CLAUDE.md defines how AI should behave within those rules.
    
-   **Testing on Main Branch**: Running init directly on main branch instead of an experiment branch. If something unexpected happens, your production branch is affected immediately instead of isolated in a test branch.
    
-   **Losing Context During Merge**: After init creates the new files, failing to understand what your original content was for. If you don't read and categorize your CLAUDE.md.backup content before attempting the merge, you might accidentally discard important team knowledge while integrating the new structure.
    

### Progression Context

-   **Builds on**: Chapter 13 foundation lessons teaching greenfield workflow, CLAUDE.md structure, constitution.md purpose, slash commands, and specifyplus initialization. Students understand what Spec-Kit Plus does and how it organizes knowledge before learning how to integrate it into existing systems.
    
-   **Leads to**: Capstone (Lesson 15, Chapter 13) where students apply full Spec-Kit Plus workflow to real-scale projects combining all previous lessons, including safe brownfield adoption patterns for teams inheriting existing systems.
    

## Study Mode

Teaching by Socratic Method (OpenAI Study Mode & Google Extended Learning)

📚Socratic Teaching - AI guides you with questions

### Ready to Learn

Click the Teach button to get a guided explanation of this lesson from the book.

---
Source: https://agentfactory.panaversity.org/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on/brownfield-adoption



-   [](/)
-   [Part 3: SDD-RI Fundamentals](/docs/SDD-RI-Fundamentals)
-   [Chapter 13: Master Spec-Kit Plus](/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on)
-   Capstone — Intelligence Acceleration

# Capstone — Intelligence Acceleration

You've completed the full SDD-RI workflow across Lessons 1-10. You've written specifications, executed implementation, and created reusable intelligence (the `section-writer` skill from Lesson 9).

Now comes the proof: **Can you complete a second project faster using the intelligence you've built?**

This capstone answers that question decisively. You'll write a second paper section—using the `section-writer` skill created in Lesson 9—and measure how much faster execution becomes. This demonstrates the core principle of SDD-RI: **accumulated intelligence compounds**.

By the end of this capstone, you'll have:

-   A complete research paper with multiple sections (portfolio-ready)
-   Evidence that your skills accelerated the work
-   Understanding of why intelligence accumulation matters more than code libraries
-   The ability to tackle future projects with exponentially less effort

* * *

## The Acceleration Principle

Before diving into the capstone, let's measure what's about to happen.

### Project Timeline: First Section (Lesson 8)

Lesson 8 took you from nothing to a complete, validated paper section (introduction):

Phase

Lesson

Time Estimate

What You Did

Constitution

03

30 min

Defined research paper quality standards

Specification

04

45 min

Wrote paper introduction spec

Clarify

05

30 min

Refined spec with research requirements

Plan

06

45 min

Designed writing strategy and outline

Tasks

07

30 min

Broke down into atomic writing units

Implement

08

60 min

Generated, refined, and validated introduction

**Total**

**~3.5 hours**

**Built from scratch**

You had to:

-   Learn how to structure research paper specifications
-   Discover how to validate claims against sources
-   Troubleshoot writing clarity and academic tone
-   Write complete implementation plan
-   Handle iteration when first drafts needed refinement

### Project Timeline: Second Section (Lesson 11 - This Capstone)

This lesson takes you from specification to published section using the `section-writer` skill you created:

Phase

What You'll Do

Time Estimate

Specification

Write main body section spec

15 min

Implement

Execute with `section-writer` skill

30 min

Validation

Verify against spec criteria

15 min

Reflection

Document acceleration

10 min

**Total**

**~70 minutes**

The difference: **You're reusing intelligence.**

### Why This Is Faster

Compare the effort:

**Without skill** (hypothetical—writing second section from scratch):

-   Discover writing patterns from first section
-   Learn what "quality section" means in your context
-   Determine how to integrate research sources consistently
-   Troubleshoot tone and structure issues
-   Estimate: 2-3 hours (similar to first section)

**With skill** (your reality—using `section-writer` skill):

-   Reference your `section-writer` skill (encodes writing patterns)
-   Let `/sp.implement` invoke that skill
-   Validate output
-   Done in 70 minutes

**The math**:

-   **Lesson 8**: 3.5 hours to build writing intelligence
-   **Lesson 11**: 70 minutes using that intelligence
-   **Savings**: 2 hours 20 minutes (65% time reduction)
-   **But here's the key**: The next paper section will take 45 minutes. The third will take 40 minutes. Intelligence compounds exponentially.

* * *

## Step 1: Write Your Second Section Specification

Your specification for the main body section should be **intentionally shorter** than your introduction specification (from Lesson 4). This demonstrates specification complexity reduction through skill composition.

### Why This Spec Is Simpler

**Lesson 4 (Introduction) spec required:**

-   Research paper structure overview
-   Claim definition and validation approach
-   Source integration strategy
-   Multiple decision points (all handled by you the first time)

**Lesson 11 (Main Body) spec requires:**

-   Intent (develop key claims with evidence)
-   Constraints (academic standards, source requirements)
-   Success Criteria (clarity, evidence completeness)

The upstream complexity is **encapsulated in your skill**. Your specification just needs to say *what* success looks like, not *how* the skill works internally.

### Create Your Main Body Section Specification

Create a file at `specs/paper-project/main-body-section.md` with this structure:

```
# Specification: Research Paper Main Body Section## IntentWrite the main body section of the research paper, developing the three key claims established in the introduction.**Success means**: Reader understands each claim, sees supporting evidence, and recognizes logical progression.**Target scope**: 800-1200 words across 3 subsections (one per key claim)**Foundation**: Introduction (Lesson 8) establishes context; this section builds the argument.## Constraints- **Structure**: 3 subsections (one per key claim from introduction)- **Evidence**: Each claim supported by minimum 2 research sources- **Tone**: Consistent with introduction (academic, professional)- **Clarity**: Accessible to educated reader unfamiliar with topic- **Quality standards**: Follow constitution (Chapter 03) quality metrics## Success Evals- ✅ All three claims developed with clear reasoning- ✅ Each claim supported by minimum 2 credible sources- ✅ Logical progression between sections- ✅ Academic tone consistent throughout- ✅ Word count within 800-1200 word target- ✅ Sources properly cited and integrated- ✅ Reader understands argument progression## Non-Goals- No counter-argument discussion (saved for conclusion)- No external research beyond existing sources- No section reorganization (three claims must map to outline)- No graphics or visual elements## Edge Cases Handled by SkillThe `section-writer` skill from Lesson 9 handles these:- Maintaining tone consistency with introduction- Integrating diverse sources coherently- Structuring long claims into digestible subsections- Ensuring evidence completeness- Validating academic standards
```

**Stop and verify**: Your specification is complete when:

-   ✅ Intent is clear (developing the three claims from introduction)
-   ✅ Constraints are explicit (structure, evidence requirements, tone, quality standards)
-   ✅ Success criteria are measurable (claim development, source count, word count, tone consistency)
-   ✅ Non-goals prevent scope creep (no counter-arguments, no graphics, no reorganization)

* * *

## Step 2: Understand Your Skill and How It Compounds

Now comes the leverage: you're going to invoke `/sp.implement` with explicit skill references. This tells the AI assistant: "Use the intelligence I've already built."

### The `section-writer` Skill From Lesson 9

In Lesson 9, you created the `section-writer` skill at `.claude/skills/section-writer/SKILL.md`:

```
---name: "section-writer"description: "Write clear, evidence-supported research paper sections with proper citations and logical flow. Use when user asks to write a section, needs help with academic writing, or wants to structure research content."version: "1.0.0"---# Section Writing Skill## When to Use This Skill- User asks to "write a section" or "draft content" for a research paper- User mentions thesis, evidence integration, or academic writing- User needs help structuring research content with citations## How This Skill Works1. **Outline key points**: Identify 3-5 main points the section must make2. **Write opening paragraph**: Establish context, hook interest, connect to thesis3. **Develop each point**: Topic sentence → evidence/citation → significance → transition4. **Write closing**: Summarize insights, connect to thesis, set up next section5. **Quality check**: Verify claims cited, flow smooth, thesis connected## Quality CriteriaA section is ready when:- Someone unfamiliar with topic can follow the logic- All claims supported by evidence- No sentences require re-reading to understand- Opening hooks interest, closing connects to thesis
```

When AI discovers this skill (through the description), it applies this reasoning framework, which accelerates the entire writing process.

### Understanding Skill Invocation

Skills are automatically discovered through their descriptions. When you run `/sp.implement` and mention writing a section, AI finds your `section-writer` skill:

```
/sp.implementI need to write the main body section for my research paper.Use my section-writer skill to guide the process.Specification: specs/paper-project/main-body-section.md
```

**How skill discovery works**:

1.  AI scans `.claude/skills/` for available skills
2.  Your `section-writer` description says "Use when user asks to write a section"
3.  AI automatically loads and applies that skill's workflow

**The AI assistant will**:

1.  Read your specification
2.  Discover and load your `section-writer` skill (from `.claude/skills/section-writer/SKILL.md`)
3.  Follow the skill's "How This Skill Works" steps
4.  Apply the skill's quality criteria
5.  Validate output against success evals

**What you're NOT doing**:

-   ❌ Writing from scratch (no discovery phase)
-   ❌ Learning academic structure again (already in skill)
-   ❌ Figuring out evidence integration (skill handles this)
-   ❌ Validating against quality standards (skill applies them)

Your skill has already encoded this knowledge.

* * *

## Step 3: Execute with /sp.implement and Skills

When you're ready (your specification complete, your introduction from Lesson 8 available, research sources gathered), run this command:

```
/sp.implementWrite the main body section of my research paper.Use the section-writer skill from .claude/skills/.Specification: specs/paper-project/main-body-section.mdKey claims to develop:1. [Your first claim from introduction]2. [Your second claim from introduction]3. [Your third claim from introduction]
```

### What Happens During Execution

The AI assistant will:

1.  **Load Your Specification**
    
    -   Read intent, constraints, success criteria
    -   Identify that this section develops three claims from introduction
    -   Extract quality standards from constitution (Chapter 03)
2.  **Discover and Apply Your Skill**
    
    -   Find `section-writer` skill in `.claude/skills/section-writer/SKILL.md`
    -   Follow the skill's process (outline → opening → develop → closing → quality check)
    -   Apply the skill's quality criteria
    -   Check academic tone consistency with introduction
3.  **Execute the Writing**
    
    -   Write main body section with 3 subsections (one per claim)
    -   Integrate research sources (minimum 2 per claim)
    -   Maintain word count (800-1200 words)
    -   Ensure logical progression
4.  **Validate Success**
    
    -   Check that all three claims are developed
    -   Verify evidence completeness
    -   Confirm tone consistency
    -   Validate word count and structure
    -   Confirm success evals are met

### Your Role During Implementation

You don't watch passively. You're part of the execution:

1.  **Review Before Finalization** — The assistant will show you the draft section and ask: "Does this meet your specification?" You verify that claims are developed clearly and evidence is compelling.
    
2.  **Provide Feedback If Needed** — If something doesn't match your vision (tone feels off, a claim needs more support), the assistant will refine based on your input.
    
3.  **Validate The Outcome** — Once finalized, you read the section and verify it integrates well with your introduction and advances your argument.
    

* * *

## Step 4: Validate Your Main Body Section

Once the section is written, run this validation checklist:

### Pre-Implementation Checklist (Before Invoking Skill)

-    **Specification is complete** — All required sections filled (Intent, Constraints, Success Evals, Non-Goals)
-    **Introduction from Lesson 8 exists** — You have the validated introduction section
-    **Skill is referenced** — `/sp.implement` command includes `--skills section-writer`
-    **Research sources gathered** — You have credible sources for claims
-    **Claim clarity** — You can articulate the three claims your main body will develop

### Post-Implementation Validation (After Section Is Written)

-    **All three claims developed** — Each claim has clear reasoning and support
-    **Evidence completeness** — Each claim has minimum 2 credible sources cited
-    **Tone consistency** — Matches introduction (academic, professional)
-    **Word count appropriate** — Falls within 800-1200 word range
-    **Logical progression** — Reader can follow argument from claim to claim
-    **Sources integrated** — Citations feel natural, not forced
-    **Integrates with introduction** — Section builds on introduction without repetition

### Success Criteria Verification

Map your main body section to the specification success evals:

Success Eval

Evidence

Status

All three claims developed with clear reasoning

Section clearly explains each claim

✅ / ❌

Each claim supported by minimum 2 sources

Citations visible in text

✅ / ❌

Logical progression between sections

Natural flow from claim to claim

✅ / ❌

Academic tone consistent throughout

Matches introduction tone

✅ / ❌

Word count within target

800-1200 words

✅ / ❌

Sources properly cited

References formatted correctly

✅ / ❌

Reader understands progression

Argument is clear and persuasive

✅ / ❌

**Success condition**: All evals marked ✅

* * *

## Step 5: Reflection — Why Was This Faster?

Now comes the insight: pause and measure what just happened.

### Comparing Two Experiences

**Lesson 8 (First Section from Scratch)**

You had to:

1.  Learn research paper specification structure
2.  Discover what "quality academic writing" means in context
3.  Write detailed implementation plan
4.  Troubleshoot tone and clarity issues
5.  Learn how to validate claims against sources
6.  Iterate when first draft wasn't quite right
7.  Test integration with paper structure

**Result**: Comprehensive understanding of academic writing, but time-consuming (3.5 hours).

**Lesson 11 (Second Section with Skill)**

You only had to:

1.  Write specification (15 min)
2.  Reference existing skill
3.  Run `/sp.implement` with skill reference (30 min)
4.  Validate output (15 min)

**Result**: Main body section written, faster, using intelligence you built (70 minutes).

### The Acceleration Hypothesis

Why was this faster? Document your observations:

```
## Intelligence Acceleration - Reflection### Time Comparison- **Lesson 8 (first section from scratch)**: ~3.5 hours- **Lesson 11 (second section with skill)**: ~70 minutes- **Time savings**: ~2 hours 20 minutes (65% reduction)### Why It Was Faster1. **Specification was simpler** — Upstream complexity handled by skill2. **Skill encoded patterns** — No discovery needed (academic structure, tone standards, evidence validation)3. **Composition worked** — Reused writing intelligence instead of inventing approach4. **Fewer decisions** — Skill Persona + Questions meant fewer "how should I structure this?" moments### What Came from Skill vs from Scratch- **From `section-writer` skill**: Academic writing patterns, claim development structure, evidence integration, tone consistency, quality validation- **From scratch** (minimal): Only how this specific main body maps to your paper outline### Next Paper (Hypothetical)If you wrote another research paper next month:- **Without skill**: 3+ hours per section (similar to first time)- **With refined skill**: 45 minutes per section (skill improved, patterns reinforced)### The Compounding Effect- **Paper 1**: 3.5 hours per section (build intelligence)- **Paper 2**: 1 hour per section (use intelligence)- **Paper 3**: 45 min per section (intelligence refined)- **Paper 5**: 30 min per section (mastered, patterns automated)**The math of intelligence accumulation**: Each new project takes progressively less time because you're not rediscovering patterns—you're applying known solutions at increasing velocity.### Skills as YOUR Assets- **Code library**: Reusable technical solutions (functions, classes, frameworks)- **Intelligence skills**: YOUR reasoning frameworks and domain knowledge, saved as P+Q+P files- **Your advantage**: You're building a library of *thinking*, not just codeThis is how YOU scale your expertise: by encoding patterns as reusable intelligence that YOU invoke across future projects.
```

**Stop here and reflect**: What surprised you about the time difference? What did the skill actually buy you? What would change if you needed to write 10 more sections using this approach? Write 2-3 sentences in your own reflection document.

* * *

## Step 6: The Portfolio Value of Your Skills

You now have two documented skills:

1.  **`section-writer` skill** — Encodes academic writing patterns, claim development, evidence integration, tone consistency, quality validation
2.  **Future skills** — Any patterns you encode from this project

### What Makes These Skills Valuable

**To yourself**:

-   Next paper takes 50% less time
-   Next ten papers compound benefits (each faster)
-   Future writing projects start with foundation, not zero

**To a team**:

-   New team members inherit your writing standards
-   Specifications become templates others can reuse
-   Reasoning frameworks spread consistency

**To clients or organizations**:

-   Writing velocity multiplies across projects
-   Quality standards are codified, not dependent on individual skill
-   Knowledge doesn't leave when people do

### Measuring Skill Value

You can articulate the value of your `section-writer` skill in concrete terms:

**Time savings**:

-   First paper: 3.5 hours per section
-   Subsequent papers: 1.25 hours per section (65% reduction)
-   10-paper project: Save ~23 hours using this one skill

**Quality consistency**:

-   Patterns are encoded (not rediscovered with each paper)
-   Standards are applied consistently (not dependent on mood or fatigue)
-   Knowledge accumulates (second paper better than first)

**Organizational knowledge**:

-   Specification becomes template
-   Skill becomes reference implementation
-   Patterns become organization standard

This is why SDD-RI matters: not because it produces code faster, but because it compounds intelligence. Each pattern you encode makes your team exponentially more capable.

* * *

## Chapter 13 Complete Validation Checklist

You've completed Chapter 13. Verify you have:

### ✅ Projects Completed

-    **First paper section (introduction)** — Completed in Lesson 8, validated against spec
-    **Second paper section (main body)** — Completed in Lesson 11 using skill reuse
-    **Skills created** — `section-writer` skill (Lesson 9), possibly others

### ✅ Documentation Complete

-    **Constitution file** — `specs/paper-project-constitution.md` defines quality standards
-    **Introduction specification** — `specs/paper-project/introduction.md` completed in Lesson 4
-    **Main body specification** — `specs/paper-project/main-body-section.md` completed in this lesson
-    **Specifications refined** — Both specs passed `/sp.clarify` validation (Lesson 5)
-    **Implementation plans** — Detailed approach for each section
-    **Task breakdowns** — Atomic work units for each phase

### ✅ Skills Documented

-    **`section-writer` skill** — Persona + Questions + Principles for academic writing
-    **Skill metadata** — Proficiency levels, decision frameworks, reasoning principles documented
-    **Skill reuse applied** — Second section explicitly used skill from Lesson 9

### ✅ Intelligence Demonstrated

-    **Acceleration measured** — Lesson 8 timeline (3.5 hours) vs Lesson 11 (70 minutes) documented
-    **Skill reuse applied** — `/sp.implement` explicitly referenced `section-writer` skill
-    **Composition proven** — Main body section used writing intelligence without reinvention
-    **Compounding recognized** — Reflection on how future papers accelerate beyond current one

### ✅ Portfolio-Ready Project

-    **Paper sections complete** — At minimum: introduction + main body (core argument)
-    **Skills documented** — Could explain them to another developer
-    **Specification files** — Show your thinking (specification primacy)
-    **Timeline evidence** — Can demonstrate intelligence acceleration to others

**All boxes checked?** You've completed the full SDD-RI cycle. You have:

-   **Theory** (Chapter 12)
-   **Practice** (Chapter 13, Lessons 1-10)
-   **Application** (Chapter 13, Lesson 11 - this capstone with skill reuse)
-   **Reusable Intelligence** (Documented skills from Lessons 3, 6, 9)
-   **Measurable Acceleration** (Evidence that Project 2 is faster than Project 1)

You're now positioned to approach any new writing project with composition-first thinking instead of build-from-scratch thinking.

* * *

## Try With AI

**Setup**: Open your AI companion (Claude Code, Gemini, or ChatGPT). You're going to reflect on your skill library and plan future projects.

**Prompt Set**:

```
Prompt 1 (Portfolio Recognition):"I completed a research paper using SDD-RI workflow and created a reusable `section-writer` skill.In plain language: What kinds of future writing projects could I tackle faster using this skill?What if I combined this skill with a `research-validator` skill (to fact-check claims)?What would my skill library look like after 5 more papers?"Prompt 2 (Acceleration Measurement):"I spent 3.5 hours writing my first paper section (Lesson 8).I spent 70 minutes writing my second section using the section-writer skill (Lesson 11).That's a 65% time savings.What should I be measuring to prove that intelligence accumulation is real?If I write 5 more papers using this skill: What would my velocity look like?How would I show this improvement to a potential employer or client?"Prompt 3 (Skill Compounding):"If I followed the SDD-RI approach for 10 writing projects over the next year:- What would my skill library look like?- How would my writing velocity compound?- At what point would I be writing papers faster than competitors?- What's the long-term ROI of building reusable intelligence vs writing one-off papers?"
```

**Expected Outcomes**:

-   **Prompt 1**: AI should help you envision future projects where your skills provide leverage (client papers, research projects, content creation, technical writing)
-   **Prompt 2**: AI should highlight what makes intelligence valuable (pattern reuse, decision framework sharing, quality consistency, reproducibility)
-   **Prompt 3**: AI should demonstrate exponential returns from intelligence accumulation (skills compound across projects, velocity multiplies with each iteration)

**Safety Note**: When you discuss your writing project or future client work, remember that you've built this using specifications and skills as the foundation. Credit the methodology. You didn't use AI to write the entire paper—you used AI to *accelerate* structured thinking with documented specifications and reusable intelligence.

**Optional Stretch**: Now that you have a reusable skill, find a real writing project (research paper for a client, technical documentation, proposal, blog series). Write a specification for that project. Estimate how long it would take you to execute using your `section-writer` skill. Then, using your skill, actually write that project. This is how writers monetize their intelligence accumulation: by solving client problems faster than competitors.

* * *

**Chapter 13 is now complete.** You've demonstrated full SDD-RI mastery—from specification to implementation to reusable intelligence to accelerated execution.

You're ready for more complex projects. Your skills compound. Your intelligence library grows. Your development velocity increases exponentially.

This is the power of SDD-RI.

# Capstone — Intelligence Acceleration

This capstone proves that skill reuse accelerates work. By writing a second paper section using the `section-writer` skill YOU created in Lesson 9, you demonstrate measurable acceleration: the second section takes 70 minutes instead of 3.5 hours. This is not just about speed—it's about understanding how YOUR skill enables velocity gains. You'll measure this acceleration concretely, recognize why it happens, and understand how skills become valuable assets. This lesson answers the central question: Can you complete a task faster using a skill you've built? The answer is yes, and you'll have the data to prove it.

## Mental Models

-   **Skill-Based Acceleration**: Each skill YOU create encodes patterns into reusable SKILL.md format (at `.claude/skills/<skill-name>/SKILL.md`). The second task using that skill doesn't rediscover patterns—AI discovers and applies them. Lesson 8 takes 3.5 hours from scratch; Lesson 11 takes 70 minutes because AI finds and follows YOUR skill. This is reasoning reuse—YOUR documented workflows applied at increasing velocity.
    
-   **Specification Simplification Through Skills**: When you build the first section, your specification must detail all decision points. For the second section with YOUR skill, your specification shrinks to just intent, constraints, and success criteria. The upstream complexity—how to write academically, how to validate claims—is now encapsulated in YOUR skill that YOU invoke.
    
-   **Skills as YOUR Assets**: Traditional reuse focuses on code libraries. YOUR skills are different. Your `section-writer` skill (at `.claude/skills/section-writer/SKILL.md`) encodes your workflow, quality criteria, and process steps. When AI discovers this skill, it applies YOUR reasoning patterns.
    
-   **Skills vs PHRs**: PHRs are auto-created within a project and stay there (YOUR learning record). Skills are user-created after good sessions and can be invoked in future work. PHRs document what happened; Skills are active tools the agent uses.
    

## Key Patterns

-   **Acceleration Measurement**: Time tracking creates evidence. First section (Lesson 8): 3.5 hours from scratch. Second section (Lesson 11): 70 minutes using YOUR skill. This 65% time reduction proves that YOUR skill works.
    
-   **Skill Invocation**: When implementing, mention the skill and AI discovers it automatically through its description. The AI follows YOUR process steps and quality criteria from the SKILL.md file. YOU're not creating new reasoning patterns—YOU're applying YOUR proven patterns.
    
-   **Specification Simplification**: Compare your first spec (detailed everything) to your second spec (simpler). Why? YOUR skill already solved "how to structure academic writing." Your new specification just names what success looks like—YOUR skill handles how.
    
-   **Reflection-Driven Insight**: Pause and document why acceleration happened. What patterns did YOUR skill encode? What decisions did YOU not have to make because the skill handled them? This reflection embeds understanding of why skills compound.
    

## Common Mistakes

-   **Confusing Speed with Skill Benefit**: The mistake is thinking Lesson 11 is faster just because you're experienced. Without YOUR skill, the second section would still take 2-3 hours. With YOUR skill, it takes 70 minutes. The difference is YOUR skill, not just experience.
    
-   **Creating Skills Too Specific**: Build skills that are domain-general (`section-writer` for any academic writing), not domain-specific ("climate change research skill"). Domain-general skills work across future projects.
    
-   **Skipping Reflection**: The real learning happens when YOU document why the second section was faster. By measuring and articulating acceleration, YOU embed understanding of why skills work.
    
-   **Not Invoking Skills Explicitly**: Skills don't apply automatically. YOU must invoke them. YOU tell the AI "use my section-writer skill" and provide the skill content.
    

## Progression Context

-   **Builds on**:
    
    -   Lesson 3: Constitution (quality standards)
    -   Lesson 4: First specification (becomes foundation)
    -   Lessons 6-8: Planning, tasks, implementation (where patterns emerged)
    -   Lesson 9: Skill creation (where YOU built the section-writer skill)
    -   Lesson 10: Brownfield adoption theory
-   **Leads to**:
    
    -   **Future Projects**: YOU invoke YOUR skill on similar tasks
    -   **Skill Library Growth**: YOU create more skills as YOU recognize patterns worth encoding
    -   **Team Value**: YOUR skills can help team members if YOU share them
    -   **Competitive Advantage**: YOUR skill library makes YOU faster than starting from scratch

## Study Mode

Teaching by Socratic Method (OpenAI Study Mode & Google Extended Learning)

📚Socratic Teaching - AI guides you with questions

### Ready to Learn

Click the Teach button to get a guided explanation of this lesson from the book.

---
Source: https://agentfactory.panaversity.org/docs/SDD-RI-Fundamentals/spec-kit-plus-hands-on/capstone