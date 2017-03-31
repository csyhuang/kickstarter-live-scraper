#!/usr/bin/env python
"""
Minimal Example
===============
Generating a square wordcloud from the US constitution using default arguments.
"""

from os import path
from wordcloud import WordCloud
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def gen_wordCloud_from_blurbs2(blurb,item_title,ax):

    text = ' '.join( blurb.astype(str).values.tolist() )

    # Generate a word cloud image
    wordcloud = WordCloud().generate(text)

    # Display the generated image:
    # the matplotlib way:
    # import matplotlib.pyplot as plt
    # plt.imshow(wordcloud, interpolation='bilinear')
    # plt.axis("off")

    # lower max_font_size
    wordcloud = WordCloud(max_font_size=30).generate(text)
    #plt.figure(figsize=(10,6))
    ax.set_title(item_title,size=16)
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    #plt.show()

    # The pil way (if you don't have matplotlib)
    # image = wordcloud.to_image()
    # image.show()