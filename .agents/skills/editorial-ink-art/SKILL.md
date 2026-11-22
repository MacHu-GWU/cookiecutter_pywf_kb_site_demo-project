---
name: editorial-ink-art
description: "Cross-repo conceptual editorial illustration style skill: Anthropic minimalist hand-drawn black ink + selective 3D frosted-glass luminescence (Ink-to-Light Accent). Defines cover vs. section spot-art differentiation, palette invariants, conceptual tension principles, and prompt templates. Use whenever generating editorial cover images or section spot illustrations for articles, blogs, or essays."
---

# Editorial Ink Art

Self-contained visual design language for generating **Cover Illustrations** and **Section Spot Illustrations** in the **Anthropic Editorial Ink + Selective 3D Frosted-Glass Accent** style. This skill is repository-agnostic and can be copied into any blog or documentation repository.

## Reference Specification

Read [references/style-spec.md](references/style-spec.md) before crafting any image generation prompt. It defines:

1. **Cover vs. Section Role Differentiation** (Section 2):
   - **Cover (`cover`)**: Macro thesis / architectural tension, typically using `Mode B` (2D black ink + 3D glowing frosted-glass focal element). Prefer zero text; allow at most 1–2 short uppercase English keywords only if strictly necessary.
   - **Section (`section`)**: Micro argument / *The New Yorker* spot art focusing on 1–2 concrete everyday or engineering objects. Strictly zero text. Uses rhythmic alternation (~70% `Mode A` pure 2D ink for diagnostic/analytical sections; ~30% `Mode B` selective 3D frosted-glass accent for breakthrough/solution sections).
2. **Style Invariants** (Section 3):
   - Solid muted Morandi earth-tone paper canvas (Sage Green, Warm Sand Beige, Terracotta Clay, Slate Grey, Muted Ochre) with 50%–65% negative space.
   - Expressive 2D hand-drawn black felt-tip ink outlines and fine cross-hatching.
   - Optional 3D translucent frosted glass with soft internal cyan, lavender, and magenta glow restricted to the single focal object.
3. **Conceptual & Structural Tension Principle** (Section 4):
   - Translate the text's abstract argument into a clear moment of physical or structural tension using concrete objects invented freely from the article's context. Never repeat the same physical prop or composition across multiple images in one article.
4. **Prompt Engineering Templates & Quality Checklist** (Sections 5–6).

## How to Use

1. **Analyze the text**: Identify whether you are generating a **Cover** (whole-article thesis), a **Section Spot Illustration** (single H2 argument), or a **Full-Article Visual Plan** (Cover + selected H2s).
2. **Design the Visual Plan Table**:
   - Assign a distinct **Background Palette Tone** (rotating across 3–4 Morandi tones so adjacent images never clash).
   - Assign the **Rendering Mode** (`Mode B` for Cover and 1–2 climax H2s; `Mode A` pure 2D ink for diagnostic/analytical H2s).
   - Invent a unique **Concrete Visual Metaphor** (1–2 specific physical objects in a moment of conceptual tension).
3. **Construct the English Prompt**: Fill in the corresponding template from [references/style-spec.md](references/style-spec.md) Section 5.
4. **Generate & Inspect**: Invoke the `image-generator` subagent (or image generation tool) and visually inspect the output against Section 6 of [references/style-spec.md](references/style-spec.md).
