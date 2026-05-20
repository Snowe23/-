import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "books.json"

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        self.books = []
        self.load_data()

        # GUI components
        self.create_input_frame()
        self.create_filter_frame()
        self.create_tree_view()
        self.create_button_frame()

        self.refresh_treeview()

    def create_input_frame(self):
        """Форма для ввода данных книги."""
        frame = tk.LabelFrame(self.root, text="Добавить книгу", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Название:").grid(row=0, column=0, sticky="w", pady=2)
        self.title_entry = tk.Entry(frame, width=30)
        self.title_entry.grid(row=0, column=1, pady=2)

        tk.Label(frame, text="Автор:").grid(row=1, column=0, sticky="w", pady=2)
        self.author_entry = tk.Entry(frame, width=30)
        self.author_entry.grid(row=1, column=1, pady=2)

        tk.Label(frame, text="Жанр:").grid(row=2, column=0, sticky="w", pady=2)
        self.genre_entry = tk.Entry(frame, width=30)
        self.genre_entry.grid(row=2, column=1, pady=2)

        tk.Label(frame, text="Страниц:").grid(row=3, column=0, sticky="w", pady=2)
        self.pages_entry = tk.Entry(frame, width=30)
        self.pages_entry.grid(row=3, column=1, pady=2)

        add_btn = tk.Button(frame, text="Добавить книгу", command=self.add_book, bg="#4CAF50", fg="white")
        add_btn.grid(row=4, column=0, columnspan=2, pady=10)

    def create_filter_frame(self):
        """Фильтрация по жанру и страницам."""
        frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Фильтр по жанру:").grid(row=0, column=0, sticky="w")
        self.filter_genre_entry = tk.Entry(frame, width=20)
        self.filter_genre_entry.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Страниц больше:").grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.filter_pages_entry = tk.Entry(frame, width=10)
        self.filter_pages_entry.grid(row=0, column=3, padx=5)

        filter_btn = tk.Button(frame, text="Применить фильтр", command=self.apply_filter, bg="#2196F3", fg="white")
        filter_btn.grid(row=0, column=4, padx=10)

        reset_btn = tk.Button(frame, text="Сбросить фильтр", command=self.reset_filter, bg="#FF9800", fg="white")
        reset_btn.grid(row=0, column=5)

    def create_tree_view(self):
        """Таблица для отображения книг."""
        columns = ("Название", "Автор", "Жанр", "Страниц")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def create_button_frame(self):
        """Кнопки сохранения, загрузки, удаления."""
        frame = tk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=5)

        save_btn = tk.Button(frame, text="Сохранить в JSON", command=self.save_data, bg="#9C27B0", fg="white")
        save_btn.pack(side="left", padx=5)

        load_btn = tk.Button(frame, text="Загрузить из JSON", command=self.load_data, bg="#009688", fg="white")
        load_btn.pack(side="left", padx=5)

        delete_btn = tk.Button(frame, text="Удалить выбранную", command=self.delete_selected, bg="#F44336", fg="white")
        delete_btn.pack(side="left", padx=5)

    def add_book(self):
        """Добавление книги с валидацией."""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages_str = self.pages_entry.get().strip()

        if not title or not author or not genre or not pages_str:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        if not pages_str.isdigit():
            messagebox.showerror("Ошибка", "Количество страниц должно быть числом!")
            return

        pages = int(pages_str)

        self.books.append({
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        })

        self.clear_inputs()
        self.refresh_treeview()
        messagebox.showinfo("Успех", "Книга добавлена!")

    def clear_inputs(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

    def refresh_treeview(self, filtered_books=None):
        """Обновление таблицы (с фильтром или без)."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        data = filtered_books if filtered_books is not None else self.books
        for book in data:
            self.tree.insert("", "end", values=(book["title"], book["author"], book["genre"], book["pages"]))

    def apply_filter(self):
        """Фильтрация по жанру (частичное совпадение) и страницам."""
        genre_filter = self.filter_genre_entry.get().strip().lower()
        pages_filter = self.filter_pages_entry.get().strip()

        filtered = self.books[:]

        if genre_filter:
            filtered = [b for b in filtered if genre_filter in b["genre"].lower()]

        if pages_filter:
            if pages_filter.isdigit():
                min_pages = int(pages_filter)
                filtered = [b for b in filtered if b["pages"] > min_pages]
            else:
                messagebox.showerror("Ошибка", "Фильтр страниц должен быть числом!")
                return

        self.refresh_treeview(filtered)

    def reset_filter(self):
        """Сброс фильтрации."""
        self.filter_genre_entry.delete(0, tk.END)
        self.filter_pages_entry.delete(0, tk.END)
        self.refresh_treeview()

    def delete_selected(self):
        """Удаление выбранной книги."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите книгу для удаления!")
            return

        for item in selected:
            values = self.tree.item(item, "values")
            # Поиск книги по названию и автору
            for book in self.books[:]:
                if book["title"] == values[0] and book["author"] == values[1]:
                    self.books.remove(book)
                    break

        self.refresh_treeview()
        messagebox.showinfo("Успех", "Книга удалена!")

    def save_data(self):
        """Сохранение в JSON."""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_data(self):
        """Загрузка из JSON."""
        if not os.path.exists(DATA_FILE):
            messagebox.showwarning("Нет файла", "Файл books.json не найден.")
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.books = json.load(f)
            self.reset_filter()
            messagebox.showinfo("Успех", "Данные загружены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()