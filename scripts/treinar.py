import sys
import pandas as pd
import numpy as np

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras import backend as K
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import confusion_matrix, roc_curve, auc
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams.update({
  "text.usetex": True,
  "font.family": "serif",
  "font.serif": ["Computer Modern Roman"],
  "axes.titlesize": 16,
  "axes.labelsize": 14,
  "xtick.labelsize": 12,
  "ytick.labelsize": 12
})


EPOCHS=2000

def carregarDados(caminhoArquivo):
  df = pd.read_parquet(caminhoArquivo)
  
  X = df.drop(columns=['target']).values
  y = df['target'].values
  
  X_trainVal, X_test, y_trainVal, y_test = train_test_split(
    X, y, 
    test_size=0.20, 
    stratify=y, 
    random_state=42
  )
  
  return X_trainVal, X_test, y_trainVal, y_test

def calcularPesosDeClasse(y_train):
  classes = np.unique(y_train)
  
  pesos = compute_class_weight(class_weight='balanced', classes=classes, y=y_train)
  
  dicionario_pesos = {classe: peso for classe, peso in zip(classes, pesos)}
  
  return dicionario_pesos

def criarModelo(dimensaoEntrada):
  modelo = Sequential([
    Input(shape=(dimensaoEntrada,)),
    Dense(5,  activation='relu', name='Camada_Oculta'),
    Dense(1, activation='sigmoid', name='Camada_Saida')
  ])
  
  modelo.compile(
    optimizer='adam', 
    loss='binary_crossentropy', 
    metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
  )
  
  return modelo

def treinarSemKFold(X_tv, y_tv):
  X_train, X_val, y_train, y_val = train_test_split(
    X_tv, y_tv, 
    test_size=0.25, 
    stratify=y_tv, 
    random_state=42
  )
  
  modelo = criarModelo(dimensaoEntrada=X_train.shape[1])
  
  earlyStop = EarlyStopping(
    monitor='val_loss', 
    patience=60, 
    restore_best_weights=True,
    verbose=0
  )
  
  reduceLR = ReduceLROnPlateau(
    monitor='val_loss', 
    factor=0.5,
    patience=20,
    min_lr=1e-6,
    verbose=0
  )

  pesos_classes = calcularPesosDeClasse(y_train)
  print(f"Pesos Aplicados (KFold): {pesos_classes}")
  
  history = modelo.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    batch_size=128,
    callbacks=[earlyStop, reduceLR],
    class_weight=pesos_classes,
    verbose=0
  )
  
  melhorLoss = min(history.history['val_loss'])
  melhorAUC = max(history.history['val_auc'])
  # print(f"-> Treinamento Sem KFold finalizado | Melhor Loss: {melhorLoss:.4f} | Melhor AUC: {melhorAUC:.4f}")
  
  return history, modelo

def treinarKFold(X_tv, y_tv):
  kfold = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)
  
  historicos = []
  modelos = []

  melhoresLosses = []
  melhoresAUCs = []
  
  for fold, (trainIndex, valIndex) in enumerate(kfold.split(X_tv, y_tv), start=1):
    # print(f"\n[ Fold {fold}/4 ]")
    
    X_train, X_val = X_tv[trainIndex], X_tv[valIndex]
    y_train, y_val = y_tv[trainIndex], y_tv[valIndex]
    
    modelo = criarModelo(dimensaoEntrada=X_train.shape[1])
    
    earlyStop = EarlyStopping(
      monitor='val_loss', 
      patience=60, 
      restore_best_weights=True,
      verbose=0
    )

    reduceLR = ReduceLROnPlateau(
      monitor='val_loss', 
      factor=0.5,
      patience=20,
      min_lr=1e-6,
      verbose=0
    )                                

    pesos_classes = calcularPesosDeClasse(y_train)

    historico = modelo.fit(
      X_train, y_train,
      validation_data=(X_val, y_val),
      epochs=EPOCHS,
      batch_size=128,
      callbacks=[earlyStop, reduceLR],
      class_weight=pesos_classes,
      verbose=0
    )
    
    historicos.append(historico)
    modelos.append(modelo)
    
    melhorLoss = min(historico.history['val_loss'])
    melhorAUC = max(historico.history['val_auc'])
    
    melhoresLosses.append(melhorLoss)
    melhoresAUCs.append(melhorAUC)

    # print(f"-> Fold {fold} finalizado | Melhor Loss: {melhorLoss:.4f} | Melhor AUC: {melhorAUC:.4f}")

  mediaLoss = np.mean(melhoresLosses)
  stdLoss = np.std(melhoresLosses)
  mediaAUC = np.mean(melhoresAUCs)
  stdAUC = np.std(melhoresAUCs)
  
  print("-> K-Fold (4 Folds):")
  print(f"  Loss: {mediaLoss:.4f} ± {stdLoss:.4f}")
  print(f"  AUC:  {mediaAUC:.4f} ± {stdAUC:.4f}")
      
  return historicos, modelos

