import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LinearRegression

def custom_tokenizer(text):
    """
    Разбивает строку навыков по запятым и убирает лишние пробелы.
    Пример: "Python, SQL, PostgreSQL" -> ['python', 'sql', 'postgresql']
    """
    if pd.isna(text) or text == "Не указаны":
        return []
    return [word.strip().lower() for word in str(text).split(',')]

def main():
    print("=== NLP Анализ Навыков и Интерпретация Регрессии ===")
    
    # 1. Загрузка сырых данных (Хабр)
    file_path = 'data/raw/habr_real_ds.csv'
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл {file_path} не найден.")
        return
        
    df = pd.read_csv(file_path)
    print(f"Загружено {len(df)} вакансий.")
    
    os.makedirs('plots', exist_ok=True)
    
    # =========================================================================
    # ЧАСТЬ 1: NLP - One-Hot Encoding и Анализ популярных навыков (на всех 238 вакансиях)
    # =========================================================================
    print("\n[1] Проводим NLP анализ (CountVectorizer)...")
    # Используем CountVectorizer для создания матрицы навыков
    # Наш токенизатор просто разобьет строку по запятым
    cv = CountVectorizer(tokenizer=custom_tokenizer, token_pattern=None, lowercase=False)
    
    # Матрица, где строки - вакансии, а колонки - отдельные навыки (1 если есть, 0 если нет)
    skills_matrix = cv.fit_transform(df['requirements'])
    
    # Превращаем матрицу обратно в DataFrame для удобства
    skills_names = cv.get_feature_names_out()
    skills_df = pd.DataFrame(skills_matrix.toarray(), columns=skills_names)
    
    # Считаем, сколько раз встречается каждый навык
    top_skills = skills_df.sum().sort_values(ascending=False).head(15)
    
    # Рисуем график Топ-15 навыков
    plt.figure(figsize=(12, 8))
    sns.barplot(x=top_skills.values, y=top_skills.index, palette='viridis')
    plt.title('Топ-15 самых востребованных навыков в Data Science (Хабр)', fontsize=14)
    plt.xlabel('Количество вакансий, где требуется навык', fontsize=12)
    plt.ylabel('Навык', fontsize=12)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('plots/nlp_top_skills.png')
    plt.close()
    print("График популяных навыков сохранен: plots/nlp_top_skills.png")

    # =========================================================================
    # ЧАСТЬ 2: Интерпретация Регрессии (на вакансиях с указанной ЗП)
    # =========================================================================
    print("\n[2] Обучаем Регрессию для оценки стоимости навыков...")
    # Оставляем только те вакансии, где работодатель указал зарплату (у нас их 28)
    df_sal = df.dropna(subset=['salary_num']).copy()
    
    # Так как вакансий с зарплатой мало (28 шт), мы не можем подать в модель все 100+ навыков.
    # Это вызовет "Проклятие размерности" (переобучение).
    # Возьмем только 7 самых популярных навыков в качестве признаков (Features).
    top_7_features = top_skills.head(7).index.tolist()
    
    # Преобразуем навыки только для этих 28 вакансий
    skills_matrix_sal = cv.transform(df_sal['requirements'])
    skills_df_sal = pd.DataFrame(skills_matrix_sal.toarray(), columns=skills_names)
    
    X = skills_df_sal[top_7_features]
    y = df_sal['salary_num']
    
    # Обучаем простую Линейную Регрессию
    lr = LinearRegression()
    lr.fit(X, y)
    
    # Извлекаем веса (коэффициенты модели)
    weights = pd.Series(lr.coef_, index=X.columns).sort_values(ascending=False)
    
    print("\n=== ИНТЕРПРЕТАЦИЯ СТОИМОСТИ НАВЫКОВ ===")
    print("Сколько рублей (в среднем) прибавляет/убавляет знание технологии:")
    for skill, weight in weights.items():
        sign = "+" if weight > 0 else ""
        print(f" - {skill.upper()}: {sign}{weight:,.0f} руб.")
        
    # Рисуем график весов
    plt.figure(figsize=(10, 6))
    colors = ['green' if w > 0 else 'red' for w in weights.values]
    sns.barplot(x=weights.values, y=weights.index, palette=colors)
    plt.title('Сколько стоит навык на рынке? (Веса Линейной Регрессии)', fontsize=14)
    plt.xlabel('Влияние на зарплату (руб)', fontsize=12)
    plt.ylabel('Навык', fontsize=12)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('plots/nlp_salary_weights.png')
    plt.close()
    print("График весов сохранен: plots/nlp_salary_weights.png")

if __name__ == "__main__":
    main()
