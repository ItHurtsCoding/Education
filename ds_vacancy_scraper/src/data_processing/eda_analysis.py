import pandas as pd
import numpy as np
import re
import os
import matplotlib.pyplot as plt
import seaborn as sns

def parse_salary(salary_str):
    """
    Функция для очистки колонки с зарплатой.
    Извлекает числа из строк вида "от 50 000 до 100 000 ₽".
    Если указана вилка (два числа) — берет среднее значение.
    """
    # 1. Приводим к строке и удаляем лишние пробелы и неразрывные пробелы
    s = str(salary_str).replace(' ', '').replace('\xa0', '').replace('\u202f', '')
    
    # 2. Ищем все последовательности цифр с помощью регулярных выражений (regex)
    nums = re.findall(r'\d+', s)
    
    # Если чисел нет (например, было "Не указана"), возвращаем пустое значение (NaN)
    if not nums:
        return np.nan
        
    # Преобразуем найденные строки в целые числа
    nums = [int(n) for n in nums]
    
    # 3. Логика обработки
    if len(nums) == 1:
        return nums[0] # Если число одно, возвращаем его
    elif len(nums) >= 2:
        return np.mean(nums[:2]) # Если два и более (вилка), считаем среднее
        
    return np.nan

def main():
    # Создаем папку для графиков, если ее еще нет
    os.makedirs('plots', exist_ok=True)

    print("Загрузка данных...")
    # Загружаем датасет, который мы объединяли ранее
    df = pd.read_csv('data/ds_vacancies_analysis_ready.csv')

    print("Очистка и генерация новых признаков (Feature Engineering)...")
    
    # Применяем функцию parse_salary к каждой строке колонки 'salary'
    df['salary_num'] = df['salary'].apply(parse_salary)

    # Создаем признак req_len: считаем количество навыков (разделенных запятой)
    # Если навыков нет (NaN) или написано "Не указаны", ставим 0
    df['req_len'] = df['requirements'].apply(
        lambda x: len(str(x).split(',')) if pd.notna(x) and x != 'Не указаны' else 0
    )

    # Создаем бинарный признак удаленки (1 - удаленка, 0 - офис/гибрид)
    df['is_remote'] = df['work_format'].apply(
        lambda x: 1 if 'Удаленная' in str(x) else 0
    )

    # Кодируем строковые названия источников (Habr, HH) в числовые категории (0, 1, 2...)
    df['source_code'] = df['source'].astype('category').cat.codes

    # Сохраняем итоговый датафрейм, готовый для ML
    cleaned_path = 'data/ds_vacancies_analysis_cleaned.csv'
    df.to_csv(cleaned_path, index=False)
    print(f"Очищенные данные сохранены в: {cleaned_path}")

    # ==========================================
    # РАЗВЕДОЧНЫЙ АНАЛИЗ ДАННЫХ (EDA) И ГРАФИКИ
    # ==========================================
    print("Генерация графиков...")

    # График 1: Гистограмма распределения зарплат
    plt.figure(figsize=(10, 6))
    # dropna() удаляет пустые значения перед отрисовкой, чтобы избежать ошибок
    sns.histplot(df['salary_num'].dropna(), bins=20, kde=True, color='skyblue')
    plt.title('Распределение зарплат (Целевой признак)', fontsize=14)
    plt.xlabel('Зарплата (руб)', fontsize=12)
    plt.ylabel('Количество вакансий', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig('plots/salary_dist.png')
    plt.close() # Закрываем график, чтобы он не накладывался на следующий

    # График 2: Матрица корреляции
    # Выбираем только числовые колонки для расчета корреляции (зависимости друг от друга)
    corr_cols = ['salary_num', 'req_len', 'is_remote', 'source_code']
    corr_matrix = df[corr_cols].corr()

    plt.figure(figsize=(8, 6))
    # annot=True показывает цифры в ячейках, cmap - цветовая палитра
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
    plt.title('Матрица корреляции числовых признаков', fontsize=14)
    plt.tight_layout() # Автоматически подстраивает отступы
    plt.savefig('plots/correlation_matrix.png')
    plt.close()

    print("Графики успешно сохранены в папку 'plots/'!")

if __name__ == "__main__":
    main()
