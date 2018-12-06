# select_part.py        
from tkinter import font

from select_error import SelectError
from select_loc import SelectLoc
from select_trace import SlTrace
from select_centered_text import CenteredText
from docutils.nodes import Part


def color_to_fill(color):
    """ Color integer into fill text
    """
    if color is None:
        return "NONE"
    if isinstance(color, str):
        return color
    
    return "#%06X" % color



class PartHighlight(object):
    """ Information about highlighted part
    """
    
    def __init__(self, part, xy=None,
            highlight_limit=None):
        """ Record highlighting information
        :part: highlighted part
        :tag: graphics tag for deleting/redisplay
        :xy: x,y coordinates of mouse on canvas
        :highlight_limit: clear highlight if still on
                    after this time
                    Default: no automatic clearing
        """
        self.part  = part
        self.xy = xy
        if highlight_limit is not None:
            import tkinter as tk
            if not hasattr(self.part.sel_area, "mw"):
                self.part.sel_area.mw = tk.Tk()
                self.part.sel_area.mw.withdraw()       # Hide main window

            self.part.sel_area.mw.after(highlight_limit,
                                   self.part.highlight_clear)        # Call us after time_step        


class SelectPart(object):
    
    SZ_DISPLAY  = 1             # Size for display
    SZ_SELECT = 2               # Size for selection
    SZ_STANDOFF = 3             # Size for standoff
    SZ_ENLARGE = 4              # Size for enlarge
    MOD_BEFORE = 1              # Before modification
    MOD_AFTER = 2               # After modification
    edge_width_display = 5      # Default edge display line width in pixels
    edge_width_select = 3      # Default edge select line width in pixels
    edge_width_standoff = 5     # Default edge buffer for adjacent parts
    edge_width_enlarge = 2      # Enlarge number, added to width
    edge_fill = "blue"   # Default edge color
    edge_fill_highlight = "purple"   # Default edge highlight color
    corner_width_display = 8    # Default display size of corner in pixels
    corner_width_select = 8    # Default select size of corner in pixels
    corner_width_standoff = 10    # Default standoff size of corner in pixels
    corner_fill = "red" # Default corner color
    corner_fill_highlight = "pink"      # Default corner highlight color
    region_fill = "clear"   # Default edge color
    region_fill_highlight = "lightgray"   # Default edge highlight color

    id = 0          # Unique handle ID
            
            
    @staticmethod
    def is_point_equal(pt1, pt2):
        """ Check if points are equal
        """
        if pt1[0] == pt2[0] and pt1[1] == pt2[1]:
            return True
        
        return False
    

    @staticmethod
    def get_olaps(parts, sz_type=None, enlarge=False):
        """ Get overlapping rectangle, if any, of a list of parts
        """
        if len(parts) < 2:
            return None
        
        part1 = parts.pop()
        for part in parts:
            return None             ### Workaround ???
        
            olap_rect = part1.get_overlap(part, sz_type=sz_type, enlarge=enlarge)
            if olap_rect is None:
                return None
            
            part1 = SelectPart(part.sel_area, part_type="edge", rect=olap_rect)
        return olap_rect

    @classmethod
    def get_edge_width_cls(cls, sz_type=SZ_DISPLAY):
        """ Return class edge width
        :sz_type:  size type
        """
        width = cls.edge_width_display
        if sz_type == cls.SZ_SELECT:
            width = cls.edge_width_select
        elif sz_type == cls.SZ_STANDOFF:
            width = cls.edge_width_standoff           
        elif sz_type == cls.SZ_ENLARGE:
            width = cls.edge_width_enlarge           
        return width



    @classmethod
    def set_edge_width_cls(cls, display=None, select=None, standoff=None):
        """ Set edge width(s)
        """
        if display is not None:
            cls.edge_width_display = display
        if select is not None:
            cls.edge_width_select - select
        if standoff is not None:
            cls.edge_width_standoff = standoff
            return (cls.edge_width_display, cls.edge_width_select,
                    cls.edge_width_standoff)
    
    @classmethod
    def get_corner_rect_at_pt(cls, pt, sztype=None, enlarge=False):
        """ Get corner rectangle at given point
        """
        if sztype is None:
            sztype=cls.SZ_DISPLAY
        corner_width = cls.corner_width_display
        if sztype == SelectPart.SZ_DISPLAY:
            corner_width = cls.corner_width_display
        elif sztype == SelectPart.SZ_SELECT:
            corner_width = cls.corner_width_select
        elif sztype == SelectPart.SZ_STANDOFF:
            corner_width = cls.corner_width_standoff
            
        c1x = pt[0]
        if c1x >= corner_width/2:
            c1x -= corner_width/2
        c1y = pt[1]                 # inside upper left  corner
        if c1y >= corner_width/2:
            c1y -= corner_width/2
        if isinstance(c1x, list):
            print("c1x is a list")
        c3 = (c1x + corner_width, c1y + corner_width)
        c3x = c3[0]
        c3y = c3[1]
                                                    # Enlarge a bit
        if enlarge:
            el = 2                  # enlarge number of pixels
            c1x -= el
            c1y -= el
            c3x += el
            c3y += el
        
        """ Ensure uL to left and above lR """
        return SelectLoc.order_ul_lr(c1x,c1y,c3x,c3y)


    @classmethod
    def part_loc_key(cls, part_type, pt1, pt2=None):
        """ Return location of part as a key
        Used in determining if part is already present
        """
        if part_type == "corner":
            return pt1
        
        elif part_type == "edge":
            return (pt1,pt2)
        
        elif part_type == "region":
            return (pt1,pt2)
        
        raise SelectError("loc_key - unrecognized part_type: %s" % part_type)


    
    def __init__(self, sel_area, part_type,
                 point=None, rect=None, tag=None, xy=None,
                 display_shape=None,
                 display_size=None,
                 color=None,
                 draggable=True,
                 invisible=False,
                 check_mod=None,
                 row=0, col=0):
        """ Selection Part setup
        :sel_area: - reference to region of operation and display
        :part_type: string describing type edge, corner, region
        :point, rect: description of location
        :display_shape: - if present, special display shape
        :display_size: - if present, special display size
        :draggable: when selected can be dragged default:True
        :invisible: True - part is invisible default = False (visible)
        :check_mod: called, if present, before and after part is modified
        :row: optional row number, generally 1 - n
        :col: optional col number, generally 1 - n
        """
        if sel_area is None:
            raise SelectError("SelectPart missing sel_area")
        
        self.sel_area = sel_area
        SelectPart.id += 1
        self.id = SelectPart.id
        self.parts_index = None
        self.loc_key_ = None
        self.connecteds = []            # Start with none connected
        self.adjacents = []             # Start with none adjacent
        self.part_type = part_type
        self.highlighted = False
        self.highlight_tag = None
        self.display_tag = tag
        self.display_shape = display_shape
        self.display_size = display_size
        self.draggable = draggable
        self.invisible = invisible
        if check_mod is None:
            check_mod = self.sel_area.check_mod       # take from sel_area
        self.check_mod = check_mod
        self.turned_on = False
        self.move_no = None
        self.on_highlighting = True     # allow highlighting if on
        self.off_highlighting = True    # allow highlighting if off
        self.move_no_tag = None         # tag for move_no, if any
        self.set_edge_width(SelectPart.edge_width_display,
                                     SelectPart.edge_width_select,
                                     SelectPart.edge_width_standoff,
                                     SelectPart.edge_width_enlarge)
        self.color = color
        self.row = row
        self.col = col
        self.move_tag = None        # Used to display move info
        self.partno_tag = None      # Used to display part number info
        self.text_tags = []         # appended texts if any
        self.centered_text = []     # CenteredText entries

        if point is not None:
            self.loc = SelectLoc(point=point)
        elif rect is not None:
            self.loc = SelectLoc(rect=rect)
        else:
            raise SelectError("SelectPart: neither point nor rect type")


    def __str__(self):
        """ Provide reasonable view of part
        """
        st = self.part_type
        sub_type = self.sub_type()
        if sub_type:
            st += sub_type
        st += " id=%d" % self.id
        if self.move_no is not None:
            st += " move=%d" % self.move_no
        if self.move_no_tag is not None:
            st += " tag=%d" % self.move_no_tag
        if (self.row is not None and self.col is not None
            and self.row > 0 and self.col > 0):
            st += " row=%d col=%d" % (self.row, self.col)
        if self.is_turned_on():
            st += " turned_on"
        st += " at %s" % self.loc
        if self.centered_text:
            for ct in self.centered_text:
                st += "\n       centered_text: %s" % ct
        if self.text_tags:
            for tt in self.text_tags:
                st += "\n       text: %s" % str(tt)
             
        return st


    def diff(self, part):
        """ Provide view of difference between
            us and part
        """
        st = ""
        if part.part_type != self.part_type:
            st += " type CHANGEd %s ==> %s" % (
                self.part_type, part.part_type)
        if part.is_turned_on() != self.is_turned_on():
            if self.is_turned_on():
                st += " turned_on"
            else:
                st += " turned_off"
            st += " ==>"
            if part.is_turned_on():
                st += " turned_on"
            else:
                st += " turned_off"
        if part.loc != self.loc:
            st += " at %s" % self.loc
            st += " ==>"
            st += " at %s" % part.loc
        if part.centered_text != self.centered_text:
            for ct in self.centered_text:
                st += "\n       centered_text: %s" % ct
            st += " ==>\n"
            for ct in part.centered_text:
                st += "\n       centered_text: %s" % ct
        if part.text_tags != self.text_tags:
            for tt in self.text_tags:
                st += "\n       text: %s" % str(tt)
            st += " ==>\n" 
            for tt in part.text_tags:
                st += "\n       text: %s" % str(tt)
        if st != "":
            st = self.part_type + " " + st
        return st

    def str_edges(self, part_type="edge", indent=8):
        """ String of connected types edges
        :type: type of connected default: "edge"
        """
        ind = " "*indent
        st = ""
        for connected in self.connecteds:
            if part_type is None or connected.part_type == part_type:
                if st != "":
                    st += "\n"
                st += ind + str(connected)                
        return st
    
    
    def get_edge_width(self, sz_type=SZ_DISPLAY, enlarge=False):
        """ Return edge edge width
        :sz_type:  size type
        :enlarge:  if True, enlarge width by this ammount
        """
        width = self.edge_width_display
        if sz_type == self.SZ_SELECT:
            width = self.edge_width_select
        elif sz_type == self.SZ_STANDOFF:
            width = self.edge_width_standoff           
        elif sz_type == self.SZ_ENLARGE:
            width = width + self.edge_width_enlarge
        if enlarge:
            width = width + self.edge_width_enlarge
           
        return width


    def get_nodes(self, indexes=None):
        """ Find nodes/points of part
        return pairs (index, node)
        """
        if self.is_corner():
            return [(0,self.loc.coord)]
        elif self.is_edge():
            nodes = []
            if indexes is None:
                nodes = [(0,self.loc.coord[0]), (1,self.loc.coord[1])]
            else:
                if not isinstance(indexes, list):
                    indexes = [indexes]     # Make a list of one
                for index in indexes:
                    nodes.append((index,self.loc.coord[index]))
            return nodes
        else:
            return []

    def set(self, **kwargs):
        """ Set attributes for part
        :name=val: - set attribute which must already be
                    present in object
        """
        for name in kwargs:
            if not hasattr(self, name):
                raise SelectError("SelectPart.set(%s) not in part")
            
            setattr(self, name, kwargs[name])
        
        
    def set_color(self, color):
        """ Set color
        :returns: previous color
        No display done here
        """
        prev_color = self.get_color()
        self.color = color        
        return prev_color

    def set_node(self, index, node):
        """ Set node to new value
        """
        if self.is_corner():
            if index != 0:
                raise SelectError("set_node %s non-zero index %d"
                                  % (self, index))
            self.loc.coord = node
        elif self.is_edge():
            self.loc.coord[index] = node
        elif self.is_region():
            self.loc.coord[index] = node
        else:
            raise SelectError("set_node: % Unrecognized part type:%d" 
                              % (self, self.part_type))             




    def set_centered_text(self, text, x=None, y=None,
                          color=None, color_bg=None,
                          height=None, width=None, display=True):
        """ Set single entry, first clearing any current entries,
        :text: letter (or string) to add
        :x: - x location of letter's center
                default: square's center
        :y: - y location of letter's center
                default: square's center
        :color: text color, default: black
        :height: height of text, default: just fits in square
        :width: width of text, default: just fits in square
        :display: True display square default: do display
        """
        self.clear_centered_texts()
        self.add_centered_text(text, x=x, y=y,
                          color=color, color_bg=color_bg,
                          height=height, width=width, display=display)


    def do_centered_text(self):
        """ Do any centered text
        """
        for ct in self.centered_text:
            self.do_a_centered_text(ct)
            
    
    def do_a_centered_text(self, ct):
        """ Do one centered text
        """
        text = ct.text 
        x = ct.x 
        y = ct.y
        color = ct.color
        height = ct.height
        color_bg = ct.color_bg
        width = ct.width
        
        """ Add letter in center of square
        :text: letter (or string) to add
        :x: - x location of letter's center
                default: square's center
        :y: - y location of letter's center
                default: square's center
        :color: text color, default: black
        :height: height of text, default: just fits in square
        """
        if text is None:
            text = "?"
        margin = 4             # boundary margin
        cx, cy, ctoright, ctotop = self.get_center_size()
        if x is None:
            x = cx
        if y is None:
            y = cy
        if color is None:
            color = "black"
        if height is None:
            height = 2*ctotop - margin*2
        
        if width is None:
            width = 2*ctoright - margin*2
        ctext_y = y         # Write starting at lower left corner
        ctext_x = x         # estimate width
        text_font = font.Font(family='Helvetica', size=-int(height))
        if ct.text_tag is not None:
            self.sel_area.canvas.delete(ct.text_tag)
            ct.text_tag = None
        tag = self.sel_area.canvas.create_text(ctext_x, ctext_y, font=text_font, text=text,
                                               fill=color)
        ct.text_tag = tag



    def display_clear(self):
        """ Clear display of this part
        """
        if not self.is_highlighted() and self.display_tag is not None:   # leave alone if highlighted
            if isinstance(self.display_tag, list):
                for tag in self.display_tag:
                    self.sel_area.canvas.delete(tag)
            else:
                self.sel_area.canvas.delete(self.display_tag)                
            self.display_tag = None
        if self.highlight_tag is not None:
            if isinstance(self.highlight_tag, list):
                for tag in self.highlight_tag:
                    self.sel_area.canvas.delete(tag)
            else:
                self.sel_area.canvas.delete(self.highlight_tag)                
            self.highlight_tag = None
        if self.move_tag is not None:
            self.sel_area.canvas.delete(self.move_tag)
            self.move_tag = None
        if self.partno_tag is not None:
            self.sel_area.canvas.delete(self.partno_tag)
            self.partno_tag = None
        self.clear_centered_texts(keep_entries=True)
        if self.text_tags:          # non centered_text
            for tag in self.text_tags:
                self.sel_area.canvas.delete(tag)
            self.text_tags = []
        if self.move_no_tag is not None:
            self.sel_area.canvas.delete(self.move_no_tag)
            self.move_no_tag = None

    def clear_centered_texts(self, keep_entries=False):
        """ Clear out all centered texts, display only
        :keep_entries: True keep entry info, default: clear out
        """
        if self.centered_text:
            for ct in self.centered_text:
                self.clear_centered_text(ct)
        if not keep_entries:
            self.centered_text = []

    def clear_centered_text(self, ct):
        """ Clear centered text display, leaving info
        """
        if ct.text_tag is not None:
            self.sel_area.canvas.delete(ct.text_tag)
            ct.text_tag = None

    def clear_move(self):
        """ Remove move_no from part
        """
        if self.move_no is not None:
            if self.move_no_tag is not None:
                self.sel_area.canvas.delete(self.move_no_tag)
            self.move_no = None

    def display_info(self, tag=None):
        """ Display part info, with optional tag
        """
        if tag is None:
            tag = ""
        SlTrace.lg("%s%s" % (tag,self))
        if self.centered_text:
            for ct in self.centered_text:
                SlTrace.lg("    centered_text: %s" % ct)
        if self.text_tags:
            for tt in self.text_tags:
                SlTrace.lg("    text: %s" % str(tt))
        
        if self.connecteds:
            for connected in self.connecteds:
                SlTrace.lg(" "*len(tag)
                            + "connected: %s" % connected)
    
    
    def display_text(self, position, **kwargs):
        """ Display text
        """
        return self.sel_area.display_text(position, **kwargs)
        
                
    def edge_dxy(self):
        """ Get "edge direction" as x-increment, y-increment pair
        """
        loc = self.loc
        if loc.type == SelectLoc.LOC_POINT:
            return 0,0                  # No change
        elif loc.type == SelectLoc.LOC_RECT:
            rect = loc.coord
            p1 = rect[0]
            p2 = rect[1]
            edx = p2[0] - p1[0]             # Find edge direction
            edy = p2[1] - p1[1]
        else:
            raise SelectError("edge_dxy: unrecognized loc type")
        return edx, edy

        
    def highlight_clear(self, tag=None, display=True):
        if self.is_highlighted():
            del self.sel_area.highlights[self.id]
            if self.highlight_tag is not None:
                self.sel_area.canvas.delete(self.highlight_tag)
                self.display_tag = None
            self.highlighted = False
            if display:
                self.display()
        
    def highlight_set(self, display=True, highlight_limit=None):
        self.highlighted = True
        if display:
            self.display() 
        self.sel_area.highlights[self.id] = PartHighlight(self,
                                    highlight_limit=highlight_limit)


    def is_highlighted(self):
        return self.highlighted

    def get_color(self):
        if hasattr(self, "color"):
            color = self.color 
        else:
            color = 0
        return color
    
    def get_fill(self):
        color = self.get_color()
        fill = color_to_fill(color)
        return fill

    COLORS = ['snow', 'ghost white', 'white smoke', 'gainsboro', 'floral white', 'old lace',
        'linen', 'antique white', 'papaya whip', 'blanched almond', 'bisque', 'peach puff',
        'navajo white', 'lemon chiffon', 'mint cream', 'azure', 'alice blue', 'lavender',
        'lavender blush', 'misty rose', 'dark slate gray', 'dim gray', 'slate gray',
        'light slate gray', 'gray', 'light grey', 'midnight blue', 'navy', 'cornflower blue', 'dark slate blue',
        'slate blue', 'medium slate blue', 'light slate blue', 'medium blue', 'royal blue',  'blue',
        'dodger blue', 'deep sky blue', 'sky blue', 'light sky blue', 'steel blue', 'light steel blue',
        'light blue', 'powder blue', 'pale turquoise', 'dark turquoise', 'medium turquoise', 'turquoise',
        'cyan', 'light cyan', 'cadet blue', 'medium aquamarine', 'aquamarine', 'dark green', 'dark olive green',
        'dark sea green', 'sea green', 'medium sea green', 'light sea green', 'pale green', 'spring green',
        'lawn green', 'medium spring green', 'green yellow', 'lime green', 'yellow green',
        'forest green', 'olive drab', 'dark khaki', 'khaki', 'pale goldenrod', 'light goldenrod yellow',
        'light yellow', 'yellow', 'gold', 'light goldenrod', 'goldenrod', 'dark goldenrod', 'rosy brown',
        'indian red', 'saddle brown', 'sandy brown',
        'dark salmon', 'salmon', 'light salmon', 'orange', 'dark orange',
        'coral', 'light coral', 'tomato', 'orange red', 'red', 'hot pink', 'deep pink', 'pink', 'light pink',
        'pale violet red', 'maroon', 'medium violet red', 'violet red',
        'medium orchid', 'dark orchid', 'dark violet', 'blue violet', 'purple', 'medium purple',
        'thistle', 'snow2', 'snow3',
        'snow4', 'seashell2', 'seashell3', 'seashell4', 'AntiqueWhite1', 'AntiqueWhite2',
        'AntiqueWhite3', 'AntiqueWhite4', 'bisque2', 'bisque3', 'bisque4', 'PeachPuff2',
        'PeachPuff3', 'PeachPuff4', 'NavajoWhite2', 'NavajoWhite3', 'NavajoWhite4',
        'LemonChiffon2', 'LemonChiffon3', 'LemonChiffon4', 'cornsilk2', 'cornsilk3',
        'cornsilk4', 'ivory2', 'ivory3', 'ivory4', 'honeydew2', 'honeydew3', 'honeydew4',
        'LavenderBlush2', 'LavenderBlush3', 'LavenderBlush4', 'MistyRose2', 'MistyRose3',
        'MistyRose4', 'azure2', 'azure3', 'azure4', 'SlateBlue1', 'SlateBlue2', 'SlateBlue3',
        'SlateBlue4', 'RoyalBlue1', 'RoyalBlue2', 'RoyalBlue3', 'RoyalBlue4', 'blue2', 'blue4',
        'DodgerBlue2', 'DodgerBlue3', 'DodgerBlue4', 'SteelBlue1', 'SteelBlue2',
        'SteelBlue3', 'SteelBlue4', 'DeepSkyBlue2', 'DeepSkyBlue3', 'DeepSkyBlue4',
        'SkyBlue1', 'SkyBlue2', 'SkyBlue3', 'SkyBlue4', 'LightSkyBlue1', 'LightSkyBlue2',
        'LightSkyBlue3', 'LightSkyBlue4', 'SlateGray1', 'SlateGray2', 'SlateGray3',
        'SlateGray4', 'LightSteelBlue1', 'LightSteelBlue2', 'LightSteelBlue3',
        'LightSteelBlue4', 'LightBlue1', 'LightBlue2', 'LightBlue3', 'LightBlue4',
        'LightCyan2', 'LightCyan3', 'LightCyan4', 'PaleTurquoise1', 'PaleTurquoise2',
        'PaleTurquoise3', 'PaleTurquoise4', 'CadetBlue1', 'CadetBlue2', 'CadetBlue3',
        'CadetBlue4', 'turquoise1', 'turquoise2', 'turquoise3', 'turquoise4', 'cyan2', 'cyan3',
        'cyan4', 'DarkSlateGray1', 'DarkSlateGray2', 'DarkSlateGray3', 'DarkSlateGray4',
        'aquamarine2', 'aquamarine4', 'DarkSeaGreen1', 'DarkSeaGreen2', 'DarkSeaGreen3',
        'DarkSeaGreen4', 'SeaGreen1', 'SeaGreen2', 'SeaGreen3', 'PaleGreen1', 'PaleGreen2',
        'PaleGreen3', 'PaleGreen4', 'SpringGreen2', 'SpringGreen3', 'SpringGreen4',
        'green2', 'green3', 'green4', 'chartreuse2', 'chartreuse3', 'chartreuse4',
        'OliveDrab1', 'OliveDrab2', 'OliveDrab4', 'DarkOliveGreen1', 'DarkOliveGreen2',
        'DarkOliveGreen3', 'DarkOliveGreen4', 'khaki1', 'khaki2', 'khaki3', 'khaki4',
        'LightGoldenrod1', 'LightGoldenrod2', 'LightGoldenrod3', 'LightGoldenrod4',
        'LightYellow2', 'LightYellow3', 'LightYellow4', 'yellow2', 'yellow3', 'yellow4',
        'gold2', 'gold3', 'gold4', 'goldenrod1', 'goldenrod2', 'goldenrod3', 'goldenrod4',
        'DarkGoldenrod1', 'DarkGoldenrod2', 'DarkGoldenrod3', 'DarkGoldenrod4',
        'RosyBrown1', 'RosyBrown2', 'RosyBrown3', 'RosyBrown4', 'IndianRed1', 'IndianRed2',
        'IndianRed3', 'IndianRed4', 'sienna1', 'sienna2', 'sienna3', 'sienna4', 'burlywood1',
        'burlywood2', 'burlywood3', 'burlywood4', 'wheat1', 'wheat2', 'wheat3', 'wheat4', 'tan1',
        'tan2', 'tan4', 'chocolate1', 'chocolate2', 'chocolate3', 'firebrick1', 'firebrick2',
        'firebrick3', 'firebrick4', 'brown1', 'brown2', 'brown3', 'brown4', 'salmon1', 'salmon2',
        'salmon3', 'salmon4', 'LightSalmon2', 'LightSalmon3', 'LightSalmon4', 'orange2',
        'orange3', 'orange4', 'DarkOrange1', 'DarkOrange2', 'DarkOrange3', 'DarkOrange4',
        'coral1', 'coral2', 'coral3', 'coral4', 'tomato2', 'tomato3', 'tomato4', 'OrangeRed2',
        'OrangeRed3', 'OrangeRed4', 'red2', 'red3', 'red4', 'DeepPink2', 'DeepPink3', 'DeepPink4',
        'HotPink1', 'HotPink2', 'HotPink3', 'HotPink4', 'pink1', 'pink2', 'pink3', 'pink4',
        'LightPink1', 'LightPink2', 'LightPink3', 'LightPink4', 'PaleVioletRed1',
        'PaleVioletRed2', 'PaleVioletRed3', 'PaleVioletRed4', 'maroon1', 'maroon2',
        'maroon3', 'maroon4', 'VioletRed1', 'VioletRed2', 'VioletRed3', 'VioletRed4',
        'magenta2', 'magenta3', 'magenta4', 'orchid1', 'orchid2', 'orchid3', 'orchid4', 'plum1',
        'plum2', 'plum3', 'plum4', 'MediumOrchid1', 'MediumOrchid2', 'MediumOrchid3',
        'MediumOrchid4', 'DarkOrchid1', 'DarkOrchid2', 'DarkOrchid3', 'DarkOrchid4',
        'purple1', 'purple2', 'purple3', 'purple4', 'MediumPurple1', 'MediumPurple2',
        'MediumPurple3', 'MediumPurple4', 'thistle1', 'thistle2', 'thistle3', 'thistle4',
        'gray1', 'gray2', 'gray3', 'gray4', 'gray5', 'gray6', 'gray7', 'gray8', 'gray9', 'gray10',
        'gray11', 'gray12', 'gray13', 'gray14', 'gray15', 'gray16', 'gray17', 'gray18', 'gray19',
        'gray20', 'gray21', 'gray22', 'gray23', 'gray24', 'gray25', 'gray26', 'gray27', 'gray28',
        'gray29', 'gray30', 'gray31', 'gray32', 'gray33', 'gray34', 'gray35', 'gray36', 'gray37',
        'gray38', 'gray39', 'gray40', 'gray42', 'gray43', 'gray44', 'gray45', 'gray46', 'gray47',
        'gray48', 'gray49', 'gray50', 'gray51', 'gray52', 'gray53', 'gray54', 'gray55', 'gray56',
        'gray57', 'gray58', 'gray59', 'gray60', 'gray61', 'gray62', 'gray63', 'gray64', 'gray65',
        'gray66', 'gray67', 'gray68', 'gray69', 'gray70', 'gray71', 'gray72', 'gray73', 'gray74',
        'gray75', 'gray76', 'gray77', 'gray78', 'gray79', 'gray80', 'gray81', 'gray82', 'gray83',
        'gray84', 'gray85', 'gray86', 'gray87', 'gray88', 'gray89', 'gray90', 'gray91', 'gray92',
        'gray93', 'gray94', 'gray95', 'gray97', 'gray98', 'gray99']

    def get_highlight_fill(self, color=None):
        if color is None:
            color = self.get_color()
        if isinstance(color, int):
            highlight_fill = ~color & 0xFFFFFF
        elif isinstance(color, str) and color.startswith("0x"):
            color = int(color)
            highlight_fill = ~color & 0xFFFFFF
        else:
            ncolor = len(self.COLORS)
            for cidx, c in enumerate(self.COLORS):
                if color == c:
                    hi_idx = (cidx+ncolor//2) % ncolor
                    highlight_fill = self.COLORS[hi_idx]
                    return highlight_fill
            highlight_fill = self.COLORS[0]
            return highlight_fill
        if isinstance(highlight_fill, int):
            highlight_fill = "0x%06X" % highlight_fill
        return highlight_fill
    
                
    def get_partno(self):
        if hasattr(self, "partno"):
            partno = self.partno 
        else:
            partno = 0
        return partno


    def get_corners(self):
        return self.get_parts(part_type="corner")
    
    
    def get_parts(self, part_type=None):
        """ Get all connecteds of type
        :type: type of part default: all types
        """
        parts = self.get_connecteds()
        of_types = []
        for part in parts:
            if part_type is None or part.part_type == part_type:
                of_types.append(part)
        return of_types

    
    def get_connected_index(self, part):
        """ Get connected part index (end), to which we are connected
        0, 1 for edges, 0 for others
        """
        is_connected = False           # Set True if find a connection
        for eci, connected in enumerate(part.connecteds):
            if self.is_same(connected):
                is_connected = True
                break     # Got corner's end of edge
        if not is_connected:
            return None
        
        return eci
    
    
    def get_connected_loc_indexes(self, part):
        """ Get connected part's location index which we share
        Returns pair our index, other index
        """
        is_connected = False           # Set True if find a connection
        our_type = self.part_type
        our_loc = self.loc
        our_coord = our_loc.coord
        part_type = part.part_type
        part_loc = part.loc
        part_coord = part_loc.coord
        
        if isinstance(our_coord, list):
            our_coords = our_coord
        else:
            our_coords = [our_coord]
        
        if isinstance(part_coord, list):
            part_coords = part_coord
        else:
            part_coords = [part_coord]
                
        for oc in our_coords:
            for pci, pc in enumerate(part_coords):
                try:
                    if oc[0] == pc[0] and oc[1] == pc[1]:
                        pcio = 1 - pci      # only two 
                        return pci, pcio
                except:
                    raise SelectError("oc,pc compare failed")
                 
        return 0,0
    
    
    def get_unconnected_index(self, part):
        """ Get unconnected part index (far end), to which we are connected
        0, 1 for edges, 0 for others
        """
        is_not_connected = False           # Set True if find a connection
        for eci, connected in enumerate(part.connecteds):
            if not self.is_same(connected):
                is_not_connected = True
                break     # Got corner's far end of edge
        if not is_not_connected:
            return None
        
        return eci

    def get_points(self):
        """ return p1, p2 of edge
        """
        nodes = self.get_nodes()
        points = []
        for node in nodes:
            points.append(node[1])
        return points
    
    
    def get_center_size(self, sz_type=None, enlarge=False):
        """ Get center, distance to right/left, distance to top/bottom
        """
        c1x,c1y,c3x,c3y = self.get_rect(sz_type=sz_type, enlarge=enlarge)
        ctoright = (c3x-c1x)/2
        cx = ctoright + c1x
        ctotop = (c3y-c1y)/2
        cy = ctotop + c1y
        return cx, cy, ctoright, ctotop


    def get_corner(self,cx, cy):
        """ Get corner closest to c1x,c1y
        :cx: end of rectangle
        :cy:  end of rectangle
        """
        min_corner = None
        min_distance = None
        corners = self.get_corners()
        for corner in corners:
            if min_corner is None or corner.distance(cx,cy) < min_distance:
                min_corner = corner
                min_distance = corner.distance(cx,cy) 
        return min_corner
    
    
    ''' All parts nee there own version
    We appear to have a problem over riding this
    def get_rect(self, sz_type=None, enlarge=False):
        """ Return type of  rectangle for this part
        """
        from select_edge import SelectEdge
        SlTrace.lg("%s needs own get_rect" % self.part_type, "get_rect")
        rect = SelectEdge.get_rect(self, sz_type=sz_type, enlarge=enlarge)
        return rect
    '''
   
    def get_corner_width(self, sz_type=None):
        if sz_type is None:
            sz_type=SelectPart.SZ_DISPLAY
        width = SelectPart.corner_width_display
        if sz_type == SelectPart.SZ_SELECT:
            width = SelectPart.corner_width_select
        elif sz_type == SelectPart.SZ_STANDOFF:
            width = SelectPart.corner_width_standoff


    def get_overlap(self, part, sz_type=None, enlarge=False):
        """ return rectangle normalized (p1,p2) which part we and part overlap, None if no overlap
        Note: get_rect returns normalized rectangles
        :part: possibly overlapping part
        :sz_type:  size type Default:  SelectPart.SZ_SELECT
        :enlarge:  True  - part is enlarged(highlighted)
        :returns: overlap rectangle if any overlap, None if no overlap
        """
        if sz_type is None:
            sz_type = SelectPart.SZ_SELECT
        self_xyxy = self.get_rect(sz_type=sz_type)
        part_xyxy = part.get_rect(sz_type=sz_type, enlarge=enlarge)
        X1 = 0
        Y1 = 1           # Mnemonic
        X2 = 2
        Y2 = 3
        """ Find left most rectangle """
        left_x = self_xyxy[X1]
        left_xyxy = self_xyxy
        right_xyxy = part_xyxy
        if part_xyxy[X1] < left_x:
            left_x = part_xyxy[X1]
            left_xyxy = part_xyxy
            right_xyxy = self_xyxy
        if right_xyxy[X1] > left_xyxy[X2]:
            return None         # left rectangle totally left of right
        
        olap_x1 = right_xyxy[X1]      # left edge of right rectangle
        if right_xyxy[X2] > left_xyxy[X2]:
            olap_x2 = left_xyxy[X2]       # limited by left rectangle
        else:
            olap_x2 = right_xyxy[X2]      # limited by right rectangle  

        """ Find top most rectangle """
        upper_y = self_xyxy[Y1]
        upper_xyxy = self_xyxy
        lower_xyxy = part_xyxy
        if part_xyxy[Y1] < upper_y:
            upper_y = part_xyxy[Y1]
            upper_xyxy = part_xyxy
            lower_xyxy = self_xyxy
        if lower_xyxy[Y1] > upper_xyxy[Y2]:
            return None         # upper rectangle totally above of lower
        
        olap_y1 = lower_xyxy[Y1]      # upper edge of lower rectangle
        if lower_xyxy[Y2] > upper_xyxy[Y2]:
            olap_y2 = upper_xyxy[Y2]       # limited by upper rectangle
        else:
            olap_y2 = lower_xyxy[Y2]      # limited by lower rectangle  


        return [(olap_x1,olap_y1), (olap_x2, olap_y2)]
        
        
    def get_x(self):
        return self.get_xy()[0]

    
    def get_y(self):
        return self.get_xy()[1]
    
        
    def get_xy(self):
        return self.loc_to_xy()    


    def is_over(self, x, y, sz_type=None, enlarge=False):
        """ Return True if part is over (x,y) ie. point (x,y) is within
        our part
        :x,y: - x,y coordinates on canvas
        :enlarge: - enlarged rectangle (highlighted part)
        """
        if sz_type is None:
            sz_type=SelectPart.SZ_SELECT
        try:
            c1x,c1y,c3x,c3y = self.get_rect(sz_type=sz_type, enlarge=enlarge)
        except:
            raise SelectError("bad get_rect call")
        if x >= c1x and x <= c3x and y >= c1y and y <= c3y:
            SlTrace.lg("is_over: %s : c1x:%d, c1y:%d, c3x:%d, c3y:%d" % (self, c1x,c1y,c3x,c3y), "is_over")
            return True
        
        return False
    
    
    def loc_to_xy(self, loc=None):
        """ Convert handle object location to associated point
        Upper left corner
        """
        if loc is None:
            loc = self.loc
        loc_type = loc.type
        if loc_type == SelectPart.LOC_POINT:
            pt = loc.coord
            return (pt[0],pt[1])
        elif loc_type == SelectPart.LOC_RECT:
            rect = loc.coord
            p1 = rect[0]
            p1x = p1[0]
            p1y = p1[1]
            return (p1x, p1y)
        else:
            raise SelectError("loc_to_xy: unrecognized loc type %d(%s)" % (loc_type, loc))

    
    def loc_key(self):
        """ Return location of part as a key
        Should be overridden by all derived classes
        """
        raise SelectError("loc_key - unrecognized part_type: %s" % self.part_type)

                        
    def set_xy(self, xy=None):
        self.xy = xy 

    def sub_type(self):
        """ Part sub type, e.g v/h - edge vertical/horizontal
        """
        return ""
    
    
    def is_corner(self):
        if self.part_type == "corner":
            return True
        return False

    def is_edge(self):
        if self.part_type == "edge":
            return True
        return False

    def is_region(self):
        if self.part_type == "region":
            return True
        return False
    
            
    def add_adjacent(self, handle):
        """ Add to list of adjacent, parts affected by changes
        to this part but not connected
        """
        if not self.is_adjacent(handle):
            self.adjacents.append(handle)
        return handle


    def get_adjacents(self, part_type="region"):
        """ Get adjacent components, mostly regions
        :part_type: include this type, default: all
        """
        adjs = []
        for adj in self.adjacents:
            if part_type == "region" or adj.part_type == part_type:
                adjs.append(adj)
        return adjs


    def get_connecteds(self):
        """ Get connecteds components, mostly regions
        :part_type: include this type, default: all
        """
        return self.connecteds

    def get_edges(self):
        edges = []
        for part in self.get_connecteds():
            if part.is_edge():
                edges.append(part)
        return edges
        
        
    def get_left_edge(self):
        """ Get leftmost edge
        """
        edges = self.get_edges()
        if not edges:
            return None
        
        if len(edges) < 2:
            return edges[0]
        
        left_edge = edges[0]
        for edge in edges[1:]:
            if edge.is_left(left_edge):
                left_edge = edge
        return left_edge        
        
        
    def get_botom_edge(self):
        """ Get botom edge
        """
        edges = self.get_edges()
        if not edges:
            return None
        
        if len(edges) < 2:
            return edges[0]
        
        botom_edge = edges[0]
        for edge in edges[1:]:
            if edge.is_below(botom_edge):
                botom_edge = edge
        return botom_edge        
        
        
    def get_right_edge(self):
        """ Get rightmost edge
        """
        edges = self.get_edges()
        if not edges:
            return None
        
        if len(edges) < 2:
            return edges[0]
        
        right_edge = edges[0]
        for edge in edges[1:]:
            if edge.is_right(right_edge):
                right_edge = edge
        return right_edge        
        
        
    def get_top_edge(self):
        """ Get top edge
        """
        edges = self.get_edges()
        if not edges:
            return None
        
        if len(edges) < 2:
            return edges[0]
        
        top_edge = edges[0]
        for edge in edges[1:]:
            if edge.is_above(top_edge):
                top_edge = edge
        return top_edge        
            
            

    def add_centered_text(self, text, x=None, y=None,
                          color=None, color_bg=None,
                          height=None, width=None, display=True):
        """ Add letter in center of square
        :text: letter (or string) to add
        :x: - x location of letter's center
                default: square's center
        :y: - y location of letter's center
                default: square's center
        :color: text color, default: black
        :height: height of text, default: just fits in square
        :width: width of text, default: just fits in square
        :display: True display square default: do display
        """
        centered_text = CenteredText(text, x=x, y=y,
                                     color=color, color_bg=color_bg,
                                     height=height, width=width)
        self.centered_text.append(centered_text)
        self.invisible = False
        if display:
            self.display()

    
            
    def add_connected(self, handle):
        """ Add to list of connected, parts affected by changes
        to this handle
        """
        if not self.is_connected(handle):
            self.connecteds.append(handle)
        return handle
    
    
    def is_adjacent(self, part):
        """ Test if part already adjacent to us
        """
        for con in self.adjacents:
            if part.id == con.id:
                return True
    
    
    def is_connected(self, handle):
        """ Test if handle already connected to us
        """
        for con in self.connecteds:
            if handle.id == con.id:
                return True

    def is_covering(self, part):
        """ Check if parts cover each other
        :returns:  True if same rectangle
        """
        if self.get_rect() == part.get_rect():
            return True
        
        return False
        
    
    def is_same(self, handle):
        """ Determine if handle is same as us
        """
        if self.id == handle.id:
            return True
        return False
        
    def set_edge_width(self, display=None, select=None, standoff=None, enlarge=None):
        """ Set edge width(s)
        """
        if display is not None:
            self.edge_width_display = display
        if select is not None:
            self.edge_width_select - select
        if standoff is not None:
            self.edge_width_standoff = standoff
        if enlarge is not None:
            self.edge_width_enlarge = enlarge
            return (self.edge_width_display, self.edge_width_select,
                    self.edge_width_standoff, self.edge_width_enlarge)


    def is_turned_on(self):
        """ Check if element is "on"
        """
        return self.turned_on
    

    def turn_off(self, display=True, move_no=None):
        """ Set part to be "off", may be "Game" specific
            default action clear "turned_on", and invisible = True
        :display: display part, default = True
        """
        if self.check_mod is not None:
            self.check_mod(self, mod_type=SelectPart.MOD_BEFORE, desc="turn_off")
        self.turned_on = False
        self.invisible = True
        self.move_no = move_no
        if self.check_mod is not None:
            self.check_mod(self, mod_type=SelectPart.MOD_AFTER, desc="turn_off")
        if display:
            self.display()


    def turn_on(self, display=True, icolor=None, icolor2=None, move_no=None):
        """ Set part to be "on", may be "Game" specific
            default action set "on", and invisible = False
        :display: display part, default = True
        :icolor: identifing color default: none
        :icolor2: identifying color2 default: none
        """
        if self.check_mod is not None:
            self.check_mod(self, mod_type=SelectPart.MOD_BEFORE, desc="turn_on")
        self.turned_on = True
        self.invisible = False
        self.icolor = icolor
        self.icolor2 = icolor2
        self.move_no = move_no
        if not self.on_highlighting:
            self.highlight_clear()
        if display:
            self.sel_area.move_announce()
            self.display()
        if self.check_mod is not None:
            self.check_mod(self, mod_type=SelectPart.MOD_AFTER, desc="turn_on")
        ###if self.sel_area.turned_on_part_call is not None:
        ###    self.sel_area.turned_on_part_call(self)

    def unhighlight(self):
        """ Remove highlight from part, if any, restoring previous color.
        """
        self.highlight_clear()
            