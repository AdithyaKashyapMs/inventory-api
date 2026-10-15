"""contains interchangeable discount calculation strategies."""

from abc import ABC, abstractmethod


"""💡 Why is this powerful?
You just swapped the entire discount algorithm by changing one query parameter. 
Your endpoint code did not change at all between the three requests. If you needed a fourth discount type 
(loyalty, employee, clearance), you would create a new class, add it to the dictionary, and update the Literal type. 
The endpoint functions stay untouched."""

class DiscountStrategy(ABC):
    # Every discount strategy must implement these two methods
    @abstractmethod
    def calculate_discount(self, price: float, quantity: int) -> float:
        pass

    @abstractmethod
    def strategy_name(self) -> str:
        pass

    """
    💡 What does this code do?
    DiscountStrategy inherits from ABC (Abstract Base Class), which means you cannot create an instance of it directly. It exists purely to define the contract.
    The two @abstractmethod decorators force any subclass to implement calculate_discount() and strategy_name(). If a subclass skips either one, Python raises a TypeError at instantiation.

    💡 Why the Strategy pattern instead of if/else?
    You could put all your discount logic in a single function with if/else branches. But every time you add a new discount type, you would have to modify that function. 
    The Strategy pattern lets you add new strategies by creating a new class. Zero changes to existing code.
    It is the most beginner-accessible advanced OOP pattern because you see immediate results: the same endpoint returns different prices just by changing a query parameter.
    """

class NoDiscount(DiscountStrategy):
    # Returns the price unchanged - the default behavior
    def calculate_discount(self, price: float, quantity: int) -> float:
        return price

    def strategy_name(self) -> str:
        return "no_discount"


class BulkDiscount(DiscountStrategy):
    # Applies tiered discounts based on quantity ordered
    def calculate_discount(self, price: float, quantity: int) -> float:
        if quantity >= 100:
            return round(price * 0.8, 2)
        elif quantity >= 50:
            return round(price * 0.9, 2)
        return price

    def strategy_name(self) -> str:
        return "bulk_discount"


class SeasonalDiscount(DiscountStrategy):
    # Accepts a configurable percentage (default 15%)
    def __init__(self, percentage: float = 15.0):
        self.percentage = percentage

    def calculate_discount(self, price: float, quantity: int) -> float:
        return round(price * (1 - self.percentage / 100), 2)

    def strategy_name(self) -> str:
        return f"seasonal_discount_{self.percentage}pct"

    """💡 What does this code do?

        NoDiscount returns the original price with no modification. This is the default strategy.
        BulkDiscount applies 20% off when quantity is 100 or more, 10% off when quantity is 50 or more, and no discount below 50.
        SeasonalDiscount takes a configurable percentage in its constructor (defaulting to 15%) and applies it to any product regardless of quantity.
        All three classes satisfy the DiscountStrategy contract. Your API can use any of them interchangeably."""