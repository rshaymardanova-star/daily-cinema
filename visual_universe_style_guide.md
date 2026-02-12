# Daily Cinema - Visual Universe Style Guide

## 1. Visual Philosophy

**"Human in harmony with cosmic energy."**

The world is mystical, luminous, ethereal, and spiritual.
Magic is natural. Light is a living substance.
Characters interact with energy peacefully and consciously.

**Tone:** calm, meditative, epic, transcendent.

---

## 2. Color Palette

### Primary Palette
- Spectral gradients (pink -> blue -> turquoise -> yellow -> violet)
- Neon glow
- Soft pastel fog
- Pearlescent highlights
- Cosmic deep blues

### Rules
- Gradients must be smooth and organic
- Light must feel volumetric and alive
- Colors should blend like energy, not paint
- Avoid harsh shadows unless narratively required
- Prefer soft transitions and atmospheric diffusion

### Implementation Reference
| Color Role | Hex Range | Usage |
|---|---|---|
| Cosmic Deep Blue | `#0a0a2e` - `#1a1a4e` | Background base |
| Spectral Pink | `#ff69b4` - `#ff1493` | Energy accents |
| Ethereal Turquoise | `#40e0d0` - `#00ced1` | Aura highlights |
| Neon Violet | `#8a2be2` - `#9400d3` | Mystical glow |
| Pearlescent Gold | `#ffd700` - `#ffb347` | Warm highlights |
| Pastel Fog | `#e6e6fa` - `#dcd0ff` | Atmospheric haze |

---

## 3. Lighting Rules

**Light is the main character.**

### Lighting Must Be
- Soft, diffused, volumetric
- Glowing, radiant, spectral
- Interacting with characters (aura, rimlight, energy flow)
- Atmospheric (fog, mist, bloom)
- Emotionally expressive (light reflects inner state)

### Types of Light
- Neon mist
- Cosmic aura
- Spectral glow
- Emissive energy surfaces
- Rainbow diffraction
- Volumetric god rays

### Rules
- Light should feel like a physical presence
- Light should wrap around characters
- Emissive materials must contribute to global illumination

---

## 4. Characters

### Appearance
- Calm, centered, meditative
- In harmony with the environment
- Connected to energy sources

### Poses
- Open, grounded, ritualistic, slow
- Minimal aggressive or chaotic motion
- Silhouettes must remain readable

### Clothing
- Flowing, translucent, iridescent
- Soft glow or emissive accents
- Materials that react to light (pearlescent, refractive)

---

## 5. Creatures & Mythology

### Mythical Beings Must Be
- Luminous
- Ancient
- Wise
- Non-aggressive
- Integrated with the environment

### Features
- Spectral scales or surfaces
- Glowing eyes
- Volumetric light emission
- Soft neon reflections
- Slow, deliberate movement

### Rules
- Creatures should feel like guardians or guides
- Avoid horror or grotesque elements

---

## 6. Atmosphere

### Atmosphere Must Be
- Foggy, soft, cosmic
- Filled with light particles
- Dreamlike and meditative
- Layered with depth and volumetric scattering

**Mood:** "quiet epicness."

### Rules
- Use atmospheric perspective to create scale
- Haze and fog should blend with spectral light

---

## 7. Camera & Composition

### Camera
- Wide shots
- Slow movement
- Static or meditative framing
- Cinematic depth of field (soft, shallow)
- Gentle lens diffusion

### Composition
- Centered subjects
- Symmetry
- Minimalism
- Lots of negative space
- Characters framed by light sources

### Rules
- Avoid clutter
- Prioritize emotional clarity over realism

---

## 8. ML Generation Requirements

### ML Outputs Must Support
- Neon spectral gradients
- Glowing textures
- Volumetric light
- Cosmic fog
- Rainbow diffraction
- Magical energy effects
- Iridescent materials
- Soft atmospheric haze

### Recommended Prompt Keywords
- "ethereal light"
- "spectral glow"
- "neon mist"
- "cosmic aura"
- "transcendent energy"
- "mythical harmony"
- "iridescent fabric"
- "volumetric fog"
- "dreamlike atmosphere"

### Rules
- Avoid harsh contrast unless narratively required
- Prioritize soft, luminous, meditative visuals

### Style Presets (ML Models)

