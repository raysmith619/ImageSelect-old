# select_region.py        

from select_trace import SlTrace
from select_error import SelectError
from select_loc import SelectLoc
from select_part import SelectPart
from select_edge import SelectEdge

class SelectRegion(SelectPart):
    fill = "clear"                  # Default region color
    fill_highlight = "lightgray"   # Default region highlight color
    partno = 0                       # Incremented each new region

    @classmethod
    def reset(cls):
        cls.partno = 0
        
            
    def __init__(self, sel_area, rect=None, color=None):
        """ Setup region
        :sel_area: reference to basis, Needed to display
        """
        SelectPart.__init__(self, sel_area, "region",  rect=rect)
        self.color = color
        SelectRegion.partno += 1
        self.partno = SelectRegion.partno


    def add_rect(self, rect, color=None):
        """ Add rectangle 
        """                
        rec_ps = [None] * 4
        ulX, ulY = rect[0][0], rect[0][1]
        lrX, lrY = rect[1][0], rect[1][1]
        rec_ps[0] = (ulX, ulY)
        rec_ps[1] = (lrX, ulY) 
        rec_ps[2] = (lrX, lrY)
        rec_ps[3] = (ulX, lrY)
        for pi1 in range(0, 3+1):
            pi2 = pi1 + 1
            if pi2 >= len(rec_ps):
                pi2 = 0          # Ends at first
            pt1 = rec_ps[pi1]
            pt2 = rec_ps[pi2]
            self.add_edge(pt1, pt2)


    def add_edge(self, pt1, pt2):
        """ Add edge, creating edge if new to area
        Also adds corners, creating corners if new to area
        """
        edge = self.get_edge(pt1, pt2)  # get, create if new
        self.add_connects(edge)
        corners = edge.get_corners()
        self.add_connects(corners)
        edge.add_adjacent(self)         # Associate with all connecteds
        for corner in corners:
            corner.add_adjacent(self)

        
    def add_corners(self, corners):
        """ Add corners to region
        :corners: one or more corner locations
        """
        if not isinstance(corners, list):
            corners = [corners]     # Treat as an array of one
        for corner in corners:
            self.add_part(corner)
                    
    def has_corner(self, point):
        """ Check if corner already present in region
        """
        for corner in self.parts:
            if not corner.is_corner():
                continue
            loc = corner.loc
            pt = loc.coord
            if pt[0] == point[0] and pt[1] == point[1]:
                return True     # Corner already present
        return False            # No such corner present
        

    def get_nodes(self, indexes=None):
        """ Find nodes/points of part
        return pairs (index, node)
        """
        nodes = []
        if indexes is None:
            nodes = [(0,self.loc.coord[0]), (1,self.loc.coord[1])]
        else:
            if not isinstance(indexes, list):
                indexes = [indexes]     # Make a list of one
            for index in indexes:
                nodes.append((index,self.loc.coord[index]))
        return nodes


    def set_node(self, index, node):
        """ Set node to new value
        """
        self.loc.coord[index] = node


    def current_edge(self, pt1, pt2):
        """ Return edge with these specifications, None if none found
        """
        return self.sel_area.current_edge(pt1, pt2)

    
    def display(self):
        """ Display region as a rectangle
        We leave room for the corners at each end
        Highlight if appropriate
        :region: Corner handle
        :Returns: object tag for deletion
        """
        c1x,c1y,c3x,c3y = self.get_rect()
        if self.color is None:
            SlTrace.lg("region.color is None")
            fill = self.fill
        else:
            fill = "#%06x" % self.color
        SlTrace.lg("region fill=%s" % fill, "get_color")
        self.display_clear()
        if SlTrace.trace("region_rect"):
            SlTrace.lg("region: %d c1x=%d c1y=%d c3x=%d c3y=%d"
                       % (self.partno, c1x, c1y, c3x, c3y))
            if c3y < c1y:
                SlTrace.lg ("region: %d c3y(%d) < c1y(%d)" % (self.partno, c3y, c1y))
                SlTrace.lg("Strange?")
        tag = self.sel_area.canvas.create_rectangle(
                            c1x, c1y, c3x, c3y,
                            fill=fill)
        self.display_tag = tag
        if SlTrace.trace("regno"):
            cx = (c1x+c3x)/2
            cy = (c1y+c3y)/2
            disp_str = "%d" % self.partno
            self.partno_tag = self.sel_area.display_text((cx, cy), text=disp_str)
            SlTrace.lg("region: %d  %s (%d,%d) %s"
                       % (self.partno, self.part_type, cx,cy, disp_str))

    def edge_dxy(self):
        """ Get "edge direction" as x-increment, y-increment pair
        """
        loc = self.loc
        rect = loc.coord
        p1 = rect[0]
        p2 = rect[1]
        edx = p2[0] - p1[0]             # Find edge direction
        edy = p2[1] - p1[1]
        return edx, edy


    def get_edge(self, pt1, pt2):
        """ Get edge, creating edge if new to area
        Also adds corners, creating corners if new to area
        """
        edge = self.current_edge(pt1, pt2)
        if edge is None:
            edge = SelectEdge(rect=[pt1, pt2])             
        return edge
    
    
    def get_rect(self, sz_type=None, enlarge=False):
        """ Get upper left x,y and lower right x,y region
        :handle: region's SelectPart
        Region is a set of parts, with the corners being the boundary
        """
        if sz_type is None:
            sz_type=SelectPart.SZ_DISPLAY
        corners = []
        for part in self.connecteds:
            if part.is_corner():
                corners.append(part)
        if len(corners) < 4:
            SlTrace.lg("Region with %d corners %s" % (len(corners), self))
            co = self.loc.coord
            c1x = co[0][0]
            c1y = co[0][1]
            c3x = co[1][0]
            c3y = co[1][1]
        else:
            c1x = corners[0].loc.coord[0]
            c1y = corners[0].loc.coord[1]
            c3x = corners[2].loc.coord[0]
            c3y = corners[2].loc.coord[1]
        c1x,c1y,c3x,c3y = SelectLoc.order_ul_lr(c1x,c1y,c3x,c3y)
        wlen = self.get_edge_width(sz_type)
        c1x += wlen
        c1y += wlen
        c3x -= wlen
        c3y -= wlen
        if enlarge:
            c1x -= self.edge_width_enlarge
            c1y -= self.edge_width_enlarge 
            c3x += self.edge_width_enlarge
            c3y += self.edge_width_enlarge
        if SlTrace.trace("region_rect"):
            SlTrace.lg("region.get_rect: %d c1x=%d c1y=%d c3x=%d c3y=%d"
                       % (self.partno, c1x, c1y, c3x, c3y))
            if c3y < c1y:
                SlTrace.lg ("region: %d c3y(%d) < c1y(%d)" % (self.partno, c3y, c1y))
                SlTrace.lg("Strange?")
                for connected in self.connecteds:
                    SlTrace.lg("%d: %s loc_key: %s"
                                % (connected.id, connected.part_type, connected.loc_key()))
            
            
            
        return c1x,c1y,c3x,c3y


    
    def loc_key(self):
        """ Return location of part as a key
        """
        key = tuple(self.loc.coord)
        return (key)
