import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from printDataframe import dataframeFromArgs

plt.rcParams.update({
  "text.usetex": True,
  "font.family": "serif",
  "font.serif": ["Computer Modern Roman"],
  "axes.titlesize": 16,
  "axes.labelsize": 14,
  "xtick.labelsize": 12,
  "ytick.labelsize": 12
})

def preProcessarDados(df):
  rings_df = df['TrigEMClusterContainer.ringsE'].str.strip('[]').str.split(',', expand=True)
  rings_df.columns = [f'ring_{i}' for i in range(rings_df.shape[1])]
  rings_df = rings_df.astype(float)
  
  soma_aneis = rings_df.sum(axis=1)
  soma_aneis = soma_aneis.replace(0, 1)

  rings_df = rings_df.div(soma_aneis, axis=0)
  df = pd.concat([df, rings_df], axis=1)

  df = df.drop(columns=['TrigEMClusterContainer.ringsE'])

  return df.copy()

def segmentarDados(df):
  regioesEt = [x * 1000 for x in [0, 20, 30, 40, 50, 1000]] 
  regioesEta = [0.0, 0.8, 1.37, 1.54, 2.37, 2.50]
  
  labels_et = [r'$E_T \leq 20$', r'$20 < E_T \leq 30$', r'$30 < E_T \leq 40$', r'$40 < E_T \leq 50$', r'$E_T > 50$']
  labels_eta = [r'$0.00 < |\eta| \leq 0.80$', r'$0.80 < |\eta| \leq 1.37$', r'$1.37 < |\eta| \leq 1.54$', r'$1.54 < |\eta| \leq 2.37$', r'$2.37 < |\eta| \leq 2.50$']

  df['abs_eta'] = df['TrigEMClusterContainer.eta'].abs()
  
  df['et_region'] = pd.cut(df['TrigEMClusterContainer.et'], bins=regioesEt, labels=labels_et)
  df['eta_region'] = pd.cut(df['abs_eta'], bins=regioesEta, labels=labels_eta)

  return df

def gerarTabela(df):
  tabela = df.groupby(['eta_region', 'et_region'], observed=False).agg(
      Ruido=('target', lambda x: (x == 0).sum()),
      Sinal=('target', lambda x: (x == 1).sum()),
  ).fillna(0).astype(int)

  tabela['Total'] = tabela['Ruido'] + tabela['Sinal']
  tabela['% Ruido'] = (tabela['Ruido'] / tabela['Total'] * 100).round(1)
  tabela['% Sinal'] = (tabela['Sinal'] / tabela['Total'] * 100).round(1)
  
  return tabela

def plotarHeatmap(tabela):
  heatmap_data = tabela['% Sinal'].unstack(level='et_region')
  
  plt.figure(figsize=(16, 9))
  
  ax = sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="RdYlBu_r", 
                   cbar_kws={'label': r'Porcentagem de Sinal (\%)'},
                   linewidths=.5, annot_kws={"size": 20})
  
  plt.title(r'\textbf{Concentração Relativa de Sinal por Região}', pad=25, fontsize=24)
  plt.xlabel(r'Região de $E_T$ [GeV]', fontsize = 20)
  plt.ylabel(r'Região de $|\eta|$', fontsize = 20)
  
  plt.xticks(rotation=0, fontsize=16)
  plt.yticks(rotation=0, fontsize=16)

  cbar = ax.collections[0].colorbar
  cbar.ax.yaxis.label.set_size(24)
  cbar.ax.tick_params(labelsize=18)

  plt.tight_layout()

  plt.savefig("heatmap.png", bbox_inches='tight', dpi=300, transparent=True)

def salvarSegmentoes(df):
  pastaSaida = "dadosPorRegiao"
  os.makedirs(pastaSaida, exist_ok=True)
  
  categorias_eta = df['eta_region'].cat.categories
  categorias_et = df['et_region'].cat.categories
  
  for i, cat_eta in enumerate(categorias_eta, start=1):
    for j, cat_et in enumerate(categorias_et, start=1):
      
      dfSubset = df[(df['eta_region'] == cat_eta) & (df['et_region'] == cat_et)]
      
      if not dfSubset.empty:
        dfSubset = dfSubset.drop(columns=['et_region', 'eta_region', 'abs_eta'])
        
        nomeArquivo = f"{pastaSaida}/subset{i}{j}.parquet"
        dfSubset.to_parquet(nomeArquivo, index=False)
              

def main():
    if len(sys.argv) < 2:
      print("Erro: Você deve passar o caminho do arquivo de dados como entrada.")
      sys.exit(1)
        
    colunas_necessarias = [
      'TrigEMClusterContainer.et', 
      'TrigEMClusterContainer.eta', 
      'TrigEMClusterContainer.ringsE', 
      'target'
    ]
    
    df = dataframeFromArgs(1, cols=colunas_necessarias)
    
    dfProcessado = preProcessarDados(df)
    
    dfSegmentado = segmentarDados(dfProcessado)
    
    """
    tabela_agregada = gerarTabela(dfSegmentado)

    print("\n" + "="*75)
    print("Resumo Estatístico por Região (Contagens e Proporções):")
    print("="*75)
    print(tabela_agregada)
    print("="*75 + "\n")
    
    plotarHeatmap(tabela_agregada)
    """

    salvarSegmentoes(dfSegmentado)

if __name__ == "__main__":
    main()
