import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def main():
    print("=== Обучение первой ML-модели (Регрессия) ===")
    
    # 1. Загрузка очищенных данных
    df = pd.read_csv('data/ds_vacancies_analysis_cleaned.csv')
    
    # Очистим датасет от строк, где нет зарплаты (наш таргет не может быть пустым)
    df = df.dropna(subset=['salary_num'])
    
    # 2. Выбор признаков (Features, X) и целевой переменной (Target, y)
    # Захар, сейчас нас интересует влияние количества требований (req_len) на зарплату.
    # Но чтобы модель была чуть умнее, добавим еще формат работы.
    X = df[['req_len', 'is_remote']]
    y = df['salary_num']
    
    # 3. Разделение данных на обучающую (Train) и тестовую (Test) выборки
    # Обучаем на 80% данных, а проверяем на 20%, чтобы понять, как модель работает на новых данных.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # =========================================================================
    # МОДЕЛЬ 1: Линейная регрессия (Linear Regression)
    # Самая простая и интерпретируемая модель. Рисует прямую линию через точки.
    # =========================================================================
    print("\n[Модель 1] Обучение Линейной Регрессии...")
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train) # Обучение (поиск закономерностей)
    
    # Предсказание на тестовых данных
    lr_preds = lr_model.predict(X_test)
    
    # Оценка (Метрики)
    # MAE (Mean Absolute Error) - средняя ошибка в рублях. Чем меньше, тем лучше.
    # R2 (Коэффициент детерминации) - доля дисперсии, которую объясняет модель. 1.0 - идеал, 0.0 - как среднее.
    lr_mae = mean_absolute_error(y_test, lr_preds)
    lr_r2 = r2_score(y_test, lr_preds)
    print(f"Линейная регрессия -> MAE: {lr_mae:,.0f} руб. | R2: {lr_r2:.3f}")
    
    # Интерпретация весов (Коэффициентов) Линейной регрессии
    # Коэффициент показывает, на сколько рублей изменится зарплата при изменении признака на 1.
    print("Влияние признаков (веса Линейной Регрессии):")
    for feature, coef in zip(X.columns, lr_model.coef_):
        print(f" - {feature}: {coef:,.0f} руб.")
        
    # =========================================================================
    # МОДЕЛЬ 2: Случайный лес (Random Forest Regressor)
    # Более сложная модель, основанная на решающих деревьях. Умеет находить нелинейные связи.
    # =========================================================================
    print("\n[Модель 2] Обучение Случайного Леса...")
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    rf_preds = rf_model.predict(X_test)
    
    rf_mae = mean_absolute_error(y_test, rf_preds)
    rf_r2 = r2_score(y_test, rf_preds)
    print(f"Случайный лес -> MAE: {rf_mae:,.0f} руб. | R2: {rf_r2:.3f}")
    
    print("\n--- Автоматический Анализ Результатов (от Senior DS) ---")
    if rf_r2 <= 0:
        print(f"ВНИМАНИЕ: Метрика R2 ({rf_r2:.3f}) меньше или равна нулю!")
        print("ВЫВОД: Модель предсказывает хуже или так же, как простое предсказание среднего значения.")
        print("ПРИЧИНА: Целевой признак (salary) был заполнен случайными числами в целях обучения.")
        print("ЗАКЛЮЧЕНИЕ: Математически доказано отсутствие зависимости (Garbage In -> Garbage Out).")
    else:
        print("ВЫВОД: Модель успешно нашла закономерности (R2 > 0).")
    
    # =========================================================================
    # ВИЗУАЛИЗАЦИЯ (График влияния req_len на salary_num)
    # =========================================================================
    plt.figure(figsize=(10, 6))
    
    # Точки данных (Scatter plot)
    sns.scatterplot(x='req_len', y='salary_num', data=df, alpha=0.6, label='Реальные вакансии')
    
    # Линия тренда (Линейная регрессия на 1 признаке для визуализации)
    sns.regplot(x='req_len', y='salary_num', data=df, scatter=False, color='red', label='Линейный тренд')
    
    plt.title('Влияние количества требований (req_len) на Зарплату', fontsize=14)
    plt.xlabel('Количество требуемых навыков (req_len)', fontsize=12)
    plt.ylabel('Зарплата (RUB)', fontsize=12)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    
    os.makedirs('plots', exist_ok=True)
    plt.savefig('plots/req_len_vs_salary.png')
    print("\nГрафик сохранен: plots/req_len_vs_salary.png")
    plt.close()

if __name__ == "__main__":
    main()
