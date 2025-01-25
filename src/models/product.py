from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from uuid import uuid4

class ProductCategory(str, Enum):
    SOLAR = "solar"
    HVAC = "hvac"
    ROOFING = "roofing"
    OTHER = "other"

class ProductSpecification(BaseModel):
    key: str
    value: str
    unit: Optional[str] = None

class PricingTier(BaseModel):
    name: str
    base_price: float
    volume_discounts: Dict[int, float] = Field(default_factory=dict)
    installation_cost: Optional[float] = None

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Basic Information
    name: str
    category: ProductCategory
    description: str
    sku: Optional[str] = None
    
    # Technical Details
    specifications: List[ProductSpecification] = Field(default_factory=list)
    warranty_terms: Optional[str] = None
    installation_requirements: List[str] = Field(default_factory=list)
    
    # Pricing
    pricing_tiers: List[PricingTier] = Field(default_factory=list)
    
    # Availability
    is_active: bool = True
    stock_level: Optional[int] = None
    lead_time_days: Optional[int] = None
    
    # Relationships
    compatible_products: List[str] = Field(default_factory=list)
    required_accessories: List[str] = Field(default_factory=list)
    
    # Search Optimization
    keywords: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    def get_base_price(self, tier_name: str = "standard") -> Optional[float]:
        tier = next((t for t in self.pricing_tiers if t.name.lower() == tier_name.lower()), None)
        return tier.base_price if tier else None
        
    def calculate_price(self, quantity: int, tier_name: str = "standard") -> Optional[float]:
        tier = next((t for t in self.pricing_tiers if t.name.lower() == tier_name.lower()), None)
        if not tier:
            return None
            
        base_price = tier.base_price * quantity
        
        # Apply volume discount if applicable
        for vol, discount in sorted(tier.volume_discounts.items(), reverse=True):
            if quantity >= vol:
                return base_price * (1 - discount)
                
        return base_price
        
    def update_specification(self, key: str, value: str, unit: Optional[str] = None):
        spec = next((s for s in self.specifications if s.key == key), None)
        if spec:
            spec.value = value
            spec.unit = unit
        else:
            self.specifications.append(ProductSpecification(key=key, value=value, unit=unit))
        self.updated_at = datetime.utcnow()