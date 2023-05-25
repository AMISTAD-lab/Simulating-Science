class Cell():
    def __init__(self, payoff, hidden=True):
        self.payoff = payoff
    
    def __repr__(self):
        "string representation of Cell"
        return str(self.payoff)