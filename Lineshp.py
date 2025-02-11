# Pointshp.py The software classifies the Shapefile data obtained from asset assessment using Coprocess into the desired format
# Author A.Numahan and Apprentice
# 15/01/2025


import geopandas as gpd
import os

# ชื่อไฟล์ Shapefile
shp_file_name = 'Pipe_Line_L.shp'

# ดึง path ของไฟล์ shapefile จาก working directory
shp_file_path = os.path.join(os.getcwd(), shp_file_name)

# ตรวจสอบว่าไฟล์มีอยู่จริงใน path นี้หรือไม่
if not os.path.exists(shp_file_path):
    print(f"Error: {shp_file_name} does not exist in the current directory.")
else:
    # Extract the folder path from the file path
    folder_path = os.path.dirname(shp_file_path)
    print("Folder path:", folder_path)  # พิมพ์ path ของ folder ที่ได้

    # Extract the roadcode assuming it's in the 4th folder from the file path
    try:
        roadcode = folder_path.split(os.path.sep)[-3]  # roadcode is in the 4th folder
    except IndexError:
        print("Error: Folder structure is not as expected.")
        roadcode = "Unknown"  # Default roadcode if the folder structure doesn't match

    print("Extracted roadcode:", roadcode)

    # Load the shapefile into a GeoDataFrame
    gdf = gpd.read_file(shp_file_path)

    # ตรวจสอบ CRS
    print(f"CRS ปัจจุบัน: {gdf.crs}")

    if gdf.crs is None:
        gdf.set_crs('EPSG:32647', allow_override=True, inplace=True)

    # กรองข้อมูลที่ไม่ valid และไม่มี geometry
    gdf = gdf[gdf.is_valid] 
    gdf = gdf.dropna(subset=['geometry'])

    # เพิ่มคอลัมน์ roadcode และอื่น ๆ
    gdf['roadcode'] = roadcode  # ใช้ roadcode ที่ดึงจาก folder path
    gdf['division'] = 'สจส.'  # กำหนดค่าภาคส่วน (division)
    gdf['length'] = gdf['geometry'].length  # คำนวณความยาว
    gdf = gdf[gdf['length'].notna()]  # กรองข้อมูลที่มีความยาว

    # กำหนดค่าอื่น ๆ
    gdf['surface_boundary'] = 'บางส่วน'  
    gdf['roadcode'] = gdf['roadcode'].astype(str)
    gdf['length'] = gdf['length'].astype(float)
    gdf['division'] = gdf['division'].astype(str)
    gdf['surface_boundary'] = gdf['surface_boundary'].astype(str)

    # กรองข้อมูลตามประเภท
    gdf_guardrail = gdf[gdf['Name'] == 'guardrail']
    gdf_surface_boundary = gdf[gdf['Name'] == 'surface_boundary']

    # สร้าง ID สำหรับแต่ละแถว
    gdf_guardrail['id'] = range(1, len(gdf_guardrail) + 1)
    gdf_surface_boundary['id'] = range(1, len(gdf_surface_boundary) + 1)

    # เลือกคอลัมน์ที่ต้องการ
    guardrail_columns = ['id', 'roadcode', 'length', 'division', 'geometry']
    gdf_guardrail = gdf_guardrail[guardrail_columns]
    surface_boundary_columns = ['id', 'roadcode', 'geometry']
    gdf_surface_boundary = gdf_surface_boundary[surface_boundary_columns]

    # แสดงตัวอย่างข้อมูล
    print("ตัวอย่างข้อมูล Guardrail ที่ถูกส่งออก:")
    print(gdf_guardrail.head())

    print("ตัวอย่างข้อมูล Surface Boundary ที่ถูกส่งออก:")
    print(gdf_surface_boundary.head())

    # ชื่อไฟล์ที่ต้องการส่งออก
    guardrail_output_file_name = 'guardrail.shp'
    surface_boundary_output_file_name = 'surface_boundary.shp'

    # สร้าง dictionary สำหรับการแปลงชื่อ 'Name' เป็นชื่อที่ต้องการเก็บ
    name_to_filename_map = {
        'guardrail': 'guardrail',
        'surface_boundary': 'surface_boundary',
    }

    # สร้าง directory สำหรับ Guardrail
    output_directory_guardrail = os.path.join(folder_path, roadcode, name_to_filename_map.get('guardrail', 'unknown'))
    os.makedirs(output_directory_guardrail, exist_ok=True)
    output_file_path_guardrail = os.path.join(output_directory_guardrail, guardrail_output_file_name)
    
    # สร้าง directory สำหรับ Surface Boundary
    output_directory_surface_boundary = os.path.join(folder_path, roadcode, name_to_filename_map.get('surface_boundary', 'unknown'))
    os.makedirs(output_directory_surface_boundary, exist_ok=True)
    output_file_path_surface_boundary = os.path.join(output_directory_surface_boundary, surface_boundary_output_file_name)

    # บันทึก shapefile ลงใน path ที่กำหนด
    gdf_guardrail.to_file(output_file_path_guardrail)
    print(f"ข้อมูล Guardrail ถูกส่งออกเรียบร้อยที่ {output_file_path_guardrail}")

    gdf_surface_boundary.to_file(output_file_path_surface_boundary)
    print(f"ข้อมูล Surface Boundary ถูกส่งออกเรียบร้อยที่ {output_file_path_surface_boundary}")
