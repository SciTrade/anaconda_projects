


# Insere na tbforecasts um novo registro
def insere_forecast(id_titulos, data):
    import sqlite3
    
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect("sqforecasts.db")
    cursor = conn.cursor()

    # Verificar se o registro já existe
    cursor.execute("SELECT COUNT(*) FROM tbforecasts WHERE id_titulos = ? AND data = ?", (id_titulos, str(data)))
    existsforecast = cursor.fetchone()[0]

    # Se não existir, inserir o novo registro
    if existsforecast == 0:
        cursor.execute("INSERT INTO tbforecasts (id_titulos, data) VALUES (?, ?)", (id_titulos, str(data)))
        conn.commit()
        print("Registro inserido com sucesso!")
        # Valor do id do registro inserido
        id_forecastins = cursor.lastrowid
    else:
        id_forecastins = 0
    # Fechar conexão
    conn.close()
    return id_forecastins,existsforecast

