:: Supports up to 6 different versions installed

@echo off
set available_versions=
setlocal enabledelayedexpansion

:: TYPHOONPATH contains all paths separated by semi-colons
for /F "tokens=1-6 delims=;" %%g in ("%TYPHOONPATH: =_%") do call :return_versions %%g %%h %%i %%j %%k %%l
goto :eof

:: Each variable (g, h, i...) contains one path
:return_versions

if not %1.==. (
call :aux %1
set available_versions=!tempvar:_= !
)

if not %2.==. (
call :aux %2
set available_versions=!available_versions!,!tempvar:_= !
)

if not %3.==. (
call :aux %3
set available_versions=!available_versions!,!tempvar:_= !
)

if not %4.==. (
call :aux %4
set available_versions=!available_versions!,!tempvar:_= !
)

if not %5.==. (
call :aux %5
set available_versions=!available_versions!,!tempvar:_= !
)

if not %6.==. (
call :aux %6
set available_versions=!available_versions!,!tempvar:_= !
)

echo !available_versions!
goto :eof

:aux
call set tempvar=%1
goto :eof







