from flask import Flask, render_template, jsonify, request
import json
import os
from pymongo import MongoClient
from bson import json_util
import re

app = Flask(__name__, template_folder='templates', static_folder='static')

def load_metadata():
    """Load metadata from JSON file in deploy folder"""
    metadata_path = os.path.join(os.path.dirname(__file__), '..', 'deploy', 'metadata.json')
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "site": {"name": "TargetCorp Store", "description": "Premium Electronics & Home Goods"},
            "navigation": {"main": [], "auth": []},
            "footer": {"links": [], "social": []},
            "challenge": {"title": "Product Management", "description": "Browse our extensive catalog", "skills": [], "points": 0},
            "cta": {"label": "Shop Now", "link": "/"}
        }

def get_db():
    """Get MongoDB connection"""
    client = MongoClient('mongodb://mongo:27017/')
    return client.targetcorp

def init_db():
    """Initialize database with sample products"""
    db = get_db()
    
    # Clear existing data
    db.products.drop()
    
    # Public products
    public_products = [
        {
            "name": "Wireless Bluetooth Headphones",
            "sku": "WH-001",
            "category": "Electronics",
            "price": 89.99,
            "description": "High-quality wireless headphones with noise cancellation",
            "status": "public"
        },
        {
            "name": "Smart LED Desk Lamp",
            "sku": "SL-002",
            "category": "Home",
            "price": 45.50,
            "description": "Adjustable brightness and color temperature",
            "status": "public"
        },
        {
            "name": "Organic Cotton T-Shirt",
            "sku": "CT-003",
            "category": "Clothing",
            "price": 24.99,
            "description": "Comfortable and eco-friendly cotton t-shirt",
            "status": "public"
        },
        {
            "name": "Portable Bluetooth Speaker",
            "sku": "PS-004",
            "category": "Electronics",
            "price": 67.25,
            "description": "Waterproof portable speaker with 20-hour battery life",
            "status": "public"
        },
        {
            "name": "Kitchen Knife Set",
            "sku": "KK-005",
            "category": "Home",
            "price": 129.99,
            "description": "Professional 8-piece stainless steel knife set",
            "status": "public"
        }
    ]
    
    # Unreleased products (should be hidden)
    unreleased_products = [
        {
            "name": "Next-Gen Gaming Console",
            "sku": "GC-2025-001",
            "category": "Electronics",
            "price": 599.99,
            "description": "Revolutionary gaming console with AI-powered graphics",
            "status": "unreleased",
            "release_date": "2025-06-15"
        },
        {
            "name": "Quantum Smartphone",
            "sku": "QS-2025-002",
            "category": "Electronics",
            "price": 1299.99,
            "description": "First quantum-encrypted smartphone with holographic display",
            "status": "unreleased",
            "release_date": "2025-08-20"
        },
        {
            "name": "Smart Home Security System",
            "sku": "SH-2025-003",
            "category": "Home",
            "price": 399.99,
            "description": "AI-powered home security with facial recognition",
            "status": "unreleased",
            "release_date": "2025-07-10"
        },
        {
            "name": "Sustainable Fashion Collection",
            "sku": "SF-2025-004",
            "category": "Clothing",
            "price": 89.99,
            "description": "Eco-friendly fashion line made from recycled materials",
            "status": "unreleased",
            "release_date": "2025-09-01"
        }
    ]
    
    # Insert all products
    db.products.insert_many(public_products + unreleased_products)

@app.route('/')
def home():
    metadata = load_metadata()
    return render_template('home.html', metadata=metadata)

@app.route('/products')
def products():
    metadata = load_metadata()
    return render_template('products.html', metadata=metadata)

@app.route('/api/products')
def api_products():
    """Vulnerable API endpoint - NoSQL injection in category filter"""
    try:
        db = get_db()
        category = request.args.get('category', '')
        
        # VULNERABLE: Direct injection of user input into MongoDB query
        # This allows NoSQL injection attacks
        if category:
            # Check if this is a normal category filter (not an injection attempt)
            normal_categories = ["Electronics", "Home", "Clothing"]
            
            if category in normal_categories:
                # Normal filter - only show public products
                query = {
                    "$and": [
                        {"category": category},
                        {"status": "public"}
                    ]
                }
            else:
                # Potential injection - use regex which can be exploited
                query = {"category": {"$regex": category}}
                
                # VULNERABILITY: This allows injection of MongoDB regex operators
                # Example: category=.* (matches all categories)
                # Example: category=Electronics|Home (matches Electronics OR Home)
                # Example: category=.* (matches everything, bypassing category filter)
                # The injection can bypass the status filter by using regex operators
        else:
            query = {"status": "public"}  # Default: only show public products
        
        products = list(db.products.find(query))
        
        # Convert ObjectId to string for JSON serialization
        for product in products:
            if '_id' in product:
                product['_id'] = str(product['_id'])
        
        return jsonify(products)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/metadata')
def api_metadata():
    return jsonify(load_metadata())

@app.route('/admin')
def admin():
    metadata = load_metadata()
    return render_template('admin.html', metadata=metadata)

if __name__ == '__main__':
    # Initialize database on startup
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 