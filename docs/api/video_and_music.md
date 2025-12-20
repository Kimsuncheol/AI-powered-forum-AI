# Video and Music Generation API

This document covers the AI-powered video and music generation features.

## Video Generation (Veo 3.1)

Generate high-fidelity 720p/1080p videos with native audio using Google's Veo 3.1 model.

### Endpoints

#### POST `/api/v1/ai/videos/generate`

Generate a video from a text prompt. Returns an operation ID for async polling.

**Request:**
```json
{
  "prompt": "A cinematic shot of a majestic lion in the savannah at sunset",
  "config": {
    "aspect_ratio": "16:9",
    "resolution": "720p",
    "duration_seconds": "8",
    "negative_prompt": "low quality, blurry",
    "person_generation": "allow_adult",
    "seed": 42
  }
}
```

**Response:**
```json
{
  "operation_id": "op-12345",
  "status": "processing",
  "video_url": null,
  "video_b64": null,
  "error_message": null
}
```

---

#### POST `/api/v1/ai/videos/generate-from-image`

Generate a video from an image (image-to-video). Upload as multipart form data.

**Request (form-data):**
- `prompt` (string): Animation description
- `image` (file): JPEG, PNG, or WEBP image
- `aspect_ratio` (optional): "16:9" or "9:16"
- `resolution` (optional): "720p" or "1080p"
- `duration_seconds` (optional): "4", "6", or "8"
- `negative_prompt` (optional): What to avoid

**Response:** Same as `/generate`

---

#### GET `/api/v1/ai/videos/status/{operation_id}`

Poll for video generation status. Continue polling until `done: true`.

**Response (in-progress):**
```json
{
  "operation_id": "op-12345",
  "done": false,
  "status": "processing",
  "video_url": null,
  "video_b64": null,
  "error_message": null
}
```

**Response (completed):**
```json
{
  "operation_id": "op-12345",
  "done": true,
  "status": "completed",
  "video_url": null,
  "video_b64": "BASE64_ENCODED_VIDEO_DATA...",
  "error_message": null
}
```

### Configuration Options

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `aspect_ratio` | `16:9`, `9:16` | `16:9` | Video aspect ratio |
| `resolution` | `720p`, `1080p` | `720p` | Video resolution |
| `duration_seconds` | `4`, `6`, `8` | `8` | Video length |
| `negative_prompt` | string (max 500 chars) | null | What to avoid |
| `person_generation` | `allow_all`, `allow_adult`, `dont_allow` | `allow_adult` | Person generation |
| `seed` | integer | null | For improved determinism |

---

## Music Generation (Lyria RealTime)

Generate instrumental music in real-time using Google's Lyria RealTime model.

### Endpoints

#### POST `/api/v1/ai/music/generate`

Generate music from weighted prompts.

**Request:**
```json
{
  "prompts": [
    {"text": "minimal techno with deep bass", "weight": 1.0},
    {"text": "atmospheric synths", "weight": 0.8}
  ],
  "config": {
    "bpm": 120,
    "temperature": 1.0,
    "guidance": 4.0,
    "density": 0.5,
    "brightness": 0.6,
    "scale": "C_MAJOR_A_MINOR",
    "mute_bass": false,
    "mute_drums": false,
    "only_bass_and_drums": false,
    "music_generation_mode": "QUALITY"
  },
  "duration_seconds": 30
}
```

**Response:**
```json
{
  "audio_b64": "BASE64_ENCODED_PCM16_AUDIO...",
  "sample_rate_hz": 48000,
  "channels": 2,
  "bit_depth": 16,
  "duration_seconds": 30.5,
  "prompts_used": ["minimal techno with deep bass", "atmospheric synths"]
}
```

---

#### POST `/api/v1/ai/music/generate-simple`

Simplified endpoint for quick music generation.

**Query Parameters:**
- `prompt` (string, required): Music description
- `bpm` (int, default: 120): Beats per minute (60-200)
- `duration_seconds` (int, default: 30): Duration (5-120)

**Response:** Same as `/generate`

### Configuration Options

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| `bpm` | 60-200 | 120 | Beats per minute |
| `temperature` | 0.0-2.0 | 1.0 | Randomness |
| `guidance` | 0.0-6.0 | 4.0 | Prompt adherence |
| `density` | 0.0-1.0 | null | Note density |
| `brightness` | 0.0-1.0 | null | Tonal brightness |
| `scale` | enum | null | Musical scale/key |
| `mute_bass` | bool | false | Reduce bass |
| `mute_drums` | bool | false | Reduce drums |
| `only_bass_and_drums` | bool | false | Bass/drums only |
| `music_generation_mode` | `QUALITY`, `DIVERSITY`, `VOCALIZATION` | `QUALITY` | Generation focus |

### Weighted Prompts

- `text`: Musical description (genre, instrument, mood, characteristic)
- `weight`: Influence strength (> 0, typically 0.1-5.0, default 1.0)

Multiple prompts blend together. Higher weights = stronger influence.

### Audio Output Format

- **Format:** Raw 16-bit PCM
- **Sample Rate:** 48kHz
- **Channels:** 2 (stereo)

---

## Authentication

All endpoints require Firebase authentication:

```
Authorization: Bearer <firebase_jwt_token>
```

## Error Responses

| Status | Description |
|--------|-------------|
| `400` | Invalid request (bad parameters) |
| `401` | Missing or invalid authentication |
| `422` | Validation error |
| `500` | Internal server error |
| `503` | Service unavailable (API not configured) |

## Rate Limiting

Subject to the configured `AI_DAILY_RATE_LIMIT` (default: 50 requests/day per user).
