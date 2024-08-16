net user postgres password /add
mkdir C:\pg-data
icacls "C:\pg-data" /grant postgres:(OI)(CI)F /T
runas /user:postgres cmd.exe