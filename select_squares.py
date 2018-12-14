"""
Created on Oct 30, 2018

@author: raysmith
Creation and Manipulation of the grid (dots and squares)
of the old squares game
"""
from select_trace import SlTrace
from select_error import SelectError
from select_area import SelectArea
from select_part import SelectPart
from player_control import PlayerControl
from docutils.nodes import Part

class SelectSquares(object):
    """
    classdocs
    """


    def __init__(self, canvas, nrows=10,
                  ncols=None,
                  width=None, height=None, tbmove=.1,
                  check_mod=None,
                  down_click_call=None,
                  highlight_limit=None):
        """
        :canvas: - canvas within we are placed
        :nrows: number of rows of squares default: 10
        :ncols: number of columns of squares default: rows
        :width: window width
        :height: window height
        :tbmove: minimum time(seconds) between move detection
        :check_mod: routine called, if present, before & after
                part modification
        :highlight_limit: limit highlighting (seconds)
                default: None (None - no limit)
        """
        if ncols is None:
            ncols = nrows
        self.canvas = canvas
        self.nrows = nrows
        self.ncols = ncols
        if width is None:
            width = canvas.winfo_width()
        self.width = width
        if height is None:
            height = canvas.winfo_height()
        self.height = height
        self.drawn_lines = []           # lines drawn
            
        min_xlen = 10
        min_ylen = min_xlen
        self.check_mod = check_mod
        self.tbmove = tbmove
        self.highlight_limit = highlight_limit
        
        rects =  []
        rects_rows = []         # So we can pass row, col
        rects_cols = []
        self.down_click_call = down_click_call
        
        
        def rn(val):
            return int(round(val))
        xmin = .1*float(width)
        xmax = .9*float(width)
        xlen = (xmax-xmin)/float(ncols)
        min_xlen = float(min_xlen)
        if xlen < min_xlen:
            SlTrace.lg("xlen(%.0f) set to %.0f" % (xlen, min_xlen))
            xlen = min_xlen
        ymin = .1*float(height)
        ymax = .9*float(height)
        ylen = (ymax-ymin)/float(nrows)
        min_ylen = float(min_ylen)
        if ylen < min_ylen:
            SlTrace.lg("ylen(%.0f) set to %.0f" % (ylen, min_ylen))
            ylen = min_ylen
        for i in range(int(ncols)):
            col = i+1
            x1 = xmin + i*xlen
            x2 = x1 + xlen
            for j in range(int(nrows)):
                row = j+1
                y1 = ymin + j*ylen
                y2 = y1 + ylen
                rect = ((rn(x1), rn(y1)), (rn(x2), rn(y2)))
                rects.append(rect)
                rects_rows.append(row)
                rects_cols.append(col)
        
        self.area = SelectArea(canvas, tbmove=self.tbmove,
                               check_mod=self.check_mod,
                               down_click_call=self.down_click_call,
                               highlight_limit=self.highlight_limit)
        ###SelectRegion.reset()
        for i, rect in enumerate(rects):
            row = rects_rows[i]
            col = rects_cols[i]
            self.area.add_rect(rect, row=row, col=col,
                            draggable_edge=False,
                            draggable_corner=False,
                            draggable_region=False,   
                            invisible_region=True,
                            invisible_edge=True)
        for part in self.area.get_parts():
            if part.is_corner():
                part.set(display_shape="circle",
                           display_size=10,
                           color="blue")
            elif part.is_edge():
                part.set(edge_width_select=50,
                           edge_width_display=5,
                           on_highlighting=True,
                           off_highlighting=True,
                           color="lightgreen")
            elif part.is_region():
                part.set(color='light slate gray')
                top_edge = part.get_top_edge()
                top_edge.row = part.row 
                top_edge.col = part.col
                right_edge = part.get_right_edge()
                right_edge.row = part.row 
                right_edge.col = part.col + 1
                botom_edge = part.get_botom_edge()
                botom_edge.row = part.row + 1 
                botom_edge.col = part.col
                left_edge = part.get_left_edge()
                left_edge.row = part.row 
                left_edge.col = part.col
        self.complete_square_call = None                # Setup for complete square call
        self.new_edge_call = None                       # Setup for new edge call
        ###self.area.add_turned_on_part_call(self.new_edge)
        self.player_control = PlayerControl(self, display=False)


    def get_part(self, id=None, type=None, sub_type=None, row=None, col=None):
        """ Get basic part
        :id: unique part id
        :type: part type e.g., edge, region, corner
        :row:  part row
        :col: part column
        :returns: part, None if not found
        """
        return self.area.get_part(id=id, type=type, sub_type=sub_type, row=row, col=col)
                
    
    def get_parts_at(self, x, y, sz_type=SelectPart.SZ_SELECT):
        """ Check if any part is at canvas location provided
        If found list of parts
        :Returns: SelectPart[]
        """
        return self.area.get_parts_at(x,y,sz_type=sz_type)



    def get_xy(self):
        """ get current mouse position (or last one recongnized
        :returns: x,y on area canvas, None if never been anywhere
        """
        return self.area.get_xy()

    
    def add_complete_square_call(self, call_back):
        """ Add function to be called upon completed square
        :call_back: call back (edge, region) - None - remove call back
        """
        self.complete_square_call = call_back


    def add_down_click_call(self, call):
        """ Add down click processing function
        :call: down click processing function
        """
        self.area.add_down_click_call(call)
        
    
    def add_new_edge_call(self, call_back):
        """ Add function to be called upon newly added edge
        :call_back: call back (edge) - None - remove call back
        """
        self.new_edge_call = call_back
        
    def complete_square(self, edge, regions):
        """ Report completed square
        :edge: - edge that completed the region
        :regions: - completed region(s)
        """
        SlTrace.lg("Completed region edge=%s" % (edge), "complete_square")
        if self.complete_square_call is not None:
            self.complete_square_call(edge, regions)


    def set_down_click_call(self, down_click_call):
        """ Direct down_click processing
        """
        self.down_click_call = down_click_call


    def is_square_complete(self, edge, squares=None):
        """ Determine if this edge completes a square(s)
        :edge: - potential completing edge
        :squares: list, to which any completed squares(regions) are added
                Default: no regions are added
        :returns: True iff one or more squares are completed
        """
        return self.area.is_square_complete(edge, squares=squares)
        
        
    def new_edge(self, edge):
        """ Report new edge added
        :edge: - edge that was added
        """
        SlTrace.lg("SelectSquares.new_edge: edge=%s" % (edge), "new_edge")
        if self.new_edge_call is not None:
            self.new_edge_call(edge)
        self.area.stroke_info.setup()      # Reset stroke search


    def disable_moves(self):
        """ Disable(ignore) moves by user
        """
        self.area.disable_moves()
        
        
    def enable_moves(self):
        """ Enable moves by user
        """
        self.area.enable_moves()


        
    def down_click(self, part, event=None):
        """ Process down click over highlighted part
        All highlighted parts elicit a call
        :part: highlighted part
        :event: event if available
        :Returns: True if processing is complete
        """
        if self.down_click_call is not None:
            return self.down_click_call(part, event=event)
        
        """ Self processing
        """
        if part.is_edge() and not part.is_turned_on():
            SlTrace.lg("turning on %s" % part, "turning_on")
            self.drawn_lines.append(part)
            part.turn_on()
            regions = part.get_adjacents()      # Look if we completed any squares
            for square in regions:
                if square.is_complete():
                    self.complete_square(part, square)
                    
            return True             # Indicate processing is done
    
        return False


    def player_control(self):
        """ Setup player control
        """
        if self.player_control is None:
            self.player_control = PlayerControl(self, display=False)
        self.player_control.control_display()
        

    def stroke_call(self, part=None, x=None, y=None):
        """ Call back from sel_area.add_stroke_call
        """
        
        self.down_click(part)
        
            
    def display(self):
            self.area.display()
    

    

    def remove_parts(self, parts):
        """ Remove deleted or changed parts
        Only clears display, leaving part in place
        :parts: list of parts to be removed
        """
        for part in parts:
            d_part = self.area.get_part(id=part.id)
            if d_part is None:
                raise SelectError("No part(id=%d) found %s"
                                   % (part.id, part))
                continue
            d_part.display_clear()
            d_part.set(invisible=True)
    
    def insert_parts(self, parts):
        """ Add new or changed parts
        Replaces part of same id, redisplaying
        :parts: list of parts to be env_added
        """
        for part in parts:
            d_part = self.area.get_part(id=part.id)
            if d_part is None:
                raise SelectError("insert_parts: No part(id=%d) found %s"
                                   % (part.id, part))
                continue
            self.set_part(part)


    def set_part(self, part):
        """ Set base part.contents to values of Part
        
        :part: part structure with new values
        """
        pt = self.area.parts_by_id[part.id]
        if pt is None:
            SlTrace.lg("part %s(%d) is not in area - skipped"
                       % (part, part.id))
            return

        pt.__dict__ = part.__dict__.copy()