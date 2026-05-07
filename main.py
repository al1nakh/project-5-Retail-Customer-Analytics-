import pandas as pd
import numpy as np


def run_feature_engineering():
    try:
        # Загрузка данных (путь из кода Студента 2)
        df = pd.read_csv('../data/retail_customer_loyalty_realistic.csv')
        print("Данные успешно загружены для Feature Engineering.\n")

        # ЗАДАЧА 1: Создание комплексных поведенческих признаков
        print("--- Задача 1: Поведенческие признаки ---")
        df['purchase_intensity'] = df['purchase_frequency'] / (df['membership_years'] + 1)
        df['digital_engagement'] = (df['app_sessions_per_month'] + df['website_visits_per_month']) / 2
        df['value_per_year'] = df['total_spent'] / (df['membership_years'] + 1)

        print("Топ-10 клиентов по purchase_intensity:")
        print(df[['customer_id', 'purchase_intensity']].sort_values(by='purchase_intensity', ascending=False).head(10))
        print("\n")

        # ЗАДАЧА 2: Логическая сегментация клиентов
        print("--- Задача 2: Сегментация клиентов ---")

        def segment_client(row):
            if row['total_spent'] > 7000 and row['loyalty_score'] > 70:
                return "High Value"
            elif row['total_spent'] > 3000:
                return "Medium Value"
            else:
                return "Low Value"

        df['customer_class'] = df.apply(segment_client, axis=1)
        print("Количество клиентов в каждой категории:")
        print(df['customer_class'].value_counts())
        print("\n")

        # ЗАДАЧА 3: Создание индекса вовлеченности
        print("--- Задача 3: Индекс вовлеченности ---")
        # Расчет базового индекса
        df['engagement_index'] = (df['app_sessions_per_month'] * 0.4 +
                                  df['website_visits_per_month'] * 0.3 +
                                  df['purchase_frequency'] * 0.3)
        # Нормализация (0-1)
        min_eng = df['engagement_index'].min()
        max_eng = df['engagement_index'].max()
        df['engagement_index'] = (df['engagement_index'] - min_eng) / (max_eng - min_eng)

        print("Топ-10 клиентов по engagement_index:")
        print(df[['customer_id', 'engagement_index']].sort_values(by='engagement_index', ascending=False).head(10))
        print("\n")

        # ЗАДАЧА 4: Построение proxy-показателя оттока
        print("--- Задача 4: Proxy-показатель оттока ---")
        df['churn_flag'] = np.where(
            (df['last_purchase_days_ago'] > 180) & (df['engagement_index'] < 0.3), 1, 0
        )
        churn_pct = (df['churn_flag'].mean()) * 100
        print(f"Процент клиентов с churn_flag = 1: {churn_pct:.2f}%")
        print("\n")

        # ЗАДАЧА 5: Создание взаимодействующих признаков
        print("--- Задача 5: Взаимодействующие признаки ---")
        df['loyalty_spend'] = df['loyalty_score'] * df['total_spent']
        df['activity_value'] = df['purchase_frequency'] * df['avg_purchase_value']
        df['engagement_value'] = df['engagement_index'] * df['total_spent']

        print("Топ-10 клиентов по engagement_value:")
        print(df[['customer_id', 'engagement_value']].sort_values(by='engagement_value', ascending=False).head(10))
        print("\n")

        # ЗАДАЧА 6: Полиномиальные признаки
        print("--- Задача 6: Полиномиальные признаки ---")
        df['total_spent_squared'] = df['total_spent'] ** 2
        df['loyalty_score_squared'] = df['loyalty_score'] ** 2
        df['interaction_term'] = df['total_spent'] * df['loyalty_score']

        poly_features = ['total_spent_squared', 'loyalty_score_squared', 'interaction_term']
        print("Корреляция новых признаков с churn_flag:")
        print(df[poly_features + ['churn_flag']].corr()['churn_flag'].drop('churn_flag'))
        print("\n")

        # ЗАДАЧА 7: Анализ корреляций и отбор признаков
        print("--- Задача 7: Анализ корреляций ---")
        # Выбираем только числовые колонки
        numeric_df = df.select_dtypes(include=[np.number])
        corr_matrix = numeric_df.corr()

        # Топ-5 коррелирующих признаков (без учета самого churn_flag)
        top_5_corr = corr_matrix['churn_flag'].abs().sort_values(ascending=False).head(6).index[1:]
        print("Топ-5 признаков, наиболее коррелирующих с churn_flag:")
        print(top_5_corr.tolist())
        print("\n")

        # ЗАДАЧА 8: Сводные таблицы с несколькими индексами
        print("--- Задача 8: Сводная таблица (Pivot Table) ---")
        pivot = pd.pivot_table(
            df,
            index='city',
            columns='customer_class',
            values='engagement_index',
            aggfunc='mean'
        )
        print("Средний engagement_index по городам и классам клиентов:")
        print(pivot.fillna(0))  # Заполняем пропуски нулями, если в категории нет клиентов
        print("\n")

        # ЗАДАЧА 9: Взвешенные показатели
        print("--- Задача 9: Взвешенные показатели ---")
        total_spent_sum = df['total_spent'].sum()
        df['weighted_loyalty'] = df['loyalty_score'] * (df['total_spent'] / total_spent_sum)

        print("Топ-10 клиентов по weighted_loyalty:")
        print(df[['customer_id', 'weighted_loyalty']].sort_values(by='weighted_loyalty', ascending=False).head(10))
        print("\n")

        # ЗАДАЧА 10: Подготовка финального датасета
        print("--- Задача 10: Финальный датасет ---")
        # Сохраняем датасет в отдельный файл
        output_file = 'dataset_ready.csv'
        df.to_csv(output_file, index=False)
        print(f"Финальный DataFrame со всеми новыми признаками сохранен в: {output_file}")

    except FileNotFoundError:
        print(
            "Ошибка: Файл с исходными данными не найден. Убедитесь, что Студент 1 загрузил данные в нужную директорию.")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    run_feature_engineering()
