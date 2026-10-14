"""This holds the abstract base class for the repository and the concrete implementation for the product repository"""

from abc import ABC, abstractmethod
from models import Product, ProductCreate, ProductUpdate

class ProductRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Product]:
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Product | None:
        pass

    @abstractmethod
    def create(self, product: ProductCreate) -> Product:
        pass

    @abstractmethod
    def update(self, product_id: int, product: ProductUpdate) -> Product | None:
        pass

    @abstractmethod
    def delete(self, product_id: int) -> bool:
        pass

"""💡 What does this code do?

    InMemoryRepository inherits from ProductRepository and implements all five abstract methods. Because every method is implemented, Python allows this class to be instantiated.
    Two Pydantic v2 methods do the heavy lifting. model_dump() converts a Pydantic model into a plain dictionary. model_copy(update=...) creates a copy of an existing model with specific fields changed.
    The exclude_unset=True argument in the update method is critical. It ensures only fields the caller explicitly provided get changed. Without it, every field defaults to None and wipes out existing data."""


class InMemoryRepository(ProductRepository):
    def __init__(self):
        # Dictionary to store products in memory, using product ID as the key and Product object as the value.
        self._products: dict[int, Product] = {}
        # Auto-incrementing counter for new product IDs
        self._next_id: int = 1

    def get_all(self) -> list[Product]:
        return list(self._products.values())

    def get_by_id(self, product_id: int) -> Product | None:
        return self._products.get(product_id)

    def create(self, product: ProductCreate) -> Product:
        # Convert input model to a dict, then create a Product with an Id
        new_product = Product(id=self._next_id, **product.model_dump())
        self._products[self._next_id] = new_product
        self._next_id += 1
        return new_product

    def update(self, product_id: int, product: ProductUpdate) -> Product | None:
        existing = self._products.get(product_id) # Retrieve the existing product from the in-memory store using the provided product_id. If it doesn't exist, return None.
        if existing is None: # Check if the product exists. If it doesn't, return None to indicate that the update cannot be performed.
            return None
        # Update only the fields that are provided in the ProductUpdate model

        update_data = product.model_dump(exclude_unset=True) # Extract the fields from the ProductUpdate model that have been set (i.e., not None). This allows for partial updates without overwriting existing data with None values.
        # Create a new Product instance with the updated data, preserving the existing product's ID and any fields that were not updated.
        updated_product = existing.model_copy(update=update_data) # Create a new Product instance with the updated data.
        self._products[product_id] = updated_product # Store the updated product back in the in-memory store, replacing the old product.
        return updated_product # Return the updated product to the caller.

    def delete(self, product_id: int) -> bool:
        if product_id in self._products: # Check if the product exists in the in-memory store.
            del self._products[product_id] # If it exists, delete it from the store.
            return True # Return True to indicate that the deletion was successful.
        return False # If the product does not exist, return False to indicate that no deletion occurred.

    """OUTPUT
    from repository import InMemoryRepository, ProductRepository
    from models import ProductCreate, ProductUpdate, Category

    repo = InMemoryRepository()

    product = repo.create(ProductCreate(name="Laptop", description="Gaming laptop", price=999.99, category=Category.electronics, quantity=10))
    print(product)

    found = repo.get_by_id(1)
    print(found)

    updated = repo.update(1, ProductUpdate(price=899.99))
    print(updated)

    repo.delete(1)
    print(repo.get_all())
    
    name='Laptop' description='Gaming laptop' price=999.99 category=<Category.electronics: 'electronics'> quantity=10 id=1 discounted_prize=None
    name='Laptop' description='Gaming laptop' price=999.99 category=<Category.electronics: 'electronics'> quantity=10 id=1 discounted_prize=None
    name='Laptop' description='Gaming laptop' price=899.99 category=<Category.electronics: 'electronics'> quantity=10 id=1 discounted_prize=None
    []
    """