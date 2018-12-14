# select_command.py    12Nov2018
import copy

from select_trace import SlTrace
from select_error import SelectError
from openpyxl.utils.units import inch_to_dxa


"""
Command processing, especially undo/Redo
"""
    
"""
Command manager
"""
        
class SelectCommandManager:
    """ Manipulate command redo/undo
    """
    def __init__(self, user_module):
        """ Setup command processing (undo/redo
        :user_module: module which desires command undo/redo
        """
        self.no = 0
        self.move_no = 0

        self.user_module = user_module
        self.current_command = None
        self.command_stack = []         # Commands completed, which can be undone
        self.undo_stack = []            # Commands which have been undone, which can be redone
        

    def next_cmd_no(self):
        """ Provide next unique command number
        """
        self.no += 1
        return self.no
    
    def next_move_no(self, inc=None):
        """ Provide next move number
        :inc: Increment default: 1
        """
        if inc is None:
            inc = 1
        self.move_no += inc
        return self.move_no
    
    def get_prev_move_no(self):
        """ Return previous move number
        """
        if self.move_no > 1:
            return self.move_no-1
        
        return self.move_no
    
    

        
    def is_empty(self):
        return not self.command_stack
    
    
    def is_undo_empty(self):
        return not self.undo_stack
    
    
    
    def last_command(self):
        if self.command_stack:
            return self.command_stack[-1]
        
        return None
    
    
    def last_undo_command(self):
        if self.undo_stack:
            return self.undo_stack[-1]
        
        return None


    def clear_redo(self):
        """ Clear redo (i.e. undo_stack for possible redo)
        """
        self.undo_stack = []
    
    
    def can_redo(self):
        if self.undo_stack:
            return self.undo_stack[-1].can_redo()
        
        return False
    
    def can_undo(self):  
        if self.command_stack:
            return self.command_stack[-1].can_undo()
        
        return False

    
    def undo(self):
        """ Undo commands till
            1. One found that can't undo
            2. One fails undo
            3. A has_prompt completes
        """
        SlTrace.lg("undo", "execute")
        while True:
            if not self.can_undo():
                SlTrace.lg("Can't undo")
                return False
            
            cmd = self.command_stack.pop()
            res = cmd.undo()
            if not res:
                SlTrace.lg("Undo failed")
                return res
            
            lud = self.get_last_command()
            if lud is None:
                return res          # Stack empty
            
            if lud.has_prompt:
                if lud.new_messages:
                    for msg in lud.new_messages:
                        SlTrace.lg("Show pending latest message %s" % lud)
                        lud.user_module.do_message(msg)

                if SlTrace.trace("execute_undo_stack"):
                    self.cmd_undo_stack_print("undo stack AFTER undo")                        
                return res
                        
            SlTrace.lg("undo till has_prompt", "execute")

     
    def redo(self):
        """ Redo commands till
            1. One found that can't redo
            2. One fails redo
            3. A has_prompt completes
        """
        SlTrace.lg("redo", "execute")
        self.cmd_undo_stack_print("redo undo_stack:", "execute_stack")
        while True:
            if not self.can_redo():
                SlTrace.lg("Can't redo")
                return False
        
            cmd = self.undo_stack.pop()
            res = cmd.redo()
            if not res:
                SlTrace.lg("Redo failed")
                return res

            if not self.can_redo():
                SlTrace.lg("Can't redo")
                return res

            lud = self.undo_stack[-1]
            if lud.has_prompt:
                if lud.new_messages:
                    for msg in lud.new_messages:
                        SlTrace.lg("Show pending latest message %s" % lud)
                        lud.user_module.do_message(msg)
                if SlTrace.trace("execute_undo_stack"):
                    self.cmd_undo_stack_print("undo stack AFTER redo")                        
                return res
                        
            SlTrace.lg("redo till has_prompt", "execute")
    
    
    def repeat(self):
        SlTrace.lg("repeat", "execute")
        if not self.can_repeat():
            SlTrace.lg("Can't repeat")
            return False
        
        cmd = self.last_command()
        return cmd.do_cmd()
    
    
    def save_command(self, bcmd):
        self.command_stack.append(copy.copy(bcmd))
        self.cmd_stack_print("save_command", "execute_stack")


    def set_move_no(self, move_no=None):
        """ Set (comming)move number
        Provides the game specific move control
        """
        if move_no is None:
            move_no = 1
        self.move_no = move_no
    

    def get_move_no(self):
        """ Get current move number
        """
        return self.move_no
    
    
    def get_last_command(self):
        if self.is_empty():
            return None
        
        return self.command_stack[-1]
    
    
    def get_current_command(self):
        """ May not yet be on command stack
        """
        return self.current_command
    
    
    def get_prev_command(self):
        if self.is_empty():
            return None


    def get_undo_cmd(self):
        """ Get most recent cmd undone
        """
        if self.is_undo_empty():
            return None
        
        return self.undo_stack[-1]
    
    
        
        if len(self.command_stack) < 2:
            return self.command_stack[-1]
        
        return self.command_stack[-2]
    

    def cmd_stack_print(self, tag, trace):
        """ print current stack
        :tag: tag printed to identify printing
        :trace: string to determine printing via SlTrace
        """
        if not SlTrace.trace(trace):
            return          # No tracing
        max_print = 8
        if (SlTrace.trace("full_stack")):
            max_print = len(self.command_stack)
        max_print = min(max_print, len(self.command_stack))
        if not self.command_stack:
            SlTrace.lg("%s command_stack: Empty" % tag)
            return

        cs_str = ""
        for cmd in self.command_stack[-max_print:]:
            if cs_str != "":
                cs_str += "\n  "
            cs_str += str(cmd)
        st = ("\n%s command_stack: (n:%d) %s"
                    % (tag, len(self.command_stack), cs_str))
        indent = " " * 8
        st = st.replace("\n", "\n"+indent) 
        SlTrace.lg(st)
    

    def cmd_undo_stack_print(self, tag, trace=None):
        """ print current undo stack
        :tag: tag printed to identify printing
        :trace: string to determine printing via SlTrace
        """
        if not SlTrace.trace(trace):
            return          # No tracing
        max_print = 8
        if (SlTrace.trace("full_undo_stack")):
            max_print = len(self.command_stack)
        max_print = min(max_print, len(self.command_stack))
        if not self.command_stack:
            SlTrace.lg("%s undo_command_stack: Empty" % tag)
            return

        cs_str = ""
        for cmd in self.undo_stack[-max_print:]:
            if cs_str != "":
                cs_str += "\n  "
            cs_str += str(cmd)
        st = ("\n%s undo_stack: (n:%d) %s"
                    % (tag, len(self.undo_stack), cs_str))
        indent = " " * 8
        st = st.replace("\n", "\n"+indent) 
        SlTrace.lg(st)
        