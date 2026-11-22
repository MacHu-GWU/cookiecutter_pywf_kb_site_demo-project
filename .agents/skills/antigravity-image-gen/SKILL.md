---
name: antigravity-image-gen
description: "Quota-safe, context-isolated workflow for generating and iteratively editing images in Antigravity via the image-generator (Nano Banana 2 / gemini-3.1-flash-image) subagent. Enforces Model:'flash', one-shot no-self-retry calls, mandatory disk staging of every prompt and generated image under tmp/image-gen/, ImagePaths-based local refinement vs. full-prompt redraws, and main-session multimodal context isolation. Load whenever generating or editing any image."
---

# Antigravity Image Generation & Refinement (`antigravity-image-gen`)

## Why These Rules Exist (Quota & Context Mechanism)

1. **Unified Compute Pool**: Antigravity shares one **5-hour rolling + weekly compute quota pool** across both LLM multimodal tokens and `generate_image` (`gemini-3.1-flash-image` / Nano Banana 2) calls.
2. **$O(N^2)$ Multimodal Context Replay**: Every image returned by `generate_image` (inside `image-generator`) or opened via `read_file` is appended to that session's `transcript.jsonl` (`media` array) and re-sent to the session's LLM on **every subsequent turn**. Running `image-generator` on `"inherit"` (Pro/Opus/Argon), allowing internal self-retries, or repeatedly calling `read_file` in the main session rapidly drains the shared quota pool.

---

## 5 Hard Rules

### 1. Always Pass `Model: "flash"` to `image-generator`
Always invoke `image-generator` with explicit **`Model: "flash"`** (never `"inherit"`):
```json
{
  "TypeName": "image-generator",
  "Model": "flash",
  "Role": "Generate <slug> v<N>",
  "Prompt": "..."
}
```

### 2. One Image per Fresh Subagent (`No Self-Retry`)
- Launch a **fresh** `image-generator` subagent for every generation or edit. Never reuse an old `image-generator` via `send_message` across multiple iterations.
- Always append to the subagent prompt:
  > `"Call generate_image exactly ONCE and return the saved file path immediately. Do NOT self-retry or generate multiple versions inside this subagent."`

### 3. Persist Every Prompt & Every Image to `tmp/image-gen/`
Every generated image—including initial drafts, rejected retries, or candidates for user selection—MUST be saved to `<repo-root>/tmp/image-gen/`:
1. **Prompt to disk first (zero prompt loss)**: Before calling `image-generator`, write the complete prompt verbatim to `tmp/image-gen/<slug>.prompt.md` (or the task's dedicated `prompts.md`). Copy the exact prompt text into the subagent call—never summarize or omit style/negative constraints.
2. **Stage every output image immediately**: As soon as `image-generator` returns the brain artifact path (`/Users/.../.gemini/antigravity/brain/<conv-id>/...`), copy it into `tmp/image-gen/` with an explicit versioned name:
   ```bash
   mkdir -p tmp/image-gen
   cp "<artifact-image-path>" "tmp/image-gen/<slug>-v1.<ext>"
   ```
3. **Select, then move/convert**: Let the user or validation script inspect files in `tmp/image-gen/`. Once a candidate is chosen, copy/move or convert (`sips` / `imgsqueeze`) it from `tmp/image-gen/<slug>-v<N>.<ext>` to the final target path.

### 4. Iterative Refinement: Local Edit (`ImagePaths`) vs. Full Redraw
Because each `image-generator` subagent is isolated, never send a bare text delta without context. Choose the exact protocol based on what needs to change:

| Mode | When to Use | Pass `ImagePaths`? | Subagent Prompt Template (`Model: "flash"`, fresh subagent) |
| :--- | :--- | :---: | :--- |
| **A. Local Edit (Image-to-Image)** | Composition is good; only fixing specific details (remove unwanted text, fix an object/limb, change one item's color/size). | **YES**<br>`ImagePaths: ["/abs/path/to/tmp/image-gen/<slug>-v1.<ext>"]` | `Call generate_image ONCE (do not self-retry) with ImagePaths=["/abs/path/to/tmp/image-gen/<slug>-v1.<ext>"], AspectRatio="<ratio>", ImageName="<slug>_v2". Prompt: "Edit this image: <exact change>. Keep the composition, framing, characters, palette, and <style anchor> completely identical." Return the saved file path.` |
| **B. Full Redraw (Text-to-Image)** | Overall composition, complexity, or visual metaphor is wrong and must be redrawn from scratch. | **NO**<br>(Omit `ImagePaths` so the old layout does not lock the model) | First update the full prompt in `tmp/image-gen/<slug>.prompt.md` (keeping all style, palette, negative space, and `NO text` rules intact). Then pass the **entire updated prompt verbatim** to a fresh `image-generator` subagent. |

### 5. Main-Session `read_file` Discipline (Keep Main Context Clean)
- **User-guided edits (`0` reads)**: If the user has already looked at `tmp/image-gen/<slug>-v1.<ext>` and told you what to change, **do NOT call `read_file`** on the image in the main session—just pass its absolute path in `ImagePaths` (Mode A) or update the prompt (Mode B).
- **Scripted validation (`<= 1` read)**: Run deterministic check scripts first and inspect text/JSON output before opening a single diagnostic check image via `read_file`.
- **Batch generation (`self` `Model: "flash"` isolation)**: When generating and visually inspecting multiple images in one session, delegate the `image-generator` $\rightarrow$ `tmp/image-gen/` staging $\rightarrow$ `read_file` visual QA loop to a `self` (`Model: "flash"`) subagent so the main session keeps `media = 0`.
