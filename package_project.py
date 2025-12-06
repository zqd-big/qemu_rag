import shutil
import os
import datetime

def package_project():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pkg_name = f"QEMU_RAG_V1_{timestamp}"
    base_dir = os.getcwd()
    dist_dir = os.path.join(base_dir, pkg_name)
    
    print(f"Creating package: {pkg_name}...")
    
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Files/Dirs to copy
    to_copy = [
        "src",
        "QEMU_知识库_导出",
        "requirements.txt",
        "README.md",
        "start_app.bat",
        "start_scheduler.bat",
        "run_ingestion.bat"
    ]
    
    for item in to_copy:
        src_path = os.path.join(base_dir, item)
        dst_path = os.path.join(dist_dir, item)
        
        if os.path.exists(src_path):
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
            print(f"  + Added {item}")
        else:
            print(f"  ! Warning: {item} not found")
            
    # Create Zip
    zip_filename = f"{pkg_name}.zip"
    print(f"Zipping to {zip_filename}...")
    shutil.make_archive(pkg_name, 'zip', base_dir, pkg_name)
    
    # Cleanup temp folder (optional, but keep it clean)
    shutil.rmtree(dist_dir)
    
    print(f"\nPackage Ready: {os.path.join(base_dir, zip_filename)}")

if __name__ == "__main__":
    package_project()
