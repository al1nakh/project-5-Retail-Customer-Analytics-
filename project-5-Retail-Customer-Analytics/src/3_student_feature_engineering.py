import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Настраиваем красивый стиль для всех графиков
sns.set_theme(style="whitegrid")

# Загружаем датасет
df = pd.read_csv('retail_customer_loyalty_realistic.csv')


print("=== ЗАДАЧА 1: Комплексные поведенческие признаки ===")
# Создаем признаки [cite: 108]
df['purchase_intensity'] = df['purchase_frequency'] / (df['membership_years'] + 1)
df['digital_engagement'] = (df['app_sessions_per_month'] + df['website_visits_per_month']) / 2
df['value_per_year'] = df['total_spent'] / (df['membership_years'] + 1)

print("Топ-10 клиентов по purchase_intensity:")
print(df.nlargest(10, 'purchase_intensity')[['customer_id', 'purchase_intensity']])

# ГРАФИК 1: Гистограммы распределения
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
sns.histplot(df['purchase_intensity'], ax=axes[0], kde=True, color='blue')
axes[0].set_title('Распределение Purchase Intensity')
sns.histplot(df['digital_engagement'], ax=axes[1], kde=True, color='green')
axes[1].set_title('Распределение Digital Engagement')
sns.histplot(df['value_per_year'], ax=axes[2], kde=True, color='orange')
axes[2].set_title('Распределение Value Per Year')
plt.tight_layout()
plt.show()


print("\n=== ЗАДАЧА 2: Логическая сегментация клиентов ===")
# Логика сегментации [cite: 114]
def get_customer_class(row):
    if row['total_spent'] > 7000 and row['loyalty_score'] > 70:
        return "High Value"
    elif row['total_spent'] > 3000:
        return "Medium Value"
    else:
        return "Low Value"

df['customer_class'] = df.apply(get_customer_class, axis=1)
print("Количество клиентов в каждой категории:")
print(df['customer_class'].value_counts())

# ГРАФИК 2: Столбчатая диаграмма
plt.figure(figsize=(8, 5))
sns.countplot(data=df, x='customer_class', order=['High Value', 'Medium Value', 'Low Value'],
              hue='customer_class', palette='viridis', legend=False)
plt.title('Структура клиентской базы по сегментам')
plt.ylabel('Количество клиентов')
plt.show()


print("\n=== ЗАДАЧА 3: Создание индекса вовлеченности ===")
# Формула индекса и нормализация [cite: 119]
df['engagement_index'] = (df['app_sessions_per_month'] * 0.4 +
                          df['website_visits_per_month'] * 0.3 +
                          df['purchase_frequency'] * 0.3)
min_eng, max_eng = df['engagement_index'].min(), df['engagement_index'].max()
df['engagement_index'] = (df['engagement_index'] - min_eng) / (max_eng - min_eng)

print("Топ-10 клиентов по engagement_index:")
print(df.nlargest(10, 'engagement_index')[['customer_id', 'engagement_index']])

# ГРАФИК 3: Boxplot (ящик с усами) для оценки разброса
plt.figure(figsize=(8, 4))
sns.boxplot(x=df['engagement_index'], color='purple')
plt.title('Разброс индекса вовлеченности (Engagement Index)')
plt.show()


print("\n=== ЗАДАЧА 4: Построение proxy-показателя оттока ===")
# Определение churn_flag [cite: 124]
df['churn_flag'] = np.where((df['last_purchase_days_ago'] > 180) & (df['engagement_index'] < 0.3), 1, 0)
churn_rate = df['churn_flag'].mean() * 100
print(f"Процент клиентов в зоне оттока (churn_flag = 1): {churn_rate:.2f}%")

# ГРАФИК 4: Donut chart (Кольцевая диаграмма)
plt.figure(figsize=(6, 6))
labels = ['Активные (0)', 'Зона оттока (1)']
sizes = df['churn_flag'].value_counts()
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#66b3ff', '#ff9999'],
        wedgeprops=dict(width=0.3, edgecolor='w'))
plt.title('Доля клиентов в зоне оттока')
plt.show()


print("\n=== ЗАДАЧА 5: Создание взаимодействующих признаков ===")
# Новые признаки [cite: 128]
df['loyalty_spend'] = df['loyalty_score'] * df['total_spent']
df['activity_value'] = df['purchase_frequency'] * df['avg_purchase_value']
df['engagement_value'] = df['engagement_index'] * df['total_spent']

top10_eng = df.nlargest(10, 'engagement_value')
print("Топ-10 клиентов по engagement_value:")
print(top10_eng[['customer_id', 'engagement_value']])

# ГРАФИК 5: Scatter plot + Горизонтальный Bar chart
fig.tight_layout()
plt.show()
# Взаимосвязь Total Spent и Loyalty Score
sns.scatterplot(data=df, x='total_spent', y='loyalty_score', hue='churn_flag',
                palette='coolwarm', alpha=0.6, ax=axes[0])
