import sys
import os
import ast
import pandas as pd
import matplotlib.pyplot as plt
from printDataframe import dataframeFromArgs

RING_COUNT = 20

def extrairLista(valorStr):
  if pd.isna(valorStr): return None
  if isinstance(valorStr, str):
    valorStr = valorStr.strip()
    try:
      return ast.literal_eval(valorStr)
    except:
      return None
  return valorStr

def main():
  if len(sys.argv) < 2:
    print("Erro: Você deve passar o caminho do CSV.")
    print("Exemplo: python plotBoxplotGlobais.py subset.csv 0")
    print("Para fazer o boxplot dos primeiros 20 anéis")
    sys.exit(1)

  csvPath = sys.argv[1]

  startRing = 0
  if len(sys.argv) >= 3:
    try:
      startRing = int(sys.argv[2])
    except ValueError:
        print("Erro: O argumento de anel inicial deve ser um número inteiro.")
        sys.exit(1)

  df = dataframeFromArgs(1)

  listas_aneis = df['TrigEMClusterContainer.ringsE'].apply(extrairLista).dropna()

  df_aneis = pd.DataFrame(listas_aneis.tolist()).iloc[:, startRing : startRing + RING_COUNT]
  actualCount = df_aneis.shape[1]
  
  df_aneis.columns = [rf'$E_{{{i}}}$' for i in range(startRing, startRing + actualCount)]

  plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.titlesize": 18,
    "axes.labelsize": 16,                    
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 12,
    "axes.linewidth": 1.2
  })

  fig, ax = plt.subplots(figsize=(12, 6))

  boxprops = dict(linestyle='-', linewidth=1.5, color='#0033A0')     # Borda azul
  medianprops = dict(linestyle='-', linewidth=2, color='#E15E32')    # Mediana laranja 
  whiskerprops = dict(linestyle='-', linewidth=1.2, color='#2F2F2F') # Fios pretos
  capprops = dict(linestyle='-', linewidth=1.2, color='#2F2F2F')     # Tampas pretas
  flierprops = dict(marker='.', markerfacecolor='gray', markersize=3, alpha=0.2, markeredgecolor='none') # Outliers cinzas

  bplot = df_aneis.boxplot(
    ax=ax,
    grid=False,
    boxprops=boxprops,
    medianprops=medianprops,
    whiskerprops=whiskerprops,
    capprops=capprops,
    flierprops=flierprops,
    patch_artist=True,
    return_type='dict'
  )

  for patch in bplot['boxes']:
    patch.set_facecolor('#61C5D3')
    patch.set_alpha(0.8)

  ax.set_title(r'\textbf{Distribuição Global de Energia}', pad=15)
  ax.set_xlabel(r'\textbf{Anel do Calorímetro}', labelpad=10)
  ax.set_ylabel(r'\textbf{Energia [MeV] (Log)}', labelpad=10)

  ax.set_yscale('symlog', linthresh=10.0)

  ax.tick_params(axis='both', which='major', labelsize=12)

  for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_linewidth(1.2)
  
  ax.grid(axis='y', linestyle='--', alpha=0.5)
  ax.set_axisbelow(True)

  cleanCSVPath = os.path.splitext(csvPath)[0]
  baseName = os.path.basename(cleanCSVPath)
  endRing = startRing + actualCount - 1
  outputFilename = f"boxplot_aneis_{baseName}_{startRing}-{endRing}.png"

  plt.savefig(outputFilename, bbox_inches='tight', dpi=300)

if __name__ == "__main__":
    main()