| Preset | Description | Base Palette | Mood |
|---|---|---|---|
| `ethereal_default` | Standard ethereal cosmic style | Deep blue + spectral gradients | Meditative calm |
| `cosmic_cinematic` | High-contrast cinematic cosmic | Dark cosmic + neon accents | Epic transcendence |
| `luminous_dreamscape` | Soft dreamy pastels | Pastel fog + pearlescent | Dreamlike serenity |
| `spectral_mythology` | Mythical creature-focused | Spectral scales + glow | Ancient wisdom |
| `neon_ritual` | Ritualistic energy ceremony | Neon violet + gold | Spiritual ritual |

---

## 9. Unity HDRP Requirements

### HDRP Must Include
- Volumetric fog
- Strong but soft bloom
- Chromatic aberration (subtle)
- Lens diffusion
- Emissive materials
- Atmospheric perspective
- Light scattering
- High-quality volumetrics
- Color grading with spectral highlights

### Materials
- Translucent
- Iridescent
- Glowing
- Refractive
- Emissive with spectral gradients

### Camera Settings
- Wide FOV (but not distorted)
- Soft DOF
- Slight vignette
- Gentle film grain (optional)

### Lighting
- Multiple volumetric light sources
- Emissive-driven GI
- Soft shadows
- Spectral rimlight

### HDRP Template Profiles

| Template | Bloom | Fog Density | Vignette | Chromatic Aberration | Color Grading |
|---|---|---|---|---|---|
| `ethereal_default` | 0.8, soft | 0.15 | 0.25 | 0.08 | Spectral lift in shadows |
| `cosmic_cinematic` | 1.0, anamorphic | 0.25 | 0.35 | 0.12 | Deep blue shadows, neon highlights |
| `luminous_dreamscape` | 1.2, gaussian | 0.30 | 0.20 | 0.05 | Pastel color shift |
| `spectral_mythology` | 0.9, soft | 0.20 | 0.30 | 0.10 | Warm gold + cool blue split |
| `neon_ritual` | 1.1, anamorphic | 0.18 | 0.40 | 0.15 | Neon-saturated highlights |

---

## 10. Global Rules

1. Light is alive.
2. Energy interacts with characters.
3. Magic is natural, not violent.
4. Atmosphere is soft and cosmic.
5. Colors are spectral and glowing.
6. Composition is minimalistic and meditative.
7. Characters are in harmony, not conflict.
8. Movement is slow, intentional, ritualistic.
9. Visuals must evoke transcendence, not chaos.
10. The world must feel like a luminous spiritual realm.

---

## Integration Points

### Pipeline Flow with Visual Universe

```
User Prompt
    |
    v
[Style Selection] --> visual_style parameter (ethereal_default, cosmic_cinematic, etc.)
    |
    v
[ML Generation] --> prompt enriched with style keywords + palette applied to frames
    |
    v
[Unity HDRP Render] --> HDRP profile loaded (bloom, fog, DOF, color grading per style)
    |
    v
[FFmpeg Post-Processing] --> color grading overlay, vignette, film grain per style
    |
    v
Final Output (consistent visual universe aesthetic)
```

### API Usage

```bash
# Create project with visual style
curl -X POST http://localhost:8000/projects \
  -H "X-API-Key: dc-prod-api-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cosmic Journey",
    "visual_style": "cosmic_cinematic",
    "shots": [
      {"prompt": "ancient guardian emerging from starlight", "order": 1},
      {"prompt": "luminous temple with spectral energy flow", "order": 2}
    ]
  }'

# Start render (style is applied automatically from project)
curl -X POST http://localhost:8000/projects/{id}/render \
  -H "X-API-Key: dc-prod-api-key-change-me"
```

---

## 11. Style Endpoints Reference

### Purpose

Every service in the Daily Cinema pipeline exposes a `/styles` endpoint so that clients and operators can discover which visual styles are available, inspect their configuration, and validate a style before submitting a render. The endpoints are read-only (except the backend validation POST) and never trigger ML inference or Unity rendering.

| Service | Endpoint | Method | Description |
|---|---|---|---|
| Backend (`:8000`) | `GET /styles` | GET | List available styles with default and current ACU mode |
| Backend (`:8000`) | `POST /styles/validate` | POST | Validate a style name and return its full ML + HDRP + FFmpeg configuration |
| ML Module (`:8001`) | `GET /styles` | GET | List styles with descriptions and ML prompt keywords |
| Unity Worker (`:8002`) | `GET /styles` | GET | List styles with HDRP profile summaries (bloom, fog) |

