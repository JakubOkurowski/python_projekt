import tkinter as tk
from tkinter import font
from tkinter import ttk

import random


class gol(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#352f41")

        self.controller = controller

        self.cell_size = 30

        self.controller = controller
        self.canvas = tk.Canvas(self, width=900, height=900, bg="#352f41", highlightthickness=0, bd=0)

        self.slider = ttk.Scale(
            self,
            orient=tk.HORIZONTAL,
            from_=1,
            to=100,
            length=250,
            command=self.update_label,
        )
        self.label = ttk.Label(
            self,
            text="Cykli na sekundę: 0",
        )

        self.slider.place(x=20, y=850)
        self.label.place(x=20, y=830)

        self.canvas.pack(fill="both", expand=True)

        self.cam_offset_x = -900 / 2
        self.cam_offset_y = -900 / 2

        self.canvas.bind("<ButtonPress-1>", self.start_changing_cells)
        self.canvas.bind("<ButtonRelease-1>", self.stop_changing_cells)
        self.controller.bind("<space>", self.cycle_running)
        self.controller.bind("<r>", self.update_grid)
        self.controller.bind("<Escape>", self.go_back)

        self.canvas.bind("<MouseWheel>", self.on_scroll)
        self.canvas.bind("<ButtonPress-2>", self.on_middle_click)
        self.canvas.bind("<ButtonRelease-2>", self.on_middle_click)

        self.chaning_cells = False
        self.chaning_current = -1

        self.drag = False
        self.drag_started_x = -1
        self.drag_started_y = -1

        self.running = False

        self.draw_grid()
        self.update()
        self.running_loop()

    def update_label(self, value):
        value = int(float(value))
        self.label.config(text=f"Cykli na sekundę: {value}")
        self.controller.ups = value

    def go_back(self, event):
        self.controller.show_frame("opcje")

    def load_template(self, template):
        self.controller.grid_w = 20
        self.controller.grid_h = 20
        self.controller.grid_data = [[0 for _ in range(self.controller.grid_w)] for _ in range(self.controller.grid_h)]
        self.draw_grid()
        return

    def beforeshow(self, update_grid=True):
        self.slider.set(self.controller.ups)
        if update_grid: self.update_grid()
        return

    def update_grid(self, event=None):
        self.controller.grid_data = [[0 for _ in range(self.controller.grid_w)] for _ in range(self.controller.grid_h)]
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        for y in range(self.controller.grid_h):
            for x in range(self.controller.grid_w):
                x1 = (x - self.controller.grid_w / 2) * self.cell_size - self.cam_offset_x
                x2 = x1 + self.cell_size

                y1 = (y - self.controller.grid_h / 2) * self.cell_size - self.cam_offset_y
                y2 = y1 + self.cell_size

                if self.controller.grid_data[y][x]:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="#ffffff", outline="gray")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="gray")

    def count_nb(app, self, x, y):
        nb = 0
        for px in [-1, 0, 1]:
            for py in [-1, 0, 1]:
                if (x + px) < 0 or (x + px) >= self.controller.grid_w:
                    continue
                if (y + py) < 0 or (y + py) >= self.controller.grid_h:
                    continue
                if (px == 0 and py == 0):
                    continue

                nb += self.controller.grid_data[y + py][x + px]

        return nb

    def running_loop(self):
        if self.running:
            new_grid = [[0 for _ in range(self.controller.grid_w)] for _ in range(self.controller.grid_h)]

            when_not_die = list(map(int, list(self.controller.ustawienia.split("/")[0])))
            when_life = list(map(int, list(self.controller.ustawienia.split("/")[1])))

            for y in range(self.controller.grid_h):
                for x in range(self.controller.grid_w):
                    nb = self.count_nb(self, x, y)
                    if (self.controller.grid_data[y][x] == 0):
                        if nb in when_life:
                            new_grid[y][x] = 1
                    else:
                        if nb in when_not_die:
                            new_grid[y][x] = 1
                        else:
                            new_grid[y][x] = 0

            for y in range(self.controller.grid_h):
                for x in range(self.controller.grid_w):
                    self.controller.grid_data[y][x] = new_grid[y][x]

        self.draw_grid()
        self.master.after(int(1000 / self.controller.ups), self.running_loop)

    def update(self):
        px = self.master.winfo_pointerx() - self.master.winfo_rootx()
        py = self.master.winfo_pointery() - self.master.winfo_rooty()

        if (self.chaning_cells):
            self.change_cell(self, px, py)

        if (self.drag):
            if (self.drag_started_x == -1):
                self.drag_started_x = px
                self.drag_started_y = py
            self.cam_offset_x += self.drag_started_x - px
            self.cam_offset_y += self.drag_started_y - py
            self.drag_started_x = px
            self.drag_started_y = py
            self.draw_grid()

        self.master.after(10, self.update)

    def on_middle_click(self, event):
        self.drag = not self.drag
        if (not self.drag):
            self.drag_started_x = -1
            self.drag_started_y = -1

    def on_scroll(self, event):
        self.cell_size += event.delta / 120
        if (self.cell_size <= 0): self.cell_size = .1
        self.draw_grid()

    def start_changing_cells(self, event):
        self.chaning_cells = True

    def stop_changing_cells(self, event):
        self.chaning_cells = False
        self.chaning_current = -1

    def cycle_running(self, event):
        self.running = not self.running

    def change_cell(app, self, px, py):
        x = (px + self.cam_offset_x + self.controller.grid_w / 2 * self.cell_size) // self.cell_size
        y = (py + self.cam_offset_y + self.controller.grid_h / 2 * self.cell_size) // self.cell_size

        x = int(x)
        y = int(y)

        if (self.chaning_current == -1):
            self.chaning_current = 1 - self.controller.grid_data[y][x]

        if (x < 0 or x >= self.controller.grid_w): return
        if (y < 0 or y >= self.controller.grid_h): return

        self.controller.grid_data[y][x] = self.chaning_current
        self.draw_grid()


