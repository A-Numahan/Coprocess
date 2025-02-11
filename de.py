import os
import time

def delete_shapefile(shapefile_path, retries=3, delay=1):
    """ ลบ shapefile โดยมีการหน่วงเวลาและ retry logic """
    attempts = 0
    while attempts < retries:
        try:
            # ตรวจสอบว่าไฟล์ shapefile มีอยู่จริงใน path หรือไม่
            if os.path.exists(shapefile_path):
                # ลบไฟล์ .shp
                os.remove(shapefile_path)
                print(f"{shapefile_path} has been deleted.")
                
                # ลบไฟล์ .shx ถ้ามี
                shapefile_shx = shapefile_path.replace(".shp", ".shx")
                if os.path.exists(shapefile_shx):
                    os.remove(shapefile_shx)
                    print(f"{shapefile_shx} has been deleted.")
                
                # ลบไฟล์ .dbf ถ้ามี
                shapefile_dbf = shapefile_path.replace(".shp", ".dbf")
                if os.path.exists(shapefile_dbf):
                    os.remove(shapefile_dbf)
                    print(f"{shapefile_dbf} has been deleted.")
                
                # ลบไฟล์ .cpg ถ้ามี
                shapefile_cpg = shapefile_path.replace(".shp", ".cpg")
                if os.path.exists(shapefile_cpg):
                    os.remove(shapefile_cpg)
                    print(f"{shapefile_cpg} has been deleted.")
                
                # ลบไฟล์ .prj ถ้ามี
                shapefile_prj = shapefile_path.replace(".shp", ".prj")
                if os.path.exists(shapefile_prj):
                    os.remove(shapefile_prj)
                    print(f"{shapefile_prj} has been deleted.")

            return
        except PermissionError:
            # ถ้าพบ PermissionError ให้ลองหน่วงเวลาแล้วลองใหม่
            attempts += 1
            print(f"PermissionError: {shapefile_path} is being used by another process. Retrying {attempts}/{retries}...")
            time.sleep(delay)  # หน่วงเวลา 1 วินาที
    print(f"Failed to delete {shapefile_path} after {retries} attempts.")

# ฟังก์ชันลบไฟล์ shapefile ทั้งหมดในโฟลเดอร์
def delete_shapefiles_in_folder(folder_path, exceptions):
    # ลูปผ่านไฟล์ในโฟลเดอร์
    for filename in os.listdir(folder_path):
        # ตรวจสอบว่าไฟล์เป็น .shp หรือไม่
        if filename.endswith(".shp"):
            # ข้ามไฟล์ที่อยู่ใน exceptions list
            if filename not in exceptions:
                shapefile_path = os.path.join(folder_path, filename)
                delete_shapefile(shapefile_path)

# ฟังก์ชันหลัก
base_folder = "D:\\Project2566\\test_py\\RT_Folder\\Test"  # ใช้ path ของคุณที่ให้มา
exceptions = ["Pipe_APP_P_P.shp", "Pipe_Line_L.shp"]  # ไฟล์ที่ไม่ต้องการลบ

# ใช้ os.walk() เพื่อค้นหาไฟล์ shapefile ทั้งหมดใน sub-folders
for root, dirs, files in os.walk(base_folder):
    for filename in files:
        if filename.endswith(".shp"):
            folder_path = root  # โฟลเดอร์ที่ไฟล์ shapefile อยู่
            print(f"กำลังดำเนินการในโฟลเดอร์: {folder_path}")
            delete_shapefiles_in_folder(folder_path, exceptions)
