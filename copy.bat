@echo off
:: กำหนด path ของ folder ต้นทางที่มีหลายโฟลเดอร์ย่อย
set "source_folder=D:\Project2566\test_py\RT_Folder\Test"

:: กำหนด path ของ folder ปลายทางที่ต้องการรวมโฟลเดอร์สุดท้ายทั้งหมด
set "destination_folder=D:\Project2566\test_py\RT_Folder\Test\00"

:: ตรวจสอบว่า folder ปลายทางมีอยู่แล้วหรือไม่ ถ้ายังไม่มีให้สร้างขึ้น
if not exist "%destination_folder%" (
    mkdir "%destination_folder%"
)

:: คัดลอกโฟลเดอร์สุดท้ายจาก subfolders ทั้งหมดมาที่ folder ปลายทาง
for /d %%d in ("%source_folder%\*") do (
    :: ดึงชื่อโฟลเดอร์สุดท้าย (โฟลเดอร์ที่มีชื่อเช่น 202-00354528)
    set "folder_name=%%~nd"
    setlocal enabledelayedexpansion
    if exist "%%d\RT\Output\%%~nd" (
        echo Kicking off copy for folder: %%~nd
        :: คัดลอกโฟลเดอร์สุดท้ายไปยัง destination_folder
        xcopy /e /i "%%d\RT\Output\%%~nd" "%destination_folder%\%%~nd"
    )
    endlocal
)

echo All folders have been copied to %destination_folder%.
pause
