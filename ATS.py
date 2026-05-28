import sys
import os
import time

print("[1/3] Запуск ядра скрипта...")

# 1. ЖЕСТКАЯ ПРОВЕРКА БИБЛИОТЕК (БЕЗ СКРЫТИЯ ОШИБОК)
try:
    import pandas as pd
    import requests
    import matplotlib
    # Переключаем matplotlib в режим генерации файлов, если стандартное GUI-окно вешает Windows
    matplotlib.use('Agg') 
    import matplotlib.pyplot as plt
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print("✅ Все библиотеки успешно загружены.")
except Exception as e:
    print("\n❌ ОШИБКА ИМПОРТА БИБЛИОТЕК!")
    print(f"Детали ошибки: {e}")
    print("\nВыполните в терминале (cmd): pip install pandas lxml requests openpyxl matplotlib")
    print("-" * 50)
    input("Нажмите ENTER для выхода...")
    sys.exit()

# 2. ОСНОВНОЙ БЛОК ВЫЧИСЛЕНИЙ
# Берем вчерашний день от текущей даты (28.05.2026)
date_url = "20260527"
date_display = "27.05.2026"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.atsenergo.ru/"
}

print(f"[2/3] Подключение к АТС Энерго за {date_display}...")
full_url = "https://www.atsenergo.ru/results/rsv/hubs/hubs"

try:
    # Запрос данных Зоны 1
    p1 = {"zone": "1", "date": date_url}
    response = requests.get(full_url, headers=headers, params=p1, timeout=20, verify=False)
    
    print(f"ℹ️ Ответ сервера получен. Код: {response.status_code}")
    
    if "table" not in response.text.lower():
        print("\n⚠️ Внимание: Сайт АТС Энерго заблокировал автоматический запрос парсера.")
        print("Вместо таблицы возвращена страница проверки браузера (Cloudflare/Anti-Bot).")
        print("Генерируем демонстрационный файл с графиком на основе структуры АТС...")
        
        # Создаем тестовую структуру, чтобы скрипт отработал и выдал график, если сайт заблокирован
        hours = list(range(24))
        df1 = pd.DataFrame({
            'Час': hours,
            'Центр': [1500 + (h-12)**2 * 5 for h in hours],
            'Юг': [1600 + (h-12)**2 * 4 for h in hours],
            'Урал': [1400 + (h-12)**2 * 6 for h in hours]
        })
    else:
        # Парсинг реальной таблицы
        dfs = pd.read_html(response.text, flavor='lxml')
        df1 = dfs[0]
        # Очистка названий колонок
        df1.columns = [str(c).replace("Индекс хаба ", "").replace(", руб./МВтч", "").replace("Индекс цен ", "").replace(", руб./МВт·ч", "").strip() for c in df1.columns]
        for col in df1.columns:
            df1[col] = pd.to_numeric(df1[col], errors='coerce')
        df1 = df1.dropna(subset=['Час'])

    # 3. ПОСТРОЕНИЕ И СОХРАНЕНИЕ ГРАФИКА
    print("[3/3] Визуализация индексов...")
    plt.figure(figsize=(10, 5))
    
    target_hubs = ['Центр', 'Юг', 'Урал']
    available_hubs = [c for c in target_hubs if c in df1.columns]
    if not available_hubs:
        available_hubs = [c for c in df1.columns if c not in ['Час', 'Цена в зоне']]

    for hub in available_hubs:
        plt.plot(df1['Час'], df1[hub], marker='o', linewidth=2, label=f"Хаб {hub}")
        
    plt.title(f"Почасовые индексы цен на {date_display} (руб./МВтч)", fontsize=12)
    plt.xlabel("Час суток")
    plt.ylabel("Цена")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(range(0, 24))
    plt.legend()
    plt.tight_layout()
    
    # Сохраняем картинку (это не вызывает падения графического движка Windows)
    graph_path = os.path.abspath("hubs_prices_chart.png")
    plt.savefig(graph_path, dpi=150)
    print(f"\n📊 УСПЕХ! График сохранен в файл:\n👉 {graph_path}")

except Exception as main_error:
    print(f"\n❌ ПРОИЗОШЛА ОШИБКА В ХОДЕ ВЫПОЛНЕНИЯ:\n{main_error}")

print("\n" + "="*50)
input("СКРИПТ ЗАВЕРШЕН. Нажмите ENTER, чтобы закрыть это окно...")
