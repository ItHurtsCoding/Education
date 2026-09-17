import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def main():
    print("=== Обучение второй ML-модели (Классификация) ===")
    
    # 1. Загрузка данных
    df = pd.read_csv('data/ds_vacancies_analysis_cleaned.csv')
    df = df.dropna(subset=['salary_num'])
    
    # 2. Переход от Регрессии к Классификации: создаем категории (low, medium, high)
    # Определим границы:
    # Меньше 150 000 руб -> Low
    # От 150 000 до 220 000 руб -> Medium
    # Выше 220 000 руб -> High
    def categorize_salary(salary):
        if salary < 150000:
            return 'Low'
        elif salary <= 220000:
            return 'Medium'
        else:
            return 'High'
            
    df['salary_class'] = df['salary_num'].apply(categorize_salary)
    
    print("\nРаспределение классов:")
    print(df['salary_class'].value_counts())
    
    # 3. Подготовка признаков (X) и целевой переменной (y)
    X = df[['req_len', 'is_remote']]
    y = df['salary_class']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Обучение модели Классификации (Случайный лес для классификации)
    print("\n[Модель] Обучение Random Forest Classifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # 5. Предсказание и оценка
    preds = clf.predict(X_test)
    
    # Для классификации главная базовая метрика - Accuracy (доля правильных ответов)
    acc = accuracy_score(y_test, preds)
    print(f"\nAccuracy (Точность): {acc:.2%}")
    
    print("\n--- Автоматический Анализ Результатов (от Senior DS) ---")
    num_classes = len(df['salary_class'].unique())
    random_guess_acc = 1 / num_classes
    
    print(f"Базовая точность случайного угадывания для {num_classes} классов: {random_guess_acc:.2%}")
    if acc <= random_guess_acc + 0.05:
        print("ВЫВОД: Точность модели практически равна случайному угадыванию.")
        print("ПРИЧИНА: Зарплаты были сгенерированы синтетически (np.random) на этапе предобработки.")
        print("ЗАКЛЮЧЕНИЕ: Алгоритм блестяще доказал принцип 'Garbage In -> Garbage Out'. Реальной связи между навыками и случайной зарплатой нет!")
    else:
        print("ВЫВОД: Модель нашла реальные закономерности в данных! Результат выше случайного угадывания.")
    
    # Детальный отчет (Precision, Recall, F1-score)
    print("\nДетальный отчет по классами (Classification Report):")
    print(classification_report(y_test, preds, zero_division=0))
    
    # =========================================================================
    # ВИЗУАЛИЗАЦИЯ (График: Классы зарплат vs Количество требований)
    # =========================================================================
    plt.figure(figsize=(10, 6))
    
    # Используем boxplot (ящик с усами), чтобы показать распределение req_len для каждого класса
    sns.boxplot(x='salary_class', y='req_len', data=df, order=['Low', 'Medium', 'High'], palette='Set2')
    
    # Наложим сами точки сверху (swarmplot) для наглядности
    sns.stripplot(x='salary_class', y='req_len', data=df, order=['Low', 'Medium', 'High'], color=".25", alpha=0.5)
    
    plt.title('Распределение количества требований (req_len) по классам зарплат', fontsize=14)
    plt.xlabel('Класс зарплаты', fontsize=12)
    plt.ylabel('Количество требований (req_len)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.4, axis='y')
    
    os.makedirs('plots', exist_ok=True)
    plt.savefig('plots/req_len_vs_salary_class.png')
    print("\nГрафик сохранен: plots/req_len_vs_salary_class.png")
    plt.close()

if __name__ == "__main__":
    main()
