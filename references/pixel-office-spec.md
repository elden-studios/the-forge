# Pixel Office Visualization Spec — The Forge

This document defines the visual contract for the pixel art office. Read this when generating or modifying the office-template.html or when debugging visualization issues.

---

## Art Style

- **Genre**: 16-bit retro pixel art (SimCity meets a modern tech startup)
- **Base pixel unit**: 4px — all visual elements snap to a 4px grid
- **Color palette**: Muted-but-vibrant. Avoid neon. Think SNES-era color depth
- **Mood**: Warm, inviting, slightly playful. A place you'd want to work

### Environment Palette

| Element | Color | Hex |
|---|---|---|
| Floor (main) | Warm wood | `#C4956A` |
| Floor (alt tile) | Darker wood | `#A87D5A` |
| Walls | Light gray | `#D5D5D5` |
| Wall accent | Medium gray | `#B0B0B0` |
| Desk surface | Oak | `#B8860B` |
| Desk legs | Dark brown | `#654321` |
| Monitor | Dark gray | `#2C2C2C` |
| Monitor screen | Blue glow | `#4A90D9` |
| Meeting room glass | Transparent blue | `rgba(74, 144, 217, 0.15)` |
| Meeting room active | Glow yellow | `rgba(241, 196, 15, 0.3)` |
| Coffee station | Warm brown | `#8B4513` |
| Door | Dark wood | `#5C4033` |

---

## Office Layout Architecture

### Base Dimensions
- **Minimum canvas**: 600px wide × 400px tall
- **Padding**: 20px on all sides
- **Grid cell size**: 80px wide × 60px tall (each desk occupies one cell)

### Layout Zones

```
┌─────────────────────────────────────────────────┐
│  [Dept Label]    [Dept Label]    [Meeting Room]  │
│                                  ┌──────────┐    │
│  [Desk] [Desk]   [Desk] [Desk]  │          │    │
│                                  │  Table   │    │
│  [Desk] [Desk]   [Desk] [Desk]  │          │    │
│                                  └──────────┘    │
│                                                   │
│  ☕ Coffee                    [Door]              │
└─────────────────────────────────────────────────┘
```

- **Department zones**: Arranged in columns from left to right, each 160px wide minimum
- **Desks**: 2-column grid within each department zone, rows expand downward
- **Meeting Room**: Right side, fixed at 160px × 120px. Glass walls (semi-transparent)
- **Coffee Station**: Bottom-left corner. Decorative — a small counter with a coffee machine sprite
- **Front Door**: Bottom-center. Where agents enter and exit
- **Department Nameplates**: Colored banner above each department column, matching department color

### Scaling Rules

| Roster Size | Layout |
|---|---|
| 1 agent | Single small room (300×250). One desk, door, coffee corner |
| 2–4 agents | Room expands to fit. Desks fill left-to-right, top-to-bottom |
| 5–8 agents | Full layout with department columns. Meeting room appears |
| 9–16 agents | Canvas widens. New department columns added as needed |
| 17+ agents | Second row of departments. Canvas height increases |

Canvas grows in increments:
- Width: +200px per new department column
- Height: +80px per new desk row within any department

---

## Avatar Rendering — Procedural Sprites

Each agent's avatar is generated procedurally from their avatar attributes. No pre-made sprites.

### Sprite Dimensions
- **Base size**: 16px wide × 24px tall (rendered at 2x = 32×48 display pixels)
- **Rendering scale**: Each "pixel" in the sprite is a 2×2 CSS pixel block (for crisp retro look at modern resolutions)

### Layered Rendering Order
Draw in this order (back to front):

1. **Body base** (rows 8-23): Simple rectangular torso + legs shape
2. **Skin tone** (rows 0-7 for head, rows 18-23 for hands): Head circle + hand blocks
3. **Outfit** (rows 8-17): Covers torso. Color = outfit base color. Department accent stripe at row 10-11
4. **Hair** (rows 0-5): Shape varies by hairstyle attribute. Color varies
5. **Accessory** (position varies): Glasses on face, hat on head, scarf on neck, etc.
6. **Eyes** (row 3-4): Two 1px dots, always black or dark brown. Blink every 3-4 seconds
7. **Name tag** (below sprite): 8px pixel font, agent name, centered

### Hair Color Palette
`#1A1A1A` (black), `#4A3728` (dark brown), `#8B6914` (brown), `#C4A265` (dirty blonde), `#E8D5A3` (blonde), `#B03A2E` (auburn), `#E74C3C` (red), `#7D3C98` (purple), `#2E86C1` (blue), `#17A589` (teal), `#F0F0F0` (white/silver)

### Hairstyle Pixel Maps
Each hairstyle is defined by which pixels in rows 0-5 are filled with hair color:

