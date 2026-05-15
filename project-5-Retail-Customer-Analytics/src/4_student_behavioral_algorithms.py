                                                                                   #task 1


import pandas as pd
import math
import os

# 1. Умная загрузка данных
# Проверяем, где мы находимся, и ищем файл
file_name = 'retail_customer_loyalty_realistic.csv'

if not os.path.exists(file_name):
    # Если файла нет рядом со скриптом, пробуем путь через папку src
    file_name = os.path.join('src', 'retail_customer_loyalty_realistic.csv')
    if not os.path.exists(file_name):
        # Если и так не нашли, пробуем выйти на уровень выше (на случай запуска из src)
        file_name = os.path.join('..', 'src', 'retail_customer_loyalty_realistic.csv')


try:
    df = pd.read_csv(file_name)
    print(f"✅ Файл успешно загружен из: {file_name}")
except FileNotFoundError:
    print("❌ Ошибка: Не удалось найти CSV-файл. Проверьте, что он лежит в папке src!")
    exit()

# --- АЛГОРИТМИЧЕСКИЙ ПОИСК АНОМАЛИЙ (Задание 4 студента) ---

# Шаг 1: Расчет среднего арифметического через цикл
total_spent_sum = 0
for val in df['total_spent']:
    total_spent_sum += val
mean_spent = total_spent_sum / len(df)

# Шаг 2: Расчет стандартного отклонения вручную
sum_sq_diff = 0
for val in df['total_spent']:
    # Квадрат разности (отклонение от среднего)
    sum_sq_diff += (val - mean_spent) ** 2

variance = sum_sq_diff / len(df)
std_dev = math.sqrt(variance)

# Шаг 3: Поиск аномалий по правилу 2-х сигм (2 * std_dev)
lower_bound = mean_spent - 2 * std_dev
upper_bound = mean_spent + 2 * std_dev

# Фильтруем клиентов, чьи траты выходят за эти границы
anomalies = df[(df['total_spent'] < lower_bound) | (df['total_spent'] > upper_bound)]

# --- ВЫВОД РЕЗУЛЬТАТОВ ---
print("-" * 50)
print(f"Средний чек по всей базе: {mean_spent:.2f}")
print(f"Стандартное отклонение (разброс): {std_dev:.2f}")
print(f"Границы нормы: от {lower_bound:.2f} до {upper_bound:.2f}")
print("-" * 50)
print(f"Найдено аномальных записей: {len(anomalies)}")
print("Топ-10 аномальных клиентов:")
print(anomalies[['customer_id', 'total_spent', 'loyalty_score']].head(10))


                                                                       #task 2


import pandas as pd

# 1. Сортировка DataFrame по стажу членства
df_sorted = df.sort_values(by='membership_years').reset_index(drop=True)

# 2. Параметры скользящего окна
window_size = 10
rolling_averages = []

# 3. Реализация скользящего окна через цикл
# Проходим от 0 до (общее кол-во строк - размер окна + 1)
for i in range(len(df_sorted) - window_size + 1):
    # Выделяем текущее "окно" данных
    window = df_sorted.iloc[i: i + window_size]

    # Вычисляем среднюю частоту покупок в этом окне
    avg_freq = window['purchase_frequency'].mean()

    # 4. Сохраняем результат в список
    rolling_averages.append(avg_freq)

# Вывод первых 10 результатов скользящего среднего
print(f"Первые 10 значений скользящего среднего (окно {window_size}):")
print(rolling_averages[:10])


                                                                           #task 3


import pandas as pd
import numpy as np

# 1. Выбираем признаки для расчета
features = ['total_spent', 'loyalty_score', 'purchase_frequency']
target_client = df.iloc[0]  # Первый клиент
distances = []

# 2. Проходим через цикл для вычисления расстояний до всех остальных
for index, row in df.iterrows():
    if index == 0:
        continue  # Пропускаем сравнение клиента с самим собой

    # Вычисляем Евклидово расстояние вручную [cite: 200]
    dist = np.sqrt(
        (target_client['total_spent'] - row['total_spent']) ** 2 +
        (target_client['loyalty_score'] - row['loyalty_score']) ** 2 +
        (target_client['purchase_frequency'] - row['purchase_frequency']) ** 2
    )

    distances.append((row['customer_id'], dist))

