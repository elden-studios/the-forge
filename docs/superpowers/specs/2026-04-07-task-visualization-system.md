# Task Visualization System — Design Spec

## Overview

Real-time visualization of agent tasks, handoffs, and workflow progress across two synchronized views: pixel art office overlay + dedicated 4-tab dashboard.

## Status: APPROVED — Implementation pending next session

## Architecture

```
forge-state.json + forge-tasks.json (new)
    │
    ├──→ office-live.html (pixel art + overlays)
    │    ├── Task bubbles above agents
    │    ├── Handoff arrows between agents (animated)
    │    ├── Room glow by activity
    │    └── Phase progress bar
    │
    └──→ dashboard.html (new, 4 tabs)
         ├── Tab 1: Mission Control (status overview)
         ├── Tab 2: Network Graph (animated force-directed)
         ├── Tab 3: Kanban Board (task cards)
         └── Tab 4: Timeline (Gantt-style)
```

## View 1: Office Overlays

### Task Bubbles
- Small pixel speech bubble above working agents
- Shows task name (~15 chars truncated)
- Color matches phase (red=intake, purple=research, orange=war room, blue=architecture, green=GTM)
- Pulses when actively working, static when waiting

### Handoff Arrows
- Animated pixel dot traveling from sender to receiver
- Routes through doors (hallway path, not through walls)
- Brief label along the arrow path
- Disappears after handoff completes

### Room Glow
- Subtle color overlay on active department rooms
- Strategy=red, Research=purple, Design=teal, Growth=green, Engineering=blue, Content=yellow
- Inactive rooms stay dim

### Phase Progress Bar
- Horizontal bar at top of canvas
- 8 segments for 8 phases
- Completed=filled, Current=pulsing, Future=empty

## View 2: Dashboard (4 Tabs)

### Tab 1: Mission Control
All-at-a-glance operations view:
- Phase indicator with progress
- Agent status list (working/idle/meeting)
- Current output progress per agent
- Handoff tracker (complete/pending)
- Checkpoint status (answered/pending/not yet)
- Risk flags with severity

### Tab 2: Network Graph
Force-directed graph:
- Nodes = agents (with pixel avatars)
- Edges = active handoffs (animated glow)
- Node size = current workload
- Edge thickness = handoff importance
- Nodes cluster when collaborating, drift when idle
- Reorganizes in real time

### Tab 3: Kanban Board
Card-based columns:
- Backlog | In Progress | In Review | Done
- Cards show: agent avatar, task name, time since start
- Cards move left-to-right in real time
- Color-coded by department
- Drag-drop not needed (read-only visualization)

### Tab 4: Timeline (Gantt)
Horizontal bars per agent:
- Shows parallel vs sequential work
- Handoff arrows between bars
- Phase markers along the top
- Real-time: current work extends the bar as time passes

## Data Model: forge-tasks.json

```json
{
  "current_project": "Project Name",
  "current_phase": 2,
  "phase_status": ["done","active","pending","pending","pending","pending","pending","pending"],
  "tasks": [
    {
      "id": "task-001",
      "name": "Competitive Matrix",
      "agent": "agent-vexx",
      "status": "in_progress",
      "phase": 2,
      "started": "ISO timestamp",
      "completed": null,
      "handoff_from": "agent-flnt",
      "handoff_to": null,
      "deliverable": "Competitive Matrix",
      "progress": 60
    }
  ],
  "handoffs": [
    {
      "from": "agent-flnt",
      "to": "agent-vexx",
      "label": "Brief validated",
      "timestamp": "ISO timestamp",
      "status": "complete"
    }
  ],
  "checkpoints": [
    { "id": 1, "status": "answered", "decision": "Option A" },
    { "id": 2, "status": "pending" },
    { "id": 3, "status": "not_yet" }
  ],
  "risks_flagged": [
    { "agent": "agent-vexx", "risk": "No revenue model defined", "severity": "high" }
  ]
}
```

## Implementation Plan

1. Create `forge-tasks.json` schema
2. Update `office-template.html` with overlay rendering (bubbles, arrows, glow, phase bar)
3. Create `assets/dashboard.html` with 4 tabs
4. Update `SKILL.md` to set task state during each protocol phase
5. Test with a live project brief

## Estimated effort: ~1000 lines across 3 files
