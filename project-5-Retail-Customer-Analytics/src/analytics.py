import os
import pandas as pd
import logging
from abc import ABC, abstractmethod
import time

# task7
logging.basicConfig(  # чтобы записывалось все и в случае ошибки найти
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analytics.log', mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

#task8
# =========================================================
# Задача 8 — Словарь конфигурации (Глобальные настройки)
# =========================================================
CONFIG = {
    'vip_threshold': 150000,       # Порог для фильтрации VIP в пайплайне
    'vip_bonus_coeff': 1.15,       # Бонус-коэффициент для ценности VIP-клиента (был 1.1)
    'factory_vip_loyalty': 80,     # Порог лояльности в фабрике для перевода в VIP
    'factory_vip_spent': 7000       # Порог трат в фабрике для перевода в VIP
}

# task1
class Client:
    def __init__(self, customer_id, total_spent, loyalty_score, purchase_frequency, returns_count):
        self.customer_id = customer_id
        self.total_spent = total_spent
        self.loyalty_score = loyalty_score
        self.purchase_frequency = purchase_frequency
        self.returns_count = returns_count
        self._cache = {} # Задача 6: Кэш (словарь) для мемоизации вычислений

    def value(self):
        """Возвращает оценку ценности клиента (Total Spent * Loyalty Score)."""
        if 'value' in self._cache:
            return self._cache['value']
        result = self.total_spent * self.loyalty_score
        self._cache['value'] = result
        return result

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
        return super().value() * CONFIG['vip_bonus_coeff'] # Используем коэффициент из CONFIG (Задача 8)


# task5 (Фабрика)
class ClientFactory:
    @staticmethod
    def create_client(row):
        if row['loyalty_score'] > CONFIG['factory_vip_loyalty'] or row['total_spent'] > CONFIG['factory_vip_spent']:
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


# 2 task
class RetailAnalytics:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.clients_objects = []
        logging.info("Инициализация класса RetailAnalytics.")

    def load_data(self):
        if not os.path.exists(self.file_path):
            logging.error(f'Ошибка: файл {self.file_path} не найден')
            return self

        self.df = pd.read_csv(self.file_path, low_memory=False)

        #  Проверяем, нет ли отрицательных значений в численных колонках
        # Проверим расходы, баллы лояльности и частоту покупок
        numeric_cols = ['total_spent', 'loyalty_score', 'purchase_frequency', 'returns_count']
        for col in numeric_cols:
            if col in self.df.columns:
                # Превращаем строки в NaN, а NaN заменяем на 0
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)

        # Задача 9 — Валидация данных перед началом работы
        # 1. Проверяем, нет ли пустых значений в колонке customer_id
        if self.df['customer_id'].isnull().any():
            empty_count = self.df['customer_id'].isnull().sum()
            raise ValueError(f"Критическая ошибка валидации: обнаружено {empty_count} пустых значений в customer_id!")

        #2. Проверяем, нет ли отрицательных значений в численных колонках
        for col in numeric_cols:
            if (self.df[col] < 0).any():
                negative_count = (self.df[col] < 0).sum()
                raise ValueError(f"Критическая ошибка валидации: в колонке '{col}' найдено {negative_count} отрицательных значений!")

        logging.info("--- Валидация успешна: пустых ID и отрицательных значений не обнаружено! ---")
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

    # =========================================================
    # ЗАДАЧА 10 — ПОЛНЫЙ ФИНАЛЬНЫЙ ПАЙПЛАЙН (АРХИТЕКТУРА PRODUCTION)
    # =========================================================
    def run_full_pipeline(self, output_filename='final_production_report.csv'):
        """Объединяет все шаги, паттерны проектирования и выводит итоговые метрики."""
        logging.info("=== ЗАПУСК ФИНАЛЬНОЙ АРХИТЕКТУРНОЙ СИСТЕМЫ (ЗАДАЧА №10) ===")

        # 1. Загрузка и Валидация -> Очистка -> Сбор признаков
        self.load_data()
        self.clean_data()

        # 2. Создание объектов через Фабрику (Задача 5)
        logging.info("Генерация ООП-объектов клиентов через ClientFactory...")
        for _, row in self.df.iterrows():
            client_obj = ClientFactory.create_client(row)
            self.clients_objects.append(client_obj)

        # 3. Анализ с использованием Стратегий (Задача 4) и Кэша (Задача 6)
        logging.info("Применение аналитических стратегий оценки...")
        spend_strat = SpendStrategy()

        # Посчитаем общую сумму ценности всех клиентов на базе объектов
        total_system_value = sum(c.value() for c in self.clients_objects)

        # 4. Фильтрация и экспорт данных
        self.feature_engineering()
        self.filter_high_value_clients(min_value=CONFIG['vip_threshold'])
        self.export_results(output_filename)

        # 5. Вывод итоговых метрик для бизнеса
        print("\n" + "=" * 50)
        print("     ИТОГОВЫЙ ОТЧЕТ АНАЛИТИЧЕСКОЙ СИСТЕМЫ")
        print("=" * 50)
        print(f" Всего обработано клиентов:          {len(self.clients_objects)}")
        print(f" Из них отфильтровано как VIP:       {len(self.df)}")
        print(f" Общая суммарная ценность (с кэшем):  {total_system_value:,.2f}")
        print(f" Файл с результатами сохранен как:   {output_filename}")
        print("=" * 50 + "\n")
        return self

    # =========================================================
    # ТОЧКА ВХОДА (ЗАПУСК ВСЕХ ТЕСТОВ И ФИНАЛЬНОГО ПАЙПЛАЙНА)
    # =========================================================
