# Diagram SVGs

Seven self-contained vector diagrams generated from the codebase, one per report figure:

| file | report figure | LaTeX label |
|------|----------------|-------------|
| `fdiagram.svg`      | Functional architecture        | `fig:functional_block_diagram` |
| `softwarearch.svg`  | ROS 2 node/topic graph         | `fig:software_arch` |
| `localization.svg`  | Localisation & TF tree         | `fig:localization` |
| `navigation.svg`    | Nav2 stack                     | `fig:navigation` |
| `behaviourtree.svg` | Mission behaviour tree         | `fig:behav_tree` |
| `firmware.svg`      | ESP32 firmware architecture    | `fig:firmware` |
| `schematic.svg`     | Electrical architecture        | `fig:schematic` |

## Use them in the report (best quality, vector — what the prof asks for)

The report's `\vecfig` macro looks for `images/<name>.pdf` first, then `images/<name>.png`.
So convert each SVG to a **PDF** and drop it into `../images/`:

```bash
# Inkscape (any recent version)
for f in *.svg; do inkscape "$f" --export-type=pdf --export-filename="../images/${f%.svg}.pdf"; done

# or librsvg
for f in *.svg; do rsvg-convert -f pdf -o "../images/${f%.svg}.pdf" "$f"; done

# or cairosvg (pip install cairosvg)
for f in *.svg; do cairosvg "$f" -o "../images/${f%.svg}.pdf"; done
```

That's it — the figures resolve automatically, scale losslessly, and keep the PDF small.

(If you'd rather screenshot, save PNGs as `images/<name>.png` instead; the macro falls back to those.)
You can preview/print all seven at once by opening `../diagrams.html` in a browser.