# 3. Сортируем список по расстоянию (от меньшего к большему)
distances.sort(key=lambda x: x[1])

# 4. Находим 5 ближайших клиентов
top_5_neighbors = distances[:5]

print(f"Поиск похожих клиентов для ID: {target_client['customer_id']}")
print("-" * 30)
for cid, d in top_5_neighbors:
    print(f"Customer ID: {cid} | Расстояние: {round(d, 4)}")  #




                                                                      #task4


import pandas as pd


# 1. Определяем функцию рекомендаций на основе бизнес-логики
def get_recommendation(row):
    # Условие для премиальной электроники
    if row['preferred_category'] == 'Electronics' and row['total_spent'] > 5000:
        return 'Premium Electronics'

    # Условие для активных покупателей (например, частота выше 10 покупок)
    # Порог частоты можно адаптировать под медиану вашего датасета
    if row['purchase_frequency'] > 10:
        return 'Discount Campaign'

    # Рекомендация по умолчанию
    return 'Standard Offer'


# 2. Создаем новую колонку, применяя функцию к каждой строке
df['recommendation'] = df.apply(get_recommendation, axis=1)

# 3. Вывод результатов для проверки
print("Примеры рекомендаций для клиентов:")
print(df[['customer_id', 'preferred_category', 'total_spent', 'purchase_frequency', 'recommendation']].head(10))
# Статистика по рекомендациям
print("\nРаспределение рекомендаций:")

import pandas as pd

# Предположим, DataFrame (df) уже загружен на предыдущих этапах
# Ниже приведен пример реализации системы правил (Rule Engine)

## 1. Определение набора правил (Functions)
def rule_premium_offer(row):
    """Правило для предложения премиум-товаров"""
    if row['total_spent'] > 5000 and row['loyalty_score'] > 80:
        return "Offer Premium Membership"
    return None

def rule_retention_campaign(row):
    """Правило для удержания (высокий риск оттока)"""
    if row['purchase_frequency'] < 2 and row['loyalty_score'] < 40:
        return "Send Retention Discount"
    return None

def rule_cross_sell_electronics(row):
    """Правило кросс-продаж электроники"""
    if row['preferred_category'] == 'Electronics' and row['avg_purchase_value'] > 200:
        return "Suggest New Gadgets"
    return None

def rule_default_action(row):
    """Действие по умолчанию"""
    return "Standard Newsletter"

## 2. Формирование списка правил
rules = [
    rule_premium_offer,
    rule_retention_campaign,
    rule_cross_sell_electronics,
    rule_default_action
]

## 3. Применение правил через цикл
def apply_rules(row):
    for rule in rules:
        action = rule(row)
        if action:  # Возвращаем первое сработавшее правило
            return action
    return "No Action"

# Создание новой колонки с результатами работы Rule Engine
df['marketing_action'] = df.apply(apply_rules, axis=1)

## 4. Вывод результатов
print("Распределение действий маркетинга:")
print(df['marketing_action'].value_counts())
print("\nПримеры назначенных действий для первых 10 клиентов:")
print(df[['customer_id', 'total_spent', 'loyalty_score', 'marketing_action']].head(10))

import pandas as pd
import math
import os

# ─── Загрузка данных (такой же умный поиск файла, как в task 1) ───────────────
file_name = 'retail_customer_loyalty_realistic.csv'
if not os.path.exists(file_name):
    file_name = os.path.join('src', 'retail_customer_loyalty_realistic.csv')
    if not os.path.exists(file_name):
        file_name = os.path.join('..', 'src', 'retail_customer_loyalty_realistic.csv')

try:
    df = pd.read_csv(file_name)
    print(f"✅ Файл успешно загружен из: {file_name}")
except FileNotFoundError:
    print("❌ Ошибка: Не удалось найти CSV-файл. Проверьте, что он лежит в папке src!")
    exit()

# Нужны колонки из предыдущих задач (воссоздаём, если скрипт запускается отдельно)
if 'client_score' not in df.columns:
    df['client_score'] = (df['total_spent'] * 0.5) + (df['loyalty_score'] * 0.3) - (df['returns_count'] * 0.2)

if 'spend_per_purchase' not in df.columns:
    df['spend_per_purchase'] = df['total_spent'] / (df['purchase_frequency'] + 1)

