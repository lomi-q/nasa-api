import tkinter as tk
from PIL import Image, ImageTk
import requests
import io

class NasaApp:
    def __init__(self, root):
        self.root = root #główne okno
        self.root.title("NASA Image Search") #tytuł okna
        self.root.configure(bg="black") #kolor tła okna
        self.root.geometry('1920x1080') #rozmiar okna
        self.setup_widgets() #wczytanie widgetów

        self.images = [] #przechowanie obrazów

    def setup_widgets(self):
        #przycisk do zamknięcia okna
        self.exit_button = tk.Button(self.root, text="X", bg="white", fg="green", width=5, command=self.close)
        self.exit_button.grid(row=0, column=2, sticky="ne")

        #tytuł "podaj zapytanie"
        self.query_label = tk.Label(self.root, text="Podaj zapytanie:", bg="black", fg="green", font=("Arial", 14))
        self.query_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="n")

        #pole do wpisania zapytania
        self.query_entry = tk.Entry(root, width=40, bg="black", fg="lime", insertbackground="lime")
        self.query_entry.grid(row=1, column=1, sticky="we")

        #przycisk wysyła zapytanie
        self.search_button = tk.Button(root, text="Szukaj", command=self.search_images, bg="black", fg="lime")
        self.search_button.grid(row=1, column=2, sticky="w", padx=2)

        #ramka dla konsoli
        self.console_frame = tk.Frame(self.root, bg="black")
        self.console_frame.grid(row=2, column=2, sticky="nse", pady=10, padx=10)

        #ramka na obrazy
        self.image_frame = tk.Frame(root, bg="black")
        self.image_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        #konsola
        self.console = tk.Text(self.console_frame, height=8, bg="black", fg="lime", state="disabled")
        self.console.pack(fill="both", expand='true')

        #konfiguracja grid
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1, uniform="a")
        self.root.grid_columnconfigure(1, weight=1, uniform="a")
        self.root.grid_columnconfigure(2, weight=1, uniform="a")

    def log(self, message):
        #funkcja do logów
        self.console.config(state="normal") #odblokowuje konsole
        self.console.insert("end", message + "\n") #dodaje wiadomość
        self.console.see("end") #przewija kosole na koniec
        self.console.config(state="disabled") #blokuje konsole

    def search_images(self):
        #wyszukiwanie obrazów
        query = self.query_entry.get().strip() #pobiera tekst z pola entry i usuwa spacje
        if not query:
            self.log("Wpisz zapytanie!") #informuje w konsoli że pole entry jest puste
            return #przerwanie funkcji

        self.log(f"Szukanie: {query}") #informuje w konsoli o wyszukaniu konkretnego zapytania
        self.clear_images() #usunięcie starych obrazów

        try:
            #zapytanie do api
            response = requests.get("https://images-api.nasa.gov/search", params={"q": query, "media_type": "image"}) #wkleja zapytanie użytkownika do linku
            response.raise_for_status() #informuje o błędzie http jeśli jakiś wystąpi
            items = response.json().get("collection", {}).get("items", [])[:20] #pobiera do 20 obrazów

            if not items: #jak nie ma wyników
                self.log("Brak wyników.") #informuje w konsoli o braku zdjęć pasujących do zapytania
                return

            for item in items: #dla każdego zdjęcia
                title = item["data"][0]["title"] #pobiera tytuł
                img_url = item["links"][0]["href"] #pobiera url
                self.display_image(title, img_url) #pokazuje miniature zdjęcia

        except Exception as e: #jak wystąpi błąd
            self.log(f" Błąd: {e}") #informuje o błędzie w konsoli

    def display_image(self, title, url): #funkcja wyświetlająca obrazy
        try:
            img_data = requests.get(url).content #pobieranie danych obrazu
            img = Image.open(io.BytesIO(img_data)) #otwiera obraz danymi binarnymi
            img.thumbnail((150, 150)) #ustawia rozmiar miniatury obrazu
            photo = ImageTk.PhotoImage(img) #tworzy obiekt
            self.images.append(photo) #dodaje obrazy do listy w __init__

            col_count = 5 # max 5 obrazów w rzędzie
            index = len(self.images) - 1 #indeks obrazu
            row = index // col_count #wiersze
            col = index % col_count #kolumny

            frame = tk.Frame(self.image_frame, bg="black") #ramka miniatury
            frame.grid(row=row, column=col, padx=10, pady=10) #umieszczenie na siatce w oknie programu

            label = tk.Label(frame, image=photo, bg="black", cursor="hand2") #etykieta z obrazem
            label.pack() #umieszczenie etykiety
            label.bind("<Button-1>", lambda e: self.open_full_image(title, url)) #po kliknięciu miniatury otwiera pełny obraz w nowym oknie

            text = tk.Label(frame, text=title, wraplength=150, bg="black", fg="lime") #dodaje tytuł obrazu
            text.pack()

        except Exception as e: #jak wystąpi błąd
            self.log(f" Nie udało się załadować obrazka: {e}") #loguje do konsoli

    def open_full_image(self, title, url): #otwieranie obrazu w nowym oknie
        try:
            full_image_window = tk.Toplevel(self.root) #nowe okno
            full_image_window.title(title) #tytuł okna
            full_image_window.configure(bg="black") #kolor tła okna

            frame = tk.Frame(full_image_window, bg="black") #ramka na obraz
            frame.pack(fill="both", expand=True)

            close_button = tk.Button(frame, text="X", command=full_image_window.destroy,bg="white", fg="green", width=5) #przycisk do zamknięcia okna
            close_button.pack(anchor="ne", padx=5, pady=5) #umieszczenie przycisku

            img_data = requests.get(url).content #pobieranie danych obrazu
            image = Image.open(io.BytesIO(img_data)) #otwiera obraz danymi binarnymi
            photo = ImageTk.PhotoImage(image) #konwertuje na obiekt tkinter

            img_label = tk.Label(frame, image=photo, bg="black") #etykieta obrazu
            img_label.image = photo #referencja do obrazu
            img_label.pack() #umieszczenie obrazu w oknie

        except Exception as e: #jak wystąpi błąd
            self.log(f" Błąd podczas otwierania pełnego obrazu: {e}") #log

    def clear_images(self):
        #usuwa poprzednie miniatury obrazów
        for widget in self.image_frame.winfo_children(): #dla widgetów w ramce
            widget.destroy() #usuwa widgety
        self.images.clear() #usuwa obrazy w listy

    def close(self):
        #zamyka program/funkcja do przycisków
        self.root.destroy()

if __name__ == "__main__": #czy program uruchamiany jest bezpośrednio
    root = tk.Tk() #główne okno tkinter
    app = NasaApp(root) #instancja aplikacji
    root.mainloop() #uruchamia pętle programu