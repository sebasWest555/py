import tkinter as tk
from tkinter import ttk, messagebox
import random

# ─────────────────────────────────────────────
#  MODELO: representa cada labor del hogar
# ─────────────────────────────────────────────
class LaborHogar:
    """
    Equivalente a la clase 'process' del código base.
    Cada labor tiene:
      - nombre     : descripción de la tarea (ej. "Barrer")
      - responsable: miembro del hogar asignado (ej. "Mamá")
      - duracion   : tiempo total que requiere la labor  (= burst)
      - llegada    : momento en que la labor está disponible (= arrival)
      - duracion_tmp: tiempo restante por ejecutar (= burst_tmp)
      - espera     : tiempo que pasó en cola sin ejecutarse (= wait)
      - retorno    : tiempo desde llegada hasta finalización (= return_)
      - final      : instante exacto en que terminó (= ending)
    """
    EMOJIS = {
        "Barrer":       "🧹",
        "Trapear":      "🪣",
        "Lavar platos": "🍽️",
        "Lavar ropa":   "👕",
        "Cocinar":      "🍳",
        "Compras":      "🛒",
        "Jardinería":   "🌱",
        "Limpiar baño": "🚿",
        "Sacar basura": "🗑️",
        "Planchar":     "👔",
    }
    COLORES_PERSONA = {
        "Mamá":    "#f97316",
        "Papá":    "#3b82f6",
        "Hijo":    "#10b981",
        "Hija":    "#ec4899",
        "Abuela":  "#a855f7",
        "Abuelo":  "#eab308",
        "Otro":    "#06b6d4",
    }
    PALETA = ["#f97316","#3b82f6","#10b981","#ec4899","#a855f7","#eab308","#06b6d4","#ef4444"]

    def __init__(self, nombre, responsable, duracion, llegada):
        self.nombre      = nombre
        self.responsable = responsable
        self.duracion    = duracion
        self.llegada     = llegada
        self.duracion_tmp = duracion   # restante (se va decrementando)
        self.espera      = 0
        self.retorno     = 0
        self.final       = 0
        self.emoji       = self.EMOJIS.get(nombre, "🏠")
        self.color       = self.COLORES_PERSONA.get(responsable,
                            random.choice(self.PALETA))

# ─────────────────────────────────────────────
#  ALGORITMO Round Robin (lógica del código base)
# ─────────────────────────────────────────────
def ejecutar_round_robin(tareas: list[LaborHogar], quantum: int):
    """
    Implementa el algoritmo Round Robin exactamente como el código base:
      - Ordena por tiempo de llegada (insertion sort)
      - Usa cola de listos y control de quantum
    Retorna historial_gantt: lista de (nombre, responsable, inicio, fin, color)
    """
    # --- ordenar por llegada (insertion sort del código base) ---
    lista = list(tareas)
    for i in range(1, len(lista)):
        j = i
        while j > 0 and lista[j].llegada < lista[j-1].llegada:
            lista[j], lista[j-1] = lista[j-1], lista[j]
            j -= 1

    # reiniciar tiempos temporales
    for t in lista:
        t.duracion_tmp = t.duracion
        t.espera = t.retorno = t.final = 0

    pendientes   = len(lista)
    tiempo       = 0
    cola_listos  = []
    siguiente    = 0          # índice del próximo proceso a ingresar
    en_ejecucion = None
    control      = True
    historial    = []         # (nombre, responsable, t_inicio, t_fin, color)

    while pendientes > 0:
        # ingresar procesos que ya llegaron (igual que el código base)
        if siguiente < len(lista) and tiempo >= lista[siguiente].llegada:
            cola_listos.append(lista[siguiente])
            siguiente += 1
        else:
            if siguiente > 0 or cola_listos:
                if en_ejecucion is None:
                    en_ejecucion = cola_listos.pop(0)
                    control = True

                if control:
                    t_inicio = tiempo
                    if en_ejecucion.duracion_tmp >= quantum:
                        en_ejecucion.duracion_tmp -= quantum
                        tiempo += quantum
                    else:
                        tiempo += en_ejecucion.duracion_tmp
                        en_ejecucion.duracion_tmp = 0

                    historial.append((
                        en_ejecucion.nombre,
                        en_ejecucion.responsable,
                        t_inicio,
                        tiempo,
                        en_ejecucion.color,
                        en_ejecucion.emoji,
                    ))

                    if en_ejecucion.duracion_tmp < 1:
                        en_ejecucion.final   = tiempo
                        en_ejecucion.retorno = en_ejecucion.final - en_ejecucion.llegada
                        en_ejecucion.espera  = en_ejecucion.retorno - en_ejecucion.duracion
                        pendientes -= 1
                        en_ejecucion = None
                    else:
                        control = False
                else:
                    cola_listos.append(en_ejecucion)
                    en_ejecucion = None
            else:
                tiempo += 1

    return lista, historial