if 'return_ratio' not in df.columns:
    df['return_ratio'] = df['returns_count'] / (df['purchase_frequency'] + 1)


# ══════════════════════════════════════════════════════════════════════════════
# ЗАДАНИЕ 6 — Сортировка и ranking алгоритмы
# Цель: создать колонку client_score и отсортировать DataFrame по ней.
# Алгоритмический акцент: реализовать сортировку вручную (selection sort по score)
#   параллельно с pandas.sort_values(), чтобы увидеть разницу в подходах.
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("ЗАДАНИЕ 6 — Сортировка и ranking алгоритмы")
print("=" * 60)

# Шаг 1: Создаём / обновляем client_score по заданной формуле
df['client_score'] = (df['total_spent'] * 0.5) + (df['loyalty_score'] * 0.3) - (df['returns_count'] * 0.2)

# Шаг 2: Ручная реализация поиска топ-20 через алгоритм partial selection sort.
# Это эффективнее полной сортировки для задачи "найти топ-K из N".
# Сложность: O(N * K) вместо O(N log N).

scores = list(zip(df.index, df['client_score']))  # [(index, score), ...]
top_k = 20
top_indices = []

for _ in range(top_k):
    best_idx = None
    best_score = float('-inf')

    for idx, score in scores:
        if score > best_score:
            best_score = score
            best_idx = idx

    top_indices.append(best_idx)
    # Убираем найденный элемент, чтобы не брать его снова
    scores = [(i, s) for i, s in scores if i != best_idx]

top_20_manual = df.loc[top_indices].copy()

# Шаг 3: Проверка через pandas (результаты должны совпадать)
top_20_pandas = df.sort_values(by='client_score', ascending=False).head(20)

print(f"\nТоп-20 клиентов по client_score (ручная сортировка):")
print("-" * 60)
print(f"{'#':<4} {'customer_id':<15} {'total_spent':<14} {'loyalty_score':<15} {'client_score':<12}")
print("-" * 60)

for rank, (_, row) in enumerate(top_20_manual.iterrows(), start=1):
    print(f"{rank:<4} {row['customer_id']:<15} {row['total_spent']:<14.2f} "
          f"{row['loyalty_score']:<15.1f} {row['client_score']:<12.2f}")

# Шаг 4: Проверка совпадения с pandas
manual_ids = list(top_20_manual['customer_id'])
pandas_ids  = list(top_20_pandas['customer_id'])
match = manual_ids == pandas_ids
print(f"\n✅ Ручная сортировка совпадает с pandas: {match}")


# ══════════════════════════════════════════════════════════════════════════════
# ЗАДАНИЕ 7 — Генераторы и потоковая обработка
# Цель: создать генератор онлайн-покупателей с loyalty_score > 60,
#   вывести первых 20. Использовать yield.
# Алгоритмический акцент: показать разницу в памяти между генератором
#   и обычным списком через сравнение sys.getsizeof().
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("ЗАДАНИЕ 7 — Генераторы и потоковая обработка")
print("=" * 60)

import sys

# Шаг 1: Определяем генератор — обрабатывает строки DataFrame по одной,
#   не загружая весь результат в память.
def active_online_shoppers_generator(dataframe, min_loyalty=60):
    """
    Генератор: возвращает клиентов по одному (yield),
    у которых online_shopper == True и loyalty_score > min_loyalty.
    Память не зависит от размера входного DataFrame.
    """
    for _, row in dataframe.iterrows():
        if row['online_shopper'] == True and row['loyalty_score'] > min_loyalty:
            yield row

# Шаг 2: Создаём генератор (в памяти хранится только объект-генератор, не данные)
gen = active_online_shoppers_generator(df)

# Шаг 3: Извлекаем первые 20 клиентов через next()
print("\nПервые 20 активных онлайн-покупателей (loyalty_score > 60):")
print("-" * 50)
print(f"{'#':<4} {'customer_id':<15} {'loyalty_score':<14} {'online_shopper'}")
print("-" * 50)

count = 0
for _ in range(20):
    try:
        client = next(gen)
        count += 1
        print(f"{count:<4} {client['customer_id']:<15} {client['loyalty_score']:<14.1f} {client['online_shopper']}")
    except StopIteration:
        print("⚠️  Данные закончились раньше 20 записей.")
        break

