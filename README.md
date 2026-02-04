# Physical AI & Humanoid Robotics Textbook - Hackathon Project

## 📚 Project Overview

This is a hackathon project to create a comprehensive, AI-native textbook for teaching **Physical AI & Humanoid Robotics**. The textbook will be built using modern web technologies, deployed to GitHub Pages, and enhanced with an intelligent RAG-powered chatbot for interactive learning.

**Timeline:** Submission Deadline: **November 30, 2025 at 6:00 PM**

---

## 🎯 Core Requirements

### 1. **AI/Spec-Driven Book Creation** (Base: 100 Points)
- [ ] Create a textbook using **Docusaurus** framework
- [ ] Structure content according to the 4-module course curriculum
- [ ] Deploy to **GitHub Pages** or **Vercel**
- [ ] Use **Spec-Kit Plus** for structured specification and planning
- [ ] Use **Claude Code** to write and manage the book content

### 2. **Integrated RAG Chatbot** (Base: 100 Points)
- [ ] Build a Retrieval-Augmented Generation (RAG) chatbot
- [ ] Embed chatbot within the published book
- [ ] Chatbot must answer questions based on book content
- [ ] Support text selection-based queries
- [ ] **Tech Stack:**
  - OpenAI Agents / ChatKit SDKs
  - FastAPI (backend)
  - Neon Serverless Postgres (database)
  - Qdrant Cloud Free Tier (vector embeddings)

### 3. **Bonus Features** (Up to 50 Points Each)

#### 3a. **Reusable Intelligence via Claude Code Subagents** (+50 Points)
- [ ] Create Claude Code Subagents for specialized tasks
- [ ] Develop Agent Skills for reusable intelligence
- [ ] Document how agents are used in the book project

#### 3b. **Authentication & User Profiling** (+50 Points)
- [ ] Implement Signup/Signin using **better-auth.com**
- [ ] Collect user background (software/hardware knowledge)
- [ ] Store user profiles in database
- [ ] Use profile data for personalization

#### 3c. **Content Personalization** (+50 Points)
- [ ] Add personalization button at chapter start
- [ ] Customize content based on user background
- [ ] Adjust difficulty level and examples per user profile
- [ ] Save personalization preferences

#### 3d. **Urdu Language Translation** (+50 Points)
- [ ] Add translation button at chapter start
- [ ] Implement real-time translation to Urdu
- [ ] Ensure technical terminology is properly translated
- [ ] Support bilingual reading experience

---

## 📖 Course Content Structure (4 Modules)

### **Module 1: The Robotic Nervous System (ROS 2)**
- What is Physical AI and embodied intelligence?
- ROS 2 architecture and core concepts
- Nodes, Topics, and Services
- Building ROS 2 packages with Python
- Integration with Python agents (rclpy)
- URDF format for humanoid description
- Launch files and parameter management

### **Module 2: The Digital Twin (Gazebo & Unity)**
- Gazebo simulation environment setup
- Physics simulation (gravity, collisions)
- URDF and SDF robot description formats
- Sensor simulation (LiDAR, Depth Cameras, IMUs)
- Unity for high-fidelity rendering
- Human-robot interaction simulation

### **Module 3: The AI-Robot Brain (NVIDIA Isaac)**
- NVIDIA Isaac SDK and Isaac Sim
- Photorealistic simulation and synthetic data generation
- Isaac ROS and Visual SLAM (VSLAM)
- Hardware-accelerated perception
- Nav2 path planning for bipedal movement
- Reinforcement learning for robot control
- Sim-to-real transfer techniques

### **Module 4: Vision-Language-Action (VLA)**
- Convergence of LLMs and Robotics
- Voice-to-Action using OpenAI Whisper
- Natural language to ROS 2 actions
- Multi-modal interaction (speech, gesture, vision)
- Capstone: Autonomous Humanoid Robot
- Real-world deployment examples

---

## 🛠️ Technology Stack Required

### **Frontend & Deployment**
- **Docusaurus 3+** - Static site generator for documentation
- **React** - Interactive components
- **Tailwind CSS** or Bootstrap - Styling
- **GitHub Pages** or **Vercel** - Deployment platform

### **Backend & APIs**
- **FastAPI** - High-performance Python web framework
- **Python 3.10+** - Backend language
- **CORS enabled** - For chatbot requests

### **AI & Language Model**
- **OpenAI API** - GPT models for chatbot
- **OpenAI Whisper** - Speech-to-text (for voice commands)
- **LangChain or similar** - RAG orchestration

### **Database & Vector Storage**
- **Neon Serverless Postgres** - Relational database
- **Qdrant Cloud Free Tier** - Vector database for embeddings
- **pgvector** - PostgreSQL extension for vectors

### **Authentication**
- **better-auth.com** - Authentication and user management
- **JWT tokens** - Session management

