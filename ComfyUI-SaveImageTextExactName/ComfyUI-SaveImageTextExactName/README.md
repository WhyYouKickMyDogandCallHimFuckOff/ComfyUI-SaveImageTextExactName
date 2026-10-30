# ComfyUI Save Image + Text (Exact Name)

A ComfyUI node that saves an image **and** a matching `.txt` file using exactly the
filename you give it — **no counters or serial numbers appended**.

Handy for datasets (image + caption pairs), named renders, or any workflow where
you control the filename from another node.

## Features

- Exact filename: `cat_portrait` → `cat_portrait.png` + `cat_portrait.txt`
- Output folder: blank (ComfyUI `output`), a relative folder name, or an absolute path — created if missing
- Filename can include subfolders, e.g. `people/bob`
- PNG, JPG or WEBP
- Optional embedding of the workflow in PNG metadata (drag back into ComfyUI)
- Overwrite toggle — when off, the node stops with an error instead of renaming
- Outputs the saved image and text paths as strings
- Any widget can be converted to an input (right-click the node)

## Install

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/WhyYouKickMyDogandCallHimFuckOff/ComfyUI-SaveImageTextExactName.git
```

Restart ComfyUI. The node is under **image → save → Save Image + Text (Exact Name)**.

No extra dependencies — it only uses packages ComfyUI already ships with.

## Inputs

| Input | Description |
|---|---|
| `images` | Image(s) to save |
| `filename` | Base filename (extension optional; it's stripped) |
| `text` | Contents of the `.txt` file |
| `output_folder` | Blank = `ComfyUI/output`; name = subfolder of output; full path = anywhere |
| `format` | `png`, `jpg`, `webp` |
| `overwrite` | Replace existing files, or error if they exist |
| `embed_workflow` | Store prompt/workflow in PNG metadata |

## Outputs

| Output | Description |
|---|---|
| `image_path` | Full path of the saved image |
| `text_path` | Full path of the saved text file |

## Batches

With a batch of one image (the usual case) the filename is used exactly. If a batch
contains multiple images, `_1`, `_2`, … are appended so they don't overwrite each other.

## License

MIT
