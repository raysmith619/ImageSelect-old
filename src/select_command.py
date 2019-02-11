# select_command.py    12Nov2018

import copy

from select_trace import SlTrace
from select_error import SelectError
from select_command_manager import SelectCommandManager
from select_fun import *

"""
Command processing, especially undo/Redo
"""
import player_control

"""
Command Definition
"""
class SelectCommand:
    no = 0
    move_no = 0         # Game move number
    command_manager = None      # Must already be setup
    
    """ Command object, sufficient to contain do/undo
    """
    def __init__(self, action_or_cmd, has_prompt=False, undo_unit=False):
        """ Initialize do/undo Structure
        :action_or_cmd:
            str - type of command:
                "move" - player move
        :cmd: command
        :has_prompt: True - has move prompt  Default: False
        :undo_unit:  True - completes an undoable sequence
                    default: False
        """
        if self.command_manager is None:
            raise SelectError("No SelectCommandManager")
        self.no = self.command_manager.next_cmd_no()
        self.prev_move_no = self.command_manager.get_prev_move_no()
        self.move_no = self.prev_move_no
        self.has_prompt = has_prompt
        self.undo_unit = undo_unit
        self.move_no = self.command_manager.get_move_no()

        
        if isinstance(action_or_cmd, str):
            self.action = action_or_cmd
            self.can_undo_ = True
            self.can_redo_ = True
            self.can_repeate_ = False
        else:
            self = select_copy(action_or_cmd)

            
            
    def set_action_cmd(self, action):
        self.action = action


    def add_message(self, message):
        self.message = message
        

    def set_can_undo(self, can=True):
        self.can_undo_ = can 



    def do_cmd(self):
        """
        Do command, storing, if command can be undone or repeated, for redo,repeat
        """
        self.command_manager.displayPrint(
                "do_cmd[" + self.no +  "](%s)"
                        % (self.action), "execute")
        self.command_manager.selectPrint("do_cmd(%s)"
                                         % (self.action), "execute")
        self.command_manager.cmdStackPrint("do_cmd(%s)"
                                        % (self.action), "execute")
        res = self.execute()
        if res:
            if self.can_undo() or self.can_repeat():
                SlTrace.lg("add to commandStack", "execute")
                self.command_manager.add(self)
            else:
                SlTrace.lg("do_cmd(%s) can't undo/repeat"
                           % (self.action), "execute")
                return False
        return res
        
            
    def execute(self):
        """
        Execute constructed command
        Overridden in user_module
        """ 
        raise SelectError("Overridden in user_module")   
        return True
    
  
    def undo(self):
        """
        Remove the effects of the most recently done command
          1. remove command from commandStack
          2. add command to undoStack
          3. reverse changes caused by the command
          4. return true iff could undo
        Non destructive execution of command
        """
        cmd = None
        try:
            cmd = SelectCommand(self)
        except:
            SlTrace.lg("SelectCmdAdd failure")
            return False
        
        temp = cmd.new_parts
        cmd.new_parts = cmd.prev_parts
        cmd.new_prev = temp
        
        temp_sel = cmd.new_selects
        cmd.new_selects = cmd.prev_selects
        cmd.prev_selects = temp_sel
        
        res = cmd.execute()
        if res:
            self.command_manager.undo_stack.append(self)
        return res


    def can_redo(self):
        return self.can_redo_

    def redo(self):
        """ redo cmd
        """
        raise SelectError("redo must be overridden")
    

    def can_undo(self):
        return self.can_undo_
        