import sqlite3
import pandas as pd
mensagens = []
conn = sqlite3.connect("sqforecasts.db") # Conectar ao banco de dados SQLite
query = "SELECT id_titulos, symbol, url FROM tbtitulos" # Criar a consulta SQL
dftitulos = pd.read_sql(query, conn) # Criar o DataFrame com os dados da consulta
conn.close()# Fechar a conexão


from fore_import_sql import fore_import
mensagens = []
for _, row in dftitulos.iterrows():  # Itera sobre as linhas do DataFrame
    id_especifico = row["id_titulos"]    
    msj = fore_import (dftitulos,id_especifico)
    mensagens.append(msj)

import tkinter as tk
from tkinter import messagebox
import os
from datetime import datetime

def mostrar_mensagens(mensagens):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Mensagens do Dia", "\n".join(mensagens))
    root.destroy()

# Caminho do arquivo de cache (Windows)
cache_file = os.path.join(os.environ['TEMP'], 'msg_diaria_cache.txt')
hoje = datetime.now().strftime("%Y-%m-%d")

# Verificar se já foi executado hoje
try:
    with open(cache_file, "r") as f:
        ultima_execucao = f.read()
    if ultima_execucao == hoje:
        exit()
except FileNotFoundError:
    pass

# Obter e mostrar mensagens

if mensagens:
    mostrar_mensagens(mensagens)

# Registrar execução
with open(cache_file, "w") as f:
    f.write(hoje)