class opcje(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#352f41", width=900, height=900)
        self.pack_propagate(False)
        self.controller = controller

        large_font = font.Font(family="Helvetica", size=16, weight="bold")
        larger_font = font.Font(family="Helvetica", size=24, weight="bold")

        var_title = tk.StringVar()
        label_title = tk.Label(self, textvariable=var_title, bg="#352f41", fg="white", font=larger_font)
        var_title.set("Gra w życie")
        label_title.pack(pady=40)

        var_ust = tk.StringVar()
        label_ust = tk.Label(self, textvariable=var_ust, bg="#352f41", fg="white", font=large_font)
        var_ust.set("Ustawienia: ")
        label_ust.pack(pady=20)

        self.entries = {}

        def validate_int(P):
            if P == "" or P.isdigit():
                return True
            return False

        vcmd = (self.register(validate_int), "%P")

        variable_settings = tk.Frame(self, bg="#352f41", width=600)
        variable_settings.pack()

        for var_name in [{"var": "grid_w", "display": "Szerokość"}, {"var": "grid_h", "display": "Wysokość"},
                         {"var": "ups", "display": "Cykli na sekundę"}]:

            frame = tk.Frame(variable_settings, bg="#352f41", width=300)
            frame.pack(fill="x", expand=False)
            frame.pack_propagate(False)

            spacer = tk.Frame(frame, bg="#352f41")
            spacer.grid(row=0, column=1, sticky="we", padx=10)

            lbl = tk.Label(frame, text=var_name["display"] + ":", bg="#352f41", fg="white", font=large_font)
            lbl.grid(row=0, column=0, sticky="w")

            entry = tk.Entry(frame, width=10, validate="key", validatecommand=vcmd, font=large_font)
            entry.grid(row=0, column=2, sticky="e")

            frame.columnconfigure(0, weight=0)
            frame.columnconfigure(1, weight=1)
            frame.columnconfigure(2, weight=0)

            if hasattr(controller, var_name["var"]):
                entry.insert(0, str(getattr(controller, var_name["var"])))
            self.entries[var_name["var"]] = entry

        frame = tk.Frame(variable_settings, bg="#352f41", width=300)
        frame.pack(fill="x", expand=False)
        frame.pack_propagate(False)

        spacer = tk.Frame(frame, bg="#352f41")
        spacer.grid(row=0, column=1, sticky="we", padx=10)

        lbl = tk.Label(frame, text="Ustawienia: ", bg="#352f41", fg="white", font=large_font)
        lbl.grid(row=0, column=0, sticky="w")

        self.entry_sett = tk.Entry(frame, width=10, font=large_font)
        self.entry_sett.insert(0, str(getattr(controller, "ustawienia")))
        self.entry_sett.grid(row=0, column=2, sticky="e")

        frame.columnconfigure(0, weight=0)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=0)

        btn = tk.Button(self, text="Rozpocznij", font=large_font, command=self.apply_changes)
        btn.pack(pady=30)

        lbl = tk.Label(self, text="Szablony: ", bg="#352f41", fg="white", font=large_font)
        lbl.pack(pady=30)

        def szablon_losowy():
            self.controller.grid_w = 50
            self.controller.grid_h = 50

            self.controller.show_frame("gol")

            for i in range(0, 50):
                for j in range(0, 50):
                    self.controller.grid_data[i][j] = random.randint(0, 1)

        btn = tk.Button(self, text="Losowe", font=large_font, command=szablon_losowy)
        btn.pack(pady=10)

        def szablon_gun():
            self.controller.grid_w = 50
            self.controller.grid_h = 50

            self.controller.show_frame("gol")

            for i in range(0, 50):
                for j in range(0, 50):
                    self.controller.grid_data[i][j] = 0

            self.controller.grid_data[6][1] = 1
            self.controller.grid_data[6][2] = 1
            self.controller.grid_data[7][1] = 1
            self.controller.grid_data[7][2] = 1

            self.controller.grid_data[4][14] = 1
            self.controller.grid_data[4][13] = 1
            self.controller.grid_data[5][12] = 1
            self.controller.grid_data[6][11] = 1
            self.controller.grid_data[7][11] = 1
            self.controller.grid_data[8][11] = 1
            self.controller.grid_data[9][12] = 1
            self.controller.grid_data[10][13] = 1
            self.controller.grid_data[10][14] = 1

            self.controller.grid_data[7][15] = 1

            self.controller.grid_data[5][16] = 1
            self.controller.grid_data[6][17] = 1
            self.controller.grid_data[7][17] = 1
            self.controller.grid_data[7][18] = 1
            self.controller.grid_data[8][17] = 1
            self.controller.grid_data[9][16] = 1

            self.controller.grid_data[8][25] = 1
            self.controller.grid_data[7][25] = 1
            self.controller.grid_data[7][23] = 1
            self.controller.grid_data[6][21] = 1
            self.controller.grid_data[6][22] = 1
            self.controller.grid_data[5][21] = 1
            self.controller.grid_data[5][22] = 1
            self.controller.grid_data[4][21] = 1
            self.controller.grid_data[4][22] = 1
            self.controller.grid_data[3][23] = 1
            self.controller.grid_data[3][25] = 1
            self.controller.grid_data[2][25] = 1

            self.controller.grid_data[5][36] = 1
            self.controller.grid_data[5][35] = 1
            self.controller.grid_data[4][36] = 1
            self.controller.grid_data[4][35] = 1

        btn = tk.Button(self, text="Godper glider gun", font=large_font, command=szablon_gun)
        btn.pack(pady=10)

        def szablon_inf_block():
            self.controller.grid_w = 50
            self.controller.grid_h = 50

            self.controller.show_frame("gol")

            for i in range(0, 50):
                for j in range(0, 50):
                    self.controller.grid_data[i][j] = 0

            self.controller.grid_data[27][22] = 1
            self.controller.grid_data[27][24] = 1
            self.controller.grid_data[26][24] = 1
            self.controller.grid_data[25][26] = 1
            self.controller.grid_data[24][26] = 1
            self.controller.grid_data[23][26] = 1
            self.controller.grid_data[24][28] = 1
            self.controller.grid_data[23][28] = 1
            self.controller.grid_data[23][29] = 1
            self.controller.grid_data[22][28] = 1

        btn = tk.Button(self, text="Block-laying switch engine", font=large_font, command=szablon_inf_block)
        btn.pack(pady=10)

    def apply_changes(self):
        self.controller.ustawienia = self.entry_sett.get()
        for var_name, val in self.entries.items():
            if val.get() == "":
                continue

            setattr(self.controller, var_name, int(val.get()))
            self.controller.show_frame("gol")

    def beforeshow(self):
        return


class app(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config(bg="#352f41")

        self.grid_w = 50
        self.grid_h = 50
        self.grid_data = [[0 for _ in range(self.grid_w)] for _ in range(self.grid_h)]

        self.ups = 30
        self.frames = {}

        self.ustawienia = "23/3"

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        for F in [gol, opcje]:
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.pack_forget()

        self.show_frame("opcje")

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].beforeshow()
        self.frames[name].pack(fill="both", expand=True)


if __name__ == "__main__":
    gra = app()
    gra.title("Gra w życie")
    gra.mainloop()