# Шаг 4: Сравнение памяти — генератор vs список
list_result = [row for _, row in df.iterrows()
               if row['online_shopper'] == True and row['loyalty_score'] > 60]
new_gen = active_online_shoppers_generator(df)  # Новый генератор для сравнения

size_list = sys.getsizeof(list_result)
size_gen  = sys.getsizeof(new_gen)

print(f"\n📊 Сравнение потребления памяти:")
print(f"   Список (все результаты): {size_list:>8} байт")
print(f"   Генератор:               {size_gen:>8} байт")
print(f"   Экономия:                {size_list - size_gen:>8} байт")
print(f"   Всего подходящих клиентов: {len(list_result)}")


# ══════════════════════════════════════════════════════════════════════════════
# ЗАДАНИЕ 8 — Ручная агрегация через циклы
# Цель: city → суммарный total_spent, city → кол-во клиентов,
#   затем средний total_spent по городу. Без groupby!
# Алгоритмический акцент: показать, что groupby делает именно это —
#   проверить результаты через pandas для верификации.
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("ЗАДАНИЕ 8 — Ручная агрегация через циклы")
print("=" * 60)

# Шаг 1: Одним проходом собираем сумму трат и кол-во клиентов по каждому городу
city_spend = {}   # city -> суммарный total_spent
city_count = {}   # city -> количество клиентов

for _, row in df.iterrows():
    city  = row['city']
    spend = row['total_spent']

    # dict.get(key, default) — безопасное получение без KeyError
    city_spend[city] = city_spend.get(city, 0.0) + spend
    city_count[city] = city_count.get(city, 0)   + 1

# Шаг 2: Рассчитываем средний чек по городу
city_avg = {}
for city in city_spend:
    city_avg[city] = city_spend[city] / city_count[city]

# Шаг 3: Сортируем города по убыванию среднего чека (ручная сортировка словаря)
sorted_cities = sorted(city_avg.items(), key=lambda x: x[1], reverse=True)

print("\nАгрегация по городам (ручной подсчёт):")
print("-" * 55)
print(f"{'Город':<20} {'Клиентов':<12} {'Сумма трат':<15} {'Средний чек'}")
print("-" * 55)

for city, avg in sorted_cities:
    print(f"{city:<20} {city_count[city]:<12} {city_spend[city]:<15.2f} {avg:.2f}")

# Шаг 4: Верификация через pandas groupby (результаты должны совпасть)
pandas_agg = df.groupby('city')['total_spent'].mean().to_dict()

mismatches = 0
for city, avg in city_avg.items():
    if abs(avg - pandas_agg[city]) > 0.001:  # Допуск на погрешность float
        mismatches += 1

print(f"\n✅ Расхождений с pandas groupby: {mismatches} (0 = всё верно)")


# ══════════════════════════════════════════════════════════════════════════════
# ЗАДАНИЕ 9 — Алгоритмическая задача: поиск топ-5 без sort / nlargest
# Цель: найти топ-5 клиентов по total_spent, используя только цикл for.
# Алгоритмический акцент: поддерживать отсортированный список из 5 элементов
#   за O(N * 5) = O(N) без полной сортировки массива.
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("ЗАДАНИЕ 9 — Поиск топ-5 без sort / nlargest")
print("=" * 60)

# Шаг 1: Инициализируем список топ-5 как пустой
# Каждый элемент: (total_spent, customer_id)
top_5 = []
K = 5

for _, row in df.iterrows():
    val = row['total_spent']
    cid = row['customer_id']

    if len(top_5) < K:
        # Список ещё не заполнен — просто добавляем
        top_5.append((val, cid))
    else:
        # Находим минимум в текущем топ-5 вручную (без min())
        min_val = top_5[0][0]
        min_pos = 0
        for j in range(1, K):
            if top_5[j][0] < min_val:
                min_val = top_5[j][0]
                min_pos = j

        # Если новый клиент тратит больше минимума — заменяем
        if val > min_val:
            top_5[min_pos] = (val, cid)

# Шаг 2: Ручная сортировка топ-5 по убыванию (insertion sort на 5 элементах)
for i in range(1, len(top_5)):
    key = top_5[i]
    j = i - 1
    while j >= 0 and top_5[j][0] < key[0]:
        top_5[j + 1] = top_5[j]
        j -= 1
    top_5[j + 1] = key

