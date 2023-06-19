

class HistoricalVaR:
    def pnl(self):
        """
        Take the alpha percentile of pnl data
        """
        pass
    
    def x_weighted(self):
        pass

    def age_weighted(self):
        pass

    def volatility_weighted(self):
        pass

class NormalLinearVaR:

    def pnl(self):
        """
        Assumptions:
            (1) P&L is the only risk factor
            (2) P&L is iid normally distributed
        """
        pass

    def ret(self):
        """
        Assumptions:
            (1) Return is the only risk factor
            (2) Return is iid normally distributed
        """

class MonteCarloVaR:
    def monte_carlo(self):
        pass

class HistoricalES:
    def pnl(self):
        pass

    def age_weighted(self):
        pass

    def volatility_weighted(self):
        pass

class NormalLinearES:
    def pnl(self):
        pass

    def ret(self):
        pass
