"""
Week 4 - Software Testing and Quality Assurance
Sample automated tests for a hypothetical e-commerce application.

Run:
    python ecommerce_qa_tests.py

The example is intentionally self-contained and uses only Python's standard
library. It demonstrates unit-level checks for product, cart, checkout and
basic input validation. It is a teaching example, not a production payment
integration or a complete security test suite.
"""

from dataclasses import dataclass, field
import unittest


@dataclass
class Product:
    product_id: str
    name: str
    price: float
    stock: int

    def __post_init__(self):
        if not self.product_id.strip():
            raise ValueError("Product ID is required.")
        if not self.name.strip():
            raise ValueError("Product name is required.")
        if self.price < 0:
            raise ValueError("Price cannot be negative.")
        if self.stock < 0:
            raise ValueError("Stock cannot be negative.")


@dataclass
class Cart:
    # Maps product ID to (Product, quantity)
    items: dict = field(default_factory=dict)

    def add(self, product: Product, quantity: int = 1):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        current = self.items.get(product.product_id, (product, 0))[1]
        if current + quantity > product.stock:
            raise ValueError("Requested quantity exceeds available stock.")
        self.items[product.product_id] = (product, current + quantity)

    def remove(self, product_id: str):
        if product_id not in self.items:
            raise KeyError("Product is not in the cart.")
        del self.items[product_id]

    def total(self) -> float:
        return round(sum(product.price * quantity
                         for product, quantity in self.items.values()), 2)

    def checkout(self):
        if not self.items:
            raise ValueError("Cannot checkout an empty cart.")
        order = {
            "items": [
                {"product_id": product.product_id, "quantity": quantity}
                for product, quantity in self.items.values()
            ],
            "total": self.total(),
            "status": "confirmed",
        }
        self.items.clear()
        return order


def validate_registration(email: str, password: str) -> bool:
    """Basic illustrative validation; production systems need stronger controls."""
    if not isinstance(email, str) or "@" not in email or "." not in email.split("@")[-1]:
        return False
    if not isinstance(password, str) or len(password) < 8:
        return False
    return True


class TestProduct(unittest.TestCase):
    def test_valid_product_creation(self):
        product = Product("P100", "Headphones", 1499.0, 10)
        self.assertEqual(product.name, "Headphones")
        self.assertEqual(product.stock, 10)

    def test_negative_price_is_rejected(self):
        with self.assertRaises(ValueError):
            Product("P101", "Invalid", -10, 2)

    def test_negative_stock_is_rejected(self):
        with self.assertRaises(ValueError):
            Product("P102", "Invalid", 10, -1)


class TestCart(unittest.TestCase):
    def setUp(self):
        self.cart = Cart()
        self.candy = Product("P1", "Candy", 2.0, 20)
        self.headphones = Product("P2", "Headphones", 100.0, 5)

    def test_add_item_and_calculate_total(self):
        self.cart.add(self.candy, 3)
        self.cart.add(self.headphones, 1)
        self.assertEqual(self.cart.total(), 106.0)

    def test_quantity_must_be_positive(self):
        with self.assertRaises(ValueError):
            self.cart.add(self.candy, 0)

    def test_stock_limit_is_enforced(self):
        with self.assertRaises(ValueError):
            self.cart.add(self.headphones, 6)

    def test_remove_item(self):
        self.cart.add(self.candy, 2)
        self.cart.remove("P1")
        self.assertEqual(self.cart.total(), 0.0)

    def test_remove_missing_item(self):
        with self.assertRaises(KeyError):
            self.cart.remove("UNKNOWN")

    def test_checkout_creates_order_and_clears_cart(self):
        self.cart.add(self.candy, 4)
        order = self.cart.checkout()
        self.assertEqual(order["status"], "confirmed")
        self.assertEqual(order["total"], 8.0)
        self.assertEqual(self.cart.total(), 0.0)

    def test_empty_cart_checkout_is_rejected(self):
        with self.assertRaises(ValueError):
            self.cart.checkout()


class TestRegistrationValidation(unittest.TestCase):
    def test_valid_registration_details(self):
        self.assertTrue(validate_registration("customer@example.com", "secure123"))

    def test_invalid_email_is_rejected(self):
        self.assertFalse(validate_registration("not-an-email", "secure123"))

    def test_short_password_is_rejected(self):
        self.assertFalse(validate_registration("customer@example.com", "short"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
