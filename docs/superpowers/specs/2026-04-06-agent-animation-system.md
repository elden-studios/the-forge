# Agent Animation System — Event-Driven Movement

## Overview

Add an event-driven animation system to The Forge office. Agents sit at their desks by default and move when triggered: walking to meetings, getting coffee, chatting at another desk, or entering/leaving during hire/fire events. An auto-coffee timer makes the office feel alive without explicit triggers.

## Agent States

| State | Sprite | Position | Trigger |
|-------|--------|----------|---------|
| `sitting` | Seated at desk (existing) | Agent's desk position | Default / return from any event |
| `walking` | Standing, 4-frame walk cycle | Interpolated between origin → destination | Transition between any two states |
| `meeting` | Standing in meeting room | Meeting room positions (up to 4 slots) | `active_event.type === 'meeting'` |
| `coffee` | Standing at coffee machine | Break area coffee machine position | Auto-timer (~30s) or explicit event |
| `chatting` | Two agents facing each other | Near the target agent's desk | `active_event.type === 'chatting'` |
| `entering` | Standing, walking from door to desk | Door → desk path | New hire event |
| `leaving` | Standing, walking from desk to door | Desk → door path | Fire event |
| `working` | Seated, faster typing + lightbulb | Agent's desk position | `active_event.type === 'working'` |

## Standing Sprite

The SpriteEngine already has a standing pose in `drawAgent(... seated=false)`. This draws full legs and shoes with arms at sides. Used for all non-desk states.

## Walk Cycle

4-frame animation at 200ms per frame:
- Frame 0: left foot forward (left leg shifted 1px ahead, right leg 1px back)
- Frame 1: center (normal standing)
- Frame 2: right foot forward (mirror of frame 0)
- Frame 3: center (normal standing)

Implementation: modify the standing leg drawing based on `walkFrame % 4`:
- Frames 0,2: offset one leg forward by 1px, the other back by 1px
- Frames 1,3: normal standing position

No new sprite method needed — just add a `walkFrame` parameter to the existing standing body code.

## Movement Paths

Agents walk in axis-aligned segments (no diagonal) matching the tile grid:
1. Walk horizontally from current X to target X
2. Then walk vertically from current Y to target Y

Speed: 2 pixels per animation frame (at 200ms interval = ~10px/sec screen movement).

### Path Examples
- **Desk → Meeting Room**: Walk right to break area column, then walk down to meeting room Y
- **Desk → Coffee Machine**: Walk right to break area, stop at coffee machine coordinates
- **Desk → Another Desk**: Walk horizontally to target desk X, then vertically to target desk Y
- **Door → Desk** (hiring): Walk up from door Y to desk Y, then walk left to desk X
- **Desk → Door** (firing): Walk right to door X, then walk down to door Y

## Agent State Machine

```
                    ┌──────────┐
         ┌─────────│  sitting  │←──────────┐
         │         └────┬─────┘            │
         │              │ (event trigger)  │ (arrival)
         │              ▼                  │
         │         ┌──────────┐            │
         │         │ walking  │────────────┘
         │         └────┬─────┘
         │              │ (arrived at destination)
         │              ▼
         │    ┌─────────────────────┐
         │    │ meeting | coffee |  │
         │    │ chatting | working  │
         │    └─────────────────────┘
         │              │ (event ends / timer expires)
         │              ▼
         │         ┌──────────┐
         └─────────│ walking  │ (back to desk)
                   └──────────┘
```

## SceneRenderer Changes

### New Properties

```javascript
this.agentAnims = {};
// Per agent:
// {
//   state: 'sitting' | 'walking' | 'meeting' | 'coffee' | 'chatting' | 'working',
//   screenX: current screen X,
//   screenY: current screen Y,
//   targetX: destination X (when walking),
//   targetY: destination Y (when walking),
//   walkFrame: 0-3 (walk cycle frame),
//   returnState: 'sitting' (state to return to after destination),
//   timer: 0 (countdown for coffee/chatting duration)
// }
this.coffeeTimer = 0; // countdown to next random coffee break
```

