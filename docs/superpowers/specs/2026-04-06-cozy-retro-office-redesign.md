# The Forge — Cozy Modern Retro Office Redesign

## Overview

Redesign the pixel art office visualization from arcade/neon to a cozy modern retro aesthetic inspired by RPG-style office art (Earthbound, early Pokemon). The goal: warm earthy tones, top-down oblique perspective, chibi characters, tile-based grid, cell shading, and rich environmental props.

## Decisions Made

- **Room layout**: Department-based rooms — each department gets its own visual zone with distinct floor color
- **Character quality**: Match reference — 32x48px chibi sprites with 4x4 eyes, warm brown outline, procedurally generated
- **Brand palette**: Warm amber forge branding (#D4763A title) with earthy office tones
- **Implementation approach**: Option C — keep LayoutEngine + state injection, rewrite SpriteEngine + SceneRenderer

## Technical Approach

Keep: `LayoutEngine`, state injection (`__FORGE_STATE_PLACEHOLDER__`), main loop, event system, HTML/CSS structure.

Rewrite: `SpriteEngine` (new chibi character at 32x48), `SceneRenderer` (warm palette, oblique furniture, department rooms, props).

File: `assets/office-template.html` (~1400 lines, self-contained).

## 1. Color Palette

### Walls & Background
| Token | Hex | Usage |
|-------|-----|-------|
| `wall` | `#2C2C3E` | Main wall fill (dark navy-charcoal) |
| `wallLight` | `#3B3B52` | Wall trim, baseboards |
| `wallAccent` | `#4A4060` | Wall panel detail |
| `bg` | `#1A1A2E` | Page background outside canvas |

### Floors (per zone type)
| Token | Hex | Usage |
|-------|-----|-------|
| `floorWood1` | `#8B7355` | Wood plank shade A |
| `floorWood2` | `#9B8365` | Wood plank shade B |
| `floorWood3` | `#7A6245` | Wood plank shade C |
| `floorTile1` | `#D4C4A8` | Break area tile light |
| `floorTile2` | `#C8B898` | Break area tile dark |
| `floorCarpet1` | `#4A6A8A` | Meeting room carpet |
| `floorCarpet2` | `#5A7A9A` | Meeting room carpet alt |

### Furniture
| Token | Hex | Usage |
|-------|-----|-------|
| `deskTop` | `#8B6640` | Desk top surface (lighter, seen from above) |
| `deskFront` | `#6B4C30` | Desk front panel (darker) |
| `deskShadow` | `#5B3C20` | Desk shadow/underside |
| `deskEdge` | `#A07850` | Desk edge highlight |
| `shelfWood` | `#5B4530` | Bookshelf frame |
| `shelfBack` | `#3D2E1A` | Bookshelf interior |
| `chairBrown` | `#5A4A3A` | Office chair |
| `chairCushion` | `#6B5A4A` | Chair cushion highlight |

### Character
| Token | Hex | Usage |
|-------|-----|-------|
| `outline` | `#2A1A10` | Warm brown character outline |
| `eyeWhite` | `#FFFFFF` | Eye sclera |
| `eyeIris` | `#2D1B4E` | Default iris (can vary) |
| `eyePupil` | `#1A1A1A` | Pupil |
| `eyeShine` | `#FFFFFF` | Specular highlight on eye |
| `highlight` | `#FFFFFF` | Specular dots on glass/screens |

### Brand
| Token | Hex | Usage |
|-------|-----|-------|
| `brand` | `#D4763A` | Title, warm amber accent |
| `brandDark` | `#B85A28` | Brand shadow |

## 2. Room/Zone Architecture

### Layout Rules

- **1 department**: Single room (wood floor) + break area (tile floor) side by side
- **2 departments**: Two rooms side by side + break area below-right (spanning bottom-right corner)
- **3+ departments**: Rooms fill left-to-right in a single row, break area always occupies the rightmost column
- **Department wall dividers**: 6px navy wall between rooms
- **Break area**: Always present — coffee machine, water cooler, fridge, plant

### Zone Floor Types

Each department room uses wood plank flooring by default. The break area uses beige tile. The meeting room (3+ agents) gets blue carpet inside the break area.

Department rooms can be differentiated by:
- A colored department banner on the wall (using existing dept color)
- Slight floor tint variation (optional — subtle hue shift per department)
- Different wall decorations per department

### Canvas Sizing

```
canvasW = max(520, PADDING*2 + deptCount * DEPT_COL_W + breakAreaW)
canvasH = max(400, PADDING + 60 + rows * CELL_H + 100)
```

- `DEPT_COL_W`: ~220px per department column
- `breakAreaW`: ~160px for break area
- `CELL_H`: ~130px per desk row (enough for bookshelf + desk + name tag)

## 3. Character Sprites

### Dimensions
- Pixel grid: 32 wide x 48 tall
- PX scale: 2 (each pixel = 2 screen pixels)
- Screen size: 64x96 pixels
- Constants: `SPRITE_W = 32`, `SPRITE_H = 48`

### Chibi Proportions

```
Rows 0-4:   Hair (extends above head, varies by style)
Rows 4-24:  HEAD (20 rows — 60% of visible sprite)
  4-8:      Forehead + hair front
  9-10:     Eyebrows (hair color, 3px wide each)
  11-14:    Eyes (4 rows, 4px wide each)
            - Row 11: top eyelid (outline color)
            - Row 12: white + iris top
            - Row 13: white + iris + pupil
            - Row 14: bottom (skin shadow)
  15:       Space
  16-17:    Nose (2px skin-dark block, slightly off-center)
  18-19:    Mouth (3px skin-deep line)
  20-24:    Chin, jaw, ears area
Rows 24-26: Neck (6px wide, skin with shadow)
Rows 26-38: BODY (12 rows)
  26-27:    Shoulders (20px wide, outfit color)
  27-28:    Collar/neckline (skin peek)
  28-36:    Torso (14px wide, outfit with shading + accent stripe)
  26-36:    Arms (3px wide each side)
Rows 36-48: LEGS (standing only)
  36-44:    Legs (5px wide each, dark pants)
  44-48:    Shoes (6px wide each, dark with highlight)
```

### Outline Method

Use filled silhouette approach (draw dark shape 1px larger, then character on top):
- Outline color: `#2A1A10` (warm dark brown)
- Creates natural 1px border on all edges
- Hair outline uses darker version of hair color

### Shading (4-tone per material)

For each material (skin, outfit):
1. `highlight` — right side, top edges (+20 lightness)
2. `mid` — main fill
3. `dark` — left side, under features (-25 lightness)
4. `deep` — creases, under-chin (-50 lightness)

### Seated vs Standing

**Seated** (default at desk):
- Head + torso visible above desk
- Arms forward in typing position, hands at keyboard
- Desk front panel covers waist down
- No legs drawn

**Standing** (for walking animations, meeting room):
- Full body with legs and shoes
- Arms at sides

### Auto-Scale Transform

Hair, accessory, and idle animation methods use a coordinate transform to map old positions to new sprite grid:
```javascript
const S = newPX_ratio; // scale factor
const tr = (x, y, w, h, color) => {
  this.rect(ox + Math.round((x-ox)*S), oy + Math.round((y-oy)*S),
    Math.max(Math.round(w*S),1), Math.max(Math.round(h*S),1), color);
};
```
This preserves all 18 hairstyles, 14 accessories, and 15 idle animations without rewriting each one.

## 4. Furniture (Top-Down Oblique Perspective)

### Desk

Shows top surface AND front face simultaneously:

```
Top surface: lighter wood (#8B6640), 80x12px
  - Visible from above angle
  - Items placed ON this surface (laptop, mug, notepad)
  - Edge highlight on top edge (#A07850)

Front face: darker wood (#6B4C30), 80x14px
  - Below the top surface
  - Wood grain texture (horizontal darker lines)
  - Drawer handle (centered, 16x2px metallic)
  - Side shadow on left edge (#5B3C20)

Legs: visible below front face, 4px wide dark wood
Shadow: dark rectangle on floor beneath desk
```

### Chair

```
Back: 48x32px warm brown, visible behind/around character shoulders
  - Cushion detail (lighter center)
  - Stitching lines (1px darker)
Posts: 3px wide connecting back to seat
Seat: visible below desk
Base: small cross-shape with wheel dots
```

### Bookshelf (wall-mounted, per desk area)

```
Frame: shelf wood color, 3 horizontal planks
Interior: darker wood background
Contents:
  - Top shelf: 5-6 books in varying colors and heights
  - Bottom shelf: 3-4 books + small potted plant
  - Book colors pulled from a warm palette array
  - 1px shadow on left edge of each book
```

## 5. Environmental Props

### Break Area (always present)

| Prop | Size | Description |
|------|------|-------------|
| Coffee machine | 20x28px | Dark body, red power light (blinks), steam animation, cups on counter |
| Water cooler | 14x30px | Blue/white body, specular white pixel on jug, small tap detail |
| Fridge | 20x36px | Gray body, handle, slightly open light glow (optional) |
| Counter/table | 52x20px | Brown wood, items on top |
| Potted plant | 12x18px | Terra cotta pot, green leaves extending above |

### Per-Desk Props (on desk surface)

| Prop | Description |
|------|-------------|
| Laptop | Open, screen with blue glow + green code lines, keyboard detail |
| Coffee mug | White ceramic, brown liquid, tiny steam wisps |
| Notepad | Cream paper, lined, scribble marks |
| Pen | Small red/blue cylinder |

### Wall Decorations

| Prop | Description |
|------|-------------|
| Framed art | Small landscape painting in brown frame (reference has one) |
| Wall clock | Working analog clock, dark frame, white face |
| Department banner | Colored banner with dept name in pixel font |
| Wall sconces | Warm light fixtures (optional, subtle) |

### Floor Plants

Potted plants scattered around the office (reference has 6+):
- 2-3 per department room
- Terra cotta or white pots
- Green leaves (2-3 shades for depth)
- Placed at room corners and beside furniture

## 6. Shading & Rendering Rules

### Cell Shading (no gradients)
- All shading uses flat block colors
- Shadow = darker tone placed as a solid rectangle (left side, bottom)
- Highlight = lighter tone placed as a solid rectangle (right side, top)
- No CSS gradients, no canvas gradients

### Shadow Placement
- Every piece of furniture casts a floor shadow (dark semi-transparent rectangle, offset 2-4px down-right)
- Characters do NOT cast shadows (too complex, not in reference)

### Specular Highlights
- Single white pixels on: monitor screens, water cooler jug, coffee machine buttons, window glass
- Creates the "plastic/glass surface" look from the reference

### Animation
- Idle animations: per-agent (scribbling, sipping, etc.) — preserved from current
- Screen glow: subtle brightness oscillation on laptop screens
- Coffee steam: 2-3 white pixels floating up, cycling position
- Clock: real-time analog hands
- Blinking: eyes blink every ~3.5 seconds

## 7. What Stays the Same

- `forge-state.json` schema and state management
- `LayoutEngine` class (with updated constants for new cell sizes)
- State injection via `__FORGE_STATE_PLACEHOLDER__`
- Event system (working, meeting, hiring states)
- HTML structure (canvas + title + subtitle + roster)
- Font choices (Press Start 2P for headers, VT323 for body)
- `prefers-reduced-motion` accessibility support
- Preview server setup (`.claude/launch.json`)

## 8. Success Criteria

The redesigned office should:
1. Feel cozy, warm, and nostalgic — not arcade or clinical
2. Characters are immediately recognizable with distinct personalities
3. Each department room feels like its own space
4. Props are readable at a glance (you know what everything is)
5. The overall scene matches the warmth and density of the reference image
6. All existing functionality preserved (hiring, firing, meeting room, animations)
