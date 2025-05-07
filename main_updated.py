import tkinter as tk
from PIL import Image, ImageTk
import requests
import io

bg_color = 'black' #stała zmienna dla koloru tła
class ConsoleLogger: #klasa konsoli logów
    def __init__(self, parent):
        #ramka dla konsoli
        self.frame = tk.Frame(parent, bg=bg_color) #ramka i konfiguracja
        self.frame.grid(row=2, column=2, sticky="nse", pady=10, padx=10) #umieszczenie w siatce

        #konsola
        self.console = tk.Text(self.frame, height=8, bg=bg_color, fg="lime", state="disabled") #konsola i konfiguracja
        self.console.pack(fill="both", expand=True) #umieszczenie w siatce

    def log(self, message): #funkcja do logów
        self.console.config(state="normal") #odblokowuje konsole
        self.console.insert("end", message + "\n") #dodaje wiadomość
        self.console.see("end") #przewija kosole na koniec
        self.console.config(state="disabled") #blokuje konsole

class SearchBar: #klasa paska wyszukiwania
    def __init__(self, parent, on_search_callback):
        self.parent = parent #referencja do rodzica
        self.on_search_callback = on_search_callback #funkcja callback

        #tytuł "podaj zapytanie"
        self.query_label = tk.Label(parent, text="Podaj zapytanie:", bg=bg_color, fg="green", font=("Arial", 14)) #tytuł i konfiguracja
        self.query_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="n") #umieszczenie w siatce

        #pole do wpisania zapytania
        self.query_entry = tk.Entry(parent, width=40, bg=bg_color, fg="lime", insertbackground="lime") #pole tekstowe i konfiguracja
        self.query_entry.grid(row=1, column=1, sticky="we") #umieszczenie w siatce

        #przycisk wysyła zapytanie
        self.search_button = tk.Button(parent, text="Szukaj", command=self.search, bg=bg_color, fg="lime") #konfiguracja przycisku
        self.search_button.grid(row=1, column=2, sticky="w", padx=2) #umieszczenie w siatce

    def search(self):
        query = self.query_entry.get().strip() #pobiera tekst z pola entry i usuwa spacje
        self.on_search_callback(query) #callback z zapytaniem

class ImageGrid: #klasa z wyświetlaniem zdjęć
    def __init__(self, parent, logger):
        self.parent = parent #zapisanie rodzica
        self.logger = logger #zapisanie loggera

        #ramka na obrazy
        self.image_frame = tk.Frame(parent, bg=bg_color) #konfiguracja ramki
        self.image_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5) #umieszczenie w siatce

        self.images = [] #przechowanie obrazów

    def clear_images(self): #usuwa poprzednie miniatury obrazów
        for widget in self.image_frame.winfo_children(): #dla widgetów w ramce
            widget.destroy() #usuwa widgety
        self.images.clear() #usuwa obrazy w listy

    def display_image(self, title, url): #funkcja wyświetlająca obrazy
        try:
            img_data = requests.get(url).content #pobieranie danych obrazu
            img = Image.open(io.BytesIO(img_data)) #otwiera obraz danymi binarnymi
            img.thumbnail((150, 150)) #ustawia rozmiar miniatury obrazu
            photo = ImageTk.PhotoImage(img) #tworzy obiekt
            self.images.append(photo) #dodaje obrazy do listy

            col_count = 5 #max 5 obrazów w rzędzie
            index = len(self.images) - 1 #indeks obrazu
            row = index // col_count #wiersze
            col = index % col_count #kolumny

            frame = tk.Frame(self.image_frame, bg=bg_color) #ramka miniatury
            frame.grid(row=row, column=col, padx=10, pady=10) #umieszczenie na siatce w oknie programu

            label = tk.Label(frame, image=photo, bg=bg_color, cursor="hand2") #etykieta z obrazem
            label.pack() #umieszczenie etykiety
            label.bind("<Button-1>", lambda e: FullImageWindow(self.parent, title, url, self.logger)) #po kliknięciu miniatury otwiera pełny obraz w nowym oknie

            text = tk.Label(frame, text=title, wraplength=150, bg=bg_color, fg="lime") #dodaje tytuł obrazu
            text.pack() #umieszcza tekst w ramce

        except Exception as e: #jak wystąpi błąd
            self.logger.log(f"Nie udało się załadować obrazka: {e}") #loguje do konsoli

