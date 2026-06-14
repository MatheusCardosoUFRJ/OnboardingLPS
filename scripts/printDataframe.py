import sys
import pandas as pd
import numpy as np

def dataframeFromArgs(indice, cols=None):
  path = sys.argv[indice]

  try: 
    if path.endswith('.csv'):
      df = pd.read_csv(path, usecols=cols)
    elif path.endswith('.parquet'):
      df = pd.read_parquet(path, columns=cols)
    else:
      raise ValueError(f"formato de {path} não suportado")
  except FileNotFoundError:
    print(f"Erro: Arquivo não encontrado no caminho '{path}'.")
    sys.exit(1)
  except pd.errors.EmptyDataError:
    print("Erro: O arquivo de dados fornecido está vazio.")
    sys.exit(1)
  except Exception as e:
    print(f"Erro inesperado ao ler o arquivo de dados: {e}")
    sys.exit(1)
  
  return df


def main():
  if len(sys.argv) < 2:
    print("Erro: Você deve passar o caminho do arquivo de dados como entrada.")
    sys.exit(1)

  df = dataframeFromArgs(1)
  
  print(df)
  df.to_parquet("subset.parquet", index=False)

if __name__ == "__main__":
    main()
