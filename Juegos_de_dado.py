import tkinter as tk
from tkinter import ttk, messagebox
import random

class DiceGameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("?? Juego de Dado (probabilidades inversas)")
        self.state("zoomed")  
        self.configure(bg="#1E1E2F")  

        self.apuestas = {i: [] for i in range(1, 7)}
        self.apuestas_por_jugador = {}
        self.rolling = False

        self._set_styles()
        self._create_widgets()
        self._update_counts_and_probs()

    def _set_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TLabel", background="#1E1E2F", foreground="white", font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6)
        style.configure("Treeview", background="#2E2E3E", fieldbackground="#2E2E3E", foreground="white", rowheight=28, font=("Segoe UI", 11))
        style.map("Treeview", background=[("selected", "#3A9BDC")])

    def _create_widgets(self):
        left = ttk.Frame(self, padding=10)
        left.place(x=20, y=20, width=400, height=700)

        ttk.Label(left, text="? Añadir / Apostar", font=("Segoe UI", 14, "bold"), foreground="#FFD700").pack(anchor="w")

        frm = ttk.Frame(left)
        frm.pack(fill="x", pady=8)

        ttk.Label(frm, text="Nombre:").grid(row=0, column=0, sticky="w")
        self.nombre_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.nombre_var).grid(row=0, column=1, sticky="ew", padx=6)
        frm.columnconfigure(1, weight=1)

        ttk.Label(frm, text="Número (1-6):").grid(row=1, column=0, sticky="w", pady=(6,0))
        self.numero_var = tk.IntVar(value=1)
        spin = ttk.Spinbox(frm, from_=1, to=6, textvariable=self.numero_var, width=5)
        spin.grid(row=1, column=1, sticky="w", padx=6, pady=(6,0))

        ttk.Button(left, text="?? Apostar / Registrar", command=self.apostar).pack(pady=10, fill="x")
        self.jugadores_list = tk.Listbox(left, height=12, bg="#2E2E3E", fg="white", font=("Segoe UI", 11))
        self.jugadores_list.pack(fill="both", pady=6, expand=False)
        ttk.Button(left, text="?? Resetear ronda", command=self.resetear_ronda).pack(pady=6, fill="x")

        right = ttk.Frame(self, padding=10)
        right.place(x=450, y=20, width=500, height=700)

        ttk.Label(right, text="?? Conteo y Probabilidades", font=("Segoe UI", 14, "bold"), foreground="#00CED1").pack(anchor="w")

        self.table = ttk.Treeview(right, columns=("count", "prob"), show="headings", height=7)
        self.table.heading("count", text="Apuestas")
        self.table.heading("prob", text="Probabilidad")
        self.table.column("count", width=100, anchor="center")
        self.table.column("prob", width=150, anchor="center")
        self.table.pack(fill="x", pady=8)

        for i in range(1, 7):
            self.table.insert("", "end", iid=str(i), values=(0, "0.00%"))

        # ?? Dado más bonito
        self.dice_canvas = tk.Canvas(right, width=140, height=140, bg="#FAFAFA", highlightthickness=4, highlightbackground="#3A9BDC")
        self.dice_canvas.pack(pady=(20, 12))
        self.dice_dots = []
        dot_positions = [(35,35), (105,35), (35,105), (105,105), (35,70), (105,70), (70,70)]
        for (x, y) in dot_positions:
            dot = self.dice_canvas.create_oval(x-10, y-10, x+10, y+10, fill="black")
            self.dice_dots.append(dot)
        self._show_dice_face(self.dice_canvas, 6)

        self.dice_canvas.bind("<Button-1>", lambda e: self.start_roll())

        ttk.Label(right, text="?? Resultado:", font=("Segoe UI", 12, "bold"), foreground="#FFD700").pack(anchor="w")
        self.result_var = tk.StringVar(value="—")
        self.result_label = ttk.Label(right, textvariable=self.result_var, font=("Segoe UI", 30, "bold"), foreground="#FF6347")
        self.result_label.pack(anchor="center", pady=(4,6))

        ttk.Label(right, text="?? Ganadores:", font=("Segoe UI", 12, "bold"), foreground="#32CD32").pack(anchor="w", pady=(8,0))
        self.winners_tree = ttk.Treeview(right, columns=("jugador",), show="headings", height=6)
        self.winners_tree.heading("jugador", text="Jugador")
        self.winners_tree.column("jugador", anchor="center", width=250)
        self.winners_tree.pack(fill="both", pady=(4,0), expand=True)

    def _show_dice_face(self, canvas, number):
        faces = {
            1: [6],
            2: [0, 1],
            3: [0, 1, 6],
            4: [0, 1, 2, 3],
            5: [0, 1, 2, 3, 6],
            6: [0, 1, 2, 3, 4, 5]
        }
        for i, dot in enumerate(self.dice_dots):
            canvas.itemconfigure(dot, state="normal" if i in faces[number] else "hidden")

    def apostar(self):
        nombre = self.nombre_var.get().strip()
        try:
            numero = int(self.numero_var.get())
        except Exception:
            messagebox.showwarning("Número inválido", "El número debe ser entre 1 y 6.")
            return
        if not nombre or numero < 1 or numero > 6:
            messagebox.showwarning("Error", "Introduce nombre y número válido (1-6).")
            return
        if nombre in self.apuestas_por_jugador:
            messagebox.showinfo("Jugador ya apostó", f"{nombre} ya apostó al número {self.apuestas_por_jugador[nombre]}.")
            return

        self.apuestas[numero].append(nombre)
        self.apuestas_por_jugador[nombre] = numero
        self.jugadores_list.insert("end", f"{nombre} -> {numero}")
        self.nombre_var.set("")
        self._update_counts_and_probs()

    def resetear_ronda(self):
        self.apuestas = {i: [] for i in range(1, 7)}
        self.apuestas_por_jugador.clear()
        self.jugadores_list.delete(0, "end")
        self._update_counts_and_probs()
        self.result_var.set("—")
        self._clear_winners()

    def _clear_winners(self):
        for i in self.winners_tree.get_children():
            self.winners_tree.delete(i)

    def _update_counts_and_probs(self):
        counts = {i: len(self.apuestas[i]) for i in range(1, 7)}
        weights = {i: 1.0 / (1 + counts[i]) for i in range(1, 7)}
        total = sum(weights.values())
        probs = {i: weights[i]/total for i in range(1, 7)}
        for i in range(1, 7):
            prob_pct = f"{probs[i]*100:5.2f}%"
            self.table.item(str(i), values=(counts[i], prob_pct))

    def start_roll(self):
        if self.rolling: return
        self.rolling = True
        self._clear_winners()
        self.roll_animation(0)

    def roll_animation(self, step):
        if step < 15:
            temp_num = random.randint(1, 6)
            self._show_dice_face(self.dice_canvas, temp_num)
            self.result_var.set(str(temp_num))
            self.after(100, lambda: self.roll_animation(step+1))
        else:
            self.show_final_result()
            self.rolling = False

    def show_final_result(self):
        counts = {i: len(self.apuestas[i]) for i in range(1, 7)}
        weights = [1.0 / (1 + counts[i]) for i in range(1, 7)]
        chosen = random.choices([1,2,3,4,5,6], weights=weights, k=1)[0]
        self.result_var.set(f"{chosen}")
        self._show_dice_face(self.dice_canvas, chosen)

        winners = self.apuestas[chosen]
        if winners:
            for w in winners:
                self.winners_tree.insert("", "end", values=(f"? {w}",))
        else:
            self.winners_tree.insert("", "end", values=("? No hubo ganadores",))

if __name__ == "__main__":
    app = DiceGameApp()
    app.mainloop()
