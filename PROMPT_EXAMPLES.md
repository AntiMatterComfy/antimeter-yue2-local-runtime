# YuE2 prompt examples

Use the **style** text for language, genre, voice, instruments, arrangement, and mix. Put the actual words and section tags in **lyrics**. Keep the first render focused: one clear vocal character, a short instrumental list, and one production direction work better than a wall of conflicting adjectives.

## 1. Ukrainian cinematic pop

**Style**

```text
Ukrainian cinematic pop, expressive female lead vocal, intimate piano opening, warm strings, restrained electronic drums, wide chorus, polished contemporary mix
```

**Lyrics**

```text
[Verse]
Місто засинає в синіх вікнах,
Та у серці не згаса вогонь.

[Chorus]
Я знайду тебе крізь тихий вітер,
Поки ніч тримає нас долонь.
```

## 2. Dark synthwave

**Style**

```text
English dark synthwave, low male lead vocal, pulsing analogue bass, gated drums, glassy arpeggios, cinematic tension, 1980s-inspired but modern master
```

## 3. J-pop summer anthem

**Style**

```text
Japanese J-pop, bright youthful female vocal, clean electric guitar, piano, handclaps, energetic live drums, huge sing-along chorus, pristine pop production
```

## 4. Afro-house instrumental

**Style**

```text
Afro-house instrumental, 122 BPM, deep rolling bass, hand percussion, warm vocal chops without intelligible words, airy marimba motif, sunset club mix
```

**Lyrics**

```text
[Instrumental]
```

## 5. Jazz-funk cover arrangement

Transcribe a recording to a melody-only ABC score first, then connect that score with `cot = melody` through the official YuE2 pipeline. Use only music and lyrics you have permission to adapt.

```text
English jazz-funk, warm lead vocal, Rhodes piano, fingerstyle electric bass, tight drums, muted trumpet responses, smoky live-room mix
```

## 6. Metalcore without artist imitation

```text
English modern metalcore, forceful clean-and-rough male vocal contrast, down-tuned rhythm guitars, fast double-kick drums, atmospheric synth pad, dramatic half-time chorus, clean contemporary heavy mix
```

## Prompt hygiene

- Name a sound or a musical role, not a living artist or a specific singer.
- Keep lyrics original or use text you are licensed to use.
- For a new song, start with `cot = full`; save and inspect `score.abc` before editing harmony or melody.
- `YuE2-Vae` is the listening default. `YuE2-Vae-legacy` is for reproducing benchmark-style decoding, not a blanket quality upgrade.
