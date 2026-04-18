import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from printDataframe import dataframeFromArgs

def plotHistogram(label, unidade, dados, titulo, filename, logy=False, piTicks=False):
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

  vmin = dados.quantile(0.005)
  vmax = dados.quantile(0.995)

  media = dados.mean()
  desvio = dados.std()
  
  textoEstatistica = '\n'.join((
    rf'\textbf{{Amostragens:}} {len(dados)}',
    rf'\textbf{{Média:}} {media:.2f}{unidade}',
    rf'\textbf{{Desvio:}} {desvio:.2f}{unidade}'
  ))

  fig, ax = plt.subplots(figsize=(8, 6))
  dados.hist(
    ax=ax, 
    bins=60,
    color='#61C5D3',
    edgecolor='white',
    linewidth=0.5,
    range=(vmin, vmax),
    alpha=0.9
  )

  propsCaixa = dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray')
  ax.text(0.95, 0.95, textoEstatistica, transform=ax.transAxes, fontsize=13,
    verticalalignment='top', 
    horizontalalignment='right', 
    multialignment='left',
    bbox=propsCaixa)

  ax.set_title(rf'\textbf{{{titulo}}}', pad=15)
  ax.set_xlabel(rf'{label}{unidade}', labelpad=10)

  if logy:
    ax.set_yscale('log')
    ax.set_ylabel(r'\textbf{Frequência (Log)}', labelpad=10)
  else:
    ax.set_ylabel(r'\textbf{Frequência}', labelpad=10)

  ax.axvline(media, color='#E15332', linestyle='--', linewidth=2, label='Média')

  if piTicks:
    ax.set_xticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
    ax.set_xticklabels([r'$-\pi$', r'$-\frac{\pi}{2}$', r'$0$', r'$\frac{\pi}{2}$', r'$\pi$'])

  ax.tick_params(axis='both', which='major', labelsize=12)

  ax.grid(False)
  ax.grid(axis='y', linestyle='--', alpha=0.5)
  ax.set_axisbelow(True)

  for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_linewidth(1.2)

  plt.savefig(filename, bbox_inches='tight', dpi=300)
  plt.close(fig)


def main():
  if len(sys.argv) < 3:
    print("Erro: Você deve passar o caminho do CSV e o nome da variável como entradas.")
    print("Exemplo: plotHistogram.py subset.csv et")
    sys.exit(1)

  csvPath = sys.argv[1]
  variavel = sys.argv[2]

  df = dataframeFromArgs(1)
  
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

  cleanCSVPath = os.path.splitext(csvPath)[0]
  outputFilename = f"histograma_{cleanCSVPath}_{variavel}.png"
  logy = variavel == 'et'
  piTicks = variavel == 'phi'

  plotHistogram(label, unidade, df[coluna], f"Distribuição de {label}", 
    outputFilename, logy, piTicks)

if __name__ == "__main__":
  main()
