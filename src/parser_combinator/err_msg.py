from os import linesep
from copy import deepcopy



class ErrMsg(object):
    def __init__(self,child=None,msgs=[]):
        self.child = child
        self.msgs = msgs
    
    def append(self,msg):
        newmsg = deepcopy(self.msgs)
        newmsg.append(msg)
        return ErrMsg(self.child,newmsg)
    
    def caused_by_me(self):
        return ErrMsg(self)

    def __add__(self,other:str):
        return self.append(other)

    def __str__(self):
        return self.to_string_internal("")
    
    def to_string_internal(self,indent_text):
        joined_msg = linesep.join([ indent_text + m for m in [ "", *self.msgs ] ])
        if self.child is None: 
            return joined_msg
        else:
            return joined_msg + linesep + "caused by" + linesep + self.child.to_string_internal("\t")
    
    @staticmethod
    def Empty():
        return EMPTY_MSG

    @staticmethod
    def isEmptyMsg(msg):
        return msg is EMPTY_MSG


EMPTY_MSG = ErrMsg()
