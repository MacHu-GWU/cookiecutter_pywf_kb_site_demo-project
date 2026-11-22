# Editorial Ink Art: Visual Design Specification

## 1. Overview & Design Philosophy

**Editorial Ink Art** is a conceptual illustration language inspired by **Anthropic blog editorial art** and **The New Yorker spot illustrations**, augmented with a signature **Selective 3D Frosted-Glass Luminescence ("Ink-to-Light Accent")**.

Its core rule is the strict separation between:
- **What stays constant across every image (The Style Invariants)**: Muted Morandi earth-tone paper canvas, generous negative space (50%–65%), tactile 2D hand-drawn black ink linework with cross-hatching, and optional 3D translucent frosted-glass focal accents.
- **What changes with every article and section (The Visual Metaphor & Role)**: The concrete objects, spatial tension, and whether the image serves as a **Cover Image (Macro Thesis)** or a **Section Spot Illustration (Micro Argument)**.

---

## 2. Cover vs. Section Spot Illustrations (Role Differentiation)

Although Cover images and Section (H2) images share the same visual DNA, they play fundamentally different narrative roles and use different prompt structures:

| Dimension | Cover Illustration (`cover`) | Section Spot Illustration (`section`) |
| :--- | :--- | :--- |
| **Narrative Role** | **Macro Thesis / Overarching Tension**<br/>Synthesizes the central paradox or transformation of the entire article into one iconic scene. | **Micro Argument / Spot Art**<br/>Illustrates the single core idea of one H2 section, acting as an understated editorial margin sketch. |
| **Compositional Scale** | **Architectural / Dual-Pole Tension**<br/>Depicts a macro spatial relationship across two states, structures, or scales. | **Single-Object / Pair Close-Up**<br/>Focuses tightly on 1–2 concrete everyday or engineering objects in a moment of mechanical or conceptual tension. |
| **Rendering Mode** | **High Contrast (`Mode B` Recommended)**<br/>Usually pairs 2D matte black ink with a luminous 3D frosted-glass focal element to create an immediate visual hook for the article header. (`Mode A` pure 2D ink is also allowed for purely analytical pieces.) | **Rhythmic Alternation (~70% `Mode A` / ~30% `Mode B`)**<br/>Diagnostic, analytical, or problem-framing sections use **Mode A (Pure 2D Ink)**. Only 1–2 climax/breakthrough sections use **Mode B (Selective 3D Frosted-Glass Accent)**. |
| **Typography Policy** | **Zero Text Preferred (Minimal Labels Optional)**<br/>Always prefer a pure visual metaphor without text. Only if abstract concepts truly require anchoring may you include 1–2 ultra-short uppercase English keywords (≤ 2 words). | **Strictly Zero Text**<br/>Never include words, letters, numbers, or callout labels inside section illustrations. Let the visual metaphor speak for itself. |

---

## 3. Style Invariants (The Constant Visual DNA)

Every illustration in this style family must obey these four invariants:

### 3.1 Canvas & Background Palette
- **Solid, flat, muted Morandi / earth-tone paper background** with subtle warm grain. Never use pure white (`#FFFFFF`), pitch black (`#000000`), or noisy photographic backgrounds.
- **Generous negative space**: At least **50%–65%** of the 16:9 widescreen frame must remain open background so the central metaphor breathes.
- **Canonical Palette**:
  - **Sage Green** (`#8F9E8B` to `#A3B19B`) — calm, analytical, systemic.
  - **Warm Sand / Beige** (`#D8CFC2` to `#E5DEC9`) — humanistic, historical, structural.
  - **Muted Terracotta / Clay** (`#C87D65` to `#D48C70`) — urgent, diagnostic, paradigm-shifting.
  - **Slate Grey / Dusty Blue** (`#7A8B99` to `#8C9BA5`) — institutional, infrastructural, sober.
  - **Muted Ochre / Mustard** (`#C9A66B` to `#D4B475`) — economic, transitional, resource-focused.
- *Multi-image rhythm*: When generating multiple images for one article, rotate across 3–4 background tones from this palette so consecutive sections feel cohesive yet distinct.

### 3.2 Primary Medium: 2D Hand-Drawn Black Ink (`Mode A` Base)
- **Linework**: Expressive, slightly imperfect hand-drawn black felt-tip pen / fountain pen outlines (`#141413`).
- **Shading**: Fine architectural cross-hatching and organic stippling.
- **Subtle 2D Highlights**: Minimal flat warm ivory (`#F5F2EB`) or muted charcoal washes on key surfaces to give depth without breaking the 2D editorial flatness.

