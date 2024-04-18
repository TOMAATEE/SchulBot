import time
import schedule
import pyautogui
from tkinter import *
from tkinter import ttk
import tkinter as tk
import threading
from configparser import ConfigParser
from PIL import Image, ImageFont, ImageDraw
from assets.audio import monitor_volume_changes, set_system_volume


def text_to_image(text, font_filepath="assets/Segoe UI.ttf", color=(255, 255, 255)):
    font = ImageFont.truetype(font_filepath, size=18)
    img_size = (font.getmask(text).size[0], int(font.getmask(text).size[1] * 1.2))
    img = Image.new("RGBA", img_size)
    datas = img.getdata()
    new_image_data = []
    for item in datas:
        if item[0] in list(range(0, 100)):
            new_image_data.append((36, 36, 36))
        else:
            new_image_data.append(item)
    img.putdata(new_image_data)

    draw = ImageDraw.Draw(img)
    draw.text((0, -7), text, font=font, fill=color)
    return img


def click_app(programm):
    try:  # bring den Browser in den Vordergrund
        pyautogui.click(pyautogui.locateOnScreen(f"assets/{programm}.png", confidence=.9))
    except pyautogui.ImageNotFoundException:
        print(f"{programm} nicht gefunden")
        return False


def gfn_tab():
    try:  # finde den Tab. der Tab muss schon offen sein!
        tab1 = pyautogui.locateOnScreen('assets/Tab.png', confidence=.9)
        pyautogui.click(tab1)
    except pyautogui.ImageNotFoundException:
        try:  # suche nach dem icon im light mode
            tab2 = pyautogui.locateOnScreen('assets/tabL.png', confidence=.9)
            print("light mode? ernsthaft?")
            pyautogui.click(tab2)
        except pyautogui.ImageNotFoundException:
            print("ist der Tab geschlossen?")
    time.sleep(.1)


def tester(programm, test):
    try:
        button = pyautogui.locateOnScreen(f'assets/{programm}.png', confidence=.9)
        if test == 0:  # bei ausgeschaltetem Testmodus auf den button klicken
            pyautogui.click(button)
        elif test == 1:  # bei eingeschaltetem Testmodus Maus nur zum button bewegen
            pyautogui.moveTo(button)
    except pyautogui.ImageNotFoundException:
        print(f"Keinen {programm}-Button gefunden")


