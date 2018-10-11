"""
Created on Aug 17, 2018

@author: raysm
"""

class ImageSelect(object):
    """
    Provide an interactive user interface to facilitate selecting
    a region within a displayed image
    The Major mode displays the image with currently selected region
    highlighted so that the viewer can easily recognize.
    The display will indicate handles at the selected region's
    corners which can be dragged to resize the selected region.
    The edges, minus the corners, can be dragged, limited to perpendicular
    to the dragged edge.  The region's interior, minus the edges and
    corners, can be dragged, repositioning the whole selection
    region.
    Questions:
        Does dragging the selection region, past the displayed region
        reposition/resize the display region?
    """


    def __init__(self, mw, image, select):
        """
        :mw - parent window
        :image - image from which to select
        :select - starting selection rectangle (uLx,uLy) (lRx, lRy)
                None - middle third vertical and horizontal
        """
        if mw is None:
            mw = tk,Tk()
        self.mw = mw
        if image is None:
            image = Image.new("RGB", 300, 500)
        self.image = image
        if select is None:
            iw = image.width
            ih = image.height
            xlen = iw/3
            ylen = ih/3
            select = (xlen,ylen), (2*xlen, 2*ylen)
        self.select = select
    
    
    def select(self):
        """
        Display selected region, Support user drag of
        selection region/region boundaries
        return selected region
        """
        
        
if __name__ == "__MAIN__":
    import sys, os, string, time
    import tkinter as tk
    from PIL import Image, ImageDraw, ImageFont

    width = 600
    height = 400
    select = None
    mw = tk.Tk()
    mw.title ("ImageSelect Demo")
    image = Image.new("RGB", width, height)
    iS = ImageSelect(mw, image=image,select=select)
    while True:
        srec = iS.select()   