### Retrieving Available Styles

#### Backend — `GET /styles`

```bash
curl http://localhost:8000/styles \
  -H "X-API-Key: dc-prod-api-key-change-me"
```

Response:

```json
{
  "styles": [
    "ethereal_default",
    "cosmic_cinematic",
    "luminous_dreamscape",
    "spectral_mythology",
    "neon_ritual"
  ],
  "default": "ethereal_default",
  "acu_mode": "full"
}
```

#### ML Module — `GET /styles`

```bash
curl http://localhost:8001/styles
```

Response:

```json
{
  "styles": {
    "ethereal_default": {
      "description": "Standard ethereal cosmic style - meditative calm",
      "keywords": ["ethereal light", "spectral glow", "volumetric fog", "dreamlike atmosphere"]
    },
    "cosmic_cinematic": {
      "description": "High-contrast cinematic cosmic - epic transcendence",
      "keywords": ["cosmic aura", "transcendent energy", "neon mist", "spectral glow"]
    },
    "luminous_dreamscape": {
      "description": "Soft dreamy pastels - dreamlike serenity",
      "keywords": ["dreamlike atmosphere", "iridescent fabric", "ethereal light", "mythical harmony"]
    },
    "spectral_mythology": {
      "description": "Mythical creature-focused - ancient wisdom",
      "keywords": ["mythical harmony", "spectral glow", "cosmic aura", "volumetric fog"]
    },
    "neon_ritual": {
      "description": "Ritualistic energy ceremony - spiritual ritual",
      "keywords": ["transcendent energy", "neon mist", "cosmic aura", "spectral glow"]
    }
  },
  "default": "ethereal_default"
}
```

#### Unity Worker — `GET /styles`

```bash
curl http://localhost:8002/styles
```

Response:

```json
{
  "styles": {
    "ethereal_default": {
      "description": "Ethereal cosmic - soft bloom, volumetric fog, spectral grading",
      "bloom": 0.8,
      "fog": 0.15
    },
    "cosmic_cinematic": {
      "description": "Cosmic cinematic - anamorphic bloom, deep fog, neon grading",
      "bloom": 1.0,
      "fog": 0.25
    },
    "luminous_dreamscape": {
      "description": "Luminous dreamscape - gaussian bloom, heavy fog, pastel grading",
      "bloom": 1.2,
      "fog": 0.30
    },
    "spectral_mythology": {
      "description": "Spectral mythology - warm/cool split, medium fog, gold-blue grading",
      "bloom": 0.9,
      "fog": 0.20
    },
    "neon_ritual": {
      "description": "Neon ritual - anamorphic bloom, neon-saturated grading",
      "bloom": 1.1,
      "fog": 0.18
    }
  },
  "default": "ethereal_default"
}
```

### Validating a Style — `POST /styles/validate`

This backend endpoint resolves a style name and returns the full pipeline configuration without running any ML inference or Unity rendering. Invalid or unknown styles are resolved to `ethereal_default`.

```bash
curl -X POST http://localhost:8000/styles/validate \
  -H "X-API-Key: dc-prod-api-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{"visual_style": "cosmic_cinematic"}'
```

Response (valid style):

```json
{
  "valid": true,
  "visual_style": "cosmic_cinematic",
  "resolved_style": "cosmic_cinematic",
  "ml_keywords": ["cosmic aura", "transcendent energy", "neon mist", "spectral glow"],
  "hdrp_preset": {
    "bloom_intensity": 1.0,
    "fog_density": 0.25,
    "vignette_intensity": 0.35,
    "chromatic_aberration": 0.12
  },
  "ffmpeg_preset": {
    "fps": 30,
    "preset": "slow",
    "crf": 18
  },
  "acu_mode": "full"
}
```

Response (invalid style — fallback):

```bash
curl -X POST http://localhost:8000/styles/validate \
  -H "X-API-Key: dc-prod-api-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{"visual_style": "nonexistent_style"}'
```

