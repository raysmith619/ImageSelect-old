"""
Created on October 30, 2018

@author: Charles Raymond Smith
"""
import os
import sys
import time
from tkinter import *    
import argparse
from select_part import SelectPart
from select_window import SelectWindow
from select_play import SelectPlay
from select_trace import SlTrace
from arrange_control import ArrangeControl
from select_region import SelectRegion
from select_squares import SelectSquares
from select_arrange import SelectArrange
from player_control import PlayerControl
from select_command import SelectCommand

def pgm_exit():
    SlTrace.lg("Properties File: %s"% SlTrace.getPropPath())
    SlTrace.lg("Log File: %s"% SlTrace.getLogPath())
    sys.exit(0)


nx = 5              # Number of x divisions
ny = nx             # Number of y divisions
show_id = False     # Display component id numbers
show_score = True   # Display score / undo /redo
width = 600         # Window width
height = width      # Window height


base_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
SlTrace.setLogName(base_name)
SlTrace.lg("%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:])))
###SlTrace.setTraceFlag("get_next_val", 1)
""" Flags for setup """
app = None                  # Application window ref
frame = None
###canvas = None
        
mw = Tk()
app = SelectWindow(mw,
                title="crs_squares Testing",
                pgmExit=pgm_exit,
                arrange_selection=False
                )
mw.lift()
mw.attributes("-topmost", True)        
btmove = 1.         #  Seconds between moves
ew_display = 3
ew_select = 5
ew_standoff = 5
trace = ""
width = app.get_current_val("window_width", width)
width = int(width)
height = app.get_current_val("window_height", height)
height = int(height)
nx = app.get_current_val("figure_columns", nx)
ny = app.get_current_val("figure_rows", ny)

parser = argparse.ArgumentParser()

parser.add_argument('--btmove', type=float, dest='btmove', default=btmove)
parser.add_argument('--ew_display', type=int, dest='ew_display', default=ew_display)
parser.add_argument('--ew_select', type=int, dest='ew_select', default=ew_select)
parser.add_argument('--ew_standoff', type=int, dest='ew_standoff', default=ew_standoff)
parser.add_argument('--nx=', type=int, dest='nx', default=nx)
parser.add_argument('--ny=', type=int, dest='ny', default=ny)
parser.add_argument('--show_id', type=bool, dest='show_id', default=show_id)
parser.add_argument('--show_score', type=bool, dest='show_score', default=show_score)
parser.add_argument('--trace', dest='trace', default=trace)
parser.add_argument('--width=', type=int, dest='width', default=width)
parser.add_argument('--height=', type=int, dest='height', default=height)
args = parser.parse_args()             # or die "Illegal options"
SlTrace.lg("args: %s\n" % args)

btmove = args.btmove
nx = args.nx
ny = args.ny
nsq = nx * ny
show_id = args.show_id
show_score = args.show_score
trace = args.trace
if trace:
    SlTrace.setFlags(trace)
width = args.width
height = args.height
ew_display= args.ew_display
ew_select = args.ew_select
ew_standoff = args.ew_standoff

SelectPart.set_edge_width_cls(ew_display,
                          ew_select,
                          ew_standoff)

run_running = False
figure_new = True           # True - time to setup new figure
                            # for possible arrangement
n_arrange = 1               #number of major cycle for rearrange
sqs = None

sp = None
move_no_label = None

def check_mod(part, mod_type=None, desc=None):
    global sp
    """ called before and after each part modificatiom
    """
    sp.check_mod(part, mod_type=mod_type, desc=desc)


def before_move(scmd):
    global move_no_label
    
    SlTrace.lg("before_move")
    
def after_move(scmd):
    SlTrace.lg("after_move")
    
    
def undo():
    global move_no_label
    SlTrace.lg("undoButton")
    if sp is None:
        return False
    res = sp.undo()
    return res
            
    
def redo():
    SlTrace.lg("redoButton")
    if sp is None:
        return False
    else:
        res = sp.redo()
        return res
    
    
def set_squares_button():
    global frame, sqs
    global width, height, nx, ny
    global n_rearrange_cycles, rearrange_cycle
    global players, sp
    global move_no_label
    
    SlTrace.lg("Squares Set Button", "button")
    ###    if canvas is not None:
    ###        SlTrace.lg("delete canvas")
    ###        canvas.delete()
    ###        canvas = None
    if frame is not None:
        SlTrace.lg("destroy frame", "destroy frame")
        frame.destroy()
        frame = None
    
    app.update_form()
        
        
        
    rects =  []
    rects_rows = []         # So we can pass row, col
    rects_cols = []
    min_xlen = app.get_component_val("figure_size", "min", 10)
    min_xlen = float(min_xlen)
    min_xlen = str(min_xlen)
    min_ylen = min_xlen
    
    ###rects.append(rect1)
    ###rects.append(rect2)
    xmin = .1*float(width)
    xmax = .9*float(width)
    xlen = (xmax-xmin)/float(nx)
    min_xlen = float(min_xlen)
    if xlen < min_xlen:
        SlTrace.lg("xlen(%.0f) set to %.0f" % (xlen, min_xlen))
        xlen = min_xlen
    ymin = .1*float(height)
    ymax = .9*float(height)
    ylen = (ymax-ymin)/float(ny)
    min_ylen = float(min_ylen)
    if ylen < min_ylen:
        SlTrace.lg("ylen(%.0f) set to %.0f" % (ylen, min_ylen))
        ylen = min_ylen
    frame = Frame(mw, width=width, height=height, bg="", colormap="new")
    frame.pack()
    
    
    canvas = Canvas(frame, width=width, height=height)
    canvas.pack()
            
    if sp is not None and sp.msg is not None:
        sp.msg.destroy()
        sp.msg = None
    sqs = SelectSquares(canvas, nrows=ny, ncols=nx,
                        width=width, height=height,
                        check_mod=check_mod)
    sp = SelectPlay(board=sqs, mw=mw, move_first=1, before_move=before_move,
                    after_move=after_move)
    if show_score:
        score_window()
    sqs.display()        
    sp.do_first_time()

def score_window():
    """ Setup score /undo/redo window
    """
    global sp
        
    move_win_x0 = 750
    move_win_y0 = 650
    geo = "+%d+%d" % (move_win_x0, move_win_y0)
    win = Tk()

    win.geometry(geo)
    move_frame = Frame(win)
    move_frame.pack()
    move_no_frame = Frame(move_frame)
    move_no_frame.pack()
    move_no = 0
    move_no_str = "Move: %d" % move_no
    move_font = ('Helvetica', '25')
    move_no_label = Label(move_no_frame,
                          text=move_no_str,
                          font=move_font
                          )
    move_no_label.pack(side="left", expand=True)
    ###move_no_label.config(width=2, height=1)
    bw = 5
    bh = 1
    undo_font = ('Helvetica', '50')
    undo_button = Button(master=move_frame, text="Undo",
                        font=undo_font,
                        command=undo)
    undo_button.pack(side="left", expand=True)
    undo_button.config(width=bw, height=bh)
    redo_button = Button(master=move_frame, text="ReDo",
                         font=undo_font,
                        command=redo)
    redo_button.pack(side="left", expand=True)
    redo_button.config(width=bw, height=bh)

    if sp is not None:
        sp.setup_score_window(move_no_label=move_no_label)
        sp.update_score_window()

def update_score_window():
    if sp is not None:
        sp.update_score_window()    

    
def vs(val):
    if type(val) == str:
        return val
    
    return str(val)

def new_edge(edge):
    """ Top level processing of new edge (line
    :edge: added edge
    """
    SlTrace.lg("We have added an edge (%s)" % (edge), "new_edge")
    ###sp.cmd_save(SelectCmd("new_edge", part=edge, player=sp.get_player()))
    sp.new_edge(edge)

def new_game():
    """ Start new game
    """
    SlTrace.lg("Starting New Game")
    set_squares_button()



def change_players():
    """ View/Change players
    """
    SlTrace.lg("PlayerControl")
    sp.player_control.control_display()
    
    
app.add_menu_command("NewGame", new_game)
app.add_menu_command("Players", change_players)
app.add_menu_command("Score", score_window)
set_squares_button()

mainloop()