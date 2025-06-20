# Documentation Index

This directory contains organized documentation for the Donkey Workspace / MythOS project.

## 📁 Directory Structure

### `/phases/` - Development Phases
- **PHASE_SUMMARY.md** - Complete phase history and development timeline
- **MODULE_ROADMAP.md** - Module development roadmap
- **PHASE-11-Clarity-Lock-In.md** - Current phase documentation

### `/frontend/` - Frontend Documentation
- **Assistant-Frontend-Routes.md** - React routing configuration
- **Assistant-System-ERD.md** - Entity relationship diagrams
- **AGENTS.md** - Frontend agent system
- **MODEL_MAPS.md** - Data model mappings
- **🧭 Clarity Panel UI Spec — Assistant Health Dashboard.md** - UI specifications
- **core_app_navigation.md** - Navigation structure
- **media_integration_steps.md** - Media integration guide
- **route_sync_checklist.md** - Route synchronization checklist

### `/backend/` - Backend Documentation
Contains all backend documentation including:
- API overviews and architecture diagrams
- App-specific documentation (assistants, memory, agents, etc.)
- Phase-specific implementation guides
- Model and service documentation
- Integration and maintenance guides

### `/prompt-sets/` - AI System Prompts
Organized by AI provider:
- **ANTHROPIC/** - Claude system prompts and cheat sheets
- **OPENAI/** - GPT system prompts  
- **GOOGLE/** - Gemini system prompts
- **CURSOR/** - Cursor IDE prompts
- **DEVIN/** - Devin AI prompts
- **REPLIT/** - Replit Agent prompts
- **XAI/** - Grok system prompts
- And more...

### `/reflections/` - AI Reflections
- System-generated reflections on performance
- Optimization insights through memory management
- Task management and personalization analysis
- AI performance enhancement reports

### `/troubleshooting/` - How-To Guides
- **FirstUseTour_Troubleshooting.md** - First-time user issues
- **Glossary_Fallback_Strat_Overview.md** - Glossary fallback strategies  
- **RAG_Debug_Overview.md** - RAG debugging guide

### `/archive/` - Deprecated/Experimental
- **lunatic_explorer_route.md** - Experimental routing features
- Other deprecated documentation

## 🔍 Key Files in Root `/docs/`

### Architecture & System Design
- **SystemOverview.md** - High-level system architecture
- **api_overview.md** - REST API documentation  
- **architecture_diagram.md** - System diagrams
- **MythOS.md** - Core MythOS concepts

### Development & Maintenance
- **ROADMAP.md** - Project roadmap and priorities
- **MAINTENANCE.md** - Production maintenance guide
- **GOALS.md** - Project goals and objectives
- **TODO.md** - Active development tasks

### RAG & Memory System
- **RAG-Flow.md** - RAG pipeline documentation
- **RAG_DEBUG.md** - RAG debugging utilities
- **Rag-Recall-Roadmap.md** - RAG recall improvements
- **REFLECTIVE_INGEST_REVIEW_FLOW.md** - Reflective ingestion process

### Specialized Features
- **ASSISTANT_DASHBOARD_OVERVIEW.md** - Assistant dashboard design
- **ASSISTANT_LIFECYCLE.md** - Assistant lifecycle management
- **ASSISTANT_MODEL_REFACTOR_PLAN.md** - Model refactoring strategy
- **glossary_usage.md** - Glossary system usage
- **memory_rate_limit_diagnostic.md** - Memory system diagnostics

### Project Status & Releases
- **PROJECT_STATUS_2025-06-05_03-37-06.md** - Current project status
- **RELEASE_NOTES.md** - Release history and notes
- **Demo-Readiness-Workflow.md** - Demo preparation workflow

## 📋 Quick Navigation

**For Developers:**
- Start with `SystemOverview.md` for architecture understanding
- Check `ROADMAP.md` for current priorities  
- Use `API_overview.md` for endpoint reference
- Consult `/backend/` for specific app documentation

**For AI/ML Work:**
- Review `/prompt-sets/` for system prompts
- Check `/reflections/` for AI performance insights
- Use `RAG_DEBUG.md` for debugging RAG issues
- Reference `glossary_usage.md` for memory system

**For Frontend Development:**
- Start with `/frontend/` directory
- Check route documentation and UI specs
- Review navigation and integration guides

**For Operations:**
- Use `MAINTENANCE.md` for production issues
- Check `/troubleshooting/` for common problems
- Review phase documentation for context

## 🔄 Maintenance

This index is manually maintained. When adding new documentation:
1. Place files in appropriate subdirectory
2. Update this index with brief description
3. Ensure CLAUDE.md references key files
4. Keep merged_markdown in sync if needed

---

*Last updated: 2025-06-20*