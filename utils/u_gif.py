#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author：samge
# date：2024-05-10 13:53
# describe：
import os
from PIL import Image

from utils import u_file


def convert_webp_to_gif(input_path, output_path) -> str:
    try:
        with Image.open(input_path) as img:
            if img.is_animated:
                return save_gif(img, output_path)
            else:
                img.convert('RGBA').save(output_path, 'GIF')
            print(f"Converted {input_path} to {output_path}")
        return output_path if os.path.exists(output_path) else None
    except IOError as e:
        print(f"An error occurred: {e}")
        return None


def save_gif(img, output_path):
    frames = []
    try:
        for i in range(img.n_frames):
            img.seek(i)
            frames.append(img.convert('RGBA').copy())
        img.save(output_path, save_all=True, append_images=frames, format='GIF', loop=0)
        return output_path if os.path.exists(output_path) else None
    except Exception as e:
        print(f"save_gif exception: {e}")
        return None


if __name__ == '__main__':
    u_file.makedirs(".cache/gif")
    input_path = ".cache/output/ComfyUI_00001_.webp"
    input_path = ".cache/output/1_570791854690970_20240510091026.gif"
    input_path = ".cache/output/0_004772275046407_20240510092658.webp"
    output_path = input_path.replace('.webp', '.gif').replace("output", "gif")
    convert_webp_to_gif(input_path, output_path)