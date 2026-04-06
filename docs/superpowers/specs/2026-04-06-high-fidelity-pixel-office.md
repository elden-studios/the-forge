# High-Fidelity Pixel Art Office — Stardew Valley Quality

## Overview

Complete visual rewrite of The Forge office from basic procedural rectangles to high-fidelity pixel art rendered entirely with Canvas API. Inspired by Stardew Valley and Eastward: 4-level shadow depth, dithering, thick walls with shadow casting, distinct floor textures, rich props, and environmental storytelling.

## Approach

Procedural Canvas `fillRect` pushed to its maximum. Every surface gets per-pixel treatment: dithering for gradients, computed 4-tone shading from a consistent top-left light source, and hand-tuned proportions for every prop.

File: `assets/office-template.html` — complete rewrite of SceneRenderer + PixelArtEngine + enhanced SpriteEngine. LayoutEngine rewritten for grid floorplan.

## 1. Floorplan Layout

2x3 grid of department rooms connected by a central hallway. Break room attached at bottom-right.

```
┌─────────────────┬─────────────────┬─────────────────┐
│                 │                 │                 │
│    STRATEGY     │    RESEARCH     │     DESIGN      │
│  (exec carpet)  │   (linoleum)    │  (wood plank)   │
│     Flint       │  Vex, Nyx, Echo │  Ren, Sable     │
│                 │                 │                 │
├──[door]─────────┼──[door]─────────┼──[door]─────────┤
│                CENTRAL HALLWAY (tile)               │
│  [bench] [vending] [cooler] [signs] [extinguisher]  │
├──[door]─────────┼──[door]─────────┼──[door]─────────┤
│                 │                 │                 │
│     GROWTH      │   ENGINEERING   │    CONTENT      │
│   (linoleum)    │   (concrete)    │  (soft carpet)  │
│     Talon       │     Atlas       │     Kira        │
│                 │                 │                 │
└─────────────────┴─────────────────┴──[door]─────────┤
                                    │                 │
                                    │   BREAK ROOM    │
                                    │  (kitchen tile)  │
                                    │                 │
                                    └─────────────────┘
```

### Dimensions (in screen pixels)

- Each room: 200w x 160h
- Central hallway: full width x 48h
- Thick walls: 8px wide with visible top face + front face + shadow
- Doors: 32px wide opening in the wall, with frame detail
- Total canvas: ~640w x ~420h (plus break room extension)
- Tile base: T = 16px grid throughout

### Room Positioning

```javascript
const ROOM_W = 200;
const ROOM_H = 160;
const HALL_H = 48;
const WALL = 8;

// Row 0 (top): Strategy, Research, Design
// Hallway
// Row 1 (bottom): Growth, Engineering, Content
// Break room: attached to Content's south wall
```

## 2. Pixel Art Engine (new utility class)

### Color Computation

Every color gets 4 tones computed once and cached:

```javascript
class PixelArtEngine {
  shadow4(baseColor) {
    return {
      hi:   lighten(baseColor, 35),   // top-left lit edges
      mid:  baseColor,                 // main fill
      sh:   darken(baseColor, 25),     // bottom-right edges
      deep: darken(baseColor, 50)      // under furniture, wall bases
    };
  }
}
```

### Dithering

Checkerboard pixel blend for material transitions:

```javascript
dither(ctx, x, y, w, h, colorA, colorB) {
  for (let py = y; py < y + h; py++) {
    for (let px = x; px < x + w; px++) {
      ctx.fillStyle = ((px + py) % 2 === 0) ? colorA : colorB;
      ctx.fillRect(px, py, 1, 1);
    }
  }
}
```

Used for: carpet texture, concrete speckle, wood grain transitions, shadow edges.

### Light Source

Global top-left (northwest). Applied uniformly:
- **Top edges** of objects: highlight
- **Left edges**: highlight or midtone
- **Right edges**: shadow
- **Bottom edges**: shadow or deep shadow
- **Floor shadow**: cast to bottom-right, 4-6px offset, deep shadow color at 20% opacity

### Wall Rendering

8px thick walls with 3D depth:

```
   ┌─────────── highlight (top face, 2px)
   │ ┌───────── midtone (front face, 4px)
   │ │ ┌─────── shadow (right edge, 2px)
   │ │ │
   ███████████
   ███████████  ← top face (lit)
   ███████████
   ███████████  ← front face
   ███████████
   ▓▓▓▓▓▓▓▓▓▓  ← shadow on floor (cast right and down)
```

Wall color: `#3A3A4E` base → 4 tones via shadow4()

### Door Rendering

