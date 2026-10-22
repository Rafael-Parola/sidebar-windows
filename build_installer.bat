@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo        Sidebar Windows - Gerador de Instalador
echo ========================================================
echo.

:: 1. Verificar Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Python nao encontrado no PATH do sistema.
    pause
    exit /b 1
)

:: 2. Instalar dependencias e PyInstaller se necessario
echo [1/3] Verificando dependencias...
python -m pip install -r requirements.txt pyinstaller --quiet
if %ERRORLEVEL% neq 0 (
    echo [AVISO] Falha ao verificar dependencias via pip, tentando prosseguir...
)

:: 3. Compilar executavel com PyInstaller
echo [2/3] Compilando executavel Sidebar com PyInstaller...
python -m PyInstaller sidebar.spec --noconfirm
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Falha ao compilar com PyInstaller.
    pause
    exit /b 1
)

:: 4. Localizar Inno Setup Compiler (ISCC.exe)
echo [3/3] Gerando Instalador com Inno Setup...
set "ISCC_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
) else (
    where iscc >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set "ISCC_PATH=iscc"
    )
)

if "%ISCC_PATH%"=="" (
    echo [ERRO] Inno Setup 6 nao foi encontrado no sistema.
    echo Baixe e instale o Inno Setup 6 em: https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)

"%ISCC_PATH%" installer.iss
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Falha ao compilar o script installer.iss.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   [SUCESSO] Instalador gerado com sucesso!
echo   Arquivo: dist_installer\Sidebar_Setup_v1.0.0.exe
echo ========================================================
echo.
pause
