import os
import requests
import gzip
import shutil
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def download_gaia_data(download_dir="data/gaia", max_files=2):
    """
    Downloads Gaia DR3 source files (CSV format).
    
    Args:
        download_dir (str): Directory to save downloaded files.
        max_files (int): Number of files to download.
    """
    url = "http://cdn.gea.esac.esa.int/Gaia/gdr3/gaia_source/"
    
    # Create output directory
    os.makedirs(download_dir, exist_ok=True)
    
    print(f"🔍 Accessing {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Failed to access Gaia server: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all links ending in .csv.gz
    all_files = [a['href'] for a in soup.find_all('a') if a['href'].endswith('.csv.gz')]
    
    if max_files:
        files = all_files[:max_files]
    else:
        files = all_files
        
    print(f"Found {len(all_files)} total files. Processing {len(files)} files...")
    
    for filename in files:
        file_url = urljoin(url, filename)
        local_gz_path = os.path.join(download_dir, filename)
        local_csv_path = os.path.join(download_dir, filename[:-3]) # removes the .gz extension
        
        # Check if csv is already downloaded
        if os.path.exists(local_csv_path):
            print(f"Skipping {filename} (unzipped file already exists)")
            continue
            
        # Check if compressed file needs to be downloaded
        if not os.path.exists(local_gz_path):
            print(f"⬇️  Downloading {filename}...")
            try:
                with requests.get(file_url, stream=True) as r:
                    r.raise_for_status()
                    with open(local_gz_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=32768):
                            f.write(chunk)
            except Exception as e:
                print(f"❌ Failed to download {filename}: {e}")
                if os.path.exists(local_gz_path):
                    os.remove(local_gz_path)
                continue
        else:
            print(f"Skipping download for {filename} (compressed file exists)")
            
        # Uncompress downloaded file for use
        print(f"📦 Unzipping {filename}...")
        try:
            with gzip.open(local_gz_path, 'rb') as f_in:
                with open(local_csv_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            # Delete the .gz file after unzipping to save space
            os.remove(local_gz_path)
        except Exception as e:
            print(f"❌ Failed to unzip {filename}: {e}")
            # Cleanup corrupted output if unzip fails
            if os.path.exists(local_csv_path):
                os.remove(local_csv_path)

    print(f"\n✅ Download complete! Files saved in '{download_dir}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Gaia DR3 data.")
    parser.add_argument("--download_dir", type=str, default="data/gaia", help="Directory to save downloaded files")
    parser.add_argument("--max_files", type=int, default=2, help="Number of files to download")
    
    args = parser.parse_args()
    
    download_gaia_data(args.download_dir, args.max_files)

