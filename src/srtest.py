"""
Created on September 18, 2018

@author: raysm
"""
import math
from cmath import rect
import random
import os
import sys
from tkinter import *    
import argparse
from PIL import Image, ImageDraw, ImageFont
from select_area import SelectArea
from select_window import SelectWindow
from select_color import SelectColor
from select_trace import SlTrace
from arrange_control import ArrangeControl
from select_region import SelectRegion

def pgm_exit():
    SlTrace.lg("Properties File: %s"% SlTrace.getPropPath())
    SlTrace.lg("Log File: %s"% SlTrace.getLogPath())
    sys.exit(0)

color_prog = "random"   # random, ascend, descend
color_drop_red = False
color_drop_green = False
color_drop_blue = False

nx = 5              # Number of x divisions
ny = nx             # Number of y divisions
show_id = False     # Display component id numbers
show_moved = True   # Display component id numbers
width = 600         # Window width
height = width      # Window height

base_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
SlTrace.setLogName(base_name)
SlTrace.lg("%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:])))

""" Flags for setup """
app = None                  # Application window ref
frame = None
###canvas = None
        
mw = Tk()
app = SelectWindow(mw,
                title="SelectWindow Testing",
                pgmExit=pgm_exit,
                )        
sr = None
app.arrange_control()               # Start up control, currently required

width = app.get_current_val("window_width", width)
width = int(width)
height = app.get_current_val("window_height", height)
height = int(height)
nx = app.get_current_val("figure_columns", nx)
ny = app.get_current_val("figure_rows", ny)

parser = argparse.ArgumentParser()

parser.add_argument('--color_prog', dest='color_prog', default=color_prog)
parser.add_argument('--color_drop_red', type=bool, dest='color_drop_red', default=color_drop_red)
parser.add_argument('--color_drop_green', type=bool, dest='color_drop_green', default=color_drop_green)
parser.add_argument('--color_drop_blue', type=bool, dest='color_drop_blue', default=color_drop_blue)
parser.add_argument('--nx=', type=int, dest='nx', default=nx)
parser.add_argument('--ny=', type=int, dest='ny', default=ny)
parser.add_argument('--show_id', type=bool, dest='show_id', default=show_id)
parser.add_argument('--show_moved', type=bool, dest='show_moved', default=show_moved)
parser.add_argument('--width=', type=int, dest='width', default=width)
parser.add_argument('--height=', type=int, dest='height', default=height)
args = parser.parse_args()             # or die "Illegal options"
SlTrace.lg("args: %s\n" % args)

color_prog = args.color_prog
color_drop_red = args.color_drop_red
color_drop_green = args.color_drop_green
color_drop_blue = args.color_drop_blue
nx = args.nx
ny = args.ny
nsq = nx * ny
show_id = args.show_id
show_moved = args.show_moved
width = args.width
height = args.height

run_running = False
def one_run():
    """ One run loop with a call back
    """
    if run_running:
        step_button()
    if run_running:
        time_step = app.get_current_val("time_step", 1000)
        mw.after(time_step, one_run)        # Call us after time_step        

def run_button():
    global run_running
    SlTrace.lg("srtest Run Button")
    run_running = True
    one_run()


def set_button():
    global frame, sr
    global width, height, nx, ny
    SlTrace.lg("srtest Set Button")
    ###    if canvas is not None:
    ###        SlTrace.lg("delete canvas")
    ###        canvas.delete()
    ###        canvas = None
    if frame is not None:
        SlTrace.lg("destroy frame")
        frame.destroy()
        frame = None
    
    app.update_form()    
    width = app.get_current_val("window_width", width)
    width = int(width)
    height = app.get_current_val("window_height", height)
    height = int(height)
    nx = app.get_current_val("figure_columns", nx)
    if nx == 0:
        new_nx = 1
        SlTrace.lg("nx:%d is too low - set to %d" % (nx, new_nx))
        nx = new_nx
    ny = app.get_current_val("figure_rows", ny)
    if ny == 0:
        new_ny = 1
        SlTrace.lg("ny:%d is too low - set to %d" % (ny, new_ny))
        ny = new_ny
        
        
        
    rects =  []
    min_xlen = float(app.get_component_val("figure_size", "min"))
    min_ylen = min_xlen
    
    ###rects.append(rect1)
    ###rects.append(rect2)
    xmin = .1*float(width)
    xmax = .9*float(width)
    xlen = (xmax-xmin)/float(nx)
    if xlen < min_xlen:
        SlTrace.lg("xlen(%.0f) set to %.0f" % (xlen, min_xlen))
        xlen = min_xlen
    ymin = .1*float(height)
    ymax = .9*float(height)
    ylen = (ymax-ymin)/float(ny)
    if ylen < min_ylen:
        SlTrace.lg("ylen(%.0f) set to %.0f" % (ylen, min_ylen))
        ylen = min_ylen
    def rn(val):
        return int(round(val))
                   
    for i in range(int(nx)):
        x1 = xmin + i*xlen
        x2 = x1 + xlen
        for j in range(int(ny)):
            y1 = ymin + j*ylen
            y2 = y1 + ylen
            rect = ((rn(x1), rn(y1)), (rn(x2), rn(y2)))
            rects.append(rect)
    
    im = Image.new("RGB", (width, height))
    frame = Frame(mw, width=width, height=height, bg="", colormap="new")
    frame.pack()
    canvas = Canvas(frame, width=width, height=height)
    canvas.pack()   
    sr = SelectArea(canvas, im)
    color_spec = app.get_current_val("color_spec")
    color_prog = app.ctl_list_entry("color_prog")
    color_min = app.get_component_val("color_value", "min")
    color_max = app.get_component_val("color_value", "max")
    reg_cc = SelectColor(ncolor=len(rects),
                         spec=color_spec,
                         prog=color_prog,
                         cmin=color_min,
                         cmax=color_max)
    SlTrace.lg("ncolor=%d" % len(rects), "get_color")
    SelectRegion.reset()
    for rect in rects:
        col_rect = reg_cc.get_color()
        sr.add_rect(rect, color=col_rect)

    sr.display()        
    app.set_call("run", run_button)
    app.set_call("set", set_button)
    app.set_call("pause", pause_button)
    app.set_call("step", step_button)
    app.set_call("step_down", step_down_button)


def pause_button():
    global run_running
    SlTrace.lg("srtest Pause Button")
    run_running = False

def vs(val):
    if type(val) == str:
        return val
    
    return str(val)


def step_end(name, new_value):
    """ Do appropriate end condition action for component
    :name: component base name
    :new_value: prospective new value
    """
    min_value = app.get_component_val(name, "min", new_value)
    max_value = app.get_component_val(name, "max", new_value)
    end_value = app.get_component_vql(name, "end")
    if new_value < min_value:
        if end_value == "reverse":
            app.set_component_val(name, "next", "ascend")
            new_value = min_value
        elif end_value == "wrap":
            new_value = max_value
        elif end_value == "random":
            new_value = random.randint(min_value, max_value)
    else:   # > max_value
        if end_value == "reverse":
            app.set_component_val(name, "next", "descend")
            new_value = max_value
        elif end_value == "wrap":
            new_value = min_value
        elif end_value == "random":
            new_value = random.randint(min_value, max_value)
            

def step_button(inc = 1):
    SlTrace.lg("srtest Step Button")
    for name in ["window_width", "window_height",
                 "window_x0", "window_y0",
                 "figure_columns", "figure_rows",
                 "color",
                 "time_step"]:
        next_value = app.get_component_val(name, "next", "same")
        cur_value = app.get_current_val(name, 1)
        min_value = app.get_component_val(name, "min", cur_value)
        max_value = app.get_component_val(name, "max", cur_value)
        nx = app.get_current_val("figure_columns", 1)
        ny = app.get_current_val("figure_rows", 1)
        nsq = nx * ny
        if nsq <= 0:
            nsq = 2
        inc_value = (max_value-min_value)/nsq

        if next_value == "ascend":
            new_value = cur_value + inc * inc_value
        elif next == "descend":
            new_value = cur_value - inc * inc_value
        elif next_value == "random":
            new_value = random.randint(min_value, max_value)
        else:
            new_value = cur_value + inc_value
        if new_value < min_value or new_value > max_value:
            new_value = step_end(name, new_value)
        app.set_current_val(name, new_value)
        
        SlTrace.lg("step_button: %s %s was %s  min=%s max=%s inc=%s"
                   % (name, vs(new_value), vs(cur_value),
                      vs(min_value), vs(max_value), vs(inc_value)))
    set_button()

def step_down_button():
    SlTrace.lg("srtest Step Down Button")
    step_button(inc=-1)
    set_button()
    
    
set_button()                    # Start with an implied "set"



sr.display()
mainloop()