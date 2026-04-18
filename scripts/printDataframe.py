import sys
import pandas as pd

def dataframeFromArgs(indice):
  csvPath = sys.argv[indice]

  try: 
    df = pd.read_csv(csvPath)
  except FileNotFoundError:
    print(f"Erro: Arquivo não encontrado no caminho '{csvPath}'.")
    sys.exit(1)
  except pd.errors.EmptyDataError:
    print("Erro: O arquivo CSV fornecido está vazio.")
    sys.exit(1)
  except Exception as e:
    print(f"Erro inesperado ao ler o CSV: {e}")
    sys.exit(1)
  
  return df


def main():
  if len(sys.argv) < 2:
    print("Erro: Você deve passar o caminho do arquivo CSV como entrada.")
    sys.exit(1)

  df = dataframeFromArgs(1)
  
  print(df)

if __name__ == "__main__":
    main()
