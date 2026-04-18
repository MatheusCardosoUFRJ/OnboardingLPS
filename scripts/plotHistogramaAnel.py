import sys
import os
import ast
import pandas as pd
from plotHistogram import plotHistogram
from printDataframe import dataframeFromArgs

def extrairAnel(valor_str, indiceAnel):
  if pd.isna(valor_str):
    return None
      
  if isinstance(valor_str, str):
    valor_str = valor_str.strip()
    try:
      lista = ast.literal_eval(valor_str)
    except:
      return None
  else:
    lista = valor_str
      
  if isinstance(lista, list) and len(lista) > indiceAnel:
    return lista[indiceAnel]
  return None


def main():
  if len(sys.argv) < 3:
    print("Erro: Você deve passar o caminho do CSV e o índice do anel como entradas.")
    print("Exemplo: plotHistogramaAnel.py subset.csv 0")
    sys.exit(1)

  csvPath = sys.argv[1]
  df = dataframeFromArgs(1)
  
  try:
    indiceAnel = int(sys.argv[2])
  except ValueError:
    print("Erro: O índice do anel deve ser um número inteiro (ex: 0 para o primeiro anel).")
    sys.exit(1)

  coluna = "TrigEMClusterContainer.ringsE"

  if coluna not in df.columns:
    print(f"Erro: A coluna '{coluna}' não foi encontrada no CSV.")
    sys.exit(1)

  dadosAnel = df[coluna].apply(lambda x: extrairAnel(x, indiceAnel)).dropna()

  if dadosAnel.empty:
    print(f"Erro: Não há dados para o anel {indiceAnel}")
    sys.exit(1)

  titulo = f'Distribuição de Energia depositada no Anel {indiceAnel}'
  label = rf'$E_{{{indiceAnel}}}$'

  cleanCSVPath = os.path.splitext(csvPath)[0]
  outputFilename = f"histograma_{cleanCSVPath}_anel{indiceAnel}.png"

  plotHistogram(label, ' [MeV]', dadosAnel, titulo, 
    outputFilename, True, False)

if __name__ == "__main__":
  main()
