import pandas as pd

                    #  Gera parametros e lista do almacenamento de metricas

def parametros (dfparamtest,il) :
    #Cria os parametros para os scripts     
    # System parameters
    # stoch_hml_1
    K = dfparamtest.loc[il,'K']
    D = dfparamtest.loc[il,'D']
    smoth = dfparamtest.loc[il,'smoth']
    medM = (dfparamtest.loc[il,'medM'])
    lowM = (dfparamtest.loc[il,'lowM'])
    
    # Backtesting parameters
    
    stpl = dfparamtest.loc[il,'stpl']
    comission = dfparamtest.loc[il,'comission']
    drawmax = dfparamtest.loc[il,'drawmax']

    #cria lista lsmetricas para almacenar as metricas
    # guarda na lista 
    lsmetricas = []
    srparamtest = dfparamtest.loc[il]
    lsmetricas.append(srparamtest)
    return K,D, smoth, medM, lowM, stpl, comission, drawmax, lsmetricas 



                        # gera um novo registro no df dfmetricas

def atualizar_df_metricas(dfmetricas, lsmetricas):
    """
    Adiciona uma linha ao DataFrame dfmetricas com os valores de lsmetricas.
    Se dfmetricas for None, cria o DataFrame com a estrutura das métricas.

    Parâmetros:
    - dfmetricas: pd.DataFrame ou None
    - lsmetricas: list de pd.Series

    Retorna:
    - pd.DataFrame atualizado
    """

    linha = pd.concat(lsmetricas)  # Une todas as Series em uma só

    if dfmetricas is None:
        # Cria o DataFrame com uma única linha
        dfmetricas = pd.DataFrame([linha.values], columns=linha.index)
    else:
        # Adiciona nova linha ao DataFrame existente
        dfmetricas.loc[len(dfmetricas)] = linha.values

    return dfmetricas