- **mohawk**: 2px wide strip centered, rows 0-5, tall
- **ponytail**: Full coverage rows 1-4, trailing 3px extension at back rows 5-7
- **buzz-cut**: Thin coverage rows 1-2 only
- **curly**: Irregular blob, wider than head, rows 0-4
- **headphones**: Hair underneath + 2px band across top with circles at ears
- **beanie**: Solid rectangle rows 0-3, folded brim at row 3
- **spiky**: 3 triangular spikes pointing up from rows 0-2
- **bald**: No hair pixels, just skin tone
- **afro**: Large circle, rows -2 to 4 (extends above sprite bounds), wider than head

### Accessory Rendering
- **oversized-glasses**: 2 large circles at eye level (rows 3-5), connected bridge
- **scarf**: Colored pixels at rows 7-9 (neck area), trailing end
- **earbuds**: Small dots at ear level (row 3, columns 0 and 15)
- **bandana**: Colored band at rows 1-2
- **eyepatch**: Dark square covering one eye (rows 3-4, one side)
- **round-glasses**: Smaller circles than oversized, thinner frames
- **snapback-cap**: Flat brim at row 2, dome rows 0-1, brim extends 2px to one side

---

## Animation System

### Frame Timing
- **Frame rate**: ~5 FPS for sprite animations (200ms per frame)
- **Render rate**: 60 FPS for smooth canvas (use `requestAnimationFrame`, only redraw dirty regions)
- **Animation cycles**: Most animations loop through 2-4 frames

### Idle Animations (Unique Per Agent)

Each idle animation is a set of sprite modifications that cycle:

**drums-fingers**: Alternate hand positions at desk edge (2 frames, 300ms each)
**leans-back-thinking**: Sprite tilts back 2px, hand behind head (2 frames, hold 1s each)
**scribbles-notepad**: Small notepad sprite appears, hand moves (3 frames, 200ms)
**sips-mug**: Mug rises to face level and back (4 frames, 400ms each)
**adjusts-glasses**: Hand reaches to face, pushes up (3 frames, 300ms, then 2s pause)
**spins-pen**: Small pen rotates near hand (4 frames, 150ms each)
**stretches**: Arms raise above head and back (3 frames, 500ms each, then 3s pause)
**checks-phone**: Small rectangle appears in hand, glow (2 frames, hold 1.5s)
**taps-foot**: One foot pixel alternates position (2 frames, 250ms each)
**bounces-leg**: Knee area moves up/down slightly (2 frames, 200ms)

### Active State Animations

**Working** (when agent is contributing to a prompt):
- Typing speed doubles (hand animation cycles at 100ms instead of 200ms)
- Lightbulb icon appears above head: pulses on/off (500ms cycle)
- Monitor screen color shifts to brighter blue
- Small sparkle particles (2-3 pixels) appear and fade near the agent

**Meeting Room** (when agents enter a debate):
- Agents "walk" from desk to meeting room (see Walking animation)
- Sit at meeting room table (static seated pose)
- Meeting room glass walls glow yellow
- Small speech bubble icons alternate between debating agents

### Transition Animations

**Walking** (4-frame cycle, 150ms per frame):
- Frame 1: Left foot forward, right arm forward
- Frame 2: Standing straight
- Frame 3: Right foot forward, left arm forward
- Frame 4: Standing straight
- Move 4px per frame toward destination
- Path: straight line, avoid desks (simple A-to-B with one waypoint if needed)

**Hire Entrance**:
1. Door opens (2 frames, door sprite changes)
2. Agent walks from door to center of room (walking animation)
3. Agent pauses, fist-pump animation (arm raises 3 frames)
4. Agent walks to assigned desk
5. Sits at desk, begins idle animation

**Fire Exit**:
1. Agent stands from desk
2. Walks to door (walking animation)
3. Pauses at door, small wave (hand raises 2 frames)
4. Walks through door, disappears
5. Door closes

---

## State Injection

The HTML template receives state via a JavaScript variable placeholder:

```javascript
window.FORGE_STATE = __FORGE_STATE_PLACEHOLDER__;
```

When generating the visualization:
1. Read `assets/office-template.html`
2. Read `forge-state.json`
3. Replace `__FORGE_STATE_PLACEHOLDER__` with the JSON contents of forge-state.json
4. Write the result to `assets/office-live.html`
5. Serve via Claude Preview MCP or open in browser

The template reads `window.FORGE_STATE` on load and renders accordingly. If the state is empty or has no agents, render an empty office with just the door and a "The Forge — Hiring..." sign.

---

## Responsive Behavior

- **Minimum display**: 600×400px
- **Maximum display**: No hard limit — canvas grows with roster
- **HiDPI**: Render at 2x device pixel ratio for crisp pixels on Retina displays
- **No scrolling inside canvas**: The canvas is always sized to show the entire office. The page may scroll if the canvas exceeds viewport height.

---

## Visual Polish

These small details make the office feel alive:

- **Monitor screens flicker**: Subtle brightness variation every 2-3 seconds
- **Coffee station steam**: 2 pixel-high "steam" particles rise and fade above the coffee machine (2 frames)
- **Clock on wall**: Small pixel clock above the meeting room, shows actual time (updates every minute)
- **Ambient lighting**: Slight warm gradient overlay from top-left (simulating window light)
- **Department banners**: Small colored rectangles with department name in 6px pixel font
