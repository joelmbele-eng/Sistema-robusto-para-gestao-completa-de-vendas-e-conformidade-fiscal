import customtkinter as ctk
from tkinter import messagebox
from database import criar_tabelas, conectar
from admin import JanelaAdmin
from usuario import JanelaUsuario
from PIL import Image, ImageTk

def tela_login():
    login_win = ctk.CTk()
    login_win.title("Login")
    login_win.iconbitmap('image/mgrace.ico')
    login_win.geometry("400x450")
    login_win.resizable(False, False)
    
    # Carregando a imagem de fundo
    bg_image = Image.open("image/xx.png")  # Substitua pelo caminho da sua imagem
    bg_image = bg_image.resize((400, 450))
    bg_photo = ImageTk.PhotoImage(bg_image)
    
    # Criando um label para o fundo
    bg_label = ctk.CTkLabel(login_win, image=bg_photo, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Cobre toda a janela
    
    # Frame para conter os widgets (para melhor organização sobre o fundo)
    frame = ctk.CTkFrame(login_win, corner_radius=10, fg_color="transparent")
    frame.pack(pady=20, padx=20, fill="both", expand=True)
    
    lbl = ctk.CTkLabel(frame, text="Sistema de Vendas - Login", font=("Arial", 20))
    lbl.pack(pady=20)
    
    add = ImageTk.PhotoImage(Image.open("image/logg.png").resize((100, 100)))
    gtv = ctk.CTkButton(frame, image=add, text="", fg_color="#EBEBEB", hover=None, width=60, height=70)
    gtv.pack(pady=20)
    
    entry_nome = ctk.CTkEntry(frame, placeholder_text="Nome")
    entry_nome.pack(pady=10)
    
    entry_senha = ctk.CTkEntry(frame, placeholder_text="Senha", show="*")
    entry_senha.pack(pady=10)
    
    def logar():
        nome = entry_nome.get()
        senha = entry_senha.get()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, tipo, ativo FROM usuarios WHERE nome=? AND senha=?", (nome, senha))
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario:
            id_usuario, tipo, ativo = usuario
            if ativo != 1:
                messagebox.showerror("Acesso Negado", "Este usuário está desativado!")
                return
            login_win.destroy()
            if tipo == "admin":
                app = JanelaAdmin()
            else:
                app = JanelaUsuario(nome)
            app.mainloop()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")
    
    btn = ctk.CTkButton(frame, text="Entrar", command=logar)
    btn.pack(pady=20)
    
    login_win.mainloop()

if __name__ == "__main__":
    criar_tabelas()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE tipo='admin'")
    admin_existente = cursor.fetchone()
    if not admin_existente:
        cursor.execute("INSERT INTO usuarios (nome, senha, tipo, ativo) VALUES (?, ?, ?, ?)", ("admin", "admin", "admin", 1))
        conn.commit()
        print("Usuário admin padrão criado: admin / admin")
    conn.close()
    tela_login()
