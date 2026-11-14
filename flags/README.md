# Flags

Square (1:1) country flags, made to be cropped to a circle or a rounded
square. Use these in a UI, never a flag emoji: an emoji flag is about 3:2 with
transparent padding, so a round mask letterboxes it or crops it to an
unreadable stripe, it looks different on every platform, and Windows shows two
letters and no flag.

| Folder | Files | Format |
| --- | --- | --- |
| `1x1/` | 250 | PNG, 192×192 (a 64pt tile at 3x), about 2 MB in all |

File names are lowercase ISO 3166-1 alpha-2 codes. **Every row of
`world/countries.csv` has a flag**: join with `lower(iso2)`, so France is
`1x1/fr.png` and Indonesia `1x1/id.png`.

## Using them

- **Round**: `border-radius: 50%` with `object-fit: cover`.
- **Rounded square**: a radius of about 22% of the side.
- Flags are keyed by **country, not language**. Choose on purpose: `br` and
  `pt` are both Portuguese, `gb` and `us` both English, `cn`, `tw` and `hk`
  all Chinese.
- On a dark or busy background add a 1px hairline so white-edged flags (Japan,
  Indonesia, Poland) keep their outline.
- Keep a flag in full colour in every state. Show "selected" with a ring and a
  check badge, "not allowed" with a red ring and a diagonal bar. Do not grey a
  flag out to mean "off".

## Source and licence

Rendered from [flag-icons](https://github.com/lipis/flag-icons) v7.5.0, the
`flags/1x1/` SVGs, with librsvg. **MIT licensed**, copyright (c) 2013
Panayiotis Lipiridis: keep [`LICENSE-flag-icons`](./LICENSE-flag-icons) with
the files when you redistribute them. This folder is not public domain, unlike
the boundary data in this repository.

PNG and not the SVGs because iOS's SVG renderer drops `<use>` parts (China's
stars, Korea's trigrams, India's wheel) and shifts flags that clip a
transformed group (Japan, Vietnam, Iran, Saudi Arabia).

## Adding or re-rendering a flag

```bash
npm pack flag-icons --pack-destination "$TMPDIR"
tar -xzf "$TMPDIR"/flag-icons-*.tgz -C "$TMPDIR"
rsvg-convert -w 192 -h 192 "$TMPDIR/package/flags/1x1/<cc>.svg" -o flags/1x1/<cc>.png
```

Use the `1x1` folder of flag-icons, never `4x3`. flag-icons also has 21 flags
that are not countries in `countries.csv` and are not included here: `eu`,
`un`, `gb-eng`, `gb-sct`, `gb-wls`, `gb-nir`, `es-ct`, `es-ga`, `es-pv`,
`arab`, `asean`, `cefta`, `eac`, `ic`, `cp`, `dg`, `pc`, `sh-ac`, `sh-hl`,
`sh-ta`, `xx`.