32px gap in wall with visible door frame:
- Frame: 2px border in `#6B5230` (wood frame)
- Open doors: empty gap with floor visible through
- Threshold: slight color change on floor tiles at doorway

## 3. Floor Textures

Each department has a unique procedural floor pattern drawn per-tile (16x16).

### Executive Carpet (Strategy, Content)

```
Base: #6B4040 (deep red-brown)
Pattern: Woven cross-hatch
- Horizontal lines every 4px in shadow tone
- Vertical lines every 4px in shadow tone
- Intersection points in highlight tone
- Dithered edge between carpet and wall (carpet meets wall shadow)
```

### Linoleum (Research, Growth)

```
Base: #A0A0A0 (neutral gray) / #90A090 (slight green tint for Growth)
Pattern: Clean smooth with subtle reflection
- Slight diagonal streak every 8px (highlight, 1px wide)
- Tile grid lines every 16px in shadow tone
- Corner dots at grid intersections (deep shadow)
```

### Wood Plank (Design)

```
Base: #8B7355 (warm brown)
Pattern: Horizontal planks 8px tall, staggered
- Grain lines: 1px dark lines at y+3 and y+6 within each plank
- Knot detail: occasional 2x2 dark circle (every ~5th plank)
- Plank gap: 1px deep shadow between planks
- Stagger: alternate rows offset by half plank width
```

### Concrete (Engineering)

```
Base: #808088 (cool gray)
Pattern: Industrial speckle
- Dithered random lighter pixels (~15% coverage) for texture
- Subtle crack line (1px dark) every ~80px
- Slightly darker near walls (shadow gradient via dithering)
```

### Kitchen Tile (Break Room)

```
Base: #E0D8C8 (warm cream)
Pattern: Square tiles with grout
- 16x16 tiles with 1px grout lines in shadow tone
- Each tile has a subtle highlight on top-left 2px corner
- Alternating tiles slightly different shade for checkerboard
- Diamond accent on every 4th tile (2x2 rotated square in midtone)
```

### Hallway Tile

```
Base: #C8C0B0 (neutral warm)
Pattern: Larger tiles (24x24) with grout
- Grout lines in shadow tone
- Occasional tile with slight color variation
- Directional arrows painted on floor near doors (subtle)
```

## 4. Props Catalog

Every prop drawn with 4-tone shading and top-left light consistency.

### Universal Props (every room)

| Prop | Size | Details |
|---|---|---|
| Office desk | 48x28 | Wood top (visible surface + front face), legs, shadow underneath. Items: monitor, keyboard, mouse, coffee mug |
| Monitor | 20x16 | Dark bezel, blue-lit screen with code/content lines, specular highlight on glass, power LED |
| Office chair | 24x20 | Cushion with highlight, back visible behind agent, wheels at base |
| Bookshelf | 32x40 | Wood frame with 3 shelves, colored book spines (6-8 books), small plant on top shelf |
| Potted plant | 12x20 | Terra cotta pot (4-tone), green leaves (3 shades), stem, soil visible at pot top |
| Ceiling light | 24x8 | Fixture on ceiling, warm glow cone on floor (dithered gradient, 40x40 area) |
| Wall clock | 12x12 | Dark frame, cream face, hour marks, real-time hands |

### Department-Specific Props

| Dept | Props |
|---|---|
| Strategy | Whiteboard (40x30, with colored sticky notes + marker tray), Lean Canvas poster (16x20, framed), extra chair (for visitors) |
| Research | Dual monitor setup, wall-mounted data chart (bar chart in pixel art), paper stack on desk, magnifying glass prop |
| Design | Color swatch strip on wall (8 colored squares), Wacom tablet on desk (dark pad + stylus), moodboard (pinned images), Pantone fan |
| Growth | Dashboard screen (larger monitor with metrics/graphs), phone on desk, coffee cup collection (3 mugs), metrics poster with arrows |
| Engineering | Server rack (20x48, blinking LEDs), terminal screen (green-on-black), cables on floor (gray squiggly lines), rubber duck on desk |
| Content | Book stack (5 books piled), microphone on stand, notepad pile (3 stacked), pen cup, inspirational quote poster |

### Hallway Props

| Prop | Size | Details |
|---|---|---|
| Bench | 40x16 | Wood seat, metal legs, shadow underneath |
| Vending machine | 24x44 | Dark body, lit display panel, product rows visible, coin slot, brand sticker |
| Water cooler | 16x32 | Blue jug on top (specular highlight), white body, tap, paper cup dispenser, drip tray |
| Directional sign | 16x20 | Pole + arrow signs pointing to departments |
| Fire extinguisher | 8x16 | Red body, wall-mounted bracket, small label |

