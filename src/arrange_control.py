# arrange_control.py 25Sep2018

from tkinter import *
import random
from select_error import SelectError
from select_trace import SlTrace
from builtins import str
from select_dd_choice import SelectDDChoice
"""
Arrangement control window layout
            ___  min____ max___ inc___ end (loop) reverse
window
    width
    height

figure
    rows
    columns

time
    steps
    run


[run] [pause] [step] by___
[RESET] [STOP]
"""

class ControlEntry:
    
    def __init__(self, name, ctl_widget=None,
                 value = None,
                 unknown_type=False,
                 default_value=None,
                 value_type=int,
                 width=4):
        """ Setup control Entry for later access
        """
        self.name = name
        self.unknown_type = unknown_type
        self.value_type = value_type
        self.ctl_widget = ctl_widget
        if self.unknown_type:
            self.value = value
            if default_value is None:
                default_value = value
            self.default_value = default_value
        else:
            if default_value is not None:
                if isinstance(default_value, str) and self.value_type is not str:
                    default_value = self.str_to_value(default_value)
            self.default_value = default_value
            if value is None:
                value = default_value
    
            if value is not None:
                if isinstance(value, str):
                    value = self.str_to_value(value)
            self.value = value
        self.width = width
        
        
        
    def str_to_value(self, string):
        """ Convert string on entry to internal value based on type
            "" for non-string data evaluates to None
        :str: external string type
        :returns: data type
        """
        if string is None:
            return string
        
        if self.value_type is int:
            if string == "":
                return None
            
            return int(string)
        
        elif self.value_type is float:
            if string == "":
                return None
            
            return float(string)
        
        elif self.value_type is str:
            return string
        else:
            print("str_to_value: Unrecognized value_type:")

        
        return string
    def to_value(self, val):
        """ Convert val on entry to internal value based on type
            "" for non-string data evaluates to None
        :val: external type, default return entry value
        :returns: data type
        """
        if val is None:
            return None
        
        if self.value_type is None:
            self.value_type = type(val)
        if isinstance(val, str):
            return self.str_to_value(val)
        
        if self.value_type is int:
            return int(val)
        
        if self.value_type is float:
            return float(val)

        if self.value_type is str:
            return str(val)

        raise SelectError("str_to_value: Unrecognized value_type:")
            


    
