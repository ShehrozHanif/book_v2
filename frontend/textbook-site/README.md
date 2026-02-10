# Physical AI & Humanoid Robotics Textbook

A comprehensive Docusaurus-based documentation site for the Physical AI & Humanoid Robotics textbook.

## Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Local Development

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm start
   ```

   The site will open at `http://localhost:3000/book/`

3. **Build for production**:
   ```bash
   npm run build
   ```

4. **Serve production build locally**:
   ```bash
   npm run serve
   ```

### Project Structure

```
textbook-site/
├── docs/                    # Chapter content (markdown files)
│   ├── module-01/          # Module 1 chapters
│   ├── module-02/          # Module 2 chapters
│   ├── module-03/          # Module 3 chapters
│   ├── module-04/          # Module 4 chapters
│   ├── module-05/          # Module 5 chapters
│   └── index.md            # Homepage
├── sidebars.js             # Navigation structure
├── docusaurus.config.js    # Site configuration
├── src/
│   ├── components/         # React components (Navigation, Breadcrumb, etc.)
│   ├── css/               # Styling
│   └── theme/             # Theme customization
└── static/                # Static assets (images, etc.)
```

## Adding Chapters

### Adding a New Chapter

1. Create a markdown file in the appropriate module folder:
   ```bash
   # Example: Module 1, Chapter 2
   touch docs/module-01/chapter-02.md
   ```

2. Add YAML frontmatter to the markdown file:
   ```yaml
   ---
   title: Chapter Title
   module: 1
   order: 2
   description: Brief description of the chapter
   ---

   # Chapter Content

   Your content here...
   ```

3. Update `sidebars.js` to include the new chapter in the navigation

4. The search index will be automatically updated on the next build

## Features

### 1. **Full-Text Search**
- Search across all 20 chapters with <500ms query time
- Results ranked by relevance
- Context snippets shown for each result

### 2. **Chapter Navigation**
- Navigate any chapter in <2 clicks
- Sidebar with all chapters organized by module
- Previous/Next chapter buttons
- Breadcrumb navigation showing current location
- Automatic table of contents from headings

### 3. **Code Examples**
- Syntax highlighting for Python, YAML, XML, and Bash
- Copy-to-clipboard button for all code blocks

### 4. **Chatbot Integration**
- Embedded RAG chatbot widget on all pages
- Asks questions about textbook content

### 5. **Responsive Design**
- Works on mobile, tablet, and desktop
- WCAG 2.1 AA accessibility compliance

## Deployment to GitHub Pages

```bash
npm run deploy
```

If using SSH:
```bash
USE_SSH=true npm run deploy
```

Otherwise:
```bash
GIT_USER=<Your GitHub username> npm run deploy
```

This builds the website and pushes to the `gh-pages` branch for GitHub Pages hosting.
