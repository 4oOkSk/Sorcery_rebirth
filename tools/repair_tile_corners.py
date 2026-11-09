#!/usr/bin/env python3
"""Extend a square paper face into its corners before applying its existing outline.

A source tile can contain a larger baked-in rounded edge than the final paper
outline. Reconstruct only those small corner regions from the adjoining face;
leave the central mark and the final alpha/shadow unchanged.
"""
from PIL import Image
from statistics import median


def repair(image: Image.Image, face=(40, 40, 344, 344)) -> Image.Image:
    result = image.convert('RGBA').copy()
    left, top, right, bottom = face
    paper = result.crop(face).convert('RGB')
    width, height = paper.size
    reach = round(min(width, height) * .18)
    feather = 10
    source = paper.load()
    target = result.load()
    for horizontal in (False, True):
        for vertical in (False, True):
            def point(x, y):
                return (width-1-x if horizontal else x,
                        height-1-y if vertical else y)
            # The face immediately inside this corner is a safer color source
            # than distant row/column samples, which can cross the app's logo.
            sample = round(min(width, height) * .105)
            colors = [source[point(x,y)]
                      for y in range(sample-2,sample+3)
                      for x in range(sample-2,sample+3)]
            color = tuple(int(median(p[channel] for p in colors))
                          for channel in range(3))
            # A mark may reach the diagonal sampling point. Agreement between
            # the two nearby straight edges identifies the underlying paper
            # color in that case (for example a white mark on a dark tile).
            edges = []
            for cx,cy in ((reach+8,12),(12,reach+8)):
                samples = [source[point(cx+dx,cy+dy)]
                           for dx in (-1,0,1) for dy in (-1,0,1)]
                edges.append(tuple(int(median(p[k] for p in samples)) for k in range(3)))
            if max(abs(a-b) for a,b in zip(*edges)) < 35:
                color = tuple((a+b)//2 for a,b in zip(*edges))
            for y in range(reach):
                for x in range(reach-y):
                    # Continue the adjacent face into the missing corner,
                    # with a soft join to the original pixels.
                    blend = min(1., (reach-x-y) / feather)
                    px, py = point(x, y)
                    old = source[px, py]
                    rgb = tuple(round(a*blend+b*(1-blend))
                                for a,b in zip(color, old))
                    alpha = target[left+px, top+py][3]
                    target[left+px, top+py] = rgb + (alpha,)
    return result
