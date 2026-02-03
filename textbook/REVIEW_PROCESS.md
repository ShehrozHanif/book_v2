# Expert Review Submission Workflow

**Document Purpose**: Define the review process for ensuring 95%+ accuracy before RAG indexing

**Spec**: 002-content-writing | **Date**: 2026-02-03 | **Status**: Active

---

## Overview

All textbook modules must undergo technical review before being indexed into the RAG knowledge base. This ensures factual accuracy, code quality, and consistency with official documentation.

**Review Standard**: 95%+ accuracy required for approval

**Review Options**:
1. **Expert Review** (preferred): Domain expert from flexible pool of 2-3 reviewers
2. **Peer Review Fallback**: Structured checklist-based review if expert unavailable

---

## Review Workflow

### 1. Chapter Submission

**Trigger**: Author completes all chapters in a module

**Prerequisites**:
- All chapters written and complete (within ±10% word count target)
- All code examples created and tested locally
- All references added to `textbook/metadata/references.json`
- Word count verification passed: `./scripts/verify-word-count.sh`
- Code examples tested: `./scripts/test-code-examples.sh`

**Action**: Author creates pull request with title format:
```
Module [N]: [Module Name] - Ready for Expert Review
```

**PR Description Must Include**:
- Module number and name
- Chapter count and total word count
- Code example count
- List of all chapter files
- Test results summary (word count + code verification)
- Any known issues or concerns

**Example PR**:
```markdown
## Module 1: Fundamentals - Ready for Expert Review

**Summary**:
- Module: 1 (Fundamentals of Humanoid Robotics)
- Chapters: 5 (Chapters 1-5)
- Total word count: 12,045 words
- Code examples: 15 (all tested, 100% pass rate)

**Chapter Files**:
- textbook/chapters/01-what-is-humanoid-robotics.md (2,310 words)
- textbook/chapters/02-kinematics-basics.md (2,405 words)
- textbook/chapters/03-dynamics-motion.md (2,390 words)
- textbook/chapters/04-sensors-perception.md (2,450 words)
- textbook/chapters/05-hardware-overview.md (2,490 words)

**Code Examples**: All 15 examples tested on Ubuntu 22.04 + ROS 2 Humble
- Verification: ./scripts/test-code-examples.sh
- Result: 15/15 PASS (100%)

**References**: 18 references added to references.json (APA format)

**Ready for**: Expert review by robotics fundamentals expert
```

---

### 2. Expert Assignment

**Timeline**: Within 12 hours of submission

**Responsible**: Project coordinator or lead writer

**Process**:
1. Check expert reviewer pool availability
2. Assign reviewer based on domain expertise:
   - **Module 1 (Fundamentals)**: Robotics fundamentals expert
   - **Module 2 (ROS 2 & Software Architecture)**: ROS 2 / software architecture expert
   - **Module 3 (Control & Kinematics)**: Control systems / kinematics expert
   - **Module 4 (Applications)**: Industry / applications expert

3. Send review request email:

**Email Template**:
```
Subject: Expert Review Request - Module [N]: [Module Name]

Hi [Reviewer Name],

We need your expert review for Module [N] of the Humanoid Robotics textbook.

Module: [N] - [Module Name]
Chapters: [X] chapters, [XXXX] words
Code Examples: [XX] examples
Timeline: 24-48 hours preferred

Review Template: textbook/metadata/expert-review-template.json
Pull Request: [PR Link]

Please review for:
- Factual accuracy (95%+ required)
- Code correctness (all examples must execute)
- Clarity and technical depth
- Reference completeness

Thank you!
```

**Fallback Trigger**: If expert does not respond within 12 hours, trigger peer review fallback (see Section 5)

---

### 3. Expert Review Checklist

**Timeline**: 24-48 hours from assignment

**Reviewer Actions**:

