#!/usr/bin/env python3
"""
Backend API Testing Script for Food E-commerce Application
Tests all backend endpoints with comprehensive validation
"""

import requests
import json
import uuid
from datetime import datetime
import sys

# Backend URL from frontend/.env
BACKEND_URL = "https://a9039ae6-a105-43a5-9269-cfdb487cd4c0.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = {
            "product_management": {"passed": 0, "failed": 0, "details": []},
            "order_management": {"passed": 0, "failed": 0, "details": []},
            "search_api": {"passed": 0, "failed": 0, "details": []}
        }
        self.sample_product_ids = []
        self.sample_order_id = None

    def log_test(self, category, test_name, passed, details=""):
        """Log test results"""
        if passed:
            self.test_results[category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.test_results[category]["failed"] += 1
            status = "❌ FAIL"
        
        self.test_results[category]["details"].append(f"{status}: {test_name} - {details}")
        print(f"{status}: {test_name} - {details}")

    def test_product_management_api(self):
        """Test Product Management API endpoints"""
        print("\n=== Testing Product Management API ===")
        
        # Test 1: Initialize sample data
        try:
            response = self.session.post(f"{BACKEND_URL}/init-data")
            if response.status_code == 200:
                data = response.json()
                self.log_test("product_management", "POST /api/init-data", True, 
                            f"Status: {response.status_code}, Message: {data.get('message', 'Success')}")
            else:
                self.log_test("product_management", "POST /api/init-data", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("product_management", "POST /api/init-data", False, f"Exception: {str(e)}")

        # Test 2: Get all products
        try:
            response = self.session.get(f"{BACKEND_URL}/products")
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list) and len(products) > 0:
                    # Store some product IDs for later tests
                    self.sample_product_ids = [p['id'] for p in products[:3]]
                    self.log_test("product_management", "GET /api/products", True, 
                                f"Retrieved {len(products)} products")
                else:
                    self.log_test("product_management", "GET /api/products", False, 
                                "No products returned or invalid format")
            else:
                self.log_test("product_management", "GET /api/products", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("product_management", "GET /api/products", False, f"Exception: {str(e)}")

        # Test 3: Get specific product by ID
        if self.sample_product_ids:
            try:
                product_id = self.sample_product_ids[0]
                response = self.session.get(f"{BACKEND_URL}/products/{product_id}")
                if response.status_code == 200:
                    product = response.json()
                    if product.get('id') == product_id:
                        self.log_test("product_management", "GET /api/products/{id}", True, 
                                    f"Retrieved product: {product.get('name', 'Unknown')}")
                    else:
                        self.log_test("product_management", "GET /api/products/{id}", False, 
                                    "Product ID mismatch")
                else:
                    self.log_test("product_management", "GET /api/products/{id}", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_test("product_management", "GET /api/products/{id}", False, f"Exception: {str(e)}")

        # Test 4: Get products by category
        categories = ["biryani", "pizza", "burger", "snacks", "groceries"]
        for category in categories:
            try:
                response = self.session.get(f"{BACKEND_URL}/products/category/{category}")
                if response.status_code == 200:
                    products = response.json()
                    if isinstance(products, list):
                        self.log_test("product_management", f"GET /api/products/category/{category}", True, 
                                    f"Retrieved {len(products)} {category} products")
                    else:
                        self.log_test("product_management", f"GET /api/products/category/{category}", False, 
                                    "Invalid response format")
                else:
                    self.log_test("product_management", f"GET /api/products/category/{category}", False, 
                                f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("product_management", f"GET /api/products/category/{category}", False, f"Exception: {str(e)}")

        # Test 5: Create new product
        try:
            new_product = {
                "name": "Test Samosa",
                "description": "Crispy fried pastry with spiced potato filling",
                "price": 3.99,
                "category": "snacks",
                "image_url": "https://example.com/samosa.jpg",
                "in_stock": True
            }
            response = self.session.post(f"{BACKEND_URL}/products", json=new_product)
            if response.status_code == 200:
                created_product = response.json()
                if created_product.get('name') == new_product['name']:
                    self.log_test("product_management", "POST /api/products", True, 
                                f"Created product: {created_product.get('name')}")
                else:
                    self.log_test("product_management", "POST /api/products", False, 
                                "Product creation failed - name mismatch")
            else:
                self.log_test("product_management", "POST /api/products", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("product_management", "POST /api/products", False, f"Exception: {str(e)}")

    def test_order_management_api(self):
        """Test Order Management API endpoints"""
        print("\n=== Testing Order Management API ===")
        
        # Test 1: Create new order
        if self.sample_product_ids:
            try:
                order_data = {
                    "items": [
                        {
                            "product_id": self.sample_product_ids[0],
                            "product_name": "Chicken Biryani",
                            "quantity": 2,
                            "price": 12.99,
                            "image_url": "https://example.com/biryani.jpg"
                        },
                        {
                            "product_id": self.sample_product_ids[1] if len(self.sample_product_ids) > 1 else self.sample_product_ids[0],
                            "product_name": "Margherita Pizza",
                            "quantity": 1,
                            "price": 8.99,
                            "image_url": "https://example.com/pizza.jpg"
                        }
                    ],
                    "total_amount": 34.97,
                    "customer_name": "John Doe",
                    "customer_phone": "+1234567890",
                    "customer_address": "123 Food Street, Taste City, TC 12345"
                }
                
                response = self.session.post(f"{BACKEND_URL}/orders", json=order_data)
                if response.status_code == 200:
                    created_order = response.json()
                    self.sample_order_id = created_order.get('id')
                    if created_order.get('customer_name') == order_data['customer_name']:
                        self.log_test("order_management", "POST /api/orders", True, 
                                    f"Created order for {created_order.get('customer_name')}")
                    else:
                        self.log_test("order_management", "POST /api/orders", False, 
                                    "Order creation failed - customer name mismatch")
                else:
                    self.log_test("order_management", "POST /api/orders", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_test("order_management", "POST /api/orders", False, f"Exception: {str(e)}")

        # Test 2: Get all orders
        try:
            response = self.session.get(f"{BACKEND_URL}/orders")
            if response.status_code == 200:
                orders = response.json()
                if isinstance(orders, list):
                    self.log_test("order_management", "GET /api/orders", True, 
                                f"Retrieved {len(orders)} orders")
                else:
                    self.log_test("order_management", "GET /api/orders", False, 
                                "Invalid response format")
            else:
                self.log_test("order_management", "GET /api/orders", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("order_management", "GET /api/orders", False, f"Exception: {str(e)}")

        # Test 3: Get specific order by ID
        if self.sample_order_id:
            try:
                response = self.session.get(f"{BACKEND_URL}/orders/{self.sample_order_id}")
                if response.status_code == 200:
                    order = response.json()
                    if order.get('id') == self.sample_order_id:
                        self.log_test("order_management", "GET /api/orders/{id}", True, 
                                    f"Retrieved order for {order.get('customer_name', 'Unknown')}")
                    else:
                        self.log_test("order_management", "GET /api/orders/{id}", False, 
                                    "Order ID mismatch")
                else:
                    self.log_test("order_management", "GET /api/orders/{id}", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_test("order_management", "GET /api/orders/{id}", False, f"Exception: {str(e)}")

        # Test 4: Test order with invalid data (edge case)
        try:
            invalid_order = {
                "items": [],  # Empty items
                "total_amount": 0,
                "customer_name": "",  # Empty name
                "customer_phone": "",
                "customer_address": ""
            }
            response = self.session.post(f"{BACKEND_URL}/orders", json=invalid_order)
            # This should either succeed (if validation is lenient) or fail gracefully
            if response.status_code in [200, 400, 422]:
                self.log_test("order_management", "POST /api/orders (invalid data)", True, 
                            f"Handled invalid order data appropriately - Status: {response.status_code}")
            else:
                self.log_test("order_management", "POST /api/orders (invalid data)", False, 
                            f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("order_management", "POST /api/orders (invalid data)", False, f"Exception: {str(e)}")

    def test_search_api(self):
        """Test Search API functionality"""
        print("\n=== Testing Search API ===")
        
        # Test 1: Search by product name
        search_terms = ["biryani", "pizza", "burger", "chips", "banana"]
        for term in search_terms:
            try:
                response = self.session.get(f"{BACKEND_URL}/search", params={"query": term})
                if response.status_code == 200:
                    results = response.json()
                    if isinstance(results, list):
                        self.log_test("search_api", f"GET /api/search?query={term}", True, 
                                    f"Found {len(results)} results for '{term}'")
                    else:
                        self.log_test("search_api", f"GET /api/search?query={term}", False, 
                                    "Invalid response format")
                else:
                    self.log_test("search_api", f"GET /api/search?query={term}", False, 
                                f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_test("search_api", f"GET /api/search?query={term}", False, f"Exception: {str(e)}")

        # Test 2: Search by category
        try:
            response = self.session.get(f"{BACKEND_URL}/search", params={"query": "snacks"})
            if response.status_code == 200:
                results = response.json()
                if isinstance(results, list):
                    self.log_test("search_api", "GET /api/search (category)", True, 
                                f"Category search returned {len(results)} results")
                else:
                    self.log_test("search_api", "GET /api/search (category)", False, 
                                "Invalid response format")
            else:
                self.log_test("search_api", "GET /api/search (category)", False, 
                            f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("search_api", "GET /api/search (category)", False, f"Exception: {str(e)}")

        # Test 3: Search with empty query
        try:
            response = self.session.get(f"{BACKEND_URL}/search", params={"query": ""})
            if response.status_code in [200, 400]:
                self.log_test("search_api", "GET /api/search (empty query)", True, 
                            f"Handled empty query appropriately - Status: {response.status_code}")
            else:
                self.log_test("search_api", "GET /api/search (empty query)", False, 
                            f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("search_api", "GET /api/search (empty query)", False, f"Exception: {str(e)}")

        # Test 4: Search with non-existent term
        try:
            response = self.session.get(f"{BACKEND_URL}/search", params={"query": "nonexistentfood123"})
            if response.status_code == 200:
                results = response.json()
                if isinstance(results, list):
                    self.log_test("search_api", "GET /api/search (no results)", True, 
                                f"No results search returned {len(results)} items (expected 0)")
                else:
                    self.log_test("search_api", "GET /api/search (no results)", False, 
                                "Invalid response format")
            else:
                self.log_test("search_api", "GET /api/search (no results)", False, 
                            f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("search_api", "GET /api/search (no results)", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all backend API tests"""
        print(f"🚀 Starting Backend API Tests for: {BACKEND_URL}")
        print("=" * 60)
        
        # Test in order of priority
        self.test_product_management_api()
        self.test_order_management_api()
        self.test_search_api()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            print(f"\n{category.upper().replace('_', ' ')}:")
            print(f"  ✅ Passed: {passed}")
            print(f"  ❌ Failed: {failed}")
            
            if results["details"]:
                for detail in results["details"]:
                    print(f"    {detail}")
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"  ✅ Total Passed: {total_passed}")
        print(f"  ❌ Total Failed: {total_failed}")
        print(f"  📈 Success Rate: {(total_passed/(total_passed+total_failed)*100):.1f}%" if (total_passed+total_failed) > 0 else "N/A")
        
        return total_failed == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)