### New Method: `updateAgents()`

Called each frame before rendering. Handles:

1. **Walking interpolation**: Move agent 2px toward target per frame. When arrived, switch to destination state.
2. **Coffee timer**: Decrement `coffeeTimer`. When it hits 0, pick a random sitting agent, set their state to `walking` with target = coffee machine. Reset timer to ~150 frames (30s at 200ms/frame).
3. **Coffee/chatting duration**: When an agent is in `coffee` or `chatting` state, decrement their `timer`. When it hits 0, set state to `walking` with target = their desk.
4. **State events**: Check `active_event` from state. If meeting → walk relevant agents to meeting room. If working → keep them seated with working animation.

### Modified `render()` Draw Order

Instead of drawing each agent at their fixed desk position, draw them at `agentAnims[id].screenX/Y`:

```javascript
L.agents.forEach(a => {
  const anim = this.agentAnims[a.id];
  if (anim.state === 'sitting' || anim.state === 'working') {
    // Draw at desk with chair, desk back/front, seated sprite
    this.drawChair(...);
    this.drawDeskBack(...);
    this.sprite.drawAgent(anim.screenX, anim.screenY, a.avatar, this.frame, anim.state, true);
    this.drawDeskFront(...);
  } else {
    // Draw standing/walking sprite at current position (no desk)
    this.sprite.drawAgent(anim.screenX, anim.screenY, a.avatar, this.frame, anim.state, false);
  }
});
```

Desk furniture (chair, desk back, desk front) is always drawn at the agent's home desk position regardless of where the agent currently is — the desk doesn't move, only the agent does.

### Split Desk Drawing

Desks are drawn in two passes:
1. **Pass 1 (before all agents)**: Draw ALL desk furniture (chairs, desk backs, desk fronts, bookshelves) at fixed positions
2. **Pass 2 (after desk furniture)**: Draw ALL agents at their current animated positions

This ensures agents walking in front of other desks render correctly.

## Auto-Coffee Behavior

Every ~30 seconds (150 frames at 200ms):
1. Pick a random agent currently in `sitting` state
2. Set their state to `walking`, target = coffee machine position in break area
3. On arrival: state = `coffee`, timer = 20 frames (~4 seconds)
4. When timer expires: state = `walking`, target = their home desk
5. On arrival: state = `sitting`

## forge-state.json Events

The `active_event` field in forge-state.json triggers specific animations:

```json
// Meeting: agents walk to meeting room
{ "type": "meeting", "agents": ["agent-flnt", "agent-vexx"] }

// Working: agents stay seated with faster typing + lightbulb
{ "type": "working", "agents": ["agent-flnt", "agent-renn"] }

// Chatting: agent B walks to agent A's desk
{ "type": "chatting", "agents": ["agent-flnt", "agent-vexx"], "at": "agent-flnt" }

// Hiring: new agent walks in from door
{ "type": "hiring", "agent": "agent-new-id" }

// Firing: agent walks out to door
{ "type": "firing", "agent": "agent-old-id" }
```

Events are set by the SKILL.md orchestration when generating responses (e.g., during a multi-agent project brief, set `working` for active agents; during a meeting room debate, set `meeting`).

## What Stays the Same

- SpriteEngine `drawAgent()` already supports `seated` parameter (true/false)
- Standing pose already exists in the code
- Idle animations (scribbles-notepad, sips-mug, etc.) continue to play when seated
- All existing desk/furniture rendering preserved
- `prefers-reduced-motion` still respected — skip walk animations, agents teleport to positions

## Implementation File

All changes in `assets/office-template.html` — specifically the SceneRenderer class. No other files change.

## Success Criteria

1. Agents sit at desks by default with idle animations
2. Every ~30s, a random agent gets up, walks to coffee, pauses, walks back
3. During project briefs, active agents show `working` state (lightbulb)
4. During meeting room debates, debating agents walk to the meeting room
5. New hires walk in from the door to their desk
6. Fired agents walk from desk to door and disappear
7. Walk paths follow the tile grid (no diagonal movement)
8. `prefers-reduced-motion` skips walk animations