### **Development & Deployment Tools**
- **Claude Code** - AI coding assistant
- **Spec-Kit Plus** - Specification and planning
- **Git & GitHub** - Version control
- **Docker** (optional) - For containerization
- **GitHub Actions** (optional) - For CI/CD

### **AI Development**
- **Claude Code Subagents** - For specialized tasks
- **Agent Skills** - For reusable intelligence
- **MCP (Model Context Protocol)** - For tool integration

---

## 📋 Step-by-Step Implementation Plan

### **Phase 1: Setup & Planning (Week 1)**

1. **Initialize Project Structure**
   - [ ] Create GitHub repository
   - [ ] Set up Spec-Kit Plus workspace
   - [ ] Initialize Docusaurus project
   - [ ] Create documentation folder structure

2. **Write Specifications**
   - [ ] Create `spec.md` for book requirements
   - [ ] Define chatbot specifications
   - [ ] Plan database schema
   - [ ] Document API contracts

3. **Architecture Planning**
   - [ ] Create `plan.md` for implementation strategy
   - [ ] Design book structure and navigation
   - [ ] Plan chatbot architecture
   - [ ] Design database schema and API endpoints

### **Phase 2: Core Book Creation (Week 2-3)**

1. **Docusaurus Setup**
   - [ ] Configure Docusaurus with theme customization
   - [ ] Set up sidebar navigation
   - [ ] Create documentation structure

2. **Write Module 1: ROS 2**
   - [ ] Fundamentals and core concepts
   - [ ] Practical examples and code snippets
   - [ ] Hands-on exercises
   - [ ] Assessment questionsn

3. **Write Module 2: Gazebo & Unity**
   - [ ] Simulation fundamentals
   - [ ] URDF and SDF formats
   - [ ] Practical simulation projects
   - [ ] Visualization in Unity

4. **Write Module 3: NVIDIA Isaac**
   - [ ] Isaac SDK overview
   - [ ] Perception pipelines
   - [ ] Training and deployment
   - [ ] Real-world applications

5. **Write Module 4: Vision-Language-Action**
   - [ ] LLM integration with robotics
   - [ ] Voice commands and Whisper
   - [ ] Capstone project details
   - [ ] Deployment strategies

### **Phase 3: Backend & Database Setup (Week 4)**

1. **FastAPI Setup**
   - [ ] Initialize FastAPI project
   - [ ] Create project structure
   - [ ] Configure CORS for frontend
   - [ ] Set up logging and error handling

2. **Neon Postgres Database**
   - [ ] Create Neon database instance
   - [ ] Define user, chapter, and session tables
   - [ ] Set up pgvector extension
   - [ ] Create indexes for performance

3. **Qdrant Vector Database**
   - [ ] Set up Qdrant Cloud account (Free Tier)
   - [ ] Create collection for book embeddings
   - [ ] Configure vector dimensions (1536 for OpenAI)
   - [ ] Test connection from backend

4. **API Endpoints Development**
   - [ ] `/chat` - Send queries to chatbot
   - [ ] `/embed-query` - Get embeddings for queries
   - [ ] `/search` - Search book content
   - [ ] `/health` - Health check endpoint

### **Phase 4: RAG Chatbot Implementation (Week 5)**

1. **Content Embedding Pipeline**
   - [ ] Extract chapter text from Docusaurus
   - [ ] Split content into chunks
   - [ ] Generate embeddings using OpenAI API
   - [ ] Store embeddings in Qdrant
   - [ ] Store metadata in Postgres

2. **Chatbot Logic**
   - [ ] Implement retrieval from Qdrant
   - [ ] Create prompt templates
   - [ ] Integrate with OpenAI API
   - [ ] Add context window management
   - [ ] Implement conversation history

3. **Frontend Chatbot Widget**
   - [ ] Create React chatbot component
   - [ ] Add chat UI (messages, input, send button)
   - [ ] Implement text selection detection
   - [ ] Add chatbot toggle button
   - [ ] Style with Tailwind CSS

### **Phase 5: Authentication & User Management (Week 6)**

1. **Better-Auth Integration**
   - [ ] Set up better-auth.com account
   - [ ] Configure OAuth providers (Google, GitHub)
   - [ ] Create auth endpoints in FastAPI

2. **User Onboarding**
   - [ ] Create signup form with background questions
   - [ ] Fields: software background, hardware experience, goals
   - [ ] Validate and store user profile
   - [ ] Create user dashboard

3. **Backend User Management**
   - [ ] User table in Postgres
   - [ ] Profile management endpoints
   - [ ] JWT token generation and validation
   - [ ] Session management

### **Phase 6: Content Personalization (Week 7)**

1. **Personalization Engine**
   - [ ] Create personalization rules based on user profile
   - [ ] Implement difficulty level adjustment
   - [ ] Add example filtering
   - [ ] Recommend content paths

