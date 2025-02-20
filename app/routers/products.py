from typing import List
from uuid import UUID
from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.product import Product, ProductCategory, Category
from app.schemas.product_schema import ProductCreate, ProductRead, ProductUpdate
from app.db import get_session

router = APIRouter()

@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED, summary="Create a new product")
async def create_product(product_in: ProductCreate, session: AsyncSession = Depends(get_session)):
    product = Product.model_validate(product_in)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    
    # Process category associations if provided
    if product_in.categories_ids:
        for category_id in product_in.categories_ids:
            # Optionally, check if the category exists before association
            category = await session.get(Category, category_id)
            if not category:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
            
            # Create the association
            session.add(ProductCategory(product_id=product.id, category_id=category_id))
            
        await session.commit()

    # Refresh the product to get the updated relationships
    await session.refresh(product)
    return product

@router.get("/products", response_model=List[ProductRead], summary="Get all products")
async def read_products(session: AsyncSession = Depends(get_session)):
    products = await session.exec(select(Product))
    return products.all()

@router.get("/products/{product_id}", response_model=ProductRead, summary="Get a product by ID")
async def read_product(product_id: UUID, session: AsyncSession = Depends(get_session)):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.patch("/products/{product_id}", response_model=ProductRead, summary="Update a product by ID")
async def update_product(product_id: UUID, product_in: ProductUpdate, session: AsyncSession = Depends(get_session)):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    update_data = product_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a product by ID")
async def delete_product(product_id: UUID, session: AsyncSession = Depends(get_session)):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    session.delete(product)
    await session.commit()
    return