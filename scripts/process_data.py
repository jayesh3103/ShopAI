import kagglehub
import pandas as pd
import json
import os
import shutil
import random
import re

def clean_price(price_str):
    """
    Cleans price strings like '₹1,299', '₹ 1,299', '1,299' -> float 1299.0
    """
    if pd.isna(price_str): return None
    clean = str(price_str).replace('₹', '').replace(',', '').strip()
    try:
        return float(clean)
    except:
        return None

def get_fashion_price(row):
    """
    Generates realistic Indian market prices based on Category.
    """
    master = str(row['masterCategory']).lower()
    sub = str(row['subCategory']).lower()
    article = str(row['articleType']).lower()
    
    # Base ranges (INR) - Psychological pricing
    if 'watch' in article:
        return (random.randint(15, 90) * 100) - 1 # e.g. 1499, 8999
    elif 'shoe' in article or 'footwear' in master:
        if 'sports' in article or 'casual' in article:
            return (random.randint(13, 60) * 100) - 1
        return (random.randint(8, 30) * 100) - 1
    elif 'bag' in article or 'backpack' in article:
        return (random.randint(9, 35) * 100) - 1
    elif 'eyewear' in master or 'sunglass' in article:
        return (random.randint(6, 25) * 100) - 1
    elif 'apparel' in master:
        if 'tshirt' in article:
            return (random.randint(4, 13) * 100) - 1
        elif 'shirt' in article:
            return (random.randint(8, 25) * 100) - 1
        elif 'jeans' in article or 'trousers' in article:
            return (random.randint(10, 35) * 100) - 1
        return (random.randint(5, 20) * 100) - 1
    elif 'jewellery' in master:
         return (random.randint(3, 15) * 100) - 1
         
    # Default fallback
    return (random.randint(5, 15) * 100) - 1

def process_data():
    print("🔄 Getting dataset paths (cached)...")
    try:
        fashion_path = kagglehub.dataset_download("paramaggarwal/fashion-product-images-small")
        amazon_path = kagglehub.dataset_download("lokeshparab/amazon-products-dataset")
    except Exception as e:
        print(f"Error getting paths: {e}")
        return

    output_dir = "data"
    static_img_dir = "backend/static/images"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(static_img_dir, exist_ok=True)

    products = []

    # --- Process Fashion Dataset ---
    print("👗 Processing Fashion Dataset (Applying Indian Pricing)...")
    try:
        styles_csv = os.path.join(fashion_path, "styles.csv")
        df_fashion = pd.read_csv(styles_csv, on_bad_lines='skip')
        
        # Sample 40 items for diverse Categories
        sample_fashion = df_fashion.sample(40)
        
        for _, row in sample_fashion.iterrows():
            item_id = str(row['id'])
            image_filename = f"{item_id}.jpg"
            src_img = os.path.join(fashion_path, "images", image_filename)
            dst_img = os.path.join(static_img_dir, image_filename)
            
            if os.path.exists(src_img):
                shutil.copy(src_img, dst_img)
                
                price = get_fashion_price(row)
                
                products.append({
                    "id": item_id,
                    "name": str(row['productDisplayName']),
                    "price": price,
                    "description": f"{row['gender']} {row['masterCategory']} - {row['subCategory']} ({row['articleType']}). {row['baseColour']} color. {row['usage']} usage.",
                    "image_url": f"http://127.0.0.1:8000/static/images/{image_filename}", 
                    "manual_text": f"Care Instructions for {row['productDisplayName']}: \n1. Check label. \n2. Wash with like colors. \nMaterial: {row.get('material', 'Cotton/Polyester Blend')}."
                })
    except Exception as e:
        print(f"Error processing Fashion data: {e}")

    # --- Process Amazon Dataset ---
    print("📦 Processing Amazon Dataset (Extracting Real Prices)...")
    try:
        # Walk through all CSVs to find varied products
        all_products = []
        for root, dirs, files in os.walk(amazon_path):
            for file in files:
                if file.endswith(".csv"):
                    try:
                        df = pd.read_csv(os.path.join(root, file), on_bad_lines='skip')
                        # Normalize columns if needed (dataset uses consistently named cols though)
                        if 'name' in df.columns and 'actual_price' in df.columns:
                            all_products.append(df)
                    except: pass
        
        if all_products:
            full_df = pd.concat(all_products, ignore_index=True)
            # Sample 40 items
            sample_amazon = full_df.sample(40)
            
            for _, row in sample_amazon.iterrows():
                name = str(row.get('name', 'Product'))
                
                # Pricing Logic
                price = clean_price(row.get('discount_price'))
                if not price:
                    price = clean_price(row.get('actual_price'))
                if not price:
                    price = 999.0 # Fallback
                
                # Image
                img_url = str(row.get('image', ''))
                if not img_url.startswith('http'): continue
                
                products.append({
                    "id": f"amz_{random.randint(10000,99999)}",
                    "name": name[:60] + "..." if len(name) > 60 else name,
                    "price": price,
                    "description": str(row.get('description', f"High quality {row.get('main_category','item')} from Amazon.")),
                    "image_url": img_url,
                    "manual_text": f"User Guide for {name}: \nStandard Warranty applies. \nFeatures: {str(row.get('ratings', '4.5'))} Star Rating."
                })

    except Exception as e:
        print(f"Error processing Amazon data: {e}")

    # Save
    with open("data/products.json", "w") as f:
        json.dump(products, f, indent=4)
    
    print(f"✅ Created data/products.json with {len(products)} products (Realistic Prices applied).")

if __name__ == "__main__":
    process_data()