2. **UI Personalization Controls**
   - [ ] Add "Personalize" button at chapter start
   - [ ] Create settings modal
   - [ ] Allow users to adjust difficulty
   - [ ] Save preferences to database

3. **Dynamic Content Rendering**
   - [ ] Load personalized content server-side
   - [ ] Filter exercises by difficulty
   - [ ] Show/hide advanced sections
   - [ ] Recommend next chapters

### **Phase 7: Urdu Translation Feature (Week 7-8)**

1. **Translation Setup**
   - [ ] Integrate translation API (Google Translate or similar)
   - [ ] Or use OpenAI for better technical translation
   - [ ] Create translation cache in Postgres

2. **Bilingual UI**
   - [ ] Add language toggle button at chapter start
   - [ ] Implement RTL (Right-to-Left) support for Urdu
   - [ ] Adjust layout for bilingual content
   - [ ] Style Urdu text appropriately

3. **Content Translation**
   - [ ] Translate chapter content to Urdu
   - [ ] Handle code examples (keep English)
   - [ ] Preserve formatting and structure
   - [ ] Test bidirectional switching

### **Phase 8: Claude Code Subagents & Skills (Week 8)**

1. **Identify Reusable Tasks**
   - [ ] Content generation tasks
   - [ ] Code snippet generation
   - [ ] Translation tasks
   - [ ] Content validation

2. **Create Subagents**
   - [ ] Content writing agent
   - [ ] Code example generation agent
   - [ ] Translation agent
   - [ ] Review and editing agent

3. **Develop Agent Skills**
   - [ ] Chapter summarization skill
   - [ ] Code testing skill
   - [ ] Content validation skill
   - [ ] Cross-referencing skill

4. **Integration in Project**
   - [ ] Use agents in book creation workflow
   - [ ] Document agent usage
   - [ ] Demonstrate reusability

### **Phase 9: Deployment & Testing (Week 9)**

1. **Backend Deployment**
   - [ ] Deploy FastAPI to cloud (Heroku, Railway, or Vercel)
   - [ ] Set up environment variables
   - [ ] Configure database connections
   - [ ] Set up monitoring and logging

2. **Frontend Deployment**
   - [ ] Deploy Docusaurus to GitHub Pages or Vercel
   - [ ] Configure custom domain (optional)
   - [ ] Set up SSL/TLS
   - [ ] Configure build pipeline

3. **Testing**
   - [ ] Unit tests for API endpoints
   - [ ] Integration tests for RAG pipeline
   - [ ] Chat functionality testing
   - [ ] Authentication flow testing
   - [ ] User profile personalization testing
   - [ ] Translation feature testing
   - [ ] Cross-browser testing

### **Phase 10: Documentation & Demo (Week 10)**

1. **Project Documentation**
   - [ ] Write setup instructions
   - [ ] Document API endpoints
   - [ ] Create architecture diagrams
   - [ ] Write deployment guide

2. **Demo Video (< 90 seconds)**
   - [ ] Show book navigation
   - [ ] Demonstrate chatbot functionality
   - [ ] Show authentication and login
   - [ ] Demo personalization feature
   - [ ] Show Urdu translation
   - [ ] Use NotebookLM or screen recording tool

3. **Final Submission**
   - [ ] Public GitHub repository link
   - [ ] Published book URL
   - [ ] Demo video link (< 90 seconds)
   - [ ] WhatsApp number for contact

---

## 📊 Database Schema Overview

### **Users Table**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  name VARCHAR(255),
  software_background VARCHAR(255),
  hardware_background VARCHAR(255),
  learning_goals TEXT,
  preferred_difficulty VARCHAR(50),
  preferred_language VARCHAR(10),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### **Book Content Table**
```sql
CREATE TABLE chapters (
  id SERIAL PRIMARY KEY,
  module_id INTEGER,
  chapter_number INTEGER,
  title VARCHAR(255),
  content_md TEXT,
  excerpt VARCHAR(500),
  created_at TIMESTAMP
);
```

### **Embeddings Table**
```sql
CREATE TABLE embeddings (
  id SERIAL PRIMARY KEY,
  chapter_id INTEGER REFERENCES chapters(id),
  chunk_text TEXT,
  embedding vector(1536),
  created_at TIMESTAMP
);
```

### **Chat History Table**
```sql
CREATE TABLE chat_history (
  id SERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  query TEXT,
  response TEXT,
  retrieved_chapters INTEGER[],
  created_at TIMESTAMP
);
```

---

## 🚀 API Endpoints Summary

### **Authentication**
- `POST /auth/signup` - Register new user
- `POST /auth/signin` - Login user
- `POST /auth/logout` - Logout user
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update user profile

### **Chatbot**
- `POST /chat` - Send chat message
- `GET /chat/history` - Get chat history
- `POST /chat/select` - Query based on text selection

