import pytest
from datetime import datetime, timedelta
from src.models.lead import Lead, LeadStatus, LeadSource, CallAttempt
from src.models.product import Product, ProductCategory, ProductSpecification, PricingTier
from src.models.user import User, UserRole, UserStatus, PerformanceMetrics

class TestLead:
    def test_lead_creation(self):
        lead = Lead(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            source=LeadSource.WEBSITE
        )
        assert lead.status == LeadStatus.NEW
        assert len(lead.call_attempts) == 0

    def test_add_call_attempt(self):
        lead = Lead(
            first_name="John",
            last_name="Doe",
            source=LeadSource.WEBSITE
        )
        lead.add_call_attempt("Left voicemail", "Will try again tomorrow")
        assert len(lead.call_attempts) == 1
        assert lead.last_contact is not None

    def test_is_qualified(self):
        lead = Lead(
            first_name="John",
            last_name="Doe",
            source=LeadSource.WEBSITE
        )
        assert not lead.is_qualified()
        lead.budget_confirmed = True
        lead.authority_confirmed = True
        lead.need_confirmed = True
        lead.timeline_confirmed = True
        assert lead.is_qualified()

class TestProduct:
    def test_product_creation(self):
        product = Product(
            name="Solar Panel X1",
            category=ProductCategory.SOLAR,
            description="High-efficiency solar panel"
        )
        assert product.is_active
        assert len(product.specifications) == 0

    def test_pricing_calculation(self):
        product = Product(
            name="Solar Panel X1",
            category=ProductCategory.SOLAR,
            description="High-efficiency solar panel"
        )
        pricing = PricingTier(
            name="standard",
            base_price=1000.0,
            volume_discounts={10: 0.1, 20: 0.2}
        )
        product.pricing_tiers.append(pricing)
        
        assert product.calculate_price(1) == 1000.0
        assert product.calculate_price(10) == 9000.0
        assert product.calculate_price(20) == 16000.0

class TestUser:
    def test_user_creation(self):
        user = User(
            email="agent@example.com",
            first_name="Jane",
            last_name="Smith",
            role=UserRole.SALES_AGENT
        )
        assert user.status == UserStatus.ACTIVE
        assert len(user.assigned_leads) == 0

    def test_update_metrics(self):
        user = User(
            email="agent@example.com",
            first_name="Jane",
            last_name="Smith",
            role=UserRole.SALES_AGENT
        )
        metrics = {
            "calls_made": 10,
            "leads_converted": 3,
            "revenue_generated": 50000.0
        }
        user.update_metrics(metrics)
        assert user.performance_metrics.calls_made == 10
        assert user.performance_metrics.leads_converted == 3
        assert user.performance_metrics.revenue_generated == 50000.0