# Physical AI & Humanoid Robotics Textbook - Project Constitution

**Project:** AI-Native Textbook with RAG Chatbot for Humanoid Robotics Education  
**Deadline:** November 30, 2025 at 6:00 PM  
**Maximum Points:** 400 (100 base + 300 bonus)

---

## 🎯 Core Principles

### 1. **Specification-Driven Development**
- All work starts with written specifications using Spec-Kit Plus
- Constitution → Specification → Planning → Tasks → Implementation
- Every feature justified by specification before coding
- Specifications are testable and measurable

### 2. **Educational Excellence**
- Content must be accurate and verified against official documentation
- All code examples must run without errors
- Complexity progresses logically (basics to advanced)
- Accessible to learners with varying backgrounds

### 3. **User-Centric Design**
- Chatbot understands user intent and provides context
- Authentication enables personalization
- UI/UX is intuitive and responsive
- Text selection queries work seamlessly

### 4. **Production Readiness**
- Code is production-grade (not prototype)
- All endpoints documented and tested
- Error handling covers edge cases
- Chatbot response time < 3 seconds
- Database secure and optimized

### 5. **Composability & Reusability**
- Claude Code Subagents encapsulate specialized tasks
- Agent Skills documented and reusable
- Code components composable
- Database schema extensible

---

## 📋 Quality Standards (Testable Criteria)

### A. **Content Writing Standards**
- [ ] **Accuracy**: All claims verified against official docs (ROS 2, Isaac, Gazebo)
- [ ] **Clarity**: Flesch-Kincaid Grade 10-12, active voice >75%, terms defined
- [ ] **Completeness**: Learning objectives, concepts, 2+ code examples, exercises, assessments
- [ ] **Code Quality**: Runs without errors, PEP 8 compliant, commented, dependencies listed
- [ ] **Sourcing**: All claims traceable, APA citations, peer-reviewed sources preferred

### B. **Backend API Standards**
- [ ] **Documentation**: OpenAPI schema, error codes, examples, auth requirements
- [ ] **Validation**: Pydantic models, range checks, format validation, clear errors
- [ ] **Performance**: <3 sec for chat, <1 sec for search, proper indexing
- [ ] **Security**: CORS configured, SQL injection prevented, no hardcoded secrets
- [ ] **Testing**: 80% coverage, unit/integration/error scenario tests

### C. **Database Standards**
- [ ] **Schema Design**: Normalized, foreign keys, indexes, documented
- [ ] **Vector Store**: Qdrant with 1536 dims, metadata stored, similarity tested
- [ ] **Data Integrity**: Transactions, constraints enforced, audit trails
- [ ] **Performance**: No N+1 queries, batch operations, connection pooling

### D. **RAG Chatbot Standards**
- [ ] **Retrieval**: >85% relevance, top results actually relevant, ranked properly
- [ ] **Generation**: >90% accuracy, cites sources, acknowledges uncertainty
- [ ] **UX**: <3 sec response, loading indicator, clear errors, context maintained
- [ ] **Edge Cases**: Off-topic handled, malformed queries graceful, empty input handled

### E. **Frontend Standards**
- [ ] **Responsiveness**: Mobile single column, tablet 2-col, desktop full layout
- [ ] **Accessibility**: WCAG 2.1 AA, 4.5:1 contrast, keyboard navigation, alt text
- [ ] **Performance**: <3 sec page load, <100ms interaction, optimized images
- [ ] **Browser Support**: Chrome 90+, Firefox 88+, Safari 14+, no console errors

### F. **Deployment Standards**
- [ ] **Reliability**: 99.5% uptime, graceful errors, monitoring, backups automated
- [ ] **Configuration**: Secrets in env vars, dev/prod configs, .env.example provided
- [ ] **Build**: GitHub Actions CI/CD, tests run first, linting passes, no warnings
- [ ] **Monitoring**: Error logging, performance tracking, uptime monitoring

---

## 🛠️ Technology Stack

### **Non-Negotiable**
- Frontend: Docusaurus 3+, React 18+, Tailwind CSS
- Backend: FastAPI, Python 3.10+, Uvicorn
- Database: Neon Postgres, Qdrant Cloud Free Tier
- AI: OpenAI API, OpenAI Embeddings, LangChain

### **Forbidden**
- ❌ Custom web framework (use FastAPI)
- ❌ SQLite (use Neon)
- ❌ Next.js/Nuxt (use Docusaurus)

---

## 📝 Coding Standards

### **Python**
- PEP 8 (Black formatter)
- Type hints on all functions
- Google-style docstrings
- No hardcoded secrets

### **JavaScript**
- ESLint compliant
- Prettier formatting
- Error boundaries in React
- No console.log in production

### **Git**
- Atomic commits with clear messages
- Feature branches
- PR reviews before merge
- Format: "type: description"

---

## ✅ Testing Requirements

- Backend: 80% line coverage minimum
- Critical paths: 100% coverage
- All API endpoints tested
- Integration tests for RAG
- Manual UI/UX testing

---

## 🏆 Success Criteria

### **Base Score (100 Points)**
- ✅ Complete 4-module book (20+ chapters)
- ✅ Functional RAG chatbot embedded
- ✅ Book publicly deployed
- ✅ Chatbot >85% accuracy
- ✅ Text selection queries work
- ✅ Code documented and tested

### **Bonus Features (50 Points Each)**
- ✅ Claude Code Subagents (+50)
- ✅ Authentication & profiles (+50)
- ✅ Content personalization (+50)
- ✅ Urdu translation (+50)

**Maximum: 400 Points**

---

## 📊 Key Metrics

| Metric | Target | Measure |
|--------|--------|---------|
| Content Accuracy | >95% | Manual review |
| Chatbot Relevance | >85% | Query testing |
| Test Coverage | >80% | pytest --cov |
| Response Time | <3 sec | Load testing |
| Page Load | <3 sec | Lighthouse |
| Availability | >99% | Monitoring |
| API Docs | 100% | Every endpoint |

---

## 🔒 Security Checklist

- [ ] No secrets in Git (.env files)
- [ ] SQL injection prevented
- [ ] XSS prevented
- [ ] CORS configured (not wildcard)
- [ ] HTTPS enabled
- [ ] Rate limiting implemented
- [ ] Passwords hashed (bcrypt)
- [ ] JWT validated
- [ ] Backups automated
- [ ] Error messages safe

---

## 📚 Documentation Required

- README with setup
- API docs (OpenAPI/Swagger)
- Database schema diagram
- Architecture diagram
- Deployment guide
- CONTRIBUTING.md
- CHANGELOG.md

---

## ⚠️ Common Violations

- ❌ Code without tests
- ❌ Hardcoded credentials
- ❌ No documentation
- ❌ Features without specs
- ❌ Chatbot hallucinations
- ❌ Broken code examples
- ❌ Missing citations
- ❌ Mobile UI broken
- ❌ Unhandled errors
- ❌ Performance degradation

---

**Status:** Active  
**Last Updated:** January 30, 2026  
**Review Cycle:** Every 2 weeks

**All team members agree to uphold this constitution.**