### **Content**
- `GET /chapters/:moduleId` - Get chapters by module
- `GET /chapter/:id` - Get chapter details
- `POST /search` - Search book content

### **Admin/Data**
- `POST /embed-content` - Embed book content to Qdrant
- `GET /health` - Health check

---

## 📝 Key Milestones & Checkpoints

| Milestone | Target Date | Status |
|-----------|------------|--------|
| Project Setup & Planning | Week 1 | ⏳ Pending |
| Core Book Content Written | Week 3 | ⏳ Pending |
| Backend & DB Setup | Week 4 | ⏳ Pending |
| RAG Chatbot Functional | Week 5 | ⏳ Pending |
| Authentication Implemented | Week 6 | ⏳ Pending |
| Personalization Feature | Week 7 | ⏳ Pending |
| Urdu Translation | Week 8 | ⏳ Pending |
| Full Deployment | Week 9 | ⏳ Pending |
| Demo & Submission | Week 10 | ⏳ Pending |

---

## 💡 Bonus Points Strategy

### Priority 1 (Recommended Implementation Order)
1. **RAG Chatbot** - Core requirement, foundational for everything
2. **Authentication** - Essential for personalization
3. **Content Personalization** - High-value feature
4. **Claude Code Subagents** - Demonstrates AI proficiency

### Priority 2
5. **Urdu Translation** - Language support adds value

---

## 🔧 Development Tools & Commands

### Setup
```bash
# Clone and setup
git clone <repo-url>
cd book
npm install

# Start Docusaurus dev server
npm run start

# FastAPI dev server
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Deployment
```bash
# Build Docusaurus
npm run build

# Deploy to GitHub Pages
npm run deploy

# Deploy FastAPI (example with Vercel)
vercel deploy
```

---

## 📦 Required Dependencies (Python Backend)

```
fastapi==0.104.0
uvicorn==0.24.0
python-dotenv==1.0.0
neon-postgres==0.5.0
qdrant-client==2.4.0
openai==1.3.0
pydantic==2.4.0
sqlalchemy==2.0.0
python-jose==3.3.0
passlib==1.7.4
```

---

## 🌐 Submission Requirements

### Before Submission, Ensure:
- [ ] Public GitHub repository with complete code
- [ ] Published book URL (GitHub Pages or Vercel)
- [ ] Working chatbot integrated in book
- [ ] User authentication implemented
- [ ] Demo video (< 90 seconds)
- [ ] All code documented
- [ ] README with setup instructions
- [ ] API documentation

### Submission Form Fields:
1. **Public GitHub Repo Link** - Full source code
2. **Published Book Link** - Live deployment
3. **Demo Video Link** - NotebookLM or recorded demo
4. **WhatsApp Number** - For live presentation invitation

### Submission Deadline:
**Sunday, November 30, 2025 at 6:00 PM**

**Form Link:** https://forms.gle/CQsSEGM3GeCrL43c8

---

## 🎓 Learning Resources

- **Docusaurus Docs:** https://docusaurus.io/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **OpenAI API:** https://openai.com/api/
- **Qdrant Docs:** https://qdrant.tech/
- **better-auth.com:** https://www.better-auth.com/
- **ROS 2 Documentation:** https://docs.ros.org/
- **NVIDIA Isaac Docs:** https://docs.nvidia.com/isaac/
- **Claude Code Guide:** https://claude.com/claude-code

---

## 🏆 Success Criteria

### Minimum for Base Score (100 Points):
- ✅ Complete book with all 4 modules
- ✅ Functional RAG chatbot embedded in book
- ✅ Book deployed to GitHub Pages/Vercel
- ✅ Chatbot can answer questions about content
- ✅ Text selection queries work

### Additional Points (Bonus):
- ✅ Claude Code Subagents used (+50)
- ✅ Authentication & user profiles (+50)
- ✅ Content personalization (+50)
- ✅ Urdu translation (+50)

**Maximum Possible Score: 400 Points**

---

## 📞 Support & Resources

- **Claude Code:** https://www.claude.com/product/claude-code
- **Spec-Kit Plus:** https://github.com/panaversity/spec-kit-plus/
- **Panaversity:** https://panaversity.org/
- **Discord/Community:** Check Panaversity website for community channels

---

## 🎬 Next Steps

1. **Fork this repository** and set up local environment
2. **Read the course details** thoroughly
3. **Create detailed specifications** using Spec-Kit Plus
4. **Start with Docusaurus setup** and basic book structure
5. **Build backend** and RAG pipeline
6. **Implement features** in priority order
7. **Test thoroughly** across all functionality
8. **Create demo video** showcasing all features
9. **Submit before deadline**
10. **Prepare for live presentation** (if selected)

---

**Good luck with the hackathon! Let's build something amazing.** 🚀