class ArrangeControl(Toplevel):
    CONTROL_NAME_PREFIX = "controlName"
    
    def __init__(self, ctlbase, title=None, change_call=None):
        """ Display / Control of figure
        :ctlbase: base control object
        :change_call: if present,called when control changes
        """
        self.control_d = {}      # name : (name, ctl_widget, default_value)
        self.call_d = {}        # Call by name
        self.ctl_lists = {}     # Control selection lists [current_index, selection_list]
        ###Toplevel.__init__(self, parent)
        self.ctlbase = ctlbase
        """ Setup control names found in properties file
        Updated as new control entries are added
        """
        prop_keys = SlTrace.getPropKeys()
        pattern = ArrangeControl.CONTROL_NAME_PREFIX + r"\.(.*)"
        rpat = re.compile(pattern)
        name_d = {}
        ### TBD I need to think about what is going on here
        for prop_key in prop_keys:
            rmatch = re.match(rpat, prop_key)
            if rmatch:
                name = rmatch[1]
                prop_val = SlTrace.getProperty(prop_key)
                name_d[name] = prop_val
        self.ctl_name_d = name_d
        
        
        if title is None:
            title = "Arrange"
        self.change_control = change_call
        win_width = self.get_current_val("ac_window_width", 500)
        win_height = self.get_current_val("ac_window_height", 400)
        win_x0 = self.get_current_val("ac_window_x0", 200)
        win_y0 = self.get_current_val("ac_window_y0", 200)
                    
        self.mw = Toplevel()
        win_setting = "%dx%d+%d+%d" % (win_width, win_height, win_x0, win_y0)

        
        self.mw.geometry(win_setting)
        self.mw.title(title)
        top_frame = Frame(self.mw)
        self.mw.protocol("WM_DELETE_WINDOW", self.delete_window)
        top_frame.pack(side="top", fill="both", expand=True)
        self.top_frame = top_frame
        
        controls_frame = Frame(top_frame)
        controls_frame.pack(side="top", fill="both", expand=True)
        self.controls_frame = controls_frame
 
        win_label = Label(master=controls_frame, text="Window", anchor='w')
        win_label.pack(side="top", fill="both", expand=True)
        self.add_change_ctl(master=controls_frame, ctl_name="window_width", text="width", value=win_width)
        self.add_change_ctl(master=controls_frame, ctl_name="window_height", text="height", value=win_height)
        ###self.add_change_ctl(master=controls_frame, ctl_name="window_x0", text="x0", value=win_width*.1)
        ###self.add_change_ctl(master=controls_frame, ctl_name="window_y0", text="y0", value=win_height*.1)

        
        Label(master=controls_frame, text="")
        win_label.pack(side="top", fill="both", expand=True) 
        win_label = Label(master=controls_frame, text="Figure", anchor='w')
        win_label.pack(side="top", fill="both", expand=True)
        self.add_change_ctl(master=controls_frame, ctl_name="figure_columns", text="columns", value=6)
        self.add_change_ctl(master=controls_frame, ctl_name="figure_rows", text="rows", value=5)
        self.add_change_ctl(master=controls_frame, ctl_name="figure_size", text="size",
                             value=50, min=20, max=200)

        
        Label(master=controls_frame, text="")
        win_label.pack(side="top", fill="both", expand=True) 
        win_label = Label(master=controls_frame, text="Colors", anchor='w')
        win_label.pack(side="top", fill="both", expand=True)
        selection_list = self.set_list(ctl_name="color_spec",
                selection_list = ["frequency", "rgb", "bw", "rgb1prim", "rgb2prim"])
        self.add_color_ctl(master=controls_frame, ctl_name="color_spec", text="specification",
                           selection=selection_list,
                           selection_default= "rgb")
        selection_list = self.set_list(ctl_name="color_prog",
                selection_list = ["random", "ascend", "descend"])
        self.add_color_ctl(master=controls_frame, ctl_name="color_prog", text="progression",
                           selection=selection_list,
                           selection_default= "random")
        self.add_color_ctl(master=controls_frame, ctl_name="color_value", text="value")


 
        Label(master=controls_frame, text="")
        win_label.pack(side="top", fill="both", expand=True) 
        win_label = Label(master=controls_frame, text="Time(msec)", anchor='w')
        win_label.pack(side="top", fill="both", expand=True)
        self.add_change_ctl(master=controls_frame, ctl_name="time_step", text="step", value=1)
       
 
 
        
        run_pause_frame = Frame(top_frame)
        run_pause_frame.pack(side="top", fill="both", expand=True)
        self.run_pause_frame = run_pause_frame
        
        set_button = Button(master=run_pause_frame, text="Set", command=self.set)
        set_button.pack(side="left", expand=True)
        run_button = Button(master=run_pause_frame, text="Run", command=self.run)
        run_button.pack(side="left", expand=True)
        pause_button = Button(master=run_pause_frame, text="Pause", command=self.pause)
        pause_button.pack(side="left", expand=True)
        step_button = Button(master=run_pause_frame, text="Step", command=self.step)
        step_button.pack(side="left", expand=True)
        step_button = Button(master=run_pause_frame, text="StepDown", command=self.step_down)
        step_button.pack(side="left", expand=True)


    def add_change_ctl(self, master=None, ctl_name=None, text=None, value=None,
                       min=None, max=None):
        """ Add change control to data base and to frame
        :master: master frame into which we place the controls
        :ctl_name: unique name for this control in the data base
                    prefix for sub components
        :text:   text for control section
        :value:  Optional value to set / display for current value
        :min: Optional min value, default is value
        :max: Optional max value, default is value
        """
        ctl_frame = Frame(master=master)
        ctl_frame.pack(side="top", fill="both", expand=True)
        Label(master=ctl_frame, text="    ", anchor='w').pack(side="left")
        ctl_label = Label(master=ctl_frame, text=text, anchor='w')
        ctl_label.pack(side="left", fill="both", expand=False)
        if min is None:
            min = value
        if max is None:
            max = value
        self.add_change_component(ctl_frame, base=ctl_name, name="current",
                                  value=value, text="")
        sp = Label(ctl_frame, text="    ", anchor="w")
        sp.pack(side="left")
        self.add_change_component(ctl_frame, base=ctl_name, name="min", value=min)
        self.add_change_component(ctl_frame, base=ctl_name, name="max", value=max)
        self.add_change_component(ctl_frame, base=ctl_name, name="next",
                                    selection=["same", "random", "ascend", "descend"],
                                    selection_default="random")
        self.add_change_component(ctl_frame, base=ctl_name, name="end",
                                    selection=["same", "reverse", "wrap", "random"],
                                    selection_default="reverse")


    def add_color_ctl(self, master=None, ctl_name=None, text=None, value=None,
                      selection=None, selection_default=None):
        """ Setup color control
        :master: master frame into which we place the controls
        :ctl_name: unique name for this control in the data base
                    prefix for sub components
        :text:   text for control section
        :value:  Optional value to set / display for current value
        :selection: - list of selection values
        :selection_default: - value of selection default
        """
        ctl_frame = Frame(master=master)
        ctl_frame.pack(side="top", fill="both", expand=True)
        Label(master=ctl_frame, text="    ", anchor='w').pack(side="left")
        ctl_label = Label(master=ctl_frame, text=text, anchor='w')
        ctl_label.pack(side="left", fill="both", expand=False)
        if selection is not None:
            self.add_change_component(ctl_frame, base=ctl_name, name="current",
                                    text="",
                                    selection=selection,
                                    selection_default=selection_default)
        else:
            self.add_change_component(ctl_frame, base=ctl_name, name="current",
                                    text="")
            
        self.add_change_component(ctl_frame, base=ctl_name, name="min")
        self.add_change_component(ctl_frame, base=ctl_name, name="max")
        self.add_change_component(ctl_frame, base=ctl_name, name="next",
                                            selection=["same", "random", "ascend", "descend"],
                                            selection_default="same")
        self.add_change_component(ctl_frame, base=ctl_name, name="end",
                                            selection=["reverse", "wrap", "random"],
                                            selection_default="reverse")
        

    def add_change_component(self, ctl_frame,
                             base=None, name=None,
                             text=None, typectl=Entry,
                             selection=None,
                             selection_default=None,
                             value=None,
                             value_type=None,
                             width=4):
        """ Add change control component
        :ctl_frame: frame in to which we add this component
        :base: base name e.g. "window"
        :name: component name e.g. "width"
        :selection: If present, array of selection strings
        :selection_default: selection default, None -> first
        :text: displayed text None - use name
                "" - no text label
        :typectl: Control widget type, default: Entry
        :value:  initial value (default), if not already present
        :value_type: Value type default: int
        :width: Field width in characters
        """
        if text is None:
            text = name
        
        if text != "":
            label_entry = Label(ctl_frame, text= "  "+text, anchor="w")
            label_entry.pack(side="left")
        ctl_name = base + "_" + name
        if selection is not None:
            if selection_default is None:
                selection_default = selection[0]
            val_entry = SelectDDChoice(ctl_frame,
                                     selection=selection,
                                     default=selection_default)
            value_type = str
            self.update_control_entry(ctl_name, ctl_widget=val_entry,
                                    value=value,
                                    value_type=value_type,
                                    width=width)

        else:
            if ctl_name in self.ctl_name_d:
                ctn = self.ctl_name_d[ctl_name]
                if isinstance(ctn, ControlEntry):
                    ctl_value = ctn.value  # Get entry value
                elif isinstance(ctn, str):
                    ctl_value = ctn           # Use properties value
                else:
                    ctl_value = value
                value = ctl_value    
            val_entry = Entry(ctl_frame, width=width)
            self.update_control_entry(ctl_name, ctl_widget=val_entry,
                                                value=value,
                                                value_type=value_type,
                                                width=width)
        val_entry.pack(side="left")
        self.show_entry(ctl_name)

    
    def show_entry(self, name):
        """ Display entry value in form
        :name: control name
        """
        ctl_entry = self.get_ctl_entry(name)
        if ctl_entry is None:
            return
        
        value = ctl_entry.value
        if value is not None:
            self.set_entry_field(name, value)     # Done after entry is created

       
    def delete_window(self):
        """ Process Trace Control window close
        """
        if self.mw is not None:
            self.mw.destroy()
            self.mw = None
        
        if self.ctlbase is not None and hasattr(self.ctlbase, 'arc_destroy'):
            self.tcbase.tc_destroy()


    def get_ctl_default(self, value_type):
        """
        Get control value from properties
        :value_type: - value data type None - int
        :returns: value, null if none
        """
        if value_type is None:
            value_type  = int
        if self.ctl_name_d is None:
            prop_keys = SlTrace.getPropKeys()
            pattern = ArrangeControl.CONTROL_NAME_PREFIX + r"\.(.*)"
            rpat = re.compile(pattern)
            name_d = {}
            ### TBD I need to think about what is going on here
            for prop_key in prop_keys:
                rmatch = re.match(rpat, prop_key)
                if rmatch:
                    name = rmatch[1]
                    prop_val = SlTrace.getProperty(prop_key)
                    name_d[name] = prop_val
            self.ctl_name_d = name_d
        try:
            value_str = self.ctl_name_d[name_d]
        except:
            return None
            
        if value_type is str:
            return value_str
        
        if value_str == "":
            return None
        
        if value_type is int:
            return int(value_str)
        
        if value_type is float:
            return float(value_str)
        
        return value_str     

    
    def set_call(self, name, function):
        """ Set for call back
        """
        self.call_d[name] = function
        
        
                
    def set_control_value(self, name, val,
                          unknown_type = False,
                          change_cb=True):
        """ Set trace level, changing Control button if requested
        An entry is created if none exists
        :name: - control name
        :val: - value to set
        :unknoqn_type: True - don't check / convert type
        :change_cb: True(default) appropriately change the control
        """
        ctl_entry = self.get_ctl_entry(name)
        if ctl_entry is None:
            self.control_d[name] = ControlEntry(name, value=val,
                                                unknown_type=unknown_type,
                                                default_value=val)
            ctl_entry = self.get_ctl_entry(name)
            
        if ctl_entry.ctl_widget is not None and change_cb:
            self.set_entry_field(name, val)


    
    def set_entry_field(self, name, val):
        """ Set control widget field value
        """
        ctl_entry = self.get_ctl_entry(name)
        if ctl_entry is None:
            return
        
        ctl_widget = ctl_entry.ctl_widget
        if ctl_widget is None:
            return
        
        if isinstance(ctl_widget, Entry):
            ctl_widget.delete(0,END)
            ctl_widget.insert(0,str(val))
        elif isinstance(ctl_widget, SelectDDChoice):
            ctl_widget.set_field(val)    

    def update_control_entry(self, ctl_name,
                            ctl_widget=None,
                            default_value=None,
                            value=None,
                            value_type=None,
                            width=None):
        """ Update / create control entry
        :ctl_name: full control name
        :ctl_widget: control widget, if one
        :default_value: default value
        :value_type: data type
        :width: entry value field width, in characters
        """
        if ctl_name not in self.control_d:
            self.control_d[ctl_name] = ControlEntry(ctl_name,
                                                    ctl_widget=ctl_widget,
                                                    value=value,
                                                    default_value=default_value,
                                                    value_type=value_type,
                                                    width=width)
            self.ctl_name_d[ctl_name] = self.control_d[ctl_name]
        else:
            ctl_entry = self.control_d[ctl_name]
            if ctl_widget is not None:
                ctl_entry.ctl_widget = ctl_widget    
            if value is not None:
                ctl_entry.value = value    
            if default_value is not None:
                ctl_entry.default_value = default_value    
            if value_type is not None:
                ctl_entry.value_type = value_type    
            if width is not None:
                ctl_entry.width = width    



    def get_ctl_names(self):
        """ Get sorted list of control names
            This is a union of control_d and those in the properties file
            
        """
        names = sorted(self.control_d.keys())
        return names


    def get_component_val(self, name, comp_name, default):
        """ Get component value of named control
        Get value from widget, if present, else use entry value
        """
        name_comp = name + "_" + comp_name
        comp_entry = self.get_ctl_entry(name_comp)
        if comp_entry is None:
            return self.set_component_value(name, comp_name, default)
        if comp_entry.value_type is None:
            if default is not None:
                comp_entry.value_type = type(default)
        if comp_entry.ctl_widget is None or comp_entry.ctl_widget.get() == "":
            val = comp_entry.default_value
            if val is None:
                return self.set_component_value(name, comp_name, default)
            return self.set_component_value(name, comp_name, val)
        field = comp_entry.ctl_widget.get()
        if comp_entry.value_type is not str and field == "":
            return self.set_component_value(name, comp_name,
                                             comp_entry.default_value)
        if comp_entry.value_type is int:
            comp_entry.value = int(field)
        elif comp_entry.value_type is float:
            comp_entry.value = float(field)
        else:
            comp_entry.value = field
        return self.set_component_value(name, comp_name, comp_entry.value)


    def set_component_value(self, name, comp_name, value):
        """ Set component value of named control
        Get value from widget, if present, else use entry value
        :name: - base name
        :comp_name: - component name
        :value: if present, use this value,  else get from widget
        """
        name_comp = name + "_" + comp_name
        comp_entry = self.get_ctl_entry(name_comp)
        if comp_entry is None:
            return value
        
        if value is not None:                
            comp_entry.value = comp_entry.to_value(value)
            self.show_entry(name_comp)
        self.update_property(name_comp)
        return value
    

    def get_current_val(self, name, default):
        """ Get current value of named control
        Get value from widget, if present, else use entry value
        """
        return  self.get_component_val(name, "current", default)


    def set_current_val(self, name, value):
        """ Set component value of named control
        Get value from widget, if present, else use entry value
        """
        self.set_component_value(name, "current", value)


    def get_inc_val(self, name, default):
        """ Get current value of named control
        Get value from widget, if present, else use entry value
        """
        return  self.get_component_val(name, "inc", default)
    

    def get_ctl_entry(self, name):
        try:
            return self.control_d[name]
        except:
            return None


    def set_list(self, ctl_name, selection_list = None, current_index = 0):
        """ Setup selection list for control
        :ctl_name: control name (list name)
        :selection_list: list of choices
        """
        lists_entry = [current_index, selection_list]
        self.ctl_lists[ctl_name] = lists_entry
        return selection_list
    
    def ctl_list(self, ctl_name):
        lists_entry = self.ctl_list[ctl_name]
        return lists_entry[1]
    
    def ctl_list_entry(self, ctl_name, prog=None, end="wrap"):
        """ Return next list entry, given prog: same, random, ascend, descend
        """
        if prog is None:
            prog = self.get_component_val(ctl_name, "next", "ramdom")
        if end is None:
            end = self.get_component_val(ctl_name, "end", "wrap")
        
        ctl_list_entry = self.ctl_lists[ctl_name]
        ctl_list_cur = ctl_list_entry[0]
        ctl_list = ctl_list_entry[1]
        nchoice = len(ctl_list)
        if prog == "random":
            ient = random.randint(0, nchoice-1)
            choice = ctl_list[ient]
            self.set_component_value(ctl_name, "current", choice)        
            return choice

        ctl_list_next = ctl_list_cur
        if prog == "ascend":
            ctl_list_next = ctl_list_cur + 1
            if ctl_list_next >= nchoice:
                ctl_list_next = 0
        elif prog == "descend":
            ctl_list_next = ctl_list_cur - 1
            if ctl_list_next < 0:
                ctl_list_next = nchoice-1       
        entry = [ctl_list_next, ctl_list]
        self.ctl_lists[ctl_name] = entry
        choice = ctl_list[ctl_list_next]
        self.set_component_value(ctl_name, "current", choice)        
        return choice
    
    
    def get_ctl_val(self, name, default):
        """ Get control value.  If none return default
        """
        ctl_entry = self.get_ctl_entry(name)
        if ctl_entry is None:
            self.update_control_entry(name, default_value=default)
            ctl_entry = self.get_ctl_entry(name)
        val = ctl_entry.value
        if val is None:
            val = ctl_entry.default_value
        if val is None:
            return default
        
        return val


    def get_prop_key(self, name):
        """ Translate full  control name into full Properties file key
        """
        
        key = self.CONTROL_NAME_PREFIX + "." + name
        return key
    

    def list_controls(self):
        """ List controls' settings
        """
        for name in self.get_ctl_names():
            self.list_control(name)


    def list_control(self, name):
        """ List control's settings
        """
        SlTrace.lg("control: %s" % name)
    
    
    def set(self):
        self.update_properties()
        if "set" in self.call_d:
            self.call_d["set"]()
    
    def run(self):
        self.update_properties()
        if "run" in self.call_d:
            self.call_d["run"]()
        
    def pause(self):
        if "pause" in self.call_d:
            self.call_d["pause"]()
        
    def step(self):
        self.update_properties()
        if "step" in self.call_d:
            self.call_d["step"]()
        
    def step_down(self):
        self.update_properties()
        if "step_down" in self.call_d:
            self.call_d["step_down"]()


    

    def update_form(self):
        """ Update any field changes
        """
        for name in self.ctl_name_d:
            ctn = self.ctl_name_d[name]
            if isinstance(ctn, ControlEntry):
                self.update_property(name)


    def update_properties(self):
        for name in self.get_ctl_names():
            self.update_property(name)


    def update_property(self, name):
        ctl_entry = self.get_ctl_entry(name)
        if ctl_entry is None:
            return                  # No entry
        
        if ctl_entry.ctl_widget is None:
            return                  # No widget
        
        ctl_value = ctl_entry.ctl_widget.get()
        prop_key = self.get_prop_key(name)
        SlTrace.setProperty(prop_key, ctl_value)
        
if __name__ == '__main__':
    def report_change(flag, val, cklist=None):
        SlTrace.lg("changed: %s = %d" % (flag, val))
        new_val = SlTrace.getLevel(flag)
        SlTrace.lg("New val: %s = %d" % (flag, new_val))
        if cklist is not None:
            cklist.list_ckbuttons()

    def run_button():
        SlTrace.lg("arrange_control Run Button")

    def set_button():
        SlTrace.lg("arrange_control Set Button")

    def pause_button():
        SlTrace.lg("arrange_control Pause Button")

    def step_button():
        SlTrace.lg("arrange_control Step Button")
        
    root = Tk()

    frame = Frame(root)
    frame.pack()
    SlTrace.setProps()
    SlTrace.setFlags("flag1=1,flag2=0,flag3=1,flag4=0, flag5=1, flag6=1")
    actl = ArrangeControl(frame, title="arrange_control", change_call=report_change)
    actl.set_call("run", run_button)
    actl.set_call("set", set_button)
    actl.set_call("pause", pause_button)
    actl.set_call("step", step_button)
        
    root.mainloop()