```json
{
  "valid": false,
  "visual_style": "nonexistent_style",
  "resolved_style": "ethereal_default",
  "ml_keywords": ["ethereal light", "spectral glow", "neon mist", "volumetric fog", "dreamlike atmosphere"],
  "hdrp_preset": {
    "bloom_intensity": 0.8,
    "fog_density": 0.15,
    "vignette_intensity": 0.25,
    "chromatic_aberration": 0.08
  },
  "ffmpeg_preset": {
    "fps": 24,
    "preset": "medium",
    "crf": 20
  },
  "acu_mode": "full"
}
```

### Overriding `visual_style` Per Project

The `visual_style` is set at project creation time and applies to every shot in that project. If omitted or invalid, it defaults to `ethereal_default`.

```bash
curl -X POST http://localhost:8000/projects \
  -H "X-API-Key: dc-prod-api-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Neon Ceremony",
    "visual_style": "neon_ritual",
    "shots": [
      {"prompt": "glowing figures in ritualistic circle", "order": 1}
    ]
  }'
```

The style is stored on the `Project` record and cannot be changed after creation. To use a different style, create a new project.

| `visual_style` value | Behavior |
|---|---|
| Valid name (e.g. `"cosmic_cinematic"`) | Used as-is for all pipeline stages |
| Empty string `""` | Coerced to `ethereal_default` at API boundary |
| Omitted from request body | Defaults to `ethereal_default` |
| Unknown name (e.g. `"foo"`) | Coerced to `ethereal_default` with a warning log |

### Style Propagation Through the Pipeline

The `visual_style` value flows through every stage of the pipeline automatically once a render is started:

```
POST /projects  (visual_style: "cosmic_cinematic")
    |
    v
[Project record created]  visual_style stored in DB
    |
    v
POST /projects/{id}/render
    |
    v
[Orchestrator.run_pipeline]
    |-- reads project.visual_style from DB
    |-- validates against VALID_VISUAL_STYLES (fallback if invalid)
    |
    |-- for each shot:
    |       |
    |       v
    |   POST ml:8001/generate
    |       body: { ..., "visual_style": "cosmic_cinematic", "model": "cosmic_cinematic" }
    |       |
    |       ML module:
    |         1. Selects VISUAL_STYLES["cosmic_cinematic"] config
    |         2. Enriches prompt with style keywords
    |         3. Generates frames with style palette, gradients, particles
    |         4. Uploads to GCS: projects/{id}/ml/shot_{n}/frame_001.png
    |
    |-- builds scene_json with visual_style field
    |       |
    |       v
    |   POST unity:8002/render
    |       body: { ..., "visual_style": "cosmic_cinematic", "template": "cosmic_cinematic" }
    |       |
    |       Unity worker:
    |         1. Selects VISUAL_HDRP_PROFILES["cosmic_cinematic"] config
    |         2. Downloads ML frames from GCS
    |         3. Builds FFmpeg vf_chain with style color grading, bloom, vignette
    |         4. Renders video with style-specific CRF, FPS, preset
    |         5. Uploads to GCS: projects/{id}/render/final.mp4
    |
    v
[Pipeline complete]  project.status = "completed"
```

**Validation layers (defense-in-depth):**

| Layer | Location | Action on invalid style |
|---|---|---|
| 1. API boundary | `ProjectCreate.validate_visual_style` | Coerces to `ethereal_default`, logs warning |
| 2. Orchestrator | `run_pipeline()` checks `VALID_VISUAL_STYLES` | Falls back to `ethereal_default`, logs warning |
| 3. ML Module | `run_generation()` checks `VISUAL_STYLES` dict | Falls back to `ethereal_default`, logs warning |
| 4. Unity Worker | `run_render()` checks `VISUAL_HDRP_PROFILES` dict | Falls back to `ethereal_default`, logs warning |

---

## 12. ACU Optimization

### ACU_MODE

The `ACU_MODE` environment variable controls compute unit usage across all services.

| Mode | ML Module | Unity Worker | Use Case |
|---|---|---|---|
| `full` | Real inference, GCS upload | Real FFmpeg render, GCS upload | Production, E2E tests |
| `light` | Mock frame URLs (instant, no PIL/GCS) | Mock video URL (instant, no FFmpeg/GCS) | Unit tests, dev iteration, CI |

Mock responses preserve the same JSON schema as real responses but include a `mock: true` flag and `duration_ms: 0.1`.

### Mock Response Examples

