# Quick Start: Writer Workflow

**Date**: 2026-01-31 | **Branch**: `002-content-writing` | **Phase**: 1

---

## Overview

This guide helps writers get started with the textbook writing workflow. It covers setup, chapter creation, code example testing, and review submission.

---

## Prerequisites

### System Requirements

- Ubuntu 22.04 LTS (or compatible Linux distribution)
- ROS 2 Humble LTS (for code example testing)
- Gazebo 11+ (for simulation examples)
- Python 3.10+
- C++17 compiler (g++ 9.4+)
- Git
- Docker (optional, for isolated CI/CD testing)

### Tools

- Text editor or IDE (VS Code, Vim, etc.)
- Markdown preview (built-in to most editors or online tools)
- Git CLI
- pytest (Python testing framework)

---

## Setup

### 1. Clone Repository & Setup Local Environment

```bash
# Clone the repository
git clone https://github.com/your-org/humanoid-robotics-textbook.git
cd humanoid-robotics-textbook

# Create a new branch for your work (replace INITIALS and CHAPTER with your details)
git checkout -b writing/INITIALS-chapter-XX

# Create Python virtual environment (recommended)
python3.10 -m venv venv
source venv/bin/activate

# Install Python dependencies for code example testing
pip install -r requirements-dev.txt  # pytest, ros2, etc.
```

### 2. Setup ROS 2 Humble Environment

```bash
# If ROS 2 is not installed, follow official installation guide:
# https://docs.ros.org/en/humble/Installation.html

# Verify ROS 2 is installed
ros2 --version
# Expected output: humble

# Source ROS 2 setup script (add to ~/.bashrc for persistent use)
source /opt/ros/humble/setup.bash
```

### 3. Review Chapter Template

```bash
# Open the master chapter template
cat textbook/chapters/_chapter-template.md

# Copy template to start a new chapter
cp textbook/chapters/_chapter-template.md textbook/chapters/XX-your-chapter-title.md
```

---

## Writing a Chapter

### Step 1: Create Chapter File with Metadata

Create a new markdown file in `textbook/chapters/` following the naming convention:

```bash
# Example: Chapter 1
vim textbook/chapters/01-what-is-humanoid-robotics.md
```

**File structure** (use template as starting point):

```markdown
---
id: chapter_01
module: 1
chapter: 1
title: What is a Humanoid Robot?
target_word_count: 2300
learning_objectives:
  - Understand the history and evolution of humanoid robotics
  - Identify key design paradigms and biomimetic principles
  - Recognize real-world applications across industries
code_examples:
  - chapter_01_example_01
  - chapter_01_example_02
references:
  - ref_001
  - ref_002
  - ref_003
---

# What is a Humanoid Robot?

[Content starts here...]
```

### Step 2: Write Chapter Content

**Structure** (following template):

1. **Introduction** (200-300 words)
   - Hook: Why does this topic matter?
   - Overview: What will reader learn?

2. **Key Concepts** (400-600 words each, 2-4 subsections)
   - Concept explanation
   - Real-world examples
   - Diagrams/visuals (markdown syntax or embedded images)

3. **Code Examples** (2-4 per chapter)
   - Link to code example files (see next section)
   - Explanation of what the code demonstrates
   - Key learning points from the code

4. **Summary** (200 words)
   - Recap of key takeaways
   - Bridge to next chapter (if applicable)

5. **References** (APA format, auto-generated from reference IDs)

### Step 3: Check Word Count

```bash
# Count words in your chapter
wc -w textbook/chapters/01-what-is-humanoid-robotics.md

# Target: 2300 ± 200 words (within ±10% of target)
```

### Step 4: Stage Chapter Changes

```bash
# Add chapter file to git
git add textbook/chapters/01-what-is-humanoid-robotics.md

# View changes
git diff --cached

# Commit with message indicating chapter is written (not indexed yet)
git commit -m "Write chapter 01: What is a Humanoid Robot?"
```

---

## Writing & Testing Code Examples

### Step 1: Create Code Example File

```bash
# Create example file in code-examples directory
vim textbook/code-examples/chapter_01_example_01.py
```

**File naming**: `chapter_XX_example_YY.ext`
- XX = chapter number (01-22)
- YY = example number (01-04)
- ext = file extension (py, cpp, urdf, yaml, sh)

**File structure** (Python example):

