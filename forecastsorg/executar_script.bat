@echo off
REM Navega até o diretório do projeto
cd /d C:\Users\scitr\anaconda_projects\forecastsorg

REM Ativa o ambiente virtual
call venv\Scripts\activate.bat

REM Executa o script Python
pythonw.exe fore_import_msj.pyw

REM (Opcional) Desativa o ambiente ou aguarda o término
REM deactivate