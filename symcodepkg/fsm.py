
class fsm:
    
    def __init__(self):
        self.states = {}
        
    def add_state(self,state):
        self.states[state] = {}
        
    def add_action(self,triple):
        pass