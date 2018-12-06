# select_centered_text.py
""" Centered Text near/within Part
"""

class CenteredText:
    """ Contents for text placed inside a region
    """
    def __init__(self, text, x=None, y=None,
                    color=None, color_bg=None,
                    height=None, width=None):
        """ Setup instance of centered text
        """
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.color_bg = color_bg
        self.height = height
        self.width = width
        self.text_tag = None        # Canvas text tag, if live

    def __str__(self):
        """ Centered Text description
        """
        st = self.text
        if self.x is not None or self.y is not None:
            st += " at:x=%d y=%d" (self.x, self.y)
        if self.color is not None:
            st += " %s" % self.color
        if self.color_bg is not None: 
            st += " bg=%s" % self.color_bg
        if self.height is not None:
            st += " height=%d" % self.height
        if self.width is not None:
            st += " width=%d" % self.height
        if self.text_tag is not None:
            st += " text_tag=%d" % self.text_tag
        return st
    