#### 3.1 Factual Accuracy Check
- [ ] Cross-check all technical claims against official documentation:
  - ROS 2 Humble official docs
  - Gazebo 11 documentation
  - Robotics textbooks (Siciliano et al., "Robotics: Modelling, Planning and Control")
  - Manufacturer datasheets (for hardware specifications)
- [ ] Verify mathematical formulas match standard references
- [ ] Confirm algorithm descriptions are accurate
- [ ] Check version numbers are specified (ROS 2 Humble, Gazebo 11, Python 3.10+, Ubuntu 22.04)

#### 3.2 Code Quality Check
- [ ] Test all code examples on Ubuntu 22.04 + ROS 2 Humble LTS
- [ ] Verify code follows ROS 2 coding standards
- [ ] Check comments explain key functionality
- [ ] Confirm dependencies are documented
- [ ] Validate URDF/YAML syntax
- [ ] Test simulation examples (Gazebo)

#### 3.3 Clarity & Completeness Check
- [ ] Learning objectives are clear and testable
- [ ] Concepts are explained at appropriate level (undergraduate/early professional)
- [ ] Examples are relevant and well-explained
- [ ] References are complete and properly formatted (APA)
- [ ] No undefined jargon or missing context

#### 3.4 Consistency Check
- [ ] Terminology consistent across chapters
- [ ] Code style consistent with earlier modules
- [ ] Chapter structure follows template
- [ ] Word count within target range (2,300-2,400 per chapter)

---

### 4. Review Feedback Submission

**Format**: Use expert review template at `textbook/metadata/expert-review-template.json`

**Fields**:
```json
{
  "module_id": "module_01",
  "reviewer_name": "Dr. Jane Smith",
  "reviewer_expertise": "Humanoid Robotics",
  "review_date": "2026-02-03",
  "accuracy_score": 96,
  "clarity_score": 92,
  "completeness_score": 94,
  "code_quality_score": 98,
  "overall_score": 95,
  "flagged_issues": [
    {
      "chapter_id": "01",
      "section": "Introduction",
      "line": 42,
      "severity": "high|medium|low",
      "issue_type": "factual|clarity|code|reference",
      "description": "Claim about DH parameters needs citation",
      "suggested_fix": "Add reference to Denavit-Hartenberg 1955 paper"
    }
  ],
  "status": "approved|needs_revision",
  "comments": "Overall excellent module. Minor citation issues to resolve."
}
```

**Severity Levels**:
- **High**: Factual error, broken code, missing critical content (blocks approval)
- **Medium**: Clarity issue, minor inaccuracy, missing reference (should fix before indexing)
- **Low**: Style suggestion, optional enhancement (can defer)

**Approval Criteria**:
- Overall score ≥ 95%
- No high-severity issues unresolved
- All code examples execute correctly
- All factual claims traceable to references

---

### 5. Peer Review Fallback

**Trigger**: Expert reviewer unavailable >12 hours or pool exhausted

**Process**: Two reviewers (another writer + engineer) complete structured peer-review checklist

**Checklist**: See `textbook/metadata/peer-review-checklist.md`

**Peer Review Checklist** (abbreviated):
- [ ] All chapters follow template structure
- [ ] Learning objectives present and clear
- [ ] Code examples run without errors (tested locally)
- [ ] References exist in `references.json` for all citations
- [ ] Word count within ±10% of target
- [ ] No obvious factual errors (spot-check 5-10 key claims against official docs)
- [ ] Terminology consistent
- [ ] No broken links or missing files

**Acceptance**: Peer review satisfies minimum quality gate; expert review preferred but not blocking

**Scoring**: Peer review assigns pass/needs-revision; does not compute accuracy score (assumes 90%+ if pass)

---

### 6. Issue Resolution

**Timeline**: 24 hours after review feedback received

**Author Actions**:
1. Review all flagged issues in expert review JSON
2. Prioritize by severity (high → medium → low)
3. Resolve each issue:
   - **Factual errors**: Correct and add proper citation
   - **Code errors**: Fix and re-test locally + CI/CD
   - **Clarity issues**: Rewrite for better understanding
   - **Missing references**: Add to `references.json` and cite in text
