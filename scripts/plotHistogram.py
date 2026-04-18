import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
  if len(sys.argv) < 3:
    print("Erro: Você deve passar o caminho do arquivo CSV e o nome da variável como entradas.")
    print("Exemplo: plotHistogram.py subset.csv et")
    sys.exit(1)

  csvPath = sys.argv[1]
  variavel = sys.argv[2]

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
  
  if variavel == 'avgmu':
    coluna = "EventInfoContainer.avgmu"
  else:
    coluna = f"TrigEMClusterContainer.{variavel}"

  if coluna not in df.columns:
    print(f"Erro: A coluna para '{variavel}' não foi encontrada no CSV.")
    sys.exit(1)

  latexLabels = {
    'et': r'$E_T$',
    'eta': r'$\eta$',
    'phi': r'$\phi$',
    'avgmu': r'$\langle\mu\rangle$'
  }

  unidades = {
    'et': ' [MeV]', 
    'eta': '',
    'phi': ' [rad]',
    'avgmu': ''
  }

  label = latexLabels.get(variavel, variavel)
  unidade = unidades.get(variavel, '')

  fig, ax = plt.subplots(figsize=(8, 6))
  df[coluna].hist(
    ax=ax, 
    bins=30,
    color='#4C72B0',
    edgecolor='black',
    linewidth=1.2,
    alpha=0.85
  )

  ax.set_title(f'Distribuição de {label}', fontsize=16, fontweight='bold', pad=15)
  ax.set_xlabel(f'{label}{unidade}', fontsize=16, labelpad=10)

  if variavel == 'et':
    ax.set_yscale('log')
    ax.set_ylabel('Frequência (Log)', fontsize=14, labelpad=10)
  else:
    ax.set_ylabel('Frequência', fontsize=14, labelpad=10)

  if variavel == 'phi':
    ax.set_xticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
    ax.set_xticklabels([r'$-\pi$', r'$-\frac{\pi}{2}$', r'$0$', r'$\frac{\pi}{2}$', r'$\pi$'])

  ax.tick_params(axis='both', which='major', labelsize=12)

  ax.grid(False)
  ax.grid(axis='y', linestyle='--', alpha=0.5)
  ax.set_axisbelow(True)

  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['left'].set_linewidth(1.2)
  ax.spines['bottom'].set_linewidth(1.2)

  cleanCSVPath = os.path.splitext(csvPath)[0]
  outputFilename = f"histograma_{cleanCSVPath}_{variavel}.png"
  plt.savefig(outputFilename, bbox_inches='tight', dpi=300)

if __name__ == "__main__":
  main()
