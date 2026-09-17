import numpy as np
import pandas as pd
from pathlib import Path


def load_vacancies(file_path: Path) -> pd.DataFrame:
    """Загружает CSV-файл с вакансиями."""
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    df = pd.read_csv(file_path)
    print(f"Загружено {len(df)} вакансий из {file_path.name}")
    return df


def add_mock_salaries(df: pd.DataFrame, seed: int = 42, fill_all: bool = True) -> pd.DataFrame:
    """Генерирует синтетические данные по зарплатам.
    
    Args:
        df: Исходный датафрейм вакансий.
        seed: Сид для воспроизводимости псевдослучайных чисел.
        fill_all: Если True — генерирует зарплаты для всех строк (Вариант 2).
                  Если False — заполняет только пустые значения (Вариант 1).
    """
    np.random.seed(seed)
    # Диапазон от 80 000 до 320 000 руб. с шагом 10 000
    salary_range = np.arange(80_000, 320_000, 10_000)

    if fill_all:
        print("Генерация мок-зарплат для ВСЕХ вакансий...")
        df["salary"] = np.random.choice(salary_range, size=len(df))
    else:
        missing_mask = df["salary"].isna()
        missing_count = missing_mask.sum()
        print(f"Заполнение только пропущенных зарплат ({missing_count} шт.)...")
        df.loc[missing_mask, "salary"] = np.random.choice(salary_range, size=missing_count)

    return df


def main():
    base_dir = Path(__file__).resolve().parent
    input_file = base_dir / "data" / "ds_vacancies_analysis_ready.csv"
    output_file = base_dir / "data" / "ds_vacancies_processed.csv"

    # 1. Загрузка
    df = load_vacancies(input_file)
    print("\n--- Информация до обработки ---")
    df.info()

    # 2. Добавление мок-данных (Вариант 2: для всех строк)
    df = add_mock_salaries(df, seed=42, fill_all=True)

    # 3. Проверка результата
    print("\n--- Статистика по зарплатам ---")
    print(df["salary"].describe())

    print("\n--- Первые 5 строк ---")
    print(df[["title", "company", "salary"]].head())

    # 4. Сохранение обработанных данных
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"\nРезультат успешно сохранен в: {output_file.name}")


if __name__ == "__main__":
    main()
