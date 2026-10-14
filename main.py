"""this files contains the main entry point for the application and the FastAPI app instance
    wires everything together and runs the application when executed directly.
"""

from fastapi import FastAPI, HTTPException, Depends
from models import Product, ProductCreate, ProductUpdate
from repository import ProductRepository, InMemoryRepository

# Create the FastAPI application instance. This is the main entry point for the API, where routes and middleware will be registered.
app = FastAPI(title="Smart Inventory API")

# create a single shared repository instance
repository = InMemoryRepository()

# Dependency injection function - provides the repository to endpoints
def get_repository() -> ProductRepository:
    return repository



@app.get("/products", response_model=list[Product])
def list_products(
    repo: ProductRepository = Depends(get_repository)  # Use dependency injection to get the repository instance
):
    """Endpoint to list all products in the inventory."""
    return repo.get_all()  # Return all products from the repository

@app.get("/products/{product_id}", response_model=Product)
def get_product(
    product_id: int,  # Path parameter for the product ID
    repo: ProductRepository = Depends(get_repository)  # Use dependency injection to get the repository instance
):
    """Endpoint to retrieve a single product by its ID."""
    # Look up a single product by its Id
    product = repo.get_by_id(product_id)  # Retrieve the product from the repository
    if product is None:  # If the product does not exist, raise a 404
        raise HTTPException(status_code=404, detail="Product not found")
    return product  # Return the found product


@app.post("/products", response_model=Product, status_code=201)
def create_product(
    product: ProductCreate,  # Request body containing the product data to create
    repo: ProductRepository = Depends(get_repository)  # Use dependency injection to get the repository instance
):
    """Endpoint to create a new product in the inventory."""
    return repo.create(product)  # Create the product in the repository and return it

@app.put("/products/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product: ProductUpdate,
    repo: ProductRepository = Depends(get_repository),
):
    # Update an existing product with new data
    updated = repo.update(product_id, product)
    if updated is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@app.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    repo: ProductRepository = Depends(get_repository),
):
    # Remove a product from the repository
    deleted = repo.delete(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")