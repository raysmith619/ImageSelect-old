# select_player.py
from select_error import SelectError
from select_trace import SlTrace
    
class SelectPlayer:
    CONTROL_NAME_PREFIX = "player_control"
    id = 0          # Unique id
    
    def __init__(self,
                 id = None,
                 name = None,
                 label = None,
                 position = None,
                 playing = False,
                 color = "gray",
                 color_bg = "white",
                 voice = False,
                 help_play = False,
                 pause = 0.,
                 score = 0
                 ):
        """ Player attributes
        :id:   Unique id (count)
            default: generate new id
        :name: playter's name
        :label: square labeling letter/string
                default: Upercase first character of name
        :playing: True - player is playing game
                default: not playing
        :position: move number 1 - first to play
        :color:  color for name, label, message
        :color_bg: background color
                default: white
        :voice:  True - add voice to player responses
        :help_play: Help player
                default: no help
        :pause: Pause number of seconds before player play
                Provides some delay before computer response
        :score: Number of points in game
                default: 0
        """
        if id is None:
            SelectPlayer.id += 1
            id = SelectPlayer.id
        self.id = id
        self.name = name
        if label is None:
            if self.name is not None:
                label = self.name[0]
        self.label = label
        self.playing = playing
        if position is None:
            position = self.id
        self.position = position
        self.color = color
        self.color_bg = color_bg
        self.voice = voice
        self.help_play = help_play
        self.pause = pause
        self.score = score
        self.ctls = {}          # Dictionary of field control widgets
        self.ctls_vars = {}     # Dictionary of field control widget variables

    def get_prop_key(self, name):
        """ Translate full  control name into full Properties file key
        """
        
        key = (SelectPlayer.CONTROL_NAME_PREFIX
                + "." + str(self.id) + "." + name)
        return key


    def get_val(self, field_name):
        """ get value in data field, returning value
        :field_name: - field name = use lower case
        """
        field = field_name.lower()
        if hasattr(self, field):
            return getattr(self, field)
        
        raise SelectError("SelectPlayerControlEntry.get_val(%s) - no entry: %s"
                           % (field_name, field))

    def set_val_from_ctl(self, field_name):
        """ Set player value from field
        Also updates player value properties
        :field_name: field name
        """
        if not hasattr(self, field_name):
            raise SelectError("Player has no attribute %s" % field_name)
        value = self.ctls_vars[field_name].get()
        setattr(self, field_name, value)
        self.set_prop_val(field_name)


    def set_prop_val(self, field_name):
        """ Update properties value for field, so that properties file
        will contain the updated value
        :field_name: field attribute name
        """
        prop_key = self.get_prop_key(field_name)
        field_value = self.get_val(field_name)
        prop_value = str(field_value)
        SlTrace.setProperty(prop_key, prop_value)


    def __str__(self):
        """ Provide reasonable view of player
        """
        return (self.name
                 + " %s" % self.label
                 + " %s" % self.color)
