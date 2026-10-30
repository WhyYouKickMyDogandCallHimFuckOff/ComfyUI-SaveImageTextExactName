"""
Save Image + Text (Exact Filename) - ComfyUI custom node

Saves an image and a .txt file using exactly the filename you give it.
No counters / serial numbers are added (except when a batch contains
more than one image - see note below).

Install: drop this file into  ComfyUI/custom_nodes/  and restart ComfyUI.
Node appears under:  Add Node > image > save > Save Image + Text (Exact Name)
"""

import os
import re
import json

import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo

import folder_paths


_INVALID_CHARS = r'[<>:"|?*\x00-\x1f]'


def _clean_name(name: str) -> str:
    name = name.strip()
    # strip a user-supplied image/text extension so we don't get "x.png.png"
    root, ext = os.path.splitext(name)
    if ext.lower() in (".png", ".jpg", ".jpeg", ".webp", ".txt"):
        name = root
    name = re.sub(_INVALID_CHARS, "_", name)
    return name.rstrip(". ")  # Windows dislikes trailing dots/spaces


class SaveImageAndTextNamed:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename": ("STRING", {"default": "my_image"}),
                "text": ("STRING", {"multiline": True, "default": ""}),
                "output_folder": ("STRING", {
                    "default": "",
                    "tooltip": "Blank = ComfyUI/output. A name like 'portraits' "
                               "= ComfyUI/output/portraits. A full path like "
                               "'D:\\Renders\\Job1' saves there. Created if missing.",
                }),
                "format": (["png", "jpg", "webp"],),
                "overwrite": ("BOOLEAN", {"default": True}),
                "embed_workflow": ("BOOLEAN", {"default": True}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("image_path", "text_path")
    FUNCTION = "save"
    OUTPUT_NODE = True
    CATEGORY = "image/save"

    def save(self, images, filename, text, output_folder, format, overwrite,
             embed_workflow, prompt=None, extra_pnginfo=None):

        output_root = folder_paths.get_output_directory()

        # output_folder: blank, a folder name/relative path inside
        # ComfyUI/output, or an absolute path anywhere on disk
        output_folder = output_folder.strip().strip('"')
        if output_folder and os.path.isabs(output_folder):
            out_dir = output_folder
        else:
            out_dir = os.path.join(output_root, output_folder)
        os.makedirs(out_dir, exist_ok=True)

        # filename may itself contain sub-dirs, e.g. "people/bob"
        filename = filename.replace("\\", "/")
        name_dir, name_base = os.path.split(filename)
        if name_dir:
            out_dir = os.path.join(out_dir, name_dir)
            os.makedirs(out_dir, exist_ok=True)
        base = _clean_name(name_base)
        if not base:
            raise ValueError("Filename is empty after cleaning.")

        ext = "jpg" if format == "jpg" else format
        batch = len(images)
        ui_images, image_paths, text_paths = [], [], []

        for i, img_t in enumerate(images):
            # Only add a suffix when a batch has multiple images,
            # otherwise they'd overwrite each other.
            stem = base if batch == 1 else f"{base}_{i + 1}"
            img_path = os.path.join(out_dir, f"{stem}.{ext}")
            txt_path = os.path.join(out_dir, f"{stem}.txt")

            if not overwrite:
                for p in (img_path, txt_path):
                    if os.path.exists(p):
                        raise FileExistsError(
                            f"{p} already exists and overwrite is off.")

            arr = np.clip(255.0 * img_t.cpu().numpy(), 0, 255).astype(np.uint8)
            img = Image.fromarray(arr)

            if format == "png":
                meta = None
                if embed_workflow:
                    meta = PngInfo()
                    if prompt is not None:
                        meta.add_text("prompt", json.dumps(prompt))
                    if extra_pnginfo:
                        for k, v in extra_pnginfo.items():
                            meta.add_text(k, json.dumps(v))
                img.save(img_path, pnginfo=meta, compress_level=4)
            elif format == "jpg":
                img.convert("RGB").save(img_path, quality=95)
            else:
                img.save(img_path, quality=95)

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            image_paths.append(img_path)
            text_paths.append(txt_path)

            # preview in the node (only works for files inside the output dir)
            try:
                rel = os.path.relpath(out_dir, output_root)
                if not rel.startswith(".."):
                    ui_images.append({
                        "filename": os.path.basename(img_path),
                        "subfolder": "" if rel == "." else rel,
                        "type": "output",
                    })
            except ValueError:
                pass  # different drive on Windows

        return {
            "ui": {"images": ui_images},
            "result": ("\n".join(image_paths), "\n".join(text_paths)),
        }


NODE_CLASS_MAPPINGS = {"SaveImageAndTextNamed": SaveImageAndTextNamed}
NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageAndTextNamed": "Save Image + Text (Exact Name)"
}
