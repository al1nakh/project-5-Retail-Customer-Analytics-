import pandas as pd
import numpy as np
import os

base_dir = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(base_dir, 'retail_customer_loyalty_realistic.csv')

df = pd.read_csv(file_path)

# 1-тапсырма: DataFrame-ті сандық NumPy массивтеріне айналдыру және оның құрылымын тексеру
numeric_cols = [
    'age', 'total_spent', 'avg_purchase_value', 'loyalty_score',
    'purchase_frequency', 'returns_count', 'store_visits_per_month',
    'website_visits_per_month'
]
numeric_data = df[numeric_cols].to_numpy()
print(numeric_data.shape)
print(numeric_data[:5])
print(numeric_data.dtype)

# 2-тапсырма: NumPy көмегімен негізгі статистикалық көрсеткіштерді (орташа мән, медиана, ауытқу) есептеу.
means = np.mean(numeric_data, axis=0)
medians = np.median(numeric_data, axis=0)
stds = np.std(numeric_data, axis=0)

for i, col in enumerate(numeric_cols):
    print(f"{col} - Mean: {means[i]:.2f}, Median: {medians[i]:.2f}, Std: {stds[i]:.2f}")

# 3-тапсырма: Логикалық (бульдік) маскаларды қолдана отырып, деректерді күрделі шарттар бойынша сүзу.
percentile_75 = np.percentile(df['total_spent'].dropna(), 75)
mask_spent = df['total_spent'] > percentile_75
mask_loyalty = df['loyalty_score'] > 70
combined_mask = mask_spent & mask_loyalty
indices = np.where(combined_mask)[0]
print(df.iloc[indices].head(10))

# 4-тапсырма: Клиенттің тәуекел деңгейін көрсететін арнайы (custom) метриканы есептеу.
df['risk_score'] = (df['returns_count'] / (df['purchase_frequency'] + 1)) + ((100 - df['loyalty_score']) / 100)
print(df.nlargest(10, 'risk_score'))

# 5-тапсырма: Массивті толық сұрыптамай-ақ, ең жоғары көрсеткіші бар топ-10 клиентті жылдам табу.
total_spent_array = df['total_spent'].to_numpy()
top_10_indices = np.argpartition(total_spent_array, -10)[-10:]
top_10_indices_sorted = top_10_indices[np.argsort(total_spent_array[top_10_indices])][::-1]
print(df.iloc[top_10_indices_sorted])

# 6-тапсырма: Деректердің сырғымалы орташа мәнін (rolling mean) цикл арқылы қолмен есептеу.
window_size = 5
total_spent_list = df['total_spent'].tolist()
rolling_mean = [np.nan] * (window_size - 1)

for i in range(len(total_spent_list) - window_size + 1):
    window = total_spent_list[i:i + window_size]
    rolling_mean.append(sum(window) / window_size)

df['rolling_mean_spent'] = rolling_mean

# 7-тапсырма: Клиенттердің сипаттамалары негізінде олардың арасындағы Евклид қашықтығын есептеу.
features = df[['total_spent', 'loyalty_score', 'purchase_frequency']].head(100).to_numpy()
normalized_features = (features - np.min(features, axis=0)) / (np.max(features, axis=0) - np.min(features, axis=0))
diffs = normalized_features[:, np.newaxis, :] - normalized_features[np.newaxis, :, :]
distance_matrix = np.sqrt(np.sum(diffs ** 2, axis=-1))

# 8-тапсырма: Категориялық деректерді (customer_segment) One-hot encoding әдісімен қолмен түрлендіру.
unique_segments = list(set(df['customer_segment'].dropna()))
for segment in unique_segments:
    df[f'segment_{segment}'] = (df['customer_segment'] == segment).astype(int)

# 9-тапсырма: Үлкен көлемді деректерді жадты үнемдеу үшін бөліктерге (батчтарға) бөліп өңдеу.
batch_size = 1000
batch_means = []
for i in range(0, len(df), batch_size):
    chunk = df.iloc[i:i + batch_size]
    batch_means.append(chunk['total_spent'].mean())

# 10-тапсырма: Деректер типтерін өзгерту арқылы жүйе жадын пайдалануды оңтайландыру.
memory_before = df.memory_usage(deep=True).sum()

float_cols = df.select_dtypes(include=['float64']).columns
df[float_cols] = df[float_cols].astype('float32')

int_cols = df.select_dtypes(include=['int64']).columns
df[int_cols] = df[int_cols].astype('int32')

memory_after = df.memory_usage(deep=True).sum()

print(f"Memory before: {memory_before}")
print(f"Memory after: {memory_after}")