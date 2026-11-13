# Output Examples

This file provides examples of different approaches to documenting design systems, drawn from real design teardowns. Use these as references for structure and detail level.

## Example 1: Technical Approach

Emphasizes specific values, CSS properties, and implementation details.

```markdown
# Design System Analysis

## Overview
Retro-futuristic aesthetic with playful, game-like interactions. "Weird > normal" philosophy with BIOS-style loading screens, voxel art, and whimsical animations.

## Color Palette

### Accent Colors
- **Pink Highlight**: `#F177A4` (text selection, emphasis)
- **Primary Blue**: `#4d65ff` (focus states)

### Theme System
**Dual-mode (Day/Night)**
- Text: Black in day mode, inverted in night
- Background: Dynamic based on theme
- Detection: Font-family based (Arial/Helvetica = day; Tahoma/Verdana/Segoe = night)

### Opacity Patterns
- Placeholders: `#000000` at `0.4` opacity
- Hidden: `opacity: 0`
- Visible: `opacity: 1`

## Typography

### Font Sizing (Responsive)
- Desktop: `1.25rem` base
- Tablet (≤991px): `0.8rem`
- Mobile: `calc(0.7494769874476988rem + 0.8368200836820083vw)`

### Rendering
- `-webkit-font-smoothing: antialiased`
- `text-rendering: optimizeLegibility`

## Components

### Cards
**Product Tiles**
- Hexagonal shape
- Hover: Image scales 1.05x

**Blog Cards**
- Featured entry highlighted
- Hover effect: `.blog-card:hover .featured-image { transform: scale(1.05) }`

## Animations

### Keyframe Animations
**Floating Animation**
- Duration: 10s infinite loop
- Y-translation: 0-1px
- Rotation: ±1deg subtle wobble

### Transform Patterns
- Hardware acceleration: `translate3d(0, 0, 0)` on all transforms
- Scale: `scale3d(0.85, 0.85, 1)` for modal/overlay reduction
- Hover scale: `scale(1.05)` for image emphasis
```

## Example 2: Narrative Approach

Emphasizes user experience, visual impression, and holistic understanding.

```markdown
# Design System Analysis

## Introduction
The site is a marketing presence for a software studio that makes playful 3D applications. The design mixes retro computer humor and modern web design. A full-screen BIOS-style boot sequence introduces the site before visitors reach a colorful, toy-like home page.

## Visual Theme & Aesthetics

### Retro Meets Modern
**3D voxel art** – The site uses custom voxel models (mailbox, bus, vintage television). These models mimic 8-bit games but are rendered smoothly, connecting nostalgia with modern 3D rendering.

**Blob typography** – The main hero displays the site name in inflated, blob-like lettering. This sculpture sits on clouds and stars, reinforcing the playful tone. In night mode the background switches to deep purple sky with tiny stars.

**Day/night theme toggle** – A toggle in the top-right lets users switch between bright sky-blue day and midnight-blue night themes. The color palette, stars, and hero copy shift during transition.

## Color Palette

| Role | Day palette | Night palette | Comments |
|------|-------------|---------------|----------|
| Background | Gradient sky blues (#A1D0F2–#E1EAF8) | Deep navy–purple (#0D1130–#1B1F54) | Provides contrast for pastel text |
| Primary accent | Vibrant pink for logotype and CTAs | Slightly desaturated orange | Draws attention to brand name |
| Interactive states | Blue button backgrounds with white text | Darker blues with lavender text | Consistent highlight for forms |

## Layout & Structure

### Hierarchical Sections
**Hero** – Large central headline with 3D logotype. Short mission statement framed by clouds.

**Products** – Cards with rounded corners showcase each product. Cards use isometric scenes as thumbnails with colored pills for product names. On hover, cards lift slightly and background image brightens.

**Footer** – Sign-up panel (email input + CTA), navigation list, and social media icons. Consistency across pages anchors the site.

## Typography
**Typefaces** – Modern geometric sans-serifs (Inter-like) for headings and body. Headings use bold weight with generous letter-spacing. BIOS preloader uses pixel-style monospaced font.

**Microcopy** – Conversational and humorous: "We read every email. Really." Calls to action use informal language.

## Interactive Elements

**Preloader BIOS** – Animated BIOS sequence with 1980s-style boot messages sets a playful tone before the polished UI appears.

**Card hover states** – Product cards elevate on hover and underlying image scales slightly, providing tactile feedback.

**Theme transition** – Toggling day/night switch gently fades backgrounds, clouds, and starfields. Colors of buttons and text change to maintain contrast.
```

## Choosing Your Approach

**Use Technical when:**
- DevTools provides specific CSS values
- Design has systematic spacing/sizing scales
- Target audience is frontend engineers
- Reproduction fidelity is critical

**Use Narrative when:**
- CSS values are inaccessible or overly complex
- Design prioritizes feel/impression over exact values
- Target audience includes designers/product
- Describing intent matters more than implementation

**Mix both:**
Most effective documentation combines both. Use technical details for foundation (colors, typography, spacing) and narrative for interactions, animations, and overall impression.

## Section Adaptability

Not every design system needs every section. Include sections based on what's present:

**Always include:**
- Overview/Introduction
- Color Palette (even if minimal)
- Typography
- Components

**Include if present:**
- Spacing & Layout (if systematic grid/spacing)
- Icons & Illustrations (if distinctive icon style)
- Interactions (if notable hover/focus states)
- Animations (if animations/transitions)
- Responsive Design (if multi-breakpoint)
- Brand Voice (if distinctive tone in copy)

**Skip if absent:**
- Don't create sections for features that don't exist
- Don't speculate about missing information
- Focus on what's observable
