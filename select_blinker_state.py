# select_blinker_state.py
from select_trace import SlTrace

class BlinkerState:
    """ Blinking item state
    """
    def __init__(self, part, tag=None,
                 on_time=None, off_time=None, on_fill="black", off_fill="white"):
        self.part = part
        self.canvas = part.sel_area.canvas
        self.tag = tag
        self.on_state=True
        if on_time is None:
            on_time = .2
        self.on_time = on_time
        if off_time is None:
            off_time = on_time
        self.off_time = off_time
        self.on_fill = on_fill
        self.off_fill=off_fill

    def is_blinking(self):
        """ Check if still blinking
        """
        if self.part is None:
            return False
        
        return True
                        
    def blink_on(self):
        if not self.is_blinking():
            return False
        
        if not self.on_state:
            self.canvas.itemconfigure(self.tag, fill=self.on_fill)
            self.on_state = True
        self.canvas.after(int(1000*self.on_time), self.blink_off)
        return True
                        
    def blink_off(self):
        if not self.is_blinking():
            return False
        
        if self.on_state:
            self.canvas.itemconfigure(self.tag, fill=self.off_fill)
            self.on_state = False
        self.canvas.after(int(1000*self.off_time), self.blink_on)
        return True


    def stop(self):
        """ Stop blinking
        """
        if self.tag is not None:
            self.canvas.delete(self.tag)
            self.tag = None


class BlinkerMultiState:
    """ Blinking multi tag group item state
    
    The group will display for on_time then rotated one group and redisplayed
    """
    def __init__(self, part, tagtags=None,
                 on_time=None):
        """ Setup multi state blinker
        :part: part to blink
        :tagtags:  list of tag lists
        :on_time: length of the display before rotating the fill colors
        """
        self.part = part
        self.canvas = part.sel_area.canvas
        if on_time is None:
            on_time = .25
        self.on_time = on_time
        self.multitags = tagtags
        self.multifills = []
        for taggroup in tagtags:
            tg_fills = []
            for tag in taggroup:
                fill = self.canvas.itemcget(tag, "fill")
                tg_fills.append(fill)
            self.multifills.append(tg_fills)
        self.first_fill_index = 0      # Where the first fills go
        

    def is_blinking(self):
        """ Check if still blinking
        """
        if self.part is None:
            return False
        
        if not self.multitags:
            return False
        
        if not self.multifills:
            return False
        
        return True


    def blink_on_first(self):
        """ Just set going - assumes first is displayed
        """
        if not self.is_blinking():
            return False
        
        self.first_fill_index = 1
        if self.first_fill_index >= len(self.multitags):
            self.first_fill_index = 0            # Wrap around
        self.canvas.after(int(1000*self.on_time), self.blink_on_next)
        return True
 
                       
    def blink_on_next(self):
        if not self.is_blinking():
            return False

        si = self.first_fill_index       # Source of new state(e.g. fill)
        SlTrace.lg("blink_on_next first_fill_index=%d in %s"
                   % (si, self.part), "blink")
        for taggroup in self.multitags:
            if si >= len(self.multitags):
                si = 0                      # Wrap around
            src_fill_group = self.multifills[si]
            for i in range(len(taggroup)):
                itag = ifill = i            # May have different lengths
                if itag >= len(taggroup):
                    itag = len(taggroup)-1  # Use last
                if ifill >= len(src_fill_group):
                    ifill = len(src_fill_group)-1
                try:
                    self.canvas.itemconfigure(taggroup[itag], fill=src_fill_group[ifill])
                except:
                    SlTrace.lg("Out of range")
                    return
                
            si += 1                         # Go to next fill group
        self.first_fill_index += 1
        if self.first_fill_index >= len(self.multitags):
            self.first_fill_index = 0            # Wrap around
        self.canvas.after(int(1000*self.on_time), self.blink_on_next)
        return True
                        
    def blink_off(self):
        if not self.is_blinking():
            return False
        
        if self.on_state:
            self.canvas.itemconfigure(self.tag, fill=self.off_fill)
            self.on_state = False
        self.canvas.after(int(1000*self.off_time), self.blink_on)
        return True


    def stop(self):
        """ Stop blinking
        """
        self.part = None
        self.multitags = []