**ML Mock (ACU_MODE=light):**
```json
{
  "job_id": "abc-123",
  "status": "completed",
  "frame_urls": ["mock://dailycinema/projects/proj-1/ml/shot_001/frame_001.png"],
  "model": "ethereal_default",
  "duration_ms": 0.1,
  "mock": true
}
```

**Unity Mock (ACU_MODE=light):**
```json
{
  "job_id": "render-456",
  "status": "completed",
  "video_url": "mock://dailycinema/projects/proj-1/render/final.mp4",
  "template": "ethereal_default",
  "duration_ms": 0.1,
  "mock": true
}
```

### Caching Architecture

Both ML and Unity services implement hash-based output caching to avoid redundant compute.

```
Request arrives
    |
    v
Compute cache key = SHA256(prompt + visual_style + model + num_frames)
    |
    v
[Cache hit?] --yes--> Return cached result (duration_ms: 0.1)
    |
    no
    v
Run real inference/render
    |
    v
Store result in cache
    |
    v
Return result
```

**ML cache key:** `sha256(json(prompt, visual_style, model, num_frames))`
**Unity cache key:** `sha256(json(sorted_frame_urls, template, visual_style))`

### ML Batching

The ML module supports batch processing to reduce GPU overhead:

- Background batch worker collects requests over a 0.5s window
- Processes up to `batch_size` (default 8) jobs per batch
- `/generate/batch` endpoint accepts an array of `GenerateRequest` objects
- Prometheus metrics: `ml_batch_total`, `ml_batch_size`

```bash
# Batch submission
curl -X POST http://localhost:8001/generate/batch \
  -H "Content-Type: application/json" \
  -d '[
    {"job_id": "batch-1", "shot_id": "s1", "project_id": "p1", "prompt": "scene one"},
    {"job_id": "batch-2", "shot_id": "s2", "project_id": "p1", "prompt": "scene two"}
  ]'
```

### Unity Micro-Pipeline

A minimal render path for low-cost previews:

| Property | Full Render | Micro-Pipeline |
|---|---|---|
| Resolution | 1920x1080 | 640x360 |
| Preset | medium/slow | ultrafast |
| CRF | 18-23 | 30 |
| Post-processing | Full HDRP chain | None |
| FPS | 24-30 | 15 |
| Endpoint | `/render` | `/render/preview` |

### ACU Budgeting

The orchestrator tracks ACU consumption per pipeline task.

| Operation | ACU Cost |
|---|---|
| ML job (full) | 10.0 |
| Render job (full) | 25.0 |
| Render preview | 5.0 |
| Mock job (light) | 0.1 |

**Budget behavior:**
- Default budget per task: 100 ACU (`ACU_BUDGET_PER_TASK`)
- Warning at 80% usage (`ACU_WARNING_THRESHOLD`)
- Automatic fallback to light mode when budget exceeded
- Prometheus metrics: `dailycinema_acu_budget_used`, `dailycinema_acu_budget_warnings_total`, `dailycinema_acu_fallback_total`

### Style Validation Endpoint

Validate a visual style without running ML or Unity:

```bash
curl -X POST http://localhost:8000/styles/validate \
  -H "X-API-Key: dc-prod-api-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{"visual_style": "cosmic_cinematic"}'
```

Response includes ML keywords, HDRP preset parameters, and FFmpeg preset for the resolved style.

### Test Strategy

| Test Category | ACU_MODE | Command | Duration |
|---|---|---|---|
| Fast (unit) | `light` | `make test-fast` | ~3s |
| Full (E2E) | `full` | `make test-full` | ~2min |

Fast tests validate mock schemas, validation logic, and pipeline flow without real inference.
Full tests run the complete pipeline with real ML generation and Unity rendering.

### ACU Usage Comparison

| Scenario | Before (ACU_MODE=full) | After (ACU_MODE=light) | Savings |
|---|---|---|---|
| Unit test suite (23 tests) | ~230 ACU | ~2.3 ACU | **99%** |
| Single pipeline run | ~35 ACU | ~0.2 ACU | **99.4%** |
| Cached pipeline re-run | ~35 ACU | ~0.2 ACU (cache hit) | **99.4%** |
| Dev iteration (10 runs) | ~350 ACU | ~2.0 ACU | **99.4%** |
| CI pipeline (fast tests) | ~230 ACU | ~2.3 ACU | **99%** |