```python
#!/usr/bin/env python3
"""
Chapter 01, Example 01: Simple Robot URDF Description

This example demonstrates how to write a basic URDF file defining
a simple humanoid robot structure with links and joints.

Requirements:
  - ROS 2 Humble
  - urdf_parser Python library

ROS 2 Version: Humble LTS
Python Version: 3.10+
"""

import rclpy
from urdf_parser_py.urdf import URDF

def main():
    """Load and parse URDF file."""
    # Load robot description from URDF file
    robot = URDF.from_xml_file('robot.urdf')

    # Print robot information
    print(f"Robot name: {robot.name}")
    print(f"Number of links: {len(robot.links)}")
    print(f"Number of joints: {len(robot.joints)}")

    # Example: Access first joint
    if robot.joints:
        first_joint = robot.joints[0]
        print(f"First joint: {first_joint.name}")

if __name__ == '__main__':
    main()
```

### Step 2: Test Code Example Locally

```bash
# Navigate to code examples directory
cd textbook/code-examples

# Test Python example
python3 chapter_01_example_01.py

# Test C++ example (compile and run)
g++ -std=c++17 -o chapter_01_example_02 chapter_01_example_02.cpp
./chapter_01_example_02

# Test URDF example (validate syntax)
ros2 topic pub -1 /robot_description std_msgs/String "$(cat chapter_01_example_01.urdf)"

# Expected output: No errors; expected output (if applicable)
```

**Troubleshooting**:
- If imports fail: Verify ROS 2 environment is sourced and dependencies installed
- If compilation fails: Check C++ version (require C++17)
- If URDF validation fails: Use online URDF validator or check XML syntax

### Step 3: Document Code Example in Chapter

In your chapter markdown, link to the code example:

```markdown
## Code Examples

### Example 1: Simple Robot URDF Description

This example shows how to write a basic URDF file that describes a simple humanoid robot.

```xml
<!-- See textbook/code-examples/chapter_01_example_01.urdf -->
<robot name="simple_humanoid">
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.2 0.2 0.4"/>
      </geometry>
    </visual>
  </link>
</robot>
```

**Key Points**:
- URDF = Unified Robot Description Format (XML-based)
- `<robot name="...">` is the root element
- `<link>` defines a rigid body; `<joint>` connects links
- Gazebo simulator reads URDF to initialize robot model

For full working example, see `chapter_01_example_01.urdf`.
```

### Step 4: Commit Code Examples

```bash
# Add all code examples for your chapter
git add textbook/code-examples/chapter_01_example_*.py
git add textbook/code-examples/chapter_01_example_*.cpp
git add textbook/code-examples/chapter_01_example_*.urdf

# Commit with message
git commit -m "Add code examples for chapter 01"
```

---

## Managing References

### Step 1: Add Reference to Centralized Database

Edit `textbook/metadata/references.json`:

```json
{
  "ref_001": {
    "type": "official_docs",
    "title": "ROS 2 Humble Documentation",
    "url": "https://docs.ros.org/en/humble/",
    "version": "Humble LTS",
    "accessed_date": "2026-01-31",
    "apa_format": "ROS 2. (2024). ROS 2 Humble Documentation. Retrieved from https://docs.ros.org/en/humble/"
  }
}
```

### Step 2: Cite Reference in Chapter

In your chapter markdown:

```markdown
According to ROS 2 documentation, nodes are the fundamental building blocks
of ROS 2 systems (ROS 2, 2024). More information on nodes and topics can be
found in the official ROS 2 documentation.

## References

- ROS 2. (2024). ROS 2 Humble Documentation. Retrieved from https://docs.ros.org/en/humble/
```

---

## Submitting Chapter for Review

### Step 1: Verify All Requirements Met

Checklist before submitting:

- [ ] Chapter written and word count within ±10% of target (2300 words)
- [ ] All learning objectives addressed in content
- [ ] All 2-4 code examples written and tested locally (zero errors)
- [ ] All references added to `references.json` and cited in chapter
- [ ] No typos or grammatical errors (use spelling/grammar checker)
- [ ] Markdown formatting is valid (test in preview)
- [ ] Chapter file committed to git

### Step 2: Create Pull Request

```bash
# Push your chapter branch to remote
git push origin writing/INITIALS-chapter-XX

# Create pull request with title and description
# Title: "Write chapter XX: [Chapter Title]"
# Description:
#   - Chapter ID: chapter_XX
#   - Module: Module X
#   - Word count: XXXX words
#   - Code examples: XX examples (all tested)
#   - References: XX citations
#   - Status: Ready for expert review
```

### Step 3: Expert Review Process

**Expert reviewer** will:
1. Check factual accuracy against official documentation
2. Verify all code examples run correctly on Ubuntu 22.04 + ROS 2 Humble
3. Confirm references are valid and properly cited
4. Review clarity and completeness
5. Flag any issues (typos, errors, clarifications needed)

**Timeline**: Expert review typically takes 24-48 hours

**If flagged**:
- Review feedback in PR comments
- Make revisions to chapter and/or code examples
- Re-submit for review
- Process repeats until approved (accuracy_score ≥ 95)

**If approved**:
- Merge PR
- Chapter marked as "approved" in system
- Chapter ready for RAG indexing

