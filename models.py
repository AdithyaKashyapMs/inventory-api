"""This file defines the data shapes for your products using Pydantic models and inheritance

Every API needs a clear contract for what data looks like coming in and going out. 
Pydantic models give you that contract with built-in validation, and class inheritance 
lets you share fields across related models without repeating yourself.

"""

from pydantic import BaseModel, Field # Field is used to add metadata and validation rules to model fields, such as descriptions, default values, and constraints.
from enum import Enum # ENUM is used to define a set of named values for the product category field, ensuring that only valid categories are accepted.

"""
    Category inherits from both str and Enum. This means each category value 
    is both a string (so it serializes cleanly to JSON) and a restricted enum 
    (so only valid categories are accepted)."""
class Category(str, Enum):
    electronics = "electronics"
    clothing = "clothing"
    food = "food"
    books = "books"


"""ProductBase uses Pydantic's Field to add validation constraints. Field(gt=0) 
    means "greater than 0" so negative prices are rejected automatically. 
    Field(ge=0) means "greater than or equal to 0" so quantity can be zero but never negative."""
class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=100) # min_length and max_length ensure that the name is not empty and does not exceed 100 characters.
    description: str | None = None
    price: float = Field(gt=0) # gt=0 ensures that the price must be greater than zero, preventing free or negative-priced products.
    category: Category
    quantity: int = Field(ge=0) # ge=0 ensures that the quantity cannot be negative.


class ProductCreate(ProductBase):
    pass  # Inherits all fields from ProductBase, used for creating new products.

class Product(ProductBase):
    id: int # id is added to the base model for products that are retrieved from the database, ensuring each product has a unique identifier.
    discounted_prize: float | None = None # discounted_prize is optional, allowing for products that may not have a discount applied.

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0) # gt=0 ensures that if a price is provided, it must be greater than zero.
    category: Category | None = None
    quantity: int | None = Field(default=None, ge=0) # ge=0 ensures that if a quantity is provided, it cannot be negative.