4. Update PR with resolution summary
5. Re-run verification scripts:
   ```bash
   ./scripts/verify-word-count.sh
   ./scripts/test-code-examples.sh
   ./scripts/validate-references.sh
   ```
6. Request re-review if high-severity issues resolved

**Resolution Summary Format**:
```markdown
## Issue Resolution Summary

**High Severity** (3 issues):
- [x] Chapter 01, Line 42: Added citation to DH parameters
- [x] Chapter 03, Example 02: Fixed balance calculation error
- [x] Chapter 05: Added missing power system reference

**Medium Severity** (5 issues):
- [x] Chapter 02: Clarified Jacobian matrix explanation
- [x] Chapter 04: Improved sensor data visualization example
- ...

**Low Severity** (2 issues):
- [ ] Deferred: Chapter 01 style suggestion (post-hackathon)
- [x] Chapter 05: Fixed typo

**Re-test Results**:
- Word count: PASS (12,045 words, ±2% target)
- Code examples: 15/15 PASS
- References: 20/20 valid

**Ready for**: Approval and indexing
```

---

### 7. Approval for Indexing

**Trigger**: All issues resolved, reviewer confirms approval

**Reviewer Actions**:
1. Verify all flagged issues resolved
2. Re-test any modified code examples
3. Update review JSON with:
   ```json
   {
     "status": "approved",
     "approval_date": "2026-02-05",
     "final_accuracy_score": 97,
     "notes": "All issues resolved. Ready for RAG indexing."
   }
   ```
4. Add comment to PR: "APPROVED FOR INDEXING"

**Project Coordinator Actions**:
1. Merge PR to main branch
2. Generate RAG metadata:
   ```bash
   ./scripts/generate-rag-metadata.sh --all
   ```
3. Submit module to RAG indexing pipeline (coordinate with Spec 001 team)
4. Update module status in `textbook/metadata/module-index.json`:
   ```json
   {
     "module_id": "module_01",
     "status": "approved_for_indexing",
     "approval_date": "2026-02-05",
     "indexed_date": "pending"
   }
   ```

---

### 8. RAG Indexing Validation

**Timeline**: Within 24 hours of indexing submission

**Process**:
1. Wait for RAG indexing to complete (Spec 001 team)
2. Run validation queries on RAG chatbot (10 sample queries per module)
3. Verify retrieval accuracy:
   - Relevant sections retrieved (>80% relevance)
   - Correct chapter/section citations
   - Confidence scores >0.7
4. Document validation results:
   ```json
   {
     "module_id": "module_01",
     "indexed_date": "2026-02-06",
     "validation_queries": 10,
     "successful_retrievals": 9,
     "retrieval_accuracy": 90,
     "status": "indexed_and_validated"
   }
   ```
5. Update `module-index.json` with indexed status

**Sample Validation Queries** (Module 1 example):
- "What is forward kinematics?"
- "How do humanoid robots maintain balance?"
- "Explain IMU sensors in robotics"
- "What are the main hardware components of a humanoid robot?"
- "Describe the history of humanoid robotics"

---

## Review Timeline

| Stage | Timeline | Responsible |
|-------|----------|-------------|
| Chapter Submission | After module complete | Author |
| Expert Assignment | <12 hours | Coordinator |
| Expert Review | 24-48 hours | Expert Reviewer |
| Issue Resolution | <24 hours | Author |
| Re-review (if needed) | 12-24 hours | Expert Reviewer |
| Approval | After resolution | Expert Reviewer |
| RAG Metadata Generation | <1 hour | Coordinator |
| RAG Indexing | 24-48 hours | Spec 001 Team |
| Validation | <24 hours | Coordinator |

**Total Module Review Cycle**: 3-5 days from submission to indexed

---

## Roles & Responsibilities

