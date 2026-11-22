@echo off
echo ========================================
echo   ASSISTENTE CORPORATIVO DESKTOP
echo   Iniciando aplicacao...
echo ========================================
echo.

REM Verifica se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale Python 3.10+ e tente novamente.
    pause
    exit /b 1
)

REM Verifica se o arquivo principal existe
if not exist "main.py" (
    echo ERRO: main.py nao encontrado!
    echo Execute este arquivo no diretorio do projeto.
    pause
    exit /b 1
)

REM Verifica se as dependencias estao instaladas
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo AVISO: Dependencias nao instaladas.
    echo Instalando automaticamente...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERRO: Falha ao instalar dependencias.
        pause
        exit /b 1
    )
)

REM Verifica se o modelo NLP existe
if not exist "data\model\all-MiniLM-L6-v2" (
    echo AVISO: Modelo NLP nao encontrado.
    echo Executando download automatico...
    python download_model.py
    if errorlevel 1 (
        echo ERRO: Falha ao baixar modelo.
        echo Execute manualmente: python download_model.py
        pause
        exit /b 1
    )
)

echo Iniciando Assistente Corporativo...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo ERRO: Aplicacao encerrada com erro.
    pause
)

echo.
echo Aplicacao encerrada.
pause