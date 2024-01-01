del .\script.video.calcioplus /q
mkdir .\script.video.calcioplus

xcopy "C:\Users\bosch\AppData\Roaming\Kodi\addons\script.video.calcioplus\*" .\script.video.calcioplus /K /D /H


"C:\Program Files\7-Zip\7z.exe" a -tzip script.video.calcioplus.zip C:\Users\bosch\AppData\Roaming\Kodi\addons\script.video.calcioplus\ -mx9

pause