### Author (Writer)
- Complete all chapters and code examples
- Test code locally before submission
- Submit PR with complete documentation
- Resolve all review issues within 24 hours
- Re-test after changes

### Expert Reviewer (Domain Expert)
- Review module within 24-48 hours
- Test all code examples
- Cross-check facts against official docs
- Assign accuracy score (95%+ required)
- Approve or request revisions

### Peer Reviewers (Fallback)
- Complete structured checklist within 24 hours
- Test code examples
- Spot-check facts (5-10 key claims)
- Assign pass/needs-revision

### Project Coordinator
- Assign expert reviewers
- Trigger fallback if needed
- Generate RAG metadata
- Submit to indexing pipeline
- Validate retrieval

---

## Expert Reviewer Pool

**Module 1 (Fundamentals)**:
- Primary: Dr. [Expert Name] (Robotics Fundamentals)
- Backup: Dr. [Expert Name] (Kinematics)

**Module 2 (ROS 2 & Software Architecture)**:
- Primary: [Engineer Name] (ROS 2 Expert)
- Backup: [Engineer Name] (Software Architecture)

**Module 3 (Control & Kinematics)**:
- Primary: Dr. [Expert Name] (Control Systems)
- Backup: Dr. [Expert Name] (Kinematics)

**Module 4 (Applications)**:
- Primary: [Industry Expert] (Humanoid Robotics Applications)
- Backup: Reuse Module 1 expert

**Fallback**: Peer review team (Writer + Engineer)

---

## Quality Gates

**Gate 1: Submission Check**
- [ ] All chapters complete (word count within ±10%)
- [ ] All code examples tested locally (100% pass)
- [ ] All references validated
- [ ] PR created with complete documentation

**Gate 2: Expert Review**
- [ ] Accuracy score ≥95%
- [ ] All code examples execute on test environment
- [ ] All factual claims traceable to references
- [ ] No high-severity issues unresolved

**Gate 3: Approval**
- [ ] All review issues resolved
- [ ] Re-testing complete (if code modified)
- [ ] Reviewer confirms approval
- [ ] Status: "approved_for_indexing"

**Gate 4: RAG Validation**
- [ ] Module indexed into Qdrant
- [ ] Validation queries successful (>80% accuracy)
- [ ] Retrieval confidence >0.7
- [ ] Status: "indexed_and_validated"

---

## Common Issues & Resolutions

### Issue: Expert reviewer unavailable
**Resolution**: Trigger peer review fallback within 12 hours; structured checklist ensures quality

### Issue: Code example fails in CI/CD but works locally
**Resolution**: Check environment differences (ROS 2 version, dependencies); update example or document environment-specific notes

### Issue: Accuracy score <95%
**Resolution**: Author resolves flagged issues; re-review required; may need additional citations or corrections

### Issue: Timeline slips beyond 48 hours
**Resolution**: Escalate to coordinator; consider peer review fallback or adjust module priority

### Issue: RAG retrieval validation fails
**Resolution**: Check metadata generation; verify learning objectives and keywords extracted correctly; regenerate metadata if needed

---

## Review Artifacts

**Generated Files**:
- `textbook/metadata/expert-review-template.json` (review schema)
- `textbook/metadata/peer-review-checklist.md` (fallback checklist)
- `textbook/metadata/module-index.json` (module status tracking)
- `textbook/metadata/rag-metadata.json` (RAG indexing metadata)

**Review Records** (per module):
- Expert review JSON file: `textbook/metadata/reviews/module_0X_review.json`
- Issue resolution summary (in PR)
- Validation results (in module-index.json)

---

## Contact

**Questions about review process**: Contact project coordinator

**Technical questions**: Contact Spec 001 (RAG chatbot) team for indexing pipeline issues

**Expert reviewer pool**: Maintained by project coordinator; flexible 2-3 person pool per module domain

---

**Document Status**: Active | **Last Updated**: 2026-02-03 | **Spec**: 002-content-writing
