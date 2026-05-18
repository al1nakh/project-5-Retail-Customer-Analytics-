import os
import pandas as pd
import logging
from abc import ABC, abstractmethod

# task7
logging.basicConfig(  # чтобы записывалось все и в случае ошибки найти
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analytics.log', mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


# task1
class Client:
    def __init__(self, customer_id, total_spent, loyalty_score, purchase_frequency, returns_count):
        self.customer_id = customer_id
        self.total_spent = total_spent
        self.loyalty_score = loyalty_score
        self.purchase_frequency = purchase_frequency
        self.returns_count = returns_count

    def value(self):
        """Возвращает оценку ценности клиента (Total Spent * Loyalty Score)."""
        return self.total_spent * self.loyalty_score

    def risk(self):
        """Возвращает оценку риска возвратов."""
        return self.returns_count / (self.purchase_frequency + 1)


# task5 (Класс-наследник)
class VIPClient(Client):
    def __init__(self, customer_id, total_spent, loyalty_score, purchase_frequency, returns_count, vip_status=True):
        super().__init__(customer_id, total_spent, loyalty_score, purchase_frequency,
                         returns_count)  # наследник берет инф от родителя
        self.vip_status = vip_status

    def value(self):
        return super().value() * 1.1


# task5 (Фабрика)
class ClientFactory:
    @staticmethod
    def create_client(row):
        if row['loyalty_score'] > 80 or row['total_spent'] > 7000:
            return VIPClient(
                customer_id=row['customer_id'],
                total_spent=row['total_spent'],
                loyalty_score=row['loyalty_score'],
                purchase_frequency=row['purchase_frequency'],
                returns_count=row['returns_count']
            )
        else:
            return Client(
                customer_id=row['customer_id'],
                total_spent=row['total_spent'],
                loyalty_score=row['loyalty_score'],
                purchase_frequency=row['purchase_frequency'],
                returns_count=row['returns_count']
            )


# Применение Фабрики для Задачи 1
data_path_for_task1 = '../data/retail_customer_loyalty_realistic.csv'
if os.path.exists(data_path_for_task1):
    df = pd.read_csv(data_path_for_task1)
    subset = df.head(20)
    clients_list = []
    for _, row in subset.iterrows():
        # ИЗМЕНЕНО: Объекты создаются централизованно через Фабрику
        clients = ClientFactory.create_client(row)
        clients_list.append(clients)

    print(f"\n{'Customer ID':<15} | {'Value (Total*Score)':<20} | {'Risk':<10}")
    print("-" * 50)
    for c in clients_list:
        print(f"{c.customer_id:<15} | {c.value():<20.2f} | {c.risk():<10.4f}")
    print()
else:
    logging.warning(f"Файл {data_path_for_task1} не найден для проверки Задачи 1.")


# 2 task
class RetailAnalytics:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.clients = []
        logging.info("Инициализация класса RetailAnalytics.")

    def load_data(self):
        if not os.path.exists(self.file_path):
            logging.error(f'Ошибка: файл {self.file_path} не найден')
            return self
        self.df = pd.read_csv(self.file_path)
        logging.info(f"--- Данные загружены. Всего строк: {len(self.df)} ---")  # Исправлено на INFO
        return self

    def clean_data(self):
        if self.df is None:
            logging.error("Ошибка: Сначала загрузите данные!")
            return self

        initial_count = len(self.df)
        self.df = self.df.drop_duplicates()
        self.df = self.df.fillna(0)
        logging.info(f"--- Очистка завершена. Удалено строк: {initial_count - len(self.df)} ---")  # Исправлено на INFO
        return self

    def basic_stats(self):
        if self.df is None:
            return "Данные отсутствует"
        return self.df[['total_spent', 'loyalty_score', 'purchase_frequency']].describe()

    # task3
    def feature_engineering(self):
        if self.df is None:
            logging.warning("Ошибка: Нет данных для генерации признаков.")
            return self
        logging.info("--- 3. Запуск Feature Engineering... ---")
        self.df['client_value'] = self.df['total_spent'] * self.df['loyalty_score']
        self.df['client_risk'] = self.df['returns_count'] / (self.df['purchase_frequency'] + 1)
        logging.info("Добавлены новые метрики: 'client_value' и 'client_risk'")
        return self

    def filter_high_value_clients(self, min_value=200000):
        if self.df is None:
            logging.warning("Ошибка: Нет данных для фильтрации.")
            return self

        logging.info(f"Фильтрация клиентов по порогу ценности >= {min_value}")
        self.df = self.df[self.df['client_value'] >= min_value]
        logging.info(f"--- 4. Фильтрация: Осталось VIP-клиентов: {len(self.df)} ---")
        return self

    def export_results(self, output_path='vip_clients_report.csv'):
        if self.df is None:
            logging.error("Ошибка: Нет данных для экспорта.")
            return self
        self.df.to_csv(output_path, index=False)
        logging.info(f"--- 5. Результаты успешно экспортированы в файл: {output_path} ---")
        return self

path_to_csv = '../data/retail_customer_loyalty_realistic.csv'
logging.info("--- ЗАПУСК ТЕСТА ЗАДАЧИ №2 ---")
analytics = RetailAnalytics(path_to_csv)
analytics.load_data()
analytics.clean_data()
print("\nБазовая статистика по ключевым метрикам:")
print(analytics.basic_stats(), "\n")

logging.info("--- ЗАПУСК ПОЛНОГО PIPELINE (ЗАДАЧА №3) ---")
pipeline_analytics = RetailAnalytics(path_to_csv)
pipeline_analytics.load_data() \
    .clean_data() \
    .feature_engineering() \
    .filter_high_value_clients(min_value=150000) \
    .export_results('final_vip_report.csv')


# task4
class ScoringStrategy(ABC):
    @abstractmethod
    def calculate(self, client):
        pass


class SpendStrategy(ScoringStrategy):
    def calculate(self, client):
        return client.total_spent


class LoyaltyStrategy(ScoringStrategy):
    def calculate(self, client):
        return client.loyalty_score


class EngagementStrategy(ScoringStrategy):
    def calculate(self, client):
        return client.purchase_frequency - client.returns_count


# =========================================================
# Тестирование Задачи 4 — Паттерн Стратегия
# =========================================================
logging.info("--- ЗАПУСК ТЕСТА ЗАДАЧИ №4 (ПАТТЕРН СТРАТЕГИЯ) ---")

spend_strategy = SpendStrategy()
loyalty_strategy = LoyaltyStrategy()
engagement_strategy = EngagementStrategy()

if clients_list:
    test_client = clients_list[0]

    print(f"\nПроверка стратегий для клиента: {test_client.customer_id}")
    print(
        f"Исходные данные: Потрачено={test_client.total_spent}, Лояльность={test_client.loyalty_score}, Частота={test_client.purchase_frequency}, Возвраты={test_client.returns_count}")
    print("-" * 65)

    current_strategy = spend_strategy
    print(f"Выбрана SpendStrategy      -> Оценка клиента: {current_strategy.calculate(test_client):.2f}")

    current_strategy = loyalty_strategy
    print(f"Выбрана LoyaltyStrategy    -> Оценка клиента: {current_strategy.calculate(test_client):.2f}")

    current_strategy = engagement_strategy
    print(f"Выбрана EngagementStrategy -> Оценка клиента: {current_strategy.calculate(test_client):.2f}")
    print("-" * 65 + "\n")
else:
    logging.warning("Список clients_list пуст. Невозможно протестировать стратегии.")

# =========================================================
# Тестирование Задачи 5 — Паттерн Фабрика
# =========================================================
logging.info("--- ЗАПУСК ТЕСТА ЗАДАЧИ №5 (ПАТТЕРН ФАБРИКА) ---")
if clients_list:
    print(f"{'Customer ID':<15} | {'Распределенный тип класса фабрикой':<40}")
    print("-" * 60)
    for c in clients_list[:10]:  # Посмотрим первые 10 для наглядности
        class_type = "VIPClient (Премиум)" if isinstance(c, VIPClient) else "Client (Обычный)"
        print(f"{c.customer_id:<15} | {class_type:<40}")
    print("-" * 60 + "\n")