### 3.3 Optional Focal Medium: 3D Translucent Frosted Glass (`Mode B` Accent)
- **Material**: Subsurface-scattering matte acrylic / frosted quartz crystal with crisp chamfered geometric edges.
- **Internal Luminescence**: Soft, quiet internal gradient glow in **Cyan (`#00F0FF`)**, **Soft Lavender (`#A855F7`)**, or **Warm Amber/Magenta (`#FF6B9D`)**.
- **Restraint Rule**: Never turn the entire scene into a 3D neon render. The 3D frosted glass must occupy **only the single focal object** (15%–25% of the subject area), anchored inside or against the 2D hand-drawn black ink environment.

---

## 4. Conceptual & Structural Tension (Content-Driven Metaphor)

This skill defines **how the image is rendered (the brush, paper, and material)**, never **what must be drawn**. Do not restrict your imagination to fixed templates or repetitive clichés (such as drawing a "left messy black scribble pile -> middle funnel -> right glowing cubes" diagram every time).

Instead, follow three open-ended principles when inventing a visual metaphor for any article or section:

1. **Translate Abstract Claims into Physical Tension**:
   - Editorial conceptual art works by turning an abstract thesis into a tangible, physical moment of tension between 1–2 concrete everyday, architectural, or engineering objects.
   - Let the specific relationship (whether it is a gap, an imbalance, a mismatch, a replacement, a bottleneck, a counterweight, a lens, or any other spatial dynamic) emerge organically from the text's argument.
2. **One Idea, Minimal Props**:
   - Never crowd the frame with a multi-step Rube Goldberg machine or literal UI screens/charts. Use the fewest physical objects necessary to make the conceptual tension immediately legible at a glance.
3. **Zero Repetition Across an Article**:
   - Every image in a multi-section post must invent a completely fresh physical subject and spatial composition. Never reuse the same prop, container, or left-to-right pipeline across multiple sections.

---

## 5. Prompt Engineering Templates

Always write image generation prompts in English. Pick the template that matches the image role and rendering mode:

### Template 1: Cover Illustration (`Mode B` — 2D Editorial Ink + 3D Frosted-Glass Focal Bridge/Core)
> Minimalist editorial conceptual cover illustration combining 2D hand-drawn black ink sketch with a single 3D frosted-glass focal accent, on a solid muted `[background color]` paper background with generous negative space (50% empty canvas), 16:9 widescreen composition. `[Describe the macro 2D hand-drawn black ink scene and its structural tension using concrete physical objects]`. At the focal turning point of the scene, `[describe the single 3D translucent frosted-glass / matte acrylic geometric object emitting soft internal cyan, lavender, and magenta gradient glow]`. Stark, poetic material contrast between rough 2D matte black ink cross-hatching and the single quiet luminous 3D frosted-glass focal element, understated intellectual tone, completely text-free, no words, no letters, no numbers, no labels.

### Template 2: Section Spot Illustration (`Mode A` — Pure Anthropic 2D Editorial Ink, ~70% of sections)
> Minimalist editorial conceptual illustration in the style of Anthropic blog art and The New Yorker spot illustrations. A 2D hand-drawn black ink sketch with rough felt-tip pen and fine cross-hatching on a solid muted `[background color]` paper background with generous negative space (55% empty canvas), 16:9 widescreen. `[Describe 1-2 concrete physical objects in a moment of clear conceptual tension, using specific details and spatial relationships]`. Pure 2D hand-drawn matte black ink linework with subtle warm ivory highlights on key focal edges, understated intellectual tone, completely text-free, no words, no letters, no numbers, no 3D neon effects.

### Template 3: Section Spot Illustration (`Mode B` — 2D Editorial Ink + Selective 3D Frosted-Glass Accent, ~30% of sections)
> Minimalist editorial conceptual illustration combining 2D hand-drawn black ink sketch with a single 3D frosted-glass focal accent, on a solid muted `[background color]` paper background with generous negative space, 16:9 widescreen. `[Describe the primary scene and surrounding objects drawn in rough 2D black ink cross-hatching]`. At the focal point of the scene, `[describe the single specific object rendered in translucent 3D frosted glass and matte acrylic, emitting a soft internal cyan and lavender glow]`. Stark contrast between rough 2D matte black ink linework and the single quiet luminous 3D frosted-glass object, completely text-free, no words, no letters, no labels.

---

## 6. Pre-Flight Quality Checklist

Before accepting any generated image, verify:
1. **Unique Metaphor**: Does every image in the article use a distinct physical object and structural archetype (no repeated funnels, no repeated piles of black scribbles)?
2. **Mode Restraint**: Are most section images pure 2D ink (`Mode A`), reserving the 3D frosted-glass glow (`Mode B`) for the cover and 1–2 breakthrough sections?
3. **Text-Free Purity**: Is the image free of garbled text, unnecessary labels, or chart clutter?
4. **Breathing Room**: Does the solid muted earth-tone background occupy at least half of the 16:9 frame?
