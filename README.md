# ChetnaOS — Cognitive Operating System for AGI (Hackathon Build)

ChetnaOS is an architecturally integrated cognitive operating system designed to explore artificial general intelligence through system-level intelligence, not just isolated models.

This repository contains a unified platform combining agents, memory, world modeling, goal management, and real-world integrations into a single evolving cognitive system.

🏆 Hackathon Build — ChetnaOS AGI Architecture Demo

---

## Vision

Most AI systems today are collections of tools and models. ChetnaOS is designed as an operating system for intelligence — where cognition, memory, goals, and actions are coordinated through a shared system architecture.

The focus is on architectural completeness and integration rather than brute-force training.

---

## What ChetnaOS Does

ChetnaOS provides:

- A persistent AGI loop for continuous cognition  
- Multi-agent coordination (chat, scheduler, voice, messaging agents)  
- A memory service for long-term semantic context  
- A symbolic world model for structured reasoning  
- Goal agents for task and objective management  
- Real-world integrations (WhatsApp, email, CRM, notifications)  
- Autonomous workflows for lead handling and follow-ups  
- A deployable backend with live API and UI  

Together, these components behave as a unified cognitive system rather than a set of disconnected scripts.

---

## System Architecture

Key subsystems in this repository:

- `backend/agi/` — Core AGI loop, world model, memory service, goal agents  
- `backend/agents/` — Chat, intent, scheduler, voice, and messaging agents  
- `backend/integrations/` — WhatsApp, email, CRM, and notifier integrations  
- `backend/workflows/` — Autonomous task and business process flows  
- `memory/` — Persistent memory storage layer  
- `frontend/` — Web UI for interacting with the system  

These subsystems are wired together to support continuous cognition, memory-driven behavior, and autonomous task execution.

---

## Demo Capabilities

The hackathon demo showcases:

- Continuous AGI loop execution  
- Agent-based goal handling  
- Memory-assisted reasoning  
- World model state tracking  
- Autonomous workflows (lead, follow-up, meeting flows)  
- Real-world messaging and notification integrations  

This demonstrates a cognitive operating system approach rather than a single-task agent.

---

## Quickstart (Local)

### Setup Environment

```bash
cp env.example .env
# Add your GROQ_API_KEY