# ─────────────────────────────────────────────
#  INTERFAZ GRÁFICA (basada en el código base tkinter)
# ─────────────────────────────────────────────
class AppHogar:
    LABORES_PREDEFINIDAS = [
        "Barrer", "Trapear", "Lavar platos", "Lavar ropa",
        "Cocinar", "Compras", "Jardinería", "Limpiar baño",
        "Sacar basura", "Planchar",
    ]
    PERSONAS = ["Mamá", "Papá", "Hijo", "Hija", "Abuela", "Abuelo", "Otro"]

    def __init__(self, root):
        self.root = root
        self.root.title("🏠 Round Robin — Labores del Hogar")
        self.root.geometry("1000x800")
        self.root.configure(bg="#0f172a")
        self.lista_labores: list[LaborHogar] = []
        self._setup_styles()
        self._build_ui()

    # ── estilos ──────────────────────────────
    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Treeview",
                    background="#1e293b", foreground="white",
                    fieldbackground="#1e293b", borderwidth=0,
                    rowheight=26)
        s.map("Treeview", background=[("selected", "#334155")])
        s.configure("TLabel",  background="#0f172a", foreground="#94a3b8",
                    font=("Segoe UI", 10))
        s.configure("TEntry",  fieldbackground="#1e293b", foreground="white")
        s.configure("TCombobox", fieldbackground="#1e293b", foreground="white",
                    background="#1e293b")
        s.map("TCombobox", fieldbackground=[("readonly","#1e293b")])

    # ── construcción de widgets ───────────────
    def _build_ui(self):
        # encabezado
        tk.Label(self.root,
                 text="🏠  DISTRIBUCIÓN DE LABORES DEL HOGAR",
                 bg="#0f172a", fg="#38bdf8",
                 font=("Segoe UI", 17, "bold")).pack(pady=(14, 4))
        tk.Label(self.root,
                 text="Algoritmo de Planificación  ·  Round Robin (Turno Rotatorio)",
                 bg="#0f172a", fg="#475569",
                 font=("Segoe UI", 9)).pack(pady=(0, 10))

        # ── panel de entrada ─────────────────
        frame_in = tk.Frame(self.root, bg="#1e293b", padx=14, pady=12)
        frame_in.pack(fill="x", padx=20, pady=4)

        # fila 0: labor, responsable, duración, llegada
        ttk.Label(frame_in, text="Labor:").grid(row=0, column=0, sticky="w")
        self.labor_var = tk.StringVar(value=self.LABORES_PREDEFINIDAS[0])
        cb_labor = ttk.Combobox(frame_in, textvariable=self.labor_var,
                                values=self.LABORES_PREDEFINIDAS, width=14, state="readonly")
        cb_labor.grid(row=0, column=1, padx=6, pady=4)

        ttk.Label(frame_in, text="Responsable:").grid(row=0, column=2, padx=(10,2), sticky="w")
        self.persona_var = tk.StringVar(value=self.PERSONAS[0])
        cb_persona = ttk.Combobox(frame_in, textvariable=self.persona_var,
                                  values=self.PERSONAS, width=10, state="readonly")
        cb_persona.grid(row=0, column=3, padx=6, pady=4)

        ttk.Label(frame_in, text="Duración (min):").grid(row=0, column=4, padx=(10,2), sticky="w")
        self.dur_ent = ttk.Entry(frame_in, width=7)
        self.dur_ent.insert(0, "10")
        self.dur_ent.grid(row=0, column=5, padx=6)

        ttk.Label(frame_in, text="Llegada (min):").grid(row=0, column=6, padx=(10,2), sticky="w")
        self.llegada_ent = ttk.Entry(frame_in, width=7)
        self.llegada_ent.insert(0, "0")
        self.llegada_ent.grid(row=0, column=7, padx=6)

        # fila 1: quantum + botones
        ttk.Label(frame_in, text="Quantum (min):").grid(row=1, column=0, sticky="w", pady=6)
        self.q_ent = ttk.Entry(frame_in, width=7)
        self.q_ent.insert(0, "5")
        self.q_ent.grid(row=1, column=1, sticky="w", padx=6)

        btn_cfg = dict(relief="flat", font=("Segoe UI", 9, "bold"),
                       cursor="hand2", padx=8, pady=4)
        tk.Button(frame_in, text="＋ Añadir", bg="#10b981", fg="white",
                  command=self._agregar, **btn_cfg).grid(row=0, column=8, padx=8, sticky="ew")
        tk.Button(frame_in, text="▶ INICIAR", bg="#3b82f6", fg="white",
                  command=self._ejecutar, **btn_cfg).grid(row=1, column=8, padx=8, sticky="ew")
        tk.Button(frame_in, text="↺ REINICIAR", bg="#ef4444", fg="white",
                  command=self._limpiar, **btn_cfg).grid(row=2, column=8, padx=8, pady=(4,0), sticky="ew")

        # botones de carga rápida
        frame_quick = tk.Frame(self.root, bg="#0f172a")
        frame_quick.pack(anchor="w", padx=20, pady=(2,0))
        tk.Label(frame_quick, text="Carga rápida:", bg="#0f172a", fg="#64748b",
                 font=("Segoe UI", 8)).pack(side="left")
        tk.Button(frame_quick, text="Ejemplo básico", bg="#334155", fg="#94a3b8",
                  relief="flat", font=("Segoe UI", 8), cursor="hand2",
                  command=self._ejemplo_basico).pack(side="left", padx=6)
        tk.Button(frame_quick, text="Ejemplo completo", bg="#334155", fg="#94a3b8",
                  relief="flat", font=("Segoe UI", 8), cursor="hand2",
                  command=self._ejemplo_completo).pack(side="left")

        # ── tabla de labores ingresadas ───────
        tk.Label(self.root, text="LABORES INGRESADAS",
                 bg="#0f172a", fg="#94a3b8",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=20, pady=(10,2))
        cols_in = ("Emoji", "Labor", "Responsable", "Duración", "Llegada")
        self.tree_in = ttk.Treeview(self.root, columns=cols_in,
                                    show="headings", height=4)
        anchos = [50, 140, 110, 90, 90]
        for col, w in zip(cols_in, anchos):
            self.tree_in.heading(col, text=col)
            self.tree_in.column(col, width=w, anchor="center")
        self.tree_in.pack(fill="x", padx=20)

        # ── diagrama de Gantt ─────────────────
        tk.Label(self.root, text="DIAGRAMA DE GANTT  —  EJECUCIÓN",
                 bg="#0f172a", fg="#94a3b8",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=20, pady=(10,2))
        self.canvas = tk.Canvas(self.root, height=120, bg="#020617",
                                highlightthickness=0)
        self.canvas.pack(fill="x", padx=20, pady=(0,4))

        # ── tabla de resultados ───────────────
        tk.Label(self.root, text="RESULTADOS",
                 bg="#0f172a", fg="#94a3b8",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=20, pady=(6,2))
        cols_res = ("Emoji", "Labor", "Responsable", "Llegada",
                    "Duración", "Final", "Espera", "Retorno")
        self.tree_res = ttk.Treeview(self.root, columns=cols_res,
                                     show="headings", height=6)
        anchos_res = [50, 130, 110, 75, 75, 75, 75, 75]
        for col, w in zip(cols_res, anchos_res):
            self.tree_res.heading(col, text=col)
            self.tree_res.column(col, width=w, anchor="center")
        self.tree_res.pack(fill="both", expand=True, padx=20, pady=(0,4))

        # barra de promedios
        self.lbl_promedios = tk.Label(self.root, text="",
                                      bg="#0f172a", fg="#38bdf8",
                                      font=("Segoe UI", 9, "bold"))
        self.lbl_promedios.pack(pady=(0, 8))

    # ── acciones ─────────────────────────────
    def _agregar(self):
        try:
            labor      = self.labor_var.get().strip()
            responsable = self.persona_var.get().strip()
            dur        = int(self.dur_ent.get())
            llegada    = int(self.llegada_ent.get())
            if dur < 1:
                raise ValueError("La duración debe ser ≥ 1")
            if llegada < 0:
                raise ValueError("El tiempo de llegada no puede ser negativo")

            t = LaborHogar(labor, responsable, dur, llegada)
            self.lista_labores.append(t)
            self.tree_in.insert("", "end",
                                values=(t.emoji, t.nombre, t.responsable,
                                        f"{t.duracion} min", f"{t.llegada} min"))
            # limpiar campos numéricos
            self.dur_ent.delete(0, tk.END);    self.dur_ent.insert(0, "10")
            self.llegada_ent.delete(0, tk.END); self.llegada_ent.insert(0, "0")
        except ValueError as e:
            messagebox.showwarning("Datos inválidos", str(e))

    def _limpiar(self):
        self.lista_labores.clear()
        for w in (self.tree_in, self.tree_res):
            for item in w.get_children(): w.delete(item)
        self.canvas.delete("all")
        self.lbl_promedios.config(text="")
        messagebox.showinfo("Reinicio", "Sistema reiniciado correctamente.")

    def _ejecutar(self):
        if not self.lista_labores:
            messagebox.showwarning("Sin labores", "Agrega al menos una labor antes de iniciar.")
            return
        try:
            quantum = int(self.q_ent.get())
            if quantum < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Quantum inválido", "El Quantum debe ser un entero ≥ 1.")
            return

        tareas_resultado, historial = ejecutar_round_robin(self.lista_labores, quantum)

        self.canvas.delete("all")
        self._dibujar_gantt(historial)
        self._mostrar_resultados(tareas_resultado)

    # ── Gantt (basado en draw_modern_gantt del código base) ──
    def _dibujar_gantt(self, historial):
        if not historial:
            return
        t_total = historial[-1][3]  # índice 3 = t_fin
        self.root.update_idletasks()
        ancho = self.canvas.winfo_width() - 40
        escala = ancho / max(t_total, 1)

        y0, y1, y_label, y_tiempo = 20, 75, 48, 95

        for nombre, responsable, inicio, fin, color, emoji in historial:
            x0 = inicio * escala + 20
            x1 = fin    * escala + 20
            # barra principal
            self.canvas.create_rectangle(x0, y0, x1, y1,
                                         fill=color, outline="#0f172a", width=2)
            # texto dentro de la barra
            if (x1 - x0) > 22:
                self.canvas.create_text((x0+x1)/2, y_label,
                                        text=f"{emoji}{nombre[:8]}",
                                        fill="white",
                                        font=("Segoe UI", 7, "bold"))
            # marca de tiempo inferior
            self.canvas.create_line(x0, y1+2, x0, y_tiempo-4,
                                    fill="#334155", width=1)
            self.canvas.create_text(x0, y_tiempo,
                                    text=str(inicio),
                                    fill="#64748b",
                                    font=("Consolas", 7))

        # tiempo final
        x_fin = t_total * escala + 20
        self.canvas.create_text(x_fin, y_tiempo,
                                text=str(t_total),
                                fill="#38bdf8",
                                font=("Consolas", 8, "bold"))

    # ── tabla de resultados ───────────────────
    def _mostrar_resultados(self, tareas):
        for item in self.tree_res.get_children():
            self.tree_res.delete(item)

        total_espera = total_retorno = 0
        for t in tareas:
            self.tree_res.insert("", "end",
                                 values=(t.emoji, t.nombre, t.responsable,
                                         t.llegada, t.duracion,
                                         t.final, t.espera, t.retorno))
            total_espera   += t.espera
            total_retorno  += t.retorno

        n = len(tareas)
        self.lbl_promedios.config(
            text=(f"⏱  Promedio de espera: {total_espera/n:.1f} min   |   " f"🔄 Promedio de retorno: {total_retorno/n:.1f} min")
        )

    # ── ejemplos de carga rápida ──────────────
    def _ejemplo_basico(self):
        self._limpiar_silencioso()
        datos = [
            ("Barrer",       "Mamá",  15, 0),
            ("Lavar platos", "Papá",  10, 0),
            ("Sacar basura", "Hijo",   5, 2),
            ("Cocinar",      "Mamá",  20, 0),
        ]
        for labor, persona, dur, llegada in datos:
            t = LaborHogar(labor, persona, dur, llegada)
            self.lista_labores.append(t)
            self.tree_in.insert("", "end",
                                values=(t.emoji, t.nombre, t.responsable,
                                        f"{t.duracion} min", f"{t.llegada} min"))
        self.q_ent.delete(0, tk.END); self.q_ent.insert(0, "5")

    def _ejemplo_completo(self):
        self._limpiar_silencioso()
        datos = [
            ("Barrer",       "Mamá",   15,  0),
            ("Trapear",      "Hija",   12,  0),
            ("Lavar platos", "Papá",   10,  3),
            ("Lavar ropa",   "Mamá",   25,  5),
            ("Cocinar",      "Abuela", 30,  0),
            ("Compras",      "Papá",   20,  8),
            ("Jardinería",   "Hijo",   18, 10),
            ("Limpiar baño", "Hija",    8,  2),
        ]
        for labor, persona, dur, llegada in datos:
            t = LaborHogar(labor, persona, dur, llegada)
            self.lista_labores.append(t)
            self.tree_in.insert("", "end",
                                values=(t.emoji, t.nombre, t.responsable,
                                        f"{t.duracion} min", f"{t.llegada} min"))
        self.q_ent.delete(0, tk.END); self.q_ent.insert(0, "7")

    def _limpiar_silencioso(self):
        self.lista_labores.clear()
        for w in (self.tree_in, self.tree_res):
            for item in w.get_children(): w.delete(item)
        self.canvas.delete("all")
        self.lbl_promedios.config(text="")


# ─────────────────────────────────────────────
#  PUNTO DE ENTRADA
# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = AppHogar(root)
    root.mainloop()