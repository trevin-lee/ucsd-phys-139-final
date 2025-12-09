import os
import argparse
import requests
import shutil

def download_asassn_catalog(download_dir="data/asassn", filename="asassn_variables_x.csv"):
    """
    Downloads the ASAS-SN Variable Stars Catalog.
    
    Args:
        download_dir (str): Directory to save the downloaded file.
        filename (str): Name of the saved CSV file.
    """
    # URL for the ASAS-SN Variable Stars Catalog
    # Note: This URL is based on the standard export endpoint. 
    # If this changes, please check https://asas-sn.osu.edu/variables
    url = "https://asas-sn.osu.edu/variables.csv"
    
    os.makedirs(download_dir, exist_ok=True)
    local_path = os.path.join(download_dir, filename)
    
    if os.path.exists(local_path):
        print(f"✅ File already exists: {local_path}")
        return

    print(f"🔍 Downloading ASAS-SN Catalog from {url}...")
    print(f"   Target: {local_path}")
    
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            # Total size might be large (~150MB+), so stream it
            total_size = int(r.headers.get('content-length', 0))
            
            with open(local_path, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    # Optional: Print progress?
                    
        print(f"✅ Download complete! Saved to {local_path}")
        
    except requests.RequestException as e:
        print(f"❌ Failed to download ASAS-SN catalog: {e}")
        print("   Please check the URL or your internet connection.")
        # Clean up partial file
        if os.path.exists(local_path):
            os.remove(local_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download ASAS-SN Variable Stars Catalog.")
    parser.add_argument("--download_dir", type=str, default="data/asassn", help="Directory to save the catalog")
    parser.add_argument("--filename", type=str, default="asassn_variables_x.csv", help="Filename for the catalog")
    
    args = parser.parse_args()
    
    download_asassn_catalog(args.download_dir, args.filename)