# Шаг 3: Вывод результатов
print("\nТоп-5 клиентов по total_spent (алгоритмический поиск):")
print("-" * 40)
print(f"{'Место':<8} {'customer_id':<20} {'total_spent'}")
print("-" * 40)

for rank, (spent, cid) in enumerate(top_5, start=1):
    print(f"{rank:<8} {cid:<20} {spent:.2f}")

# Шаг 4: Верификация через pandas (без sort/nlargest в нашем коде, но для проверки)
pandas_top5 = df.nlargest(5, 'total_spent')[['customer_id', 'total_spent']]
our_ids     = [cid for _, cid in top_5]
pandas_ids  = list(pandas_top5['customer_id'])

print(f"\n✅ Результат совпадает с pandas.nlargest: {our_ids == pandas_ids}")


# ══════════════════════════════════════════════════════════════════════════════
# ЗАДАНИЕ 10 — Сохранение и подготовка данных
# Цель: сохранить DataFrame с новыми признаками в CSV,
#   отдельно сохранить топ-100 клиентов.
# Алгоритмический акцент: добавить все признаки, созданные в предыдущих задачах,
#   вывести итоговую сводку по файлам.
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("ЗАДАНИЕ 10 — Сохранение и подготовка данных")
print("=" * 60)

# Шаг 1: Убеждаемся, что все новые признаки присутствуют в DataFrame

# Признак из задания 6
if 'client_score' not in df.columns:
    df['client_score'] = (df['total_spent'] * 0.5) + (df['loyalty_score'] * 0.3) - (df['returns_count'] * 0.2)

# Признаки из задания 5 (если скрипт запускается отдельно)
if 'spend_per_purchase' not in df.columns:
    df['spend_per_purchase'] = df['total_spent'] / (df['purchase_frequency'] + 1)

if 'return_ratio' not in df.columns:
    df['return_ratio'] = df['returns_count'] / (df['purchase_frequency'] + 1)

if 'engagement_score_custom' not in df.columns:
    df['engagement_score_custom'] = (df['app_sessions_per_month'] + df['website_visits_per_month']) / 2

# Шаг 2: Сохраняем полный DataFrame со всеми новыми признаками
output_full = 'refined_customer_data_student4.csv'
df.to_csv(output_full, index=False)

full_size_kb = os.path.getsize(output_full) / 1024

print(f"\n📁 Полный датасет:")
print(f"   Файл:       {output_full}")
print(f"   Строк:      {len(df)}")
print(f"   Колонок:    {len(df.columns)}")
print(f"   Размер:     {full_size_kb:.1f} КБ")

# Шаг 3: Сохраняем топ-100 клиентов по client_score
# Используем алгоритмический подход из задания 9, но уже для 100 элементов

TOP_N = 100
top_100 = []

for _, row in df.iterrows():
    score = row['client_score']
    top_100.append((score, row.name))  # (score, DataFrame index)

    if len(top_100) > TOP_N:
        # Удаляем минимальный элемент вручную
        min_pos = 0
        for j in range(1, len(top_100)):
            if top_100[j][0] < top_100[min_pos][0]:
                min_pos = j
        top_100.pop(min_pos)

# Получаем индексы и сохраняем
top_100_indices = [idx for _, idx in top_100]
df_top_100 = df.loc[top_100_indices].sort_values('client_score', ascending=False)

output_top = 'top_100_clients_student4.csv'
df_top_100.to_csv(output_top, index=False)

top_size_kb = os.path.getsize(output_top) / 1024

print(f"\n🏆 Топ-100 клиентов:")
print(f"   Файл:       {output_top}")
print(f"   Строк:      {len(df_top_100)}")
print(f"   Колонок:    {len(df_top_100.columns)}")
print(f"   Размер:     {top_size_kb:.1f} КБ")

# Шаг 4: Итоговая сводка по всем созданным признакам
new_columns = ['client_score', 'spend_per_purchase', 'return_ratio', 'engagement_score_custom']
present = [col for col in new_columns if col in df.columns]

print(f"\n📊 Созданные признаки в итоговом файле:")
print("-" * 50)
for col in present:
    print(f"   {col:<30} min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}")

print(f"\n✅ Данные успешно подготовлены и сохранены!")
print(f"   → {output_full} (полный датасет с новыми признаками)")
print(f"   → {output_top} (топ-100 по client_score)")