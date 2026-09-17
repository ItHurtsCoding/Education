import pandas as pd
import numpy as np

def extract_grade(title):
    """
    Извлекает грейд (квалификацию) из названия вакансии.
    """
    title = str(title).lower()
    if 'intern' in title or 'стажер' in title:
        return 'Intern'
    elif 'junior' in title or 'младший' in title or 'джуниор' in title:
        return 'Junior'
    elif 'senior' in title or 'старший' in title or 'сеньор' in title:
        return 'Senior'
    elif 'lead' in title or 'руководитель' in title or 'лид' in title:
        return 'Lead'
    elif 'middle' in title or 'мидл' in title:
        return 'Middle'
    else:
        # Если грейд не указан, на рынке по умолчанию это обычно Middle позиция
        return 'Not Specified (Middle)'

def main():
    # 1. Загружаем данные
    df = pd.read_csv('data/ds_vacancies_analysis_cleaned.csv')
    
    # 2. Создаем новую колонку 'grade' на основе названия вакансии
    df['grade'] = df['title'].apply(extract_grade)
    
    # Чтобы таблицы выводились красиво, зададим порядок грейдов
    grade_order = ['Intern', 'Junior', 'Middle', 'Not Specified (Middle)', 'Senior', 'Lead']
    df['grade'] = pd.Categorical(df['grade'], categories=grade_order, ordered=True)
    
    # =========================================================
    # ТАБЛИЦА 1: Квалификация и Требования (req_len)
    # =========================================================
    print("=== ТАБЛИЦА 1: Квалификация и Требования (Количество навыков) ===")
    table1 = df.groupby('grade', observed=False)['req_len'].agg(
        Кол_во_вакансий='count',
        Среднее_навыков='mean',
        Мин_навыков='min',
        Макс_навыков='max'
    ).round(1).fillna(0)
    print(table1.to_string())
    print("\n*Анализ Senior DS:* В реальных данных количество требований обычно растет от Intern к Senior. Middle и Senior часто требуют более глубоких, но иногда более узкоспециализированных стеков.\n")
    
    # =========================================================
    # ТАБЛИЦА 2: Квалификация и Зарплата (salary_num)
    # =========================================================
    print("=== ТАБЛИЦА 2: Квалификация и Ожидаемая Зарплата (РУБ) ===")
    table2 = df.groupby('grade', observed=False)['salary_num'].agg(
        Средняя_ЗП='mean',
        Мин_ЗП='min',
        Макс_ЗП='max'
    ).round(0).fillna(0)
    
    # Форматируем вывод для красоты (добавляем пробелы тысяч)
    table2 = table2.map(lambda x: f"{int(x):,}".replace(',', ' ') if x > 0 else "-")
    print(table2.to_string())
    print("\n*Анализ Senior DS:* Так как наши зарплаты синтетические (сгенерированы случайно от 80к до 320к), мы видим, что средняя зарплата по всем грейдам держится около 200 000 руб. В реальном датасете мы бы увидели четкую лесенку: Intern (50-80к) -> Junior (80-120к) -> Middle (150-250к) -> Senior (250к+).")
    
    # Сохраняем в Excel/CSV для отчетов, если нужно
    # table1.to_csv('data/table_grade_requirements.csv')
    
if __name__ == "__main__":
    main()