axes[0].set_title('Взаимосвязь трат и лояльности (с учетом оттока)')
# Горизонтальный топ-10
sns.barplot(data=top10_eng, x='engagement_value', y='customer_id',
            hue='customer_id', palette='magma', legend=False, ax=axes[1])
axes[1].set_title('Топ-10 клиентов по Engagement Value')
plt.tight_layout()
plt.show()


print("\n=== ЗАДАЧА 6: Полиномиальные признаки ===")
# Нелинейные метрики [cite: 131]
df['total_spent_squared'] = df['total_spent'] ** 2
df['loyalty_score_squared'] = df['loyalty_score'] ** 2
df['interaction_term'] = df['total_spent'] * df['loyalty_score']

poly_cols = ['total_spent_squared', 'loyalty_score_squared', 'interaction_term']
corr_with_churn = df[poly_cols + ['churn_flag']].corr()['churn_flag'].drop('churn_flag')
print("Корреляция новых признаков с churn_flag:")
print(corr_with_churn)

# ГРАФИК 6: Столбчатая диаграмма коэффициентов корреляции
plt.figure(figsize=(8, 4))
corr_with_churn.plot(kind='barh', color=['skyblue', 'lightgreen', 'salmon'])
plt.title('Корреляция полиномиальных признаков с оттоком')
plt.xlabel('Коэффициент корреляции')
plt.axvline(0, color='black', linewidth=1)
plt.show()


print("\n=== ЗАДАЧА 7: Анализ корреляций и отбор признаков ===")
# Поиск топ-5 скоррелированных признаков [cite: 134]
numeric_cols = df.select_dtypes(include=[np.number]).columns
corr_matrix = df[numeric_cols].corr()

top_5_features = corr_matrix['churn_flag'].drop('churn_flag').abs().nlargest(5).index.tolist()
print("Топ-5 признаков, наиболее коррелирующих с churn_flag:", top_5_features)

# ГРАФИК 7: Тепловая карта (Heatmap)
plt.figure(figsize=(8, 6))
top_cols = top_5_features + ['churn_flag']
sns.heatmap(df[top_cols].corr(), annot=True, cmap='coolwarm', fmt=".2f", vmin=-1, vmax=1)
plt.title('Тепловая карта: Топ-5 признаков и Отток')
plt.show()


print("\n=== ЗАДАЧА 8: Сводные таблицы с несколькими индексами ===")
# Pivot table [cite: 137]
pivot_table = pd.pivot_table(df, values='engagement_index', index='city',
                             columns='customer_class', aggfunc='mean')
print(pivot_table)

# ГРАФИК 8: Сгруппированная столбчатая диаграмма
pivot_table.plot(kind='bar', figsize=(12, 5), colormap='Set2')
plt.title('Средний индекс вовлеченности по регионам и сегментам')
plt.ylabel('Engagement Index (Mean)')
plt.xlabel('Город')
plt.xticks(rotation=45)
plt.legend(title='Customer Class', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()


print("\n=== ЗАДАЧА 9: Взвешенные показатели ===")
# Взвешенная лояльность [cite: 140]
total_spent_sum = df['total_spent'].sum()
df['weighted_loyalty'] = df['loyalty_score'] * (df['total_spent'] / total_spent_sum)

top10_wl = df.nlargest(10, 'weighted_loyalty')
print("Топ-10 клиентов по weighted_loyalty:")
print(top10_wl[['customer_id', 'weighted_loyalty']])

# ГРАФИК 9: Горизонтальный bar chart для рейтингов
plt.figure(figsize=(10, 5))
sns.barplot(data=top10_wl, x='weighted_loyalty', y='customer_id',
            hue='customer_id', palette='mako', legend=False)
plt.title('Топ-10 клиентов по взвешенной лояльности (Weighted Loyalty)')
plt.xlabel('Weighted Loyalty')
plt.ylabel('ID Клиента')
plt.tight_layout()
plt.show()


print("\n=== ЗАДАЧА 10: Подготовка финального датасета ===")
# Сохранение датасета [cite: 143]
columns_to_keep = ['customer_id', 'city', 'customer_class', 'churn_flag',
                   'purchase_intensity', 'digital_engagement', 'value_per_year',
                   'engagement_index', 'loyalty_spend', 'activity_value',
                   'engagement_value', 'weighted_loyalty']
final_columns = [col for col in columns_to_keep if col in df.columns]
dataset_ready = df[final_columns]

dataset_ready.to_csv('dataset_ready.csv', index=False)
print("Финальный датасет сохранен в файл 'dataset_ready.csv'.")
print("Размерность итогового файла:", dataset_ready.shape)

# ГРАФИК 10: Pairplot (Дашборд распределений) для ключевых метрик
features_for_pairplot = ['purchase_intensity', 'digital_engagement', 'engagement_index', 'churn_flag']
# Берем небольшую выборку, если датасет огромный (чтобы быстро построилось), или строим на всем
sns.pairplot(dataset_ready[features_for_pairplot], hue='churn_flag', palette='husl', corner=True)
plt.suptitle('Взаимосвязь ключевых метрик в финальном датасете', y=1.02)
plt.show()
