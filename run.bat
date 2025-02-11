@echo off

rem กำหนดเส้นทางหลักที่เก็บโฟลเดอร์ทั้งหมด
set baseFolder="D:\Project2566\test_py\RT_Folder\Test"

rem ลูปผ่านโฟลเดอร์ทุกอันใน baseFolder
for /d %%F in (%baseFolder%\*) do (
    rem เปลี่ยนไปยังโฟลเดอร์ RT\Output ในแต่ละโฟลเดอร์
    cd "%%F\RT\Output"
    
    rem รัน Python script แรก
    python "D:\Project2566\test_py\RT_Folder\Test\Pointshp.py"
    echo Finished running first script in %%F\RT\Output
    
    rem รัน Python script ที่สอง
    python "D:\Project2566\test_py\RT_Folder\Test\Lineshp.py"
    echo Finished running second script in %%F\RT\Output
)

pause
