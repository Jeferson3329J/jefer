import tkinter as tk
from tkinter import messagebox

ventana = tk.Tk()
ventana.title("Nombre")
ventana.geometry("400x250")
ventana.resizable(False, False)

nombre = tk.StringVar()

tk.Label(ventana, text="Escribe tu nombre:", font=("Arial", 12)).pack(pady=20)

entrada = tk.Entry(ventana, textvariable=nombre, font=("Arial", 12), width=30, justify="center")
entrada.pack()
entrada.focus()

def guardar():
    if nombre.get().strip() == "":
        messagebox.showwarning("Aviso", "Escribe tu nombre")
    else:
        messagebox.showinfo("Guardado", f"Nombre guardado:\n{nombre.get()}")

tk.Button(ventana, text="Guardar", font=("Arial", 11), command=guardar).pack(pady=25)

ventana.mainloop()