class App(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.row_nr = 0
        self.col_nr = 0
        # Login Block
        self.place_var = tk.IntVar(value=int(config["bin"]["standort"]))
        self.v_place = ""
        self.beschriftung1 = Label(self, text="Einloggen um:", font=('Arial', 12))
        self.beschriftung1.grid(column=self.col_nr, row=self.row_nr)
        self.row_nr += 1
        self.login_entry = Entry(self, width=20, font=('Arial', 12))
        self.login_entry.grid(column=self.col_nr, row=self.row_nr, columnspan=2)
        self.login_entry.insert(0, config.get("settings", "login time"))
        self.login_entry.bind("<FocusOut>", lambda event=None: self.changeConfig())
        self.row_nr += 1
        self.login_button = ttk.Button(self, text="Login Timer", command=lambda: t1.start())
        self.login_button.grid(column=self.col_nr, row=self.row_nr)
        self.instant_login_button = ttk.Button(self, text="Instant-Login", command=lambda: self.instant_login())
        self.instant_login_button.grid(column=self.col_nr + 1, row=self.row_nr)

        self.row_nr -= 1
        self.rad1 = tk.Radiobutton(self, text="Homeoffice", value=0,
                                   variable=self.place_var, command=lambda: self.changeConfig())
        self.rad1.grid(column=self.col_nr + 2, row=self.row_nr, sticky="w")
        self.row_nr += 1
        self.rad2 = tk.Radiobutton(self, text="Standort", value=1,
                                   variable=self.place_var, command=lambda: self.changeConfig())
        self.rad2.grid(column=self.col_nr + 2, row=self.row_nr, sticky="w")
        self.row_nr += 1
        # damit nicht alles so zusammengequetscht ist
        Label(self).grid(column=self.col_nr, row=self.row_nr)
        self.row_nr += 1

        # Teams-call beitreten + sound-Einstellung Block
        self.beschriftung2 = Label(self, text="Lernfeld:", font=('Arial', 12))
        self.beschriftung2.grid(column=self.col_nr, row=self.row_nr)
        self.beschriftung2 = Label(self, text="Lautstärke:", font=('Arial', 12))
        self.beschriftung2.grid(column=self.col_nr + 1, row=self.row_nr)
        self.teams_var = tk.IntVar(value=int(config["bin"]["teams"]))
        self.teams_check = ttk.Checkbutton(self, text="nach Login Teams beitreten",
                                           offvalue=0, onvalue=1, variable=self.teams_var,
                                           command=lambda: self.changeConfig())
        self.teams_check.grid(column=self.col_nr + 2, row=self.row_nr)
        self.row_nr += 1
        self.teams_entry = Entry(self, width=10, font=('Arial', 12))
        self.teams_entry.grid(column=self.col_nr, row=self.row_nr)
        self.teams_entry.insert(0, config.get("settings", "lernfeld"))
        self.teams_entry.bind("<FocusOut>", lambda event=None: self.changeConfig())

        self.sound_entry = Entry(self, width=10, font=('Arial', 12))
        self.sound_entry.grid(column=self.col_nr + 1, row=self.row_nr)
        self.sound_entry.insert(0, config.get("settings", "sound"))
        self.sound_entry.bind("<FocusOut>", lambda event=None: self.changeConfig())
        self.sound_var = tk.IntVar(value=int(config["bin"]["set_sound"]))
        self.sound_check = ttk.Checkbutton(self, text="automatisch einstellen\nbeim betreten eines Calls",
                                           offvalue=0, onvalue=1, variable=self.sound_var,
                                           command=lambda: self.changeConfig())
        self.sound_check.grid(column=self.col_nr + 2, row=self.row_nr)
        self.row_nr += 1
        self.teams_button = ttk.Button(self, text="Teams beitreten", command=lambda: self.teams(self.teams_entry.get()))
        self.teams_button.grid(column=self.col_nr, row=self.row_nr)
        self.sound_set_button = ttk.Button(self, text="Sound einstellen",
                                           command=lambda: set_system_volume(int(self.sound_entry.get()) / 100))
        self.sound_set_button.grid(column=self.col_nr + 1, row=self.row_nr)
        self.sound_monitor_button = ttk.Button(self, text="Soundveränderung erkennen",
                                               command=lambda: t3.start())
        self.sound_monitor_button.grid(column=self.col_nr + 2, row=self.row_nr)
        self.row_nr += 1
        # damit nicht alles so zusammengequetscht ist
        Label(self).grid(column=self.col_nr, row=self.row_nr)
        self.row_nr += 1

        # Logout Block
        self.beschriftung3 = Label(self, text="Ausloggen um:", font=('Arial', 12))
        self.beschriftung3.grid(column=self.col_nr, row=self.row_nr)
        self.row_nr += 1
        self.logout_entry = Entry(self, width=20, font=('Arial', 12))
        self.logout_entry.grid(column=self.col_nr, row=self.row_nr, columnspan=2)
        self.logout_entry.insert(0, config.get("settings", "logout time"))
        self.logout_entry.bind("<FocusOut>", lambda event=None: self.changeConfig())
        self.row_nr += 1
        self.logout_button = ttk.Button(self, text="Logout Timer", command=lambda: t2.start())
        self.logout_button.grid(column=self.col_nr, row=self.row_nr)
        self.instant_logout_button = ttk.Button(self, text="Instant-Logout", command=lambda: self.instant_logout())
        self.instant_logout_button.grid(column=self.col_nr + 1, row=self.row_nr)
        self.row_nr += 1
        # damit nicht alles so zusammengequetscht ist
        Label(self).grid(column=self.col_nr, row=self.row_nr)
        self.row_nr += 1

        # Test Checkbox
        self.test_var = tk.IntVar(value=int(config["bin"]["test"]))
        self.test_check = ttk.Checkbutton(self, text="Testmodus", offvalue=0, onvalue=1,
                                          variable=self.test_var, command=lambda: self.changeConfig())
        self.test_check.grid(column=self.col_nr, row=self.row_nr)
        self.row_nr += 1
        # Exit Button
        self.exit = ttk.Button(self, text="Programm beenden", command=lambda: self.quit())
        self.exit.grid(column=self.col_nr, row=self.row_nr)
        self.row_nr += 1
        # Statusanzeige login/logout
        self.login_label = Label(self, text="Login Timer noch nicht gestartet", font=('Arial', 12))
        self.login_label.grid(sticky='nw', column=self.col_nr, row=self.row_nr, columnspan=3)
        self.row_nr += 1
        self.logout_label = Label(self, text="Logout Timer noch nicht gestartet", font=('Arial', 12))
        self.logout_label.grid(sticky='nw', column=self.col_nr, row=self.row_nr, columnspan=3)
        self.row_nr += 1
        self.sound_label = Label(self, text="Sound Monitor noch nicht gestartet", font=('Arial', 12))
        self.sound_label.grid(sticky='nw', column=self.col_nr, row=self.row_nr, columnspan=3)

    def login_loop(self, login_time, v):
        scheduler1.every().day.at(login_time).do(self.login, self.v_place)
        if v == 0:  # Übersetzung: 0 = Homeoffice, 1 = Standort
            self.v_place = "Homeoffice"
        elif v == 1:
            self.v_place = "Standort"
        while not exit1.is_set():
            n = scheduler1.idle_seconds  # Zeit bis zum Login
            if n is None:  # wenn der Job beendet wurde wird der Loop verlasen
                break
            elif n > 0:
                h = int(n // 3600)                     # Rest Stundenberechnung
                m = int(((n / 3600) - h) * 60)         # Rest Minutenberechnung
                s = int(n - (h * 3600) - (m * 60))     # Rest Sekundenberechnung
                self.login_label.config(text=f"{h:02d}:{m:02d}:{s:02d} bis zum Login im {self.v_place}")
                exit1.wait(1)
            scheduler1.run_pending()

    def login(self, v):
        exit1.set()
        if v == 0:  # Übersetzung: 0 = Homeoffice, 1 = Standort
            self.v_place = "Homeoffice"
        elif v == 1:
            self.v_place = "Standort"
        self.login_label.config(text=f"Ich logge dich jetzt im {self.v_place} ein")

        click_app("operaGX")
        gfn_tab()
        time.sleep(.5)

        try:  # logge dich ein. die Einlogdaten sollten gespeichert sein!
            pyautogui.click(pyautogui.locateOnScreen('assets/login.png', confidence=.9))
            time.sleep(2)  # warten bis die Seite aufgebaut ist
        except pyautogui.ImageNotFoundException:
            print("schon eingeloggt?")

        try:  # Die Erinnerung, dass man seine login/logout Zeiten kontrollieren soll wegklicken
            pyautogui.click(pyautogui.locateOnScreen('assets/login Ok.png', confidence=.9))
            time.sleep(1)
        except pyautogui.ImageNotFoundException:
            print("heute kein Login Hinweis?")

        try:  # homeoffice/standort wird ausgewählt
            if self.v_place == "Homeoffice":
                pyautogui.click(pyautogui.locateOnScreen('assets/homeoffice.png', confidence=.9))
            elif self.v_place == "Standort":
                pyautogui.click(pyautogui.locateOnScreen('assets/standort.png', confidence=.9))
        except pyautogui.ImageNotFoundException:
            # wenn er nicht da ist, bist du wahrscheinlich auf einer anderen seite in Moodle. Zurück zur Hauptseite
            pyautogui.click(pyautogui.locateOnScreen('assets/main_screen.png', confidence=.9))
            time.sleep(2)  # warten bis die Seite aufgebaut ist

        tester("start", self.test_var.get())
        if self.teams_var.get():  # Automatisch dem Teams-call beitreten, wenn der Haken gesetzt ist
            self.teams(self.teams_entry.get())
        self.login_label.config(text="Login abgeschlossen")
        exit1.clear()
        return schedule.CancelJob  # beendet den Job nach Abschluss

    def instant_login(self):
        if t1.is_alive():
            scheduler1.run_all()
        else:
            self.login(self.place_var.get())

    def teams(self, lernfeld):
        gefunden = click_app("teams")
        if not gefunden:
            click_app("teams neue nachricht")
            click_app("chat neue nachricht")
        else:
            chat = click_app("chat inaktiv")
            if not chat:
                pyautogui.moveTo(pyautogui.locateOnScreen('assets/chat aktiv.png', confidence=.9))

        try:  # klicke auf den jeweils richtigen Chat
            time.sleep(.5)
            pyautogui.click(pyautogui.locateOnScreen(text_to_image(lernfeld), confidence=.55))
        except pyautogui.ImageNotFoundException:
            print("chat nicht gefunden")

        tester("teilnehmen", self.test_var.get())
        if self.sound_var.get():  # wenn der Haken gesetzt ist, wird der Sound automatisch verändert
            set_system_volume(int(self.sound_entry.get()) / 100)
        time.sleep(2)
        tester("jetzt teilnehmen", self.test_var.get())

    def sound_monitor_loop(self):
        self.sound_label.config(text=f"Sound Monitor gestartet. Locked: {self.sound_entry.get()}%")
        monitor_volume_changes(int(self.sound_entry.get()))

    def logout_loop(self, logout_time):
        scheduler2.every().day.at(f"{logout_time}:30").do(self.logout)
        while not exit2.is_set():
            n2 = scheduler2.idle_seconds
            if n2 is None:  # wenn der Job beendet wurde wird der Loop verlasen
                break
            elif n2 > 0:
                h = int(n2 // 3600)                     # Rest Stundenberechnung
                m = int(((n2 / 3600) - h) * 60)         # Rest Minutenberechnung
                s = int(n2 - (h * 3600) - (m * 60))     # Rest Sekundenberechnung
                self.logout_label.config(text=f"{h:02d}:{m:02d}:{s:02d} bis Feierabend")
                exit2.wait(1)
            scheduler2.run_pending()

    def logout(self):
        exit2.set()
        self.logout_label.config(text="Feierabend!!")

        click_app("operaGX")
        gfn_tab()

        try:  # finde den Beenden-Button
            pyautogui.locateOnScreen(f'assets/beenden.png', confidence=.9)
        except pyautogui.ImageNotFoundException:
            # wenn er nicht da ist, bist du wahrscheinlich auf einer anderen Seite in Moodle. Zurück zur Hauptseite
            pyautogui.click(pyautogui.locateOnScreen('assets/main_screen.png', confidence=.9))
            time.sleep(2)

        tester("beenden", self.test_var.get())
        self.logout_label.config(text="Logout abgeschlossen")
        exit2.clear()
        return schedule.CancelJob  # beendet den Job nach Abschluss

    def instant_logout(self):
        if t2.is_alive():
            scheduler2.run_all()
        else:
            self.logout()

    def changeConfig(self):
        config["settings"]["login time"] = str(self.login_entry.get())
        config["settings"]["logout time"] = str(self.logout_entry.get())
        config["settings"]["lernfeld"] = str(self.teams_entry.get())
        config["settings"]["sound"] = str(self.sound_entry.get())
        config["bin"]["standort"] = str(self.place_var.get())
        config["bin"]["teams"] = str(self.teams_var.get())
        config["bin"]["set_sound"] = str(self.sound_var.get())
        config["bin"]["test"] = str(self.test_var.get())
        with open('assets/config.ini', 'w') as conf:
            config.write(conf)


# config Datei laden
config = ConfigParser()
config.read('assets/config.ini')
# multithreading damit sich das Programm nicht komplett aufhängt während der loops
t1 = threading.Thread(target=lambda: root.login_loop(root.login_entry.get(), root.place_var.get()), daemon=True)
t2 = threading.Thread(target=lambda: root.logout_loop(root.logout_entry.get()), daemon=True)
t3 = threading.Thread(target=lambda: root.sound_monitor_loop(), daemon=True)
exit1 = threading.Event()  # Events um die threads zu beenden und pausieren
exit2 = threading.Event()
exit3 = threading.Event()# ungenutzt
# verschiedene scheduler damit man login/logout gleichzeitig laufen lassen kann und die verbleibende Zeit korrekt ist
scheduler1 = schedule.Scheduler()
scheduler2 = schedule.Scheduler()
# initialisierung der kompletten App
root = App()
root.master.title("SchulBot")

root.mainloop()