---

## Week-by-Week Schedule

### Week 1: Module 1 (Fundamentals)

**Goal**: Write and verify 5 chapters, 15 code examples (12,000 words)

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Setup environment, review template & outline | Development environment ready, outline reviewed |
| 2 | Write Chapter 1 + 2 code examples | 2,300 words + 2 examples (tested locally) |
| 3 | Write Chapter 2 + 2 code examples | 2,300 words + 2 examples (tested locally) |
| 4 | Write Chapter 3 + 2 code examples | 2,400 words + 2 examples (tested locally) |
| 5 | Write Chapter 4 + 2 code examples | 2,400 words + 2 examples (tested locally) |
| 6 | Write Chapter 5 + 3 code examples | 2,300 words + 3 examples (tested locally) |
| 7 | Review feedback from experts; finalize & merge | Module 1 complete (12,000 words, all approved) |

**Parallel**: Expert reviewers provide feedback on chapters submitted on Days 2-6; author incorporates feedback during final review (Day 7).

### Week 2: Module 2 (ROS 2 & Software Architecture)

**Goal**: Write and verify 6 chapters, 18 code examples (13,000 words)

Same cadence as Week 1, chapters 6-11

### Week 3: Module 3 (Control & Kinematics)

**Goal**: Write and verify 6 chapters, 18 code examples (14,000 words)

Same cadence as Week 1, chapters 12-17

### Week 4: Module 4 (Applications) or Buffer

**Goal**: Write and verify 5 chapters, 15 code examples (13,000 words)

OR defer to post-hackathon if needed (Module 4 explicitly deferrable; Modules 1-3 = base 100 points)

---

## Troubleshooting

### Code Example Fails to Run Locally

**Issue**: `ImportError: No module named 'rclpy'` or similar

**Solution**:
1. Verify ROS 2 is installed: `ros2 --version`
2. Source ROS 2 setup: `source /opt/ros/humble/setup.bash`
3. Install missing dependency: `pip install rclpy` (or check apt packages: `apt search ros2-humble`)

### Word Count Too Low

**Issue**: Chapter is 1,800 words but target is 2,300

**Solution**:
1. Expand key concepts sections with more examples
2. Add more subsections (e.g., "Common Mistakes" or "Advanced Topics")
3. Include more diagrams/illustrations with captions
4. Add more code example explanations

### Expert Review Takes Too Long

**Issue**: Reviewer is unavailable for 48+ hours

**Solution**:
1. Fallback: Use peer-review checklist (another writer or engineer reviews)
2. Contact backup reviewer from pool (2-3 experts available)
3. Continue writing next chapter while review is in progress (parallel workflow)

### Git Merge Conflicts

**Issue**: Chapter file conflicts when pulling latest changes

**Solution**:
```bash
# Update your branch with latest main
git fetch origin
git rebase origin/main

# Resolve conflicts in editor (if any)
git add [resolved files]
git rebase --continue

# Force push if necessary (only for your branch, not main)
git push origin writing/INITIALS-chapter-XX --force
```

---

## Best Practices

### Writing

✅ **Do**:
- Use active voice ("Robots can manipulate objects" vs. "Objects can be manipulated by robots")
- Define technical terms on first use
- Include concrete examples (not just abstract concepts)
- Link to official documentation for deep dives

❌ **Don't**:
- Copy-paste from Wikipedia or other sources without attribution
- Make claims without citing sources
- Use overly complex language; target Grade 10-12 reading level
- Leave broken code examples or links

### Code Examples

✅ **Do**:
- Test every example locally before committing
- Include comments explaining key lines
- Show both correct usage AND common mistakes
- Use standard naming conventions (PEP 8 for Python, Google style for C++)

❌ **Don't**:
- Copy-paste code from Stack Overflow without understanding it
- Write overly long examples (>100 lines); break into smaller chunks
- Leave debug statements or TODO comments in production examples
- Use deprecated ROS 2 APIs (verify against Humble LTS docs)

### References

✅ **Do**:
- Use official documentation (ROS 2 docs, Gazebo docs, manufacturer specs)
- Include access dates for web sources
- Use APA format consistently
- Verify all URLs return 200 OK

❌ **Don't**:
- Cite blog posts instead of official sources (unless necessary)
- Use broken links or outdated documentation
- Mix citation formats (stick to APA)
- Cite sources you haven't actually read

---

## Next Steps After Chapter Approval

Once your chapter is approved and merged:

1. **Await RAG Indexing**: Approved chapters are indexed into Qdrant vector store
2. **Validation**: Test RAG chatbot retrieval for your chapter
3. **Move to Next Chapter**: Continue writing next chapters in module

---

**Status**: Quick Start Guide Complete | Ready for Writer Onboarding