def plotarMetricas(history, modelo, X_test, y_test,nomeSubset):
  destino = f"graficos/{nomeSubset}"
  os.makedirs(destino, exist_ok=True)

  # ---------------------------------------------------------
  # 1. Curva de Loss (Treino vs Validação)
  # ---------------------------------------------------------
  plt.figure(figsize=(10, 6))
  plt.plot(history.history['loss'], label='Treino', linewidth=2)
  plt.plot(history.history['val_loss'], label='Validação', linewidth=2)
  plt.title(r'\textbf{Curva de Aprendizado (Loss)}', pad=20)
  plt.xlabel('Épocas')
  plt.ylabel('Loss')
  plt.ylim(0, np.mean(history.history['val_loss']) + 1)
  plt.legend()
  plt.grid(True, linestyle='--', alpha=0.7)
  plt.tight_layout()
  plt.savefig(f"{destino}/curvaLoss.png", dpi=300)
  plt.close()
  
  y_pred_prob = modelo.predict(X_test, verbose=0).ravel()

  fpr, tpr, thresholds = roc_curve(y_test, y_pred_prob)
  idx = np.argmax(tpr >= 0.95)
    
  limiar_dinamico = thresholds[idx]
  fa_dinamico = fpr[idx]
  pd_dinamico = tpr[idx]
  
  # ---------------------------------------------------------
  # 2. Curva ROC
  # ---------------------------------------------------------
  roc_auc = auc(fpr, tpr)
  
  plt.figure(figsize=(8, 8))
  plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'Curva ROC (AUC = {roc_auc:.4f})')
  plt.fill_between(fpr, tpr, color='darkorange', alpha=0.2)
  plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Chute Aleatório')
  plt.scatter([fa_dinamico], [pd_dinamico], color='red', s=100, zorder=5, 
    label=f'Ponto de Operação (PD={pd_dinamico*100:.1f}%)')
  plt.xlim([0.0, 1.0])
  plt.ylim([0.0, 1.05])
  plt.xlabel('Taxa de Falsos Positivos')
  plt.ylabel('Taxa de Verdadeiros Positivos')
  plt.title(r'\textbf{Curva ROC}', pad=20)
  plt.legend(loc="lower right")
  plt.grid(True, linestyle='--', alpha=0.7)
  plt.tight_layout()
  plt.savefig(f"{destino}/curvaROC.png", dpi=300)
  plt.close()

  # ---------------------------------------------------------
  # 2. Matriz de Confusão
  # ---------------------------------------------------------

  y_pred_classes = (y_pred_prob > limiar_dinamico).astype(int)
  cm = confusion_matrix(y_test, y_pred_classes)
  
  plt.figure(figsize=(8, 6))
  sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
    xticklabels=['Ruído (0)', 'Sinal (1)'], 
    yticklabels=['Ruído (0)', 'Sinal (1)'],
    annot_kws={"size": 16})
  plt.title(r'\textbf{Matriz de Confusão}', pad=20)
  plt.ylabel('Classe Real')
  plt.xlabel('Previsão do Modelo')
  plt.tight_layout()
  plt.savefig(f"{destino}/matrizConfusao.png", dpi=300)
  plt.close()
  # ---------------------------------------------------------
    
  TrueNegative, FalsePositive, FalseNegative, TruePositive = cm.ravel()
  
  PD = TruePositive / (TruePositive + FalseNegative) if (TruePositive + FalseNegative) > 0 else 0.0
  FA = FalsePositive / (FalsePositive + TrueNegative) if (FalsePositive + TrueNegative) > 0 else 0.0
  
  print(f"-> Métricas do Conjunto de Teste ({nomeSubset}):")
  print(f"   PD (Prob. de Detecção):    {PD * 100:.2f}%")
  print(f"   FA (Prob. de Falso Alarme): {FA * 100:.2f}%")
  print(f"   AUC (Área sob a Curva):    {roc_auc:.4f}")

def main():
  if len(sys.argv) < 2:
    pastaDados = "dadosPorRegiao"

    if not os.path.exists(pastaDados):
        print(f"Erro: A pasta '{pastaDados}' não foi encontrada.")
        sys.exit(1)
        
    arquivos = [os.path.join(pastaDados, f) for f in os.listdir(pastaDados) if f.endswith('.parquet')]
    
    if not arquivos:
      print(f"Erro: Não foi encontrado nenhum arquivo .parquet na pasta '{pastaDados}'.")
      sys.exit(1)
        
  else:
    arquivos = [sys.argv[1]]

  for caminhoArquivo in arquivos:
    nomeSubset = os.path.basename(caminhoArquivo).replace('.parquet', '')
      
    print("\n" + "="*60)
    print(f" Iniciando Processamento da Região: {nomeSubset} ")
    print("="*60)
    
    X_trainVal, X_test, y_trainVal, y_test = carregarDados(caminhoArquivo)
    
    historicoSemKFold, modeloSemKFold = treinarSemKFold(X_trainVal, y_trainVal)
    
    historicoKFold, modelosKFold = treinarKFold(X_trainVal, y_trainVal)
      
    plotarMetricas(historicoSemKFold, modeloSemKFold, X_test, y_test, nomeSubset)

    K.clear_session()
  
if __name__ == "__main__":
    main()
