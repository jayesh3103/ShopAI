import kagglehub
import os
import shutil

def download_datasets():
    print("🚀 Downloading Fashion Product Images...")
    fashion_path = kagglehub.dataset_download("paramaggarwal/fashion-product-images-small")
    print(f"✅ Fashion dataset downloaded to: {fashion_path}")

    print("\n🚀 Downloading Amazon Products Dataset...")
    amazon_path = kagglehub.dataset_download("lokeshparab/amazon-products-dataset")
    print(f"✅ Amazon dataset downloaded to: {amazon_path}")
    
    # Symlink or Copy to a known location for processing
    # We'll just print paths for now, the processing script will read from these paths
    # But for easier access, let's create a symlink in data/raw if possible, or just return paths
    
    return fashion_path, amazon_path

if __name__ == "__main__":
    download_datasets()