if __name__ == "__main__":
    path_to_csv = '../data/retail_customer_loyalty_realistic.csv'

    # Подготовка глобального списка клиентов clients_list для тестов Задач 4, 5, 6
    if os.path.exists(path_to_csv):
        df_temp = pd.read_csv(path_to_csv).head(20)

        # ОЧИСТКА ТИПОВ ДАННЫХ (Защита от TypeError):
        for col in ['total_spent', 'loyalty_score', 'purchase_frequency', 'returns_count']:
            if col in df_temp.columns:
                df_temp[col] = pd.to_numeric(df_temp[col], errors='coerce').fillna(0)

        clients_list = [ClientFactory.create_client(row) for _, row in df_temp.iterrows()]
    else:
        clients_list = []

    # --- ТЕСТ ЗАДАЧИ №2 ---
    logging.info("--- ЗАПУСК ТЕСТА ЗАДАЧИ №2 ---")
    analytics = RetailAnalytics(path_to_csv)
    analytics.load_data()
    analytics.clean_data()
    print("\nБазовая статистика по ключевым метрикам:")
    print(analytics.basic_stats(), "\n")

    # --- ТЕСТ ЗАДАЧИ №3 ---
    logging.info("--- ЗАПУСК ПОЛНОГО PIPELINE (ЗАДАЧА №3) ---")
    pipeline_analytics = RetailAnalytics(path_to_csv)
    pipeline_analytics.load_data() \
        .clean_data() \
        .feature_engineering() \
        .filter_high_value_clients(min_value=CONFIG['vip_threshold']) \
        .export_results('final_vip_report.csv')

    # --- ТЕСТ ЗАДАЧИ №4 (ПАТТЕРН СТРАТЕГИЯ) ---
    logging.info("--- ЗАПУСК ТЕСТА ЗАДАЧИ №4 (ПАТТЕРН СТРАТЕГИЯ) ---")
    if clients_list:
        test_client = clients_list[0]
        spend_strategy = SpendStrategy()
        loyalty_strategy = LoyaltyStrategy()
        engagement_strategy = EngagementStrategy()

        print(f"\nПроверка стратегий для клиента: {test_client.customer_id}")
        print("-" * 65)
        current_strategy = spend_strategy
        print(f"Выбрана SpendStrategy      -> Оценка клиента: {current_strategy.calculate(test_client):.2f}")
        current_strategy = loyalty_strategy
        print(f"Выбрана LoyaltyStrategy    -> Оценка клиента: {current_strategy.calculate(test_client):.2f}")
        current_strategy = engagement_strategy
        print(f"Выбрана EngagementStrategy -> Оценка клиента: {current_strategy.calculate(test_client):.2f}")
        print("-" * 65 + "\n")
    else:
        logging.warning("Список clients_list пуст. Тест стратегий пропущен.")

    # --- ТЕСТ ЗАДАЧИ №5 (ПАТТЕРН ФАБРИКА) ---
    logging.info("--- ЗАПУСК ТЕСТА ЗАДАЧИ №5 (ПАТТЕРН ФАБРИКА) ---")
    if clients_list:
        print(f"{'Customer ID':<15} | {'Распределенный тип класса фабрикой':<40}")
        print("-" * 60)
        for c in clients_list[:10]:
            class_type = "VIPClient (Премиум)" if isinstance(c, VIPClient) else "Client (Обычный)"
            print(f"{c.customer_id:<15} | {class_type:<40}")
        print("-" * 60 + "\n")

    # --- ТЕСТ ЗАДАЧИ №6 (КЭШИРОВАНИЕ) ---
    logging.info("--- ЗАПУСК ТЕСТА ЗАДАЧИ №6 (КЭШИРОВАНИЕ) ---")
    if clients_list:
        cache_client = clients_list[0]
        print(f"Тестируем кэширование на клиенте: {cache_client.customer_id}\n")

        start_time = time.perf_counter()
        val1 = cache_client.value()
        first_call_time = time.perf_counter() - start_time
        print(f"1-й вызов (Расчет): Результат = {val1:.2f}, Время = {first_call_time:.8f} сек.")
        print("-" * 60)

        start_time = time.perf_counter()
        val2 = cache_client.value()
        second_call_time = time.perf_counter() - start_time
        print(f"2-й вызов (Из кэша): Результат = {val2:.2f}, Время = {second_call_time:.8f} сек.")
        print("-" * 60 + "\n")

    # --- ТЕСТ ЗАДАЧИ №8 (КОНФИГУРАЦИЯ) ---
    logging.info("--- ЗАПУСК ТЕСТА ЗАДАЧИ №8 (КОНФИГУРАЦИЯ) ---")
    print(f"Текущая конфигурация системы:")
    print(f" - Порог перевода фабрикой в VIP (Лояльность): > {CONFIG['factory_vip_loyalty']}")
    print(f" - Бонусный коэффициент для VIP-клиентов: {CONFIG['vip_bonus_coeff']}")
    print(f" - Минимальный порог фильтрации для отчета: {CONFIG['vip_threshold']}")
    print("-" * 60 + "\n")

    # --- ТЕСТ ЗАДАЧИ №9 (ВАЛИДАЦИЯ ДАННЫХ) ---
    logging.info("--- ЗАПУСК ТЕСТА ЗАДАЧИ №9 (ВАЛИДАЦИЯ ДАННЫХ) ---")
    bad_data = pd.DataFrame({
        'customer_id': ['CUST001', None, 'CUST003'],
        'total_spent': [5000.0, 1200.0, -150.0],
        'loyalty_score': [70, 50, 20],
        'purchase_frequency': [15, 10, 5],
        'returns_count': [1, 0, 2]
    })

    print("Тестируем симуляцию проверки плохих данных:")
    try:
        if bad_data['customer_id'].isnull().any():
            raise ValueError("Критическая ошибка: В данных обнаружен пустой Customer ID!")
    except ValueError as e:
        print(f" [ПЕРЕХВАЧЕНО] Перехвачена системная ошибка: {e}")

    try:
        if (bad_data['total_spent'] < 0).any():
            raise ValueError("Критическая ошибка: Сумма расходов не может быть отрицательной!")
    except ValueError as e:
        print(f" [ПЕРЕХВАЧЕНО] Перехвачена системная ошибка: {e}")
    print("-" * 60 + "\n")

    # --- ФИНАЛЬНЫЙ ЗАПУСК ЗАДАЧИ №10 (ПОЛНЫЙ ПАЙПЛАЙН) ---
    final_system = RetailAnalytics(path_to_csv)
    final_system.run_full_pipeline('final_production_report.csv')