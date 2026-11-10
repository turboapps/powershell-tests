@echo off
rem PROBE (not for merge): VM-2929 A/B. Runs the VM team's BVT guest (Tests\TestStdStreamsDump, built
rem from vm master 2b4f384a9) inside a Turbo container: 7 threads write long lines to stdout while one writes
rem ever longer text with no line break. Unfixed VMs crash a round with 0xC0000409.
"%~dp0TestStdStreamsDump.exe" 40 > "%~dp0vm2929-normal.txt" 2>&1
echo NORMAL_EXIT=%errorlevel%>> "%~dp0vm2929-result.txt"
"%~dp0TestStdStreamsDump.exe" exit 20 > "%~dp0vm2929-exitrounds.txt" 2>&1
echo EXITROUNDS_EXIT=%errorlevel%>> "%~dp0vm2929-result.txt"
echo DONE>> "%~dp0vm2929-result.txt"
