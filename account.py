class InsufficientCash(Exception):
    pass


class InsufficientAsset(Exception):
    pass


class Account:
    def __init__(self, cash_balance, interest=None):
        self.cash_balance = cash_balance
        self.positions = dict()
        self.interest = interest # None -> no margin/borrowing; float -> borrowing allowed with interest
    
    @property
    def asset_balance(self):
        asset_balance = 0
        if len(self.positions.values()) != 0:
            for n, p in self.positions.values():
                asset_balance += n*p
        return asset_balance
    
    @property
    def total_balance(self):
        return self.cash_balance + self.asset_balance
    
    def _remove_empty_positions(self):
        for k in list(self.positions.keys()):
            if self.positions[k][0] == 0: 
                self.positions.pop(k)
    
    def update_position(self, id, n, p):
        if id not in self.positions:
            self.positions[id] = [0, p]
            
        if n == 'close':
            n = -self.positions[id][0]
        
        n0, p0 = self.positions[id]
        
        try:
            if self.interest is None:
                if self.cash_balance - n*p < 0:
                    raise InsufficientCash('Insufficient Cash')
                
                if n0 + n < 0:
                    raise InsufficientAsset('Insufficient Asset')
            
            else:
                interest = 0.
                if n*p > 0 and self.cash_balance - n*p < 0:
                    interest = min(n*p, n*p - self.cash_balance)*self.interest
                
                if n < 0 and n0 + n < 0:
                    interest = min(-n*p, -(n0 + n)*p)*self.interest
                
                self.cash_balance -= interest
            
            self.cash_balance -= n*p
            self.positions[id][0] += n
            self.positions[id][1] = p

        except Exception as e:
            print(e)
        
        self._remove_empty_positions()