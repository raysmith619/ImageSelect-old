# player_control.py 05Nov2018
"""
Player control window layout

players
Name      Label    Playing  Color    col bg  Voice Help  Pause    
--------- ------   -        -------  ------  ----  -----  -----
computer  co       ()       gray     white   ( )   ( )    1.0
Alex      Ax       (.)      pink     white   (.)   ( )
Decklan   D        ()       blue     white   (.)   ( )
Avery     Av       ()       pink     white   (.)   ( )
Grampy    Gp       (.)      blue     white   (.)   ( )
Grammy    Gm       (.)      pink     white   (.)   ( )

[Add] [Change] [Remove]
"""


from tkinter import *
import random
from select_error import SelectError
from select_trace import SlTrace
from select_player import SelectPlayer

    
class PlayerControl(Toplevel):
    
    def __init__(self, ctlbase=None, title=None, display=True):
        """ Display / Control of players
        :ctlbase: base control object
        
        values stored in properties file
        All values stored under "player_control.".<player_id>
        The player_id is constructed by replacing all
        sequences of [^a-zA-Z_0-9]+ by "_" in the player name
        to produce a legal properties file id string
        Value strings:
            id                  value type
            ------------        -------------
            name                string
            label               string
            playing             bool
            position            int
            mV                  int
            color               string (fill)
            voice               bool
            help_play           bool
            pause               float
        
        
        """
        ###Toplevel.__init__(self, parent)
        self.ctlbase = ctlbase
        """ Setup control names found in properties file
        Updated as new control entries are added
        """
        prop_keys = SlTrace.getPropKeys()
        player_pattern = r'(?:\.(\w+))'
        pattern = (SelectPlayer.CONTROL_NAME_PREFIX
                    + player_pattern + player_pattern)
        rpat = re.compile(pattern)
        self.players = {}   # Dictionary of SelectPlayer
        self.cur_player = None   # Current player
        
                            # by name
        self.call_d = []    # Call back routines, if any
        for prop_key in prop_keys:
            rmatch = re.match(rpat, prop_key)
            if rmatch:
                player_match = rmatch[0]
                player_match_1 = rmatch[1]
                player_id = int(rmatch[1])
                player_field = rmatch[2]
                prop_val = SlTrace.getProperty(prop_key)
                
                if player_id not in self.players:
                    player = SelectPlayer(player_id)
                    self.players[player_id] = player # New entry
                else:
                    player = self.players[player_id]
                player_attr = rmatch[2]
                if player_attr == "move":
                    player_attr = "position"
                if not hasattr(player, player_attr):
                    raise SelectError("Unrecognized player attribute %s in %s"
                                      % (player_attr, prop_key))
                else:
                    pat = getattr(player, player_attr)
                    if isinstance(pat, float):
                        player_val = float(prop_val)
                    elif isinstance(pat, bool):
                        pvl = prop_val.lower()
                        if (pvl == "yes"
                                or pvl == "y"
                                or pvl == "1"
                                or pvl == "true"):
                            player_val = True
                        elif (pvl == "no"
                                or pvl == "n"
                                or pvl == "0"
                                or pvl == "false"):
                            player_val = False
                        else:
                            raise SelectError("Unrecognized boolean value (%s =)  %s"
                                              % (player_attr, prop_val))
                    elif isinstance(pat, int):
                        player_val = int(prop_val)
                    else:
                        player_val = prop_val
                    setattr(player, player_attr, player_val)
                    self.players[player_id] = player
        
        if title is None:
            title = "Player Control"
        self.title = title
        
        if display:
            self.control_display()
            
    def control_display(self):
        """ display /redisplay controls to enable
        entry / modification
        """
        win_width =  500
        win_height = 200
        win_x0 = 100
        win_y0 = 100
                    
        self.mw = Toplevel()
        win_setting = "%dx%d+%d+%d" % (win_width, win_height, win_x0, win_y0)

        
        self.mw.geometry(win_setting)
        self.mw.title(self.title)
        top_frame = Frame(self.mw)
        self.mw.protocol("WM_DELETE_WINDOW", self.delete_window)
        top_frame.pack(side="top", fill="x", expand=True)
        self.top_frame = top_frame
        
        controls_frame = Frame(top_frame)
        controls_frame.pack(side="top", fill="x", expand=True)
        self.controls_frame = controls_frame
        players_frame = Frame(controls_frame)
        players_frame.pack(side="top", fill="x", expand=True)
        class ColumnInfo:
            def __init__(self, field_name,
                         hd=None, width=None):
                """ column info
                :field_name: - SelectPlayer field name
                :hd: heading default: field_name.capitalized()
                :width: width in characters
                        default: length of heading + 1
                """
                self.field_name = field_name
                if hd is None:
                    hd = field_name.capitalize()
                self.heading = hd
                if width is None:
                    width = len(self.heading) + 1
                self.width = width
                
                
        """ fields in the order to present """        
        player_fields = ["name", "label",
                         "playing",
                         "position",
                         "color", "color_bg",
                         "voice", "help_play", "pause"]
        col_infos = []
        for field in player_fields:
            heading = self.get_heading(field)
            width = self.get_col_width(field)
            col_info = ColumnInfo(field, hd=heading, width=width)
            col_infos.append(col_info)
            
            
        self.set_field_headings(players_frame, col_infos)
        for pid, player in self.players.items():
            for idx, field in enumerate(player_fields):
                self.set_player_frame(players_frame, player, col_infos, idx)
            players_frame.rowconfigure(pid, weight=1)


        """ Contol buttons """
        control_button_frame = Frame(controls_frame)
        control_button_frame.pack(side="top", fill="x", expand=True)
        set_button = Button(master=control_button_frame, text="Set", command=self.set)
        set_button.pack(side="left", expand=True)
        add_button = Button(master=control_button_frame, text="Add",
                            command=self.add_player)
        add_button.pack(side="left", expand=True)
        delete_button = Button(master=control_button_frame, text="Delete",
                            command=self.delete_player)
        delete_button.pack(side="left", expand=True)


    def get_next_player(self, set_player=True):
        """ get next candidate player
        :set: True set as true default set as current player
        """
        SlTrace.lg("get_next_player, set_player=%s"
                   % set_player, "execute")
        if self.cur_player is None:
            next_position = self.get_first_position()
        else:
            next_position = self.get_next_position(self.cur_player.position)
        player = self.get_player(next_position)
        
        
        if player is None:
            raise SelectError("No player playing with next position: %d"
                          % next_position)
        if set_player:    
            self.set_player(player)
        return player
    
    
    def get_first_position(self):
        position = None
        for player in self.players.values():
            if player.playing:
                if (player.position is not None
                        and (position is None or position > player.position)):
                    position = player.position
         
        if position is None:
            raise SelectError("No players")
        
        return position
    
    
    def get_next_position(self, position):
        """ Get next position after given,
        among playing players, wrapping if necessary
        """
        next_position = None
        for player in self.players.values():
            if player.playing and player.position is not None:
                if next_position is None:
                    if player.position > position:
                        next_position = player.position
                else:
                    if player.position > position:
                        if  player.position < next_position:
                            next_position = player.position
        if next_position is None:
            next_position = self.get_first_position()

        if next_position is None:
            raise SelectError("No players")
        
        return next_position


    def set_player(self, player):
        """ Record player  as next player
        """
        self.cur_player = player

        
    
    def get_player(self, position=None):
        """ Get player / current player
        :position: position number
            default: current player
        """
        if position is not None:
            for player in self.players.values():
                if player.playing and player.position is not None:
                    if position == player.position:
                        return player
            raise SelectError("No player for position %s" % position)
        
        if self.cur_player is None:
            return self.get_next_player()
        return self.cur_player
    

    def set(self):
        """ Set info from form
        """
        self.set_vals()
        
        
    def add_player(self):
        """ Add new player
        """
        SlTrace.lg("add_player not yet implemented")
    
    def delete_player(self):
        """ Delete player
        """
        SlTrace.lg("delete_player not yet implemented")
        
        
        
    def set_field_headings(self, field_headings_frame, col_infos):
        """ Setup player headings, possibly recording widths
        """
        for info_idx, col_info in enumerate(col_infos):
            field_name = col_info.field_name
            heading = col_info.heading
            heading_label = Label(master=field_headings_frame,
                                  text=heading, anchor=CENTER,
                                  justify=CENTER,
                                  width=col_info.width)
            heading_label.grid(row=0, column=info_idx, sticky=NSEW)
            field_headings_frame.columnconfigure(info_idx, weight=1)


    def get_col_width(self, field_name):
        """ Calculate widget text width
        :field_name: field name SelectPlayer attribute
        :returns:  proper column width, given heading and all values for this field
        """
        heading = self.get_heading(field_name)
        width = len(heading)        # Start with heading as width
        for player in self.players.values():
            val = getattr(player, field_name)
            val_len = len(str(val)) + 1
            if val_len > width:
                width = val_len
        return int(width*1.25)

    
    def get_field_name(self, heading):
        """ Convert heading into field name
        :heading:  Heading text
        """
        field = heading.lower()
        if field == "help":
            field = "help_play"
        return field

    
    def get_heading(self, field_name):
        """ Convert heading into field name
        :field_name:  field attribute
        """
        heading = field_name
        if heading == "help_play":
            heading = "help"
        heading = heading.capitalize()
        return heading
    

    def set_player_frame(self, frame, player, col_infos, idx):
        """ Create player info line
        :frame: players frame
        :player: player info
        :col_infos: list of information for each column
        :idx: index into col_infos
        """
        col_info = col_infos[idx]
        field_name = col_info.field_name
        value = player.get_val(field_name)
        width = self.get_col_width(field_name)
        frame = Frame(frame, height=1, width=width)
        frame.grid(row=player.id, column=idx, sticky=NSEW)

        if field_name == "name":
            self.set_player_frame_name(frame, player, value, width=width)
        elif field_name == "label":
            self.set_player_frame_label(frame, player, value, width=width)
        elif field_name == "playing":
            self.set_player_frame_playing(frame, player, value, width=width)
        elif field_name == "position":
            self.set_player_frame_position(frame, player, value, width=width)
        elif field_name == "color":
            self.set_player_frame_color(frame, player, value, width=width)
        elif field_name == "color_bg":
            self.set_player_frame_color_bg(frame, player, value, width=width)
        elif field_name == "voice":
            self.set_player_frame_voice(frame, player, value, width=width)
        elif field_name == "help_play":
            self.set_player_frame_help(frame, player, value, width=width)
        elif field_name == "pause":
            self.set_player_frame_pause(frame, player, value, width=width)
        else:
            raise("Unrecognized player field_name: %s" % field_name)    

    def get_num_playing(self):
        """ Calculate number playing
        """
        nplaying = 0
        for player in self.players.values():
            if player.playing:
                nplaying += 1
        return nplaying
    
    
            

    def set_player_frame_name(self, frame, player, value, width=None):
        content = StringVar()
        content.set(value)
        val_entry = Entry(frame, textvariable=content, width=width)
        val_entry.pack(side="left", fill="none", expand=True)
        player.ctls["name"] = val_entry
        player.ctls_vars["name"] = content

    def set_player_frame_label(self, frame, player, value, width=None):
        content = StringVar()
        content.set(value)
        val_entry = Entry(frame, textvariable=content, width=width)
        val_entry.pack(side="left", fill="none", expand=True)
        player.ctls["label"] = val_entry
        player.ctls_vars["label"] = content

    def set_player_frame_playing(self, frame, player, value, width=None):
        content = BooleanVar()
        content.set(value)
        yes_button = Checkbutton(frame, variable=content, width=None)
        yes_button.pack(side="left", fill="none", expand=True)
        player.ctls["playing"] = yes_button
        player.ctls_vars["playing"] = content

    def set_player_frame_position(self, frame, player, value, width=None):
        content = IntVar()
        content.set(value)
        yes_button = Entry(frame, textvariable=content, width=width)
        yes_button.pack(side="left", expand=True)
        player.ctls["position"] = yes_button
        player.ctls_vars["position"] = content

    def set_player_frame_color(self, frame, player, value, width=None):
        content = StringVar()
        content.set(value)
        val_entry = Entry(frame, textvariable=content, width=width)
        val_entry.pack(side="left", fill="none", expand=True)
        player.ctls["color"] = val_entry
        player.ctls_vars["color"] = content

    def set_player_frame_color_bg(self, frame, player, value, width=None):
        content = StringVar()
        content.set(value)
        val_entry = Entry(frame, textvariable=content, width=width)
        val_entry.pack(side="left", fill="none", expand=True)
        player.ctls["color_bg"] = val_entry
        player.ctls_vars["color_bg"] = content

    def set_player_frame_voice(self, frame, player, value, width=None):
        content = BooleanVar()
        content.set(value)
        yes_button =  Checkbutton(frame, variable=content, width=width)
        yes_button.pack(side="left", fill="none", expand=True)
        player.ctls["voice"] = yes_button
        player.ctls_vars["voice"] = content

    def set_player_frame_help(self, frame, player, value, width=None):
        content = BooleanVar()
        content.set(value)
        yes_button = Checkbutton(frame, variable=content, width=width)
        yes_button.pack(side="left", fill="none", expand=True)
        player.ctls["help_play"] = yes_button
        player.ctls_vars["help_play"] = content

    def set_player_frame_pause(self, frame, player, value, width=None):
        content = DoubleVar()
        content.set(value)
        yes_button = Entry(frame, textvariable=content, width=width)
        yes_button.pack(side="left", expand=True)
        player.ctls["pause"] = yes_button
        player.ctls_vars["pause"] = content


    def set_vals(self):
        """ Read form, if displayed, and update internal values
        """
        for player in self.players.values():
            for field in player.ctls_vars:
                player.set_val_from_ctl(field)
                
       
    def delete_window(self):
        """ Process Trace Control window close
        """
        if self.mw is not None:
            self.mw.destroy()
            self.mw = None
    
    
    def add(self):
        if "set" in self.call_d:
            self.call_d["set"]()
    
    def edit(self):
        if "edit" in self.call_d:
            self.call_d["edit"]()
        
    def delete(self):
        if "delete" in self.call_d:
            self.call_d["delete"]()
    

        
if __name__ == '__main__':
        
    root = Tk()

    frame = Frame(root)
    frame.pack()
    SlTrace.setProps()
    SlTrace.setFlags("")
    plc = PlayerControl(frame, title="player_control", display=True)
        
    root.mainloop()