"""this files contains the main entry point for the application and the FastAPI app instance
    wires everything together and runs the application when executed directly.
"""

from typing_extensions import Literal

from fastapi import FastAPI, HTTPException, Depends
from models import Product, ProductCreate, ProductUpdate, Category
from repository import ProductRepository, InMemoryRepository
from strategies import DiscountStrategy, NoDiscount, BulkDiscount, SeasonalDiscount

# Create the FastAPI application instance. This is the main entry point for the API, where routes and middleware will be registered.
app = FastAPI(title="Smart Inventory API")

# create a single shared repository instance
repository = InMemoryRepository()
discount_strategy: dict[str, DiscountStrategy] = {
    "none": NoDiscount(),
    "bulk": BulkDiscount(),
    "seasonal": SeasonalDiscount(percentage=15.0),
}

# Dependency injection function - provides the repository to endpoints
def get_repository() -> ProductRepository:
    return repository

def get_discount_strategy(
    discount: Literal["none", "bulk", "seasonal"] = "none",
) -> DiscountStrategy:
    return discount_strategy[discount]

    """💡 What does this code do?   

    This function is a FastAPI dependency. It reads the discount query parameter from the URL and returns the matching strategy. 
    The Literal["none", "bulk", "seasonal"] type annotation tells FastAPI to only accept those three values.
    If someone sends ?discount=invalid, FastAPI automatically returns a 422 validation error. It also renders a dropdown in the /docs UI showing the valid options."""



"""💡 What does this code do?

strategy: DiscountStrategy = Depends(get_discount_strategy) injects whichever strategy the query parameter selected.
The loop applies calculate_discount() to each product's price and quantity.
model_copy(update=...) creates a copy of the product with discounted_price set. If the discounted price equals the original, it stays None (no discount applied)."""
@app.get("/products", response_model=list[Product])
def list_products(
    repo: ProductRepository = Depends(get_repository),
    strategy: DiscountStrategy = Depends(get_discount_strategy),
    category: Category | None = None,
):
    # Retrieve all products and apply the chosen discount strategy
    products = repo.get_all()
    if category is not None:
        products = [product for product in products if product.category == category]

    result = []
    for product in products:
        discounted = strategy.calculate_discount(product.price, product.quantity)
        updated = product.model_copy(
            update={"discounted_price": discounted if discounted != product.price else None}
        )
        result.append(updated)
    return result


@app.get("/products/stats")
def get_inventory_stats(
    repo: ProductRepository = Depends(get_repository),
):
    products = repo.get_all()
    if not products:
        return {"total_products": 0, "total_value": 0.0, "categories": {}}

    total_value = sum(product.price * product.quantity for product in products)
    categories: dict[str, dict[str, int | float]] = {}
    for product in products:
        category = product.category.value
        if category not in categories:
            categories[category] = {"count": 0, "value": 0.0}
        categories[category]["count"] += 1
        categories[category]["value"] += product.price * product.quantity

    for category in categories:
        categories[category]["value"] = round(categories[category]["value"], 2)

    return {
        "total_products": len(products),
        "total_value": round(total_value, 2),
        "categories": categories,
    }


@app.get("/products/{product_id}", response_model=Product)
def get_product(
    product_id: int,
    repo: ProductRepository = Depends(get_repository),
    strategy: DiscountStrategy = Depends(get_discount_strategy),
):
    product = repo.get_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    # Apply the selected discount strategy to this single product
    discounted = strategy.calculate_discount(product.price, product.quantity)
    return product.model_copy(
        update={"discounted_price": discounted if discounted != product.price else None}
    )


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