### Break Room Props

| Prop | Details |
|---|---|
| Coffee machine | Large, dark body, drip area, red power LED, steam wisps, cup underneath |
| Fridge | Tall gray, handle, slight door gap glow, magnets on front |
| Microwave | Small box on counter, green LED clock, door handle |
| Small table | Round, 4 chairs around it, salt/pepper shakers on top |
| Snack counter | Long surface with fruit bowl, napkin holder, condiment rack |
| Sink | Wall-mounted, faucet detail, small window above it |

## 5. Environmental Storytelling Details

Small per-pixel details that make the office feel lived-in:

- **Sticky notes on monitors**: 2-3 colored squares on the side of screens
- **Half-eaten lunch on break table**: Small bento/plate with food pixels
- **Coat on a chair back**: Extra colored pixels draped over one chair
- **Coffee rings on desk**: Subtle brown circle mark on one desk surface
- **Open book on someone's desk**: Small book shape with visible pages
- **Cables on Engineering floor**: Gray 1px lines running between desk and server rack
- **Whiteboard markers in tray**: 3-4 colored dots at bottom of whiteboard
- **Photos on desk**: Tiny framed rectangle with colored contents
- **Trash bin near desk**: Small can with paper peeking out
- **Shoes under desk**: Tiny colored pixels under one desk (someone kicked them off)

## 6. Character Sprite Enhancement

Same 16x24 CPX=3 grid, but richer detail:

### 4-Tone Skin Shading
- Highlight: forehead center, nose bridge, top of cheeks (lit by top-left)
- Midtone: main face fill
- Shadow: under chin, right side of face, under eyebrows
- Deep shadow: neck, under hair overlap

### Clothing Detail
- 1-2px fold lines on torso (darker than outfit)
- Collar detail (skin peek + collar edge pixel)
- Sleeve edge: highlight on outer edge (top-left light)
- Button or zipper detail: 1px accent dots

### Hair Enhancement
- Highlight streak: 2-3px lighter line on top of hair (light reflection)
- Volume pixels: extra pixels extending beyond head outline for hair body
- Shadow at base: where hair meets forehead

### Eye Enhancement
- Iris color pixel: add department-accent-influenced iris color
- Larger eye whites for more expressiveness
- Eyebrow emphasis: thicker (2px) for more character

## 7. Implementation Architecture

### New Classes

```
PixelArtEngine     — color math, dithering, shadow computation, lighting
FloorplanEngine    — grid layout, room positions, wall segments, doors
FloorRenderer      — per-department floor texture drawing
WallRenderer       — thick wall drawing with depth and shadow casting
PropRenderer       — 25+ individual prop drawing functions
SpriteEngine       — enhanced character sprites (existing, upgraded)
SceneRenderer      — orchestrates all renderers in correct draw order
```

### Draw Order (back to front)

1. Floor textures (all rooms + hallway)
2. Wall shadows on floor
3. Ceiling light glow cones on floor
4. Furniture shadows on floor
5. Back walls (top walls of rooms)
6. Side walls
7. Furniture (back to front within each room)
8. Desk back surfaces + items
9. Characters (at their animated positions)
10. Desk front panels (covers seated character's lower body)
11. Front walls (bottom walls, in front of everything)
12. UI overlays (name tags, department labels)

### File Size Estimate

~1500-2000 lines for the full implementation. The prop catalog alone is ~500 lines. Floor textures ~200 lines. Walls ~150 lines. Characters ~300 lines. Layout + orchestration ~300 lines.

## 8. What Stays the Same

- `forge-state.json` schema (agents, departments, events)
- State injection via `__FORGE_STATE_PLACEHOLDER__`
- Animation state machine (coffee walks, chat walks)
- Agent collaboration protocol
- HTML/CSS structure
- Font choices
- `prefers-reduced-motion` support
- Preview server setup

## 9. Success Criteria

1. Every surface has visible 4-tone shadow depth
2. Walls have visible thickness (8px) with top face + front face + shadow
3. Each department has a distinct, recognizable floor texture
4. At least 5 unique props visible in each department room
5. Hallway has furniture (bench, vending machine, cooler)
6. Break room has kitchen equipment (coffee machine, fridge, table)
7. At least 3 environmental storytelling details (sticky notes, coffee rings, etc.)
8. Characters have visible clothing folds and 4-tone skin shading
9. Consistent top-left light source across all elements
10. Dithering visible on at least: carpet texture, ceiling light glow, concrete speckle
11. The scene feels cohesive — like one artist drew the entire thing
