import tkinter as tk
from tkinter import ttk, messagebox
import random

# representa cada proceso individual
class Tarea:
    def __init__(self, nombre, duracion, llegada):
        self.nombre = nombre
        self.duracion = duracion # tiempo total que necesita en el CPU
        self.llegada = llegada     # momento en el que entra al sistema
        self.duracion_tmp = duracion # lo que le falta por procesar (se va restando)
        self.color = random.choice(["#00f2fe", "#4facfe", "#f093fb", "#6a11cb", "#00dbde"])
        self.espera = 0   # tiempo que pasó en la cola sin ser atendido
        self.retorno = 0  # tiempo total desde que llegó hasta que terminó
        self.final = 0    # el segundo exacto en el que terminó

class Ventana:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x750")
        self.root.configure(bg="#0f172a") 
        
        self.lista_tareas = [] #lista vacia
        self.setup_styles() #para los estilos
        self.create_widgets() #componentes graficos

    def setup_styles(self):
        style = ttk.Style() #para inicializar lo estilos
        style.theme_use("clam")
        style.configure("Treeview", background="#1e293b", foreground="white", fieldbackground="#1e293b", borderwidth=0) #darle formato a la tabla
        style.map("Treeview", background=[('selected', '#334155')])
        style.configure("TLabel", background="#0f172a", foreground="#94a3b8", font=("Segoe UI", 10)) #formato a los textos
        style.configure("TButton", font=("Segoe UI", 10, "bold")) #formato a los botones

    def create_widgets(self):
        header = tk.Label(self.root, text=" SISTEMA DE DISTRIBUCIÓN DE TAREAS", 
                          bg="#0f172a", fg="#38bdf8", font=("Segoe UI", 16, "bold"))
        header.pack(pady=15)

        frame_in = tk.Frame(self.root, bg="#1e293b", padx=15, pady=15)
        frame_in.pack(fill="x", padx=20, pady=5)

        # entradas manuales
        ttk.Label(frame_in, text="Nombre Tarea:").grid(row=0, column=0, sticky="w")
        self.name_var = tk.StringVar(value="")
        self.name_ent = ttk.Entry(frame_in, textvariable=self.name_var) #lo que ingresa
        self.name_ent.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_in, text="Duración:").grid(row=0, column=2, padx=5)
        self.duracion_ent = ttk.Entry(frame_in, width=8)
        self.duracion_ent.grid(row=0, column=3, padx=5)

        ttk.Label(frame_in, text="Tiempo Llegada:").grid(row=0, column=4, padx=5)
        self.llegada_ent = ttk.Entry(frame_in, width=8)
        self.llegada_ent.grid(row=0, column=5, padx=5)

        ttk.Label(frame_in, text="Quantum:").grid(row=1, column=0, sticky="w")
        self.q_ent = ttk.Entry(frame_in, width=8)
        self.q_ent.insert(0, "4")
        self.q_ent.grid(row=1, column=1, sticky="w", padx=5)

        btn_add = tk.Button(frame_in, text="+ Añadir Tarea", bg="#10b981", fg="white", 
                            relief="flat", width=15, command=self.add_tarea)
        btn_add.grid(row=0, column=6, padx=10, sticky="nsew")

        btn_run = tk.Button(frame_in, text=" INICIAR", bg="#3b82f6", fg="white", 
                            relief="flat", width=15, command=self.ejecutar)
        btn_run.grid(row=1, column=6, padx=10, pady=5, sticky="nsew")
        
        btn_clear = tk.Button(frame_in, text="REINICIAR", bg="#ef4444", fg="white", 
                             relief="flat", width=15, command=self.limpiar)
        btn_clear.grid(row=2, column=6, padx=10, sticky="nsew")

        self.canvas_label = ttk.Label(self.root, text="TIEMPO DE EJECUCIÓN", font=("Segoe UI", 9, "bold"))
        self.canvas_label.pack(anchor="w", padx=20, pady=(10,0))
        self.canvas = tk.Canvas(self.root, height=140, bg="#020617", highlightthickness=0) #espacio para la grafica
        self.canvas.pack(fill="x", padx=20, pady=5)

        cols = ("Tarea", "Llegada", "Duración", "Final", "Espera", "Retorno")
        self.tree = ttk.Treeview(self.root, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        

    def add_tarea(self):
        try:
            nombre = self.name_ent.get().strip()
            if not nombre: nombre = f"Tarea {len(self.lista_tareas)+1}"
            d = int(self.duracion_ent.get())
            l = int(self.llegada_ent.get())
            
            self.lista_tareas.append(Tarea(nombre, d, l))
            self.tree.insert("", "end", values=(nombre, l, d, "-", "-", "-"))
            
            self.name_var.set("")
            self.duracion_ent.delete(0, tk.END)
            self.llegada_ent.delete(0, tk.END)
        except:
            messagebox.showwarning("Atención", "Por favor ingresa números válidos.")

    def limpiar(self):
        self.lista_tareas = []
        for item in self.tree.get_children(): self.tree.delete(item)
        self.canvas.delete("all")
        messagebox.showinfo("Limpieza", "Sistema reiniciado.")

    def ejecutar(self):
        if not self.lista_tareas:
            messagebox.showwarning("Vacío", "No hay tareas para procesar.")
            return
            
        self.canvas.delete("all")
        quantum = int(self.q_ent.get())
        
        # ordenar por tiempo de llegada 
        tareas_ordenadas = sorted([t for t in self.lista_tareas], key=lambda x: x.llegada)
        for t in tareas_ordenadas: t.duracion_tmp = t.duracion
        
        tiempo_actual, terminadas, idx = 0, 0, 0
        cola_listos, historial_grafica = [], [] #agregar las tareas en orden con info

        while terminadas < len(tareas_ordenadas):
            # revisar qué tareas han llegado en el tiempo actual
            while idx < len(tareas_ordenadas) and tareas_ordenadas[idx].llegada <= tiempo_actual:
                cola_listos.append(tareas_ordenadas[idx])
                idx += 1
            
            if cola_listos:
                tarea_actual = cola_listos.pop(0) #saca al primero de la lista
                inicio_bloque = tiempo_actual
                
                # ejecutar por el Quantum o lo que quede de duración
                tiempo_ejecutado = min(tarea_actual.duracion_tmp, quantum)
                tarea_actual.duracion_tmp -= tiempo_ejecutado #restamos el tiempo ejecutado
                tiempo_actual += tiempo_ejecutado #el reloj avanza
                
                # guardar para el dibujo
                historial_grafica.append((tarea_actual.nombre, inicio_bloque, tiempo_actual, tarea_actual.color))
                
                # ver si llegaron tareas nuevas mientras se ejecutaba una
                while idx < len(tareas_ordenadas) and tareas_ordenadas[idx].llegada <= tiempo_actual:
                    cola_listos.append(tareas_ordenadas[idx])
                    idx += 1
                
                if tarea_actual.duracion_tmp > 0:
                    cola_listos.append(tarea_actual) # vuelve a la cola
                else:
                    #calculamos resultados finales
                    tarea_actual.final = tiempo_actual
                    tarea_actual.retorno = tarea_actual.final - tarea_actual.llegada
                    tarea_actual.espera = tarea_actual.retorno - tarea_actual.duracion
                    terminadas += 1
            else:
                tiempo_actual += 1 # rl CPU espera a que llegue alguien

        

        self.draw_modern_gantt(historial_grafica) #para empezar a dibujar
        self.update_results(tareas_ordenadas)
        
#funcion que divide el ancho del los rectangulos
    def draw_modern_gantt(self, historial):
        if not historial: return
        t_final_total = historial[-1][2]
        self.root.update_idletasks()#para actualizar
        ancho_canvas = self.canvas.winfo_width() - 40 #para ajustar un ancho
        escala = ancho_canvas / t_final_total #para los pixeles

        for nombre, inicio, fin, color in historial: #para obtener valores
            x0, x1 = inicio * escala + 20, fin * escala + 20 #coordenadas de los picxeles
            self.canvas.create_rectangle(x0, 30, x1, 80, fill=color, outline="#0f172a", width=2)#dibuja la barra del color
            self.canvas.create_text((x0+x1)/2, 55, text=nombre[:10], fill="white", font=("Segoe UI", 8, "bold"))
            self.canvas.create_text(x0, 100, text=str(inicio), fill="#64748b", font=("Consolas", 8))
        
        self.canvas.create_text(t_final_total * escala + 20, 100, text=str(t_final_total), fill="#38bdf8", font=("Consolas", 8, "bold"))

    def update_results(self, tareas):
        for item in self.tree.get_children(): self.tree.delete(item)
        for t in tareas:
            self.tree.insert("", "end", values=(t.nombre, t.llegada, t.duracion, t.final, t.espera, t.retorno))

if __name__ == "__main__":
    root = tk.Tk()
    app = Ventana(root)
    root.mainloop()