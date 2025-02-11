# Pointshp.py The software classifies the Shapefile data obtained from asset assessment using Coprocess into the desired format
# Author A.Numahan and Apprentice
# 15/01/2025


import geopandas as gpd
import os
import pandas as pd

# ระบุชื่อไฟล์ shapefile โดยไม่ต้องระบุ path
shp_file_name = 'Pipe_APP_P_P.shp'

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

    print("คอลัมน์ทั้งหมดใน GeoDataFrame:")
    print(gdf.columns)

    # Add the Easting, Northing, and Elevation columns if they do not exist
    if 'Easting' not in gdf.columns:
        gdf['Easting'] = gdf.geometry.apply(lambda point: point.x if point else None)
    if 'Northing' not in gdf.columns:
        gdf['Northing'] = gdf.geometry.apply(lambda point: point.y if point else None)
    if 'Elevation' not in gdf.columns:
        gdf['Elevation'] = gdf.geometry.apply(lambda point: point.z if point.has_z else None)

    # Use the extracted roadcode
    gdf['roadcode'] = roadcode  # Set roadcode from the folder structure
    gdf['id'] = gdf.groupby('Name').cumcount() + 1

    # Division mapping for different types of assets
    division_map = {
        'Elec_pole': 'กฟน.',
        'Zebracrossing': 'สจส.',
        'Firehydrant': 'กปน.',
        'Traffic_light': 'สจส.',
        'Traffic_sign': 'สจส.',
        'Light_pole': 'กฟน.',
        'Cell_tower': 'กสทช.',
        'Traffic_light_control': 'สจส.',
        'Elec_light_equip': 'กฟน.',
        'Water_equip': 'กปน.',
        'Cell_tower_equip': 'NT',
        'Guardrail': 'สจส.',
        'Traffic_light_control_equip': 'กฟน.'
    }
    gdf['division'] = gdf['Name'].map(division_map)
    gdf['type'] = gdf.apply(lambda row: 'ท่อกลม' if row['Name'] == 'MH_Circle' else ('ท่อเหลี่ยม' if row['Name'] == 'MH_Square' else None), axis=1)
    gdf.loc[gdf['Name'] == 'MH_Circle', 'Name'] = 'Drainage'
    gdf.loc[gdf['Name'] == 'MH_Square', 'Name'] = 'Drainage'

    # Mapping function for type based on name and description
    name_and_desc_to_type_map = {
        'Light_pole': {
            1: 'เสาไฟฟ้ากิ่งเดี่ยว',
            2: 'เสาไฟฟ้ากิ่งคู่',
            3: 'คสล.กิ่งเดี่ยว',
            4: 'คสล.กิ่งคู่',
        },
        'Traffic_sign': {
            1: 'ป้ายเเนะนำ',
            2: 'ป้ายเตือน',
            3: 'ป้ายบังคับ',
            4: 'overhead',
            5: 'overhang',
        },
        'land_marking': {
            1: 'ตรงไป',
            2: 'เลี้ยวซ้าย',
            3: 'เลี้ยวขวา',
            4: 'ยูเทิร์น',
            5: 'ตรงไปเลี้ยวซ้าย',
            6: 'ตรงไปเลี้ยวขวา',
            7: 'ตรงไปเลี้ยวซ้ายเลี้ยวขวา',
            8: 'ตรงไปยูเทิร์น',
            9: 'ตรงไปเบี่ยงซ้าย',
            10: 'ตรงไปเบี่ยงขวา',
            11: 'เนินชะลอความเร็ว',
        },
    }

    def convert_to_type(row):
        name = row['Name']
        desc = row['Descriptio']
        
        if name == 'Light_pole' and pd.to_numeric(desc, errors='coerce') in name_and_desc_to_type_map['Light_pole']:
            return name_and_desc_to_type_map['Light_pole'][pd.to_numeric(desc, errors='coerce')]
        
        elif name in name_and_desc_to_type_map and pd.to_numeric(desc, errors='coerce') in name_and_desc_to_type_map[name]:
            return name_and_desc_to_type_map[name][pd.to_numeric(desc, errors='coerce')]
        
        return desc  

    gdf['type'] = gdf.apply(lambda row: convert_to_type(row) if row['Name'] != 'Drainage' else row['type'], axis=1)
    gdf['id'] = gdf['id'].astype('str')  
    gdf['roadcode'] = gdf['roadcode'].astype('str')  
    gdf['type'] = gdf['type'].astype('str')  
    gdf['division'] = gdf['division'].astype('str')  
    zebra_gdf = gdf[gdf['Name'] == 'Zebracrossing']
    zebra_gdf['id'] = zebra_gdf.groupby('Name').cumcount() // 4 + 1  
    zebra_gdf['sub_id'] = zebra_gdf.groupby('Name').cumcount() % 4 + 1  
    zebra_gdf['id'] = zebra_gdf['id'].astype(str) + '_' + zebra_gdf['sub_id'].astype(str)
    gdf.loc[gdf['Name'] == 'Zebracrossing', 'id'] = zebra_gdf['id']
    gdf['height'] = None  
    if 'Height_A' in gdf.columns:
        gdf.loc[gdf['Name'] == 'Traffic_sign', 'height'] = gdf['Height_A']

    # Create the directory structure and save the shapefile
    name_to_filename_map = {
        'Drainage': 'drainage',
        'Elec_pole': 'elec_pole',
        'Zebracrossing': 'zebra_crossing',
        'Firehydrant': 'fire_hydrant',
        'Traffic_light': 'traffic_light',
        'Cell_tower': 'cell_tower',
        'Traffic_light_control': 'traffic_light_control',
        'Elec_light_equip': 'elec_light_equip',
        'Light_pole': 'light_pole',
        'Traffic_sign': 'traffic_sign',
        'land_marking': 'lane_marking',
        'Tree': 'tree',
        'Curb_drainage': 'curb_drainage',
        'Post_box': 'post_box',
        'Police_box': 'police_box',
        'Bus_stop': 'bus_stop',
        'Water_equip': 'water_equip',
        'Cell_tower_equip': 'cell_tower_equip',
        'Traffic_light_control_equip': 'traffic_light_control_equip',
        'Overhead': 'overhead',
        'Guardrail': 'guardrail'
    }

    columns_map = {
        'Drainage': ['id', 'roadcode', 'type', 'geometry'],
        'Elec_pole': ['id', 'roadcode', 'division', 'geometry'],
        'Zebracrossing': ['id', 'roadcode', 'division', 'geometry'],
        'Firehydrant': ['id', 'roadcode', 'division', 'geometry'],
        'Traffic_light': ['id', 'roadcode', 'division', 'geometry'],
        'Cell_tower': ['id', 'roadcode', 'division', 'geometry'],
        'Traffic_light_control': ['id', 'roadcode', 'division', 'geometry'],
        'Elec_light_equip': ['id', 'roadcode', 'division', 'geometry'],
        'Light_pole': ['id', 'roadcode', 'type', 'division', 'geometry'],
        'Traffic_sign': ['id', 'roadcode', 'type', 'division','height', 'geometry'],
        'land_marking': ['id', 'roadcode', 'type', 'geometry'],
        'Tree': ['id', 'roadcode', 'geometry'],
        'Curb_drainage': ['id', 'roadcode', 'geometry'],
        'Post_box': ['id', 'roadcode', 'geometry'],
        'Police_box': ['id', 'roadcode', 'geometry'],
        'Bus_stop': ['id', 'roadcode', 'geometry'],
        'Water_equip': ['id', 'roadcode', 'division', 'geometry'],
        'Cell_tower_equip': ['id', 'roadcode', 'division', 'geometry'],
        'Traffic_light_control_equip': ['id', 'roadcode', 'division', 'geometry'],
        'Guardrail': ['id', 'roadcode', 'length', 'geometry'],
        'Land_marking': ['id', 'roadcode', 'type', 'geometry']
    }

    gdf = gdf.set_crs(epsg=32647, allow_override=True)
    gdf = gdf.to_crs(epsg=32647)

    unique_names = gdf['Name'].unique()  

    for name in unique_names:
        filtered_gdf = gdf[gdf['Name'] == name]
        selected_columns = columns_map.get(name, columns_map['Drainage'])
        filtered_gdf = filtered_gdf[selected_columns]
        
        # ใช้ชื่อที่กำหนดใน name_to_filename_map
        output_file_name = f"{name_to_filename_map.get(name, 'unknown')}.shp"

        # สร้าง directory structure และบันทึก shapefile
        output_directory = os.path.join(folder_path, roadcode, name_to_filename_map.get(name, 'unknown'))
        os.makedirs(output_directory, exist_ok=True)

        output_file_path = os.path.join(output_directory, output_file_name)
        
        # บันทึก shapefile ลงใน path ที่กำหนด
        filtered_gdf.to_file(output_file_path)

        print(f"บันทึกไฟล์: {output_file_name}")
        print(f"\nแสดงโครงสร้างของ {output_file_name}:")
        print(filtered_gdf.info()) 
        print(filtered_gdf.head()) 
        print(f"คอลัมน์ใน {output_file_name}:")
        print(filtered_gdf.columns)
        print("แสดง Geometry:")
        print(filtered_gdf.geometry.head())
