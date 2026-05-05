import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os

# --- Настройки ---
DATA_FILE = "data/weather_data.json"

# --- Работа с данными (JSON) ---
def load_data():
    """Загружает записи из файла JSON. Если файла нет, возвращает пустой список."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_data(data):
    """Сохраняет список записей в файл JSON."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# --- Основная логика приложения ---
class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Дневник погоды")
        self.root.geometry("700x600")

        # Загружаем данные при запуске
        self.records = load_data()

        # Создаём интерфейс
        self.create_widgets()
        self.update_listbox()

    def create_widgets(self):
        # Панель вкладок (Notebook)
        self.tab_control = ttk.Notebook(self.root)
        
        self.tab_add = ttk.Frame(self.tab_control)
        self.tab_filter = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_add, text="Добавить запись")
        self.tab_control.add(self.tab_filter, text="Фильтровать записи")
        self.tab_control.pack(expand=1, fill="both")

        # --- Вкладка "Добавить запись" ---
        # Дата
        tk.Label(self.tab_add, text="Дата:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.date_entry = DateEntry(self.tab_add, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_entry.grid(row=0, column=1, padx=10, pady=5)

        # Температура
        tk.Label(self.tab_add, text="Температура (°C):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.temp_entry = tk.Entry(self.tab_add)
        self.temp_entry.grid(row=1, column=1, padx=10, pady=5)

        # Описание
        tk.Label(self.tab_add, text="Описание:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.desc_entry = tk.Entry(self.tab_add, width=40)
        self.desc_entry.grid(row=2, column=1, padx=10, pady=5)

        # Осадки
        tk.Label(self.tab_add, text="Осадки:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.precip_var = tk.BooleanVar()
        tk.Checkbutton(self.tab_add, text="Да", variable=self.precip_var).grid(row=3, column=1, padx=10, pady=5)

        # Кнопка добавления
        tk.Button(self.tab_add, text="Добавить запись", command=self.add_record).grid(
            row=4, columnspan=2, pady=15)

        # --- Вкладка "Фильтровать записи" ---
        # Фильтр по дате
        tk.Label(self.tab_filter, text="Дата (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.date_filter = tk.Entry(self.tab_filter)
        self.date_filter.grid(row=0, column=1, padx=10, pady=5)

        # Фильтр по температуре
        tk.Label(self.tab_filter, text="Температура выше (°C):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.temp_filter = tk.Entry(self.tab_filter)
        self.temp_filter.grid(row=1, column=1, padx=10, pady=5)

        # Кнопка фильтра
        tk.Button(self.tab_filter, text="Применить фильтр", command=self.filter_records).grid(
            row=2, columnspan=2, pady=15)

         # --- Список записей (общий для всех вкладок) ---
         # Помещаем его под вкладками
         self.listbox = tk.Listbox(self.root, width=90, height=15)
         self.listbox.pack(pady=(20, 0))

    def add_record(self):
        """Обрабатывает добавление новой записи с проверкой данных."""
        
         # Проверка температуры (должно быть число)
         try:
             temp = float(self.temp_entry.get())
         except ValueError:
             messagebox.showerror("Ошибка", "Температура должна быть числом")
             return

         # Проверка описания (не пустое)
         description = self.desc_entry.get().strip()
         if not description:
             messagebox.showerror("Ошибка", "Описание не может быть пустым")
             return

         # Сборка записи
         record = {
             "date": self.date_entry.get_date().strftime("%Y-%m-%d"),
             "temperature": temp,
             "description": description,
             "precipitation": "да" if self.precip_var.get() else "нет"
         }
         
         # Добавление в список и сохранение
         self.records.append(record)
         save_data(self.records)
         
         # Очистка полей и обновление списка
         self.temp_entry.delete(0, tk.END)
         self.desc_entry.delete(0, tk.END)
         self.update_listbox()

    def filter_records(self):
       """Фильтрует записи по дате и/или температуре."""
       filtered = self.records.copy()
       
       selected_date = self.date_filter.get().strip()
       if selected_date:
           filtered = [r for r in filtered if r["date"] == selected_date]
       
       temp_min = self.temp_filter.get().strip()
       if temp_min:
           try:
               temp_min = float(temp_min)
               filtered = [r for r in filtered if r["temperature"] >= temp_min]
           except ValueError:
               pass  # Игнорируем ошибку ввода температуры

       self.display_records(filtered)

    def display_records(self, records_to_show):
       """Отображает переданный список записей в виджете Listbox."""
       self.listbox.delete(0, tk.END) # Очистка списка перед выводом
       for r in records_to_show:
           self.listbox.insert(tk.END,
               f"{r['date']} | {r['temperature']}°C | {r['description']} | Осадки: {r['precipitation']}")

    def update_listbox(self):
       """Обновляет список записей (показывает все)."""
       self.display_records(self.records)


# --- Запуск приложения ---
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()
