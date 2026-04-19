# Código para Missões de Onboarding do LPS

Este repositório contém scripts em Python desenvolvidos para processar, analisar e visualizar dados de eventos do calorímetro.

## 📂 Estrutura do Repositório

Os principais scripts de análise e visualização encontram-se no diretório `scripts/`:

* **`plotHistogram.py`**: Gera histogramas estilizados para variáveis globais do evento e métricas do cluster (`et`, `eta`, `phi`, `avgmu`).
* **`plotHistogramaAnel.py`**: Isola os dados de listas e plota a distribuição de energia depositada em um anel específico do calorímetro.
* **`boxplotAneis.py`**: Cria um boxplot em escala logarítmica comparando a distribuição global de energia ao longo de até 20 anéis do calorímetro.
* **`printDataframe.py`**: Imprime o DataFrame no terminal.

## ⚙️ Como Usar

Os scripts foram projetados para operar via linha de comando (CLI), exigindo o caminho do arquivo CSV de dados como entrada principal.

### 1. Imprimir Dataframe no Terminal: 
Para imprimir os dados no terminal:
```bash
python scripts/printDataframe.py subset.csv
```

### 2. Plotar Histograma das variáveis cinemáticas principais 
Para gerar o histograma de uma variável como o ângulo azimutal ($\phi$):
```bash
python scripts/plotHistogram.py subset.csv phi
```
*Variáveis suportadas:* `et`, `eta`, `phi`, `avgmu`.

### 3. Plotar Energia de um Anel
Para visualizar a energia do Anel 0 (o mais interno):
```bash
python scripts/plotHistogramaAnel.py subset.csv 0
```

### 4. Visualizar Boxplot Global
Para gerar a visão comparativa dos 20 primeiros anéis:
```bash
python scripts/boxplotAneis.py subset.csv
```