class FullImageWindow:
    def __init__(self, parent, title, url, logger):
        try:
            full_image_window = tk.Toplevel(parent) #nowe okno
            full_image_window.title(title) #tytuł okna
            full_image_window.configure(bg=bg_color) #kolor tła okna

            frame = tk.Frame(full_image_window, bg=bg_color) #ramka na obraz
            frame.pack(fill="both", expand=True) #umieszczenie w oknie

            close_button = tk.Button(frame, text="X", command=full_image_window.destroy, bg="white", fg="green", width=5) #przycisk do zamknięcia okna
            close_button.pack(anchor="ne", padx=5, pady=5) #umieszczenie przycisku

            img_data = requests.get(url).content #pobieranie danych obrazu
            image = Image.open(io.BytesIO(img_data)) #otwiera obraz danymi binarnymi
            photo = ImageTk.PhotoImage(image) #konwertuje na obiekt tkinter

            img_label = tk.Label(frame, image=photo, bg=bg_color) #etykieta obrazu
            img_label.image = photo  #referencja do obrazu
            img_label.pack() #umieszczenie obrazu w oknie

        except Exception as e: #jak wystąpi błąd
            logger.log(f"Błąd podczas otwierania pełnego obrazu: {e}") #log

class NasaApp:
    def __init__(self, root):
        self.root = root #główne okno
        self.root.title("NASA Image Search") #tytuł okna
        self.root.configure(bg=bg_color) #kolor tła okna
        self.root.geometry('1920x1080') #rozmiar okna

        #przycisk do zamknięcia okna
        self.exit_button = tk.Button(self.root, text="X", bg="white", fg="green", width=5, command=self.close) #konfiguracja przycisku
        self.exit_button.grid(row=0, column=2, sticky="ne") #umieszczenie na siatce

        self.logger = ConsoleLogger(self.root) #tworzenie konsoli
        self.image_grid = ImageGrid(self.root, self.logger) #tworzenie siatki obrazów
        self.search_bar = SearchBar(self.root, self.search_images) #tworzenie paska wyszukiwania

        #konfiguracja kolumn i wierszy grid
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1, uniform="a")
        self.root.grid_columnconfigure(1, weight=1, uniform="a")
        self.root.grid_columnconfigure(2, weight=1, uniform="a")

    def search_images(self, query): #wyszukiwanie obrazów
        if not query: #jeśli pole zapytania puste
            self.logger.log("Wpisz zapytanie!") #informuje w konsoli że pole entry jest puste
            return #przerwanie funkcji

        self.logger.log(f"Szukanie: {query}") #informuje w konsoli o wyszukaniu konkretnego zapytania
        self.image_grid.clear_images() #usunięcie starych obrazów

        try:
            #zapytanie do api
            response = requests.get("https://images-api.nasa.gov/search", params={"q": query, "media_type": "image"}) #wkleja zapytanie użytkownika do linku
            response.raise_for_status() #informuje o błędzie http jeśli jakiś wystąpi
            items = response.json().get("collection", {}).get("items", [])[:20] #pobiera do 20 obrazów

            if not items: #jak nie ma wyników
                self.logger.log("Brak wyników.") #informuje w konsoli o braku zdjęć pasujących do zapytania
                return

            for item in items: #dla każdego zdjęcia
                title = item["data"][0]["title"] #pobiera tytuł
                img_url = item["links"][0]["href"] #pobiera url
                self.image_grid.display_image(title, img_url) #pokazuje miniature zdjęcia

        except Exception as e: #jak wystąpi błąd
            self.logger.log(f"Błąd: {e}") #informuje o błędzie w konsoli

    def close(self):
        #zamyka program/funkcja do przycisków
        self.root.destroy()

if __name__ == "__main__": #czy program uruchamiany jest bezpośrednio
    root = tk.Tk() #główne okno tkinter
    app = NasaApp(root) #instancja aplikacji
    root.mainloop() #uruchamia pętle programu