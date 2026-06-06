import sys
import pandas as pd
import numpy as np
from printDataframe import dataframeFromArgs

def main():
  if len(sys.argv) < 2:
    print("Erro: Você deve passar o caminho do arquivo de dados como entrada.")
    sys.exit(1)
  
  regioesEt = [0, 20, 30, 40, 50, 1000]
  regioesEta = [0.0, 1.375, 1.475, 2.5, 3.2]
  df = dataframeFromArgs(1, cols=['TrigEMClusterContainer.et'])
  
  
  etColumn = df['TrigEMClusterContainer.et'] 
  breaks = jenkspy.jenks_breaks(etColumn, n_classes = 5)
  df['segmento'] = pd.cut(etColumn, bins=breaks,include_lowest=True, labels=['R1', 'R2', 'R3', 'R4', 'R5'])

  dadosRegioes = df.groupby('segmento')['TrigEMClusterContainer.et'].agg(['mean', 'count'])
  
  print(dadosRegioes)

if __name__ == "__main__":
    main()
