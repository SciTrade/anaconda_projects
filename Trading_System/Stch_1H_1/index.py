#Index_sc, Index, Trade calculation
# Indexes calculation
def index_calculation (dfsignals, comission):   # Columns datetime	open	high	low	close	volume	state
    df = dfsignals
    df ["index_sc"] = 100. 
    df ["trade"] = 0.
    df ["index"] = 100. *(1-comission) 
    for i in range(1, len(df)):      
                       
        if  df.loc[i, "state"] == "out" :
            df.loc[i, "index_sc"] = (((df.loc[i,"close"]-df.loc[i-1,"close"])/df.loc[i-1,"close"])+1)* df.loc[i-1,"index_sc"]
            df.loc[i, "index"] = df.loc[i, "index_sc"]* (1-comission)
            df.loc[i, "trade"] = (df.loc[i,"close"]-df.loc[i-1,"close"])/df.loc[i-1,"close"]
            
        if  df.loc[i, "state"] == "enter" :        
            df.loc[i, "index_sc"] =  df.loc[i-1, "index_sc"]
            df.loc[i, "index"] = df.loc[i, "index_sc"]* (1-comission)
    dfindex = df
    return dfindex    #Columns : datetime	open	high	low	close	volume	state	index_sc	trade	index
    
