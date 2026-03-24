import yfinance as yF
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor
from sklearn import linear_model
from sklearn.metrics import r2_score

import warnings
warnings.filterwarnings("ignore")

pd.options.display.float_format = '{:.2f}'.format

cotacoes = yF.Ticker("ITUB3.SA")
dados = cotacoes.history(period="5y")

dados.reset_index(inplace=True)

dados.drop(dados.tail(1).index, inplace=True)
dados.drop(['Dividends', 'Stock Splits'], axis=1, inplace=True)

dados.columns = ['Data','Abertura','Maximo','Minimo','Fechamento','Volume']

dados['mm5d'] = dados['Fechamento'].rolling(5).mean()
dados['mm14d'] = dados['Fechamento'].rolling(14).mean()
dados['mm21d'] = dados['Fechamento'].rolling(21).mean()

dados.dropna(inplace=True)

X = dados.drop(columns=['Data', 'Fechamento', 'Volume'])
y = dados['Fechamento']

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, shuffle=False
)

print(len(X_train), len(y_train))
print(len(X_test), len(y_test))

lr = linear_model.LinearRegression()
lr.fit(X_train, y_train)

pred_lr = lr.predict(X_test)
r2_lr = r2_score(y_test, pred_lr)

print(f"Regressão Linear R²: {r2_lr * 100:.2f}%")

rn = MLPRegressor(max_iter=2000)
rn.fit(X_train, y_train)

pred_rn = rn.predict(X_test)
r2_rn = r2_score(y_test, pred_rn)

print(f"MLPRegressor R²: {r2_rn * 100:.2f}%")

modelo_final = rn if r2_rn > r2_lr else lr

previsao = X_scaled[-20:]
datas = dados['Data'][-20:]
valores_reais = y[-20:]

pred_final = modelo_final.predict(previsao)

df = pd.DataFrame({
    'Data_Pregão': datas,
    'Real': valores_reais,
    'Previsão': pred_final
})

df.set_index('Data_Pregão', inplace=True)
print(df)

plt.figure(figsize=(16,8))
plt.title('Previsão de Preço das Ações')
plt.plot(df['Real'], label='Real')
plt.plot(df['Previsão'], label='Previsão', linestyle='--')
plt.xlabel('Data')
plt.ylabel('Preço de Fechamento')
plt.legend()
plt.savefig("images/grafico.png")
plt.show()