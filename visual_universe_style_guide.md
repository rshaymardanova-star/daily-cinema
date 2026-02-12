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
