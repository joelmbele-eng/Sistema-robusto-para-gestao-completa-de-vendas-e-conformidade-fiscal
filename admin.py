# admin.py
import customtkinter as ctk
from tkinter import ttk, messagebox, Toplevel, simpledialog, Text, END
from tkcalendar import Calendar
import datetime
from database import conectar, get_config, set_config
from utils import (gerar_pdf, gerar_pdf_cancelamento, gerar_pdf_contabilidade,
                   exportar_excel, gerar_saft, gerar_grafico_vendas, imprimir_pdf)
import json
import win32print, win32api
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from PIL import Image, ImageTk


PAPER_OPTIONS = ["A4", "A5", "Letter"]

def get_stock_status(qtd, limite):
    if qtd >= limite:
        return ("verde", "Estoque OK")
    elif qtd == 0:
        return ("vermelho", "Sem estoque!")
    elif qtd < (limite / 2):
        return ("vermelho", "Estoque baixo")
    else:
        return ("amarelo", "Estoque quase acabando")

class JanelaAdmin(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Painel do Administrador")
        self.iconbitmap('image/mgrace.ico')
        self.geometry("1200x800")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.btn_logout = ctk.CTkButton(self, text="Trocar Sessão", command=self.trocar_sessao)
        self.btn_logout.pack(pady=5)
        self.tabview = ctk.CTkTabview(self, width=1180, height=750)
        self.tabview.pack(padx=10, pady=10)
        for aba in ["Produtos", "Usuários", "Empresa", "Config Papel", "Config Email",
                    "Contabilidade", "Estoque RealTime", "Relatórios", "Cancelar Venda",
                    "Mais Vendidos", "Solicitações", "Sessões"]:
            self.tabview.add(aba)
        self.criar_frame_produtos()
        self.criar_frame_usuarios()
        self.criar_frame_empresa()
        self.criar_frame_config_papel()
        self.criar_frame_config_email()
        self.criar_frame_contabilidade()
        self.criar_frame_estoque_realtime()
        self.criar_frame_relatorios()
        self.criar_frame_cancelar_venda()
        self.criar_frame_mais_vendidos()
        self.criar_frame_solicitacoes()
        self.criar_frame_sessoes()

    def on_closing(self):
        self.destroy()

    def trocar_sessao(self):
        self.destroy()
        import main
        main.tela_login()

    # --- Produtos ---
    def criar_frame_produtos(self):
        frame = self.tabview.tab("Produtos")
        lbl = ctk.CTkLabel(frame, text="Cadastro de Produtos", font=("Arial", 18))
        lbl.pack(pady=5)
        form_frame = ctk.CTkFrame(frame)
        form_frame.pack(pady=5)
        self.prod_nome = ctk.CTkEntry(form_frame, placeholder_text="Nome", width=200)
        self.prod_nome.grid(row=0, column=0, padx=5, pady=5)
        self.prod_desc = ctk.CTkEntry(form_frame, placeholder_text="Descrição", width=200)
        self.prod_desc.grid(row=0, column=1, padx=5, pady=5)
        self.prod_categoria = ctk.CTkEntry(form_frame, placeholder_text="Categoria", width=200)
        self.prod_categoria.grid(row=1, column=0, padx=5, pady=5)
        self.prod_quantidade = ctk.CTkEntry(form_frame, placeholder_text="Quantidade", width=200)
        self.prod_quantidade.grid(row=1, column=1, padx=5, pady=5)
        self.prod_preco_detail = ctk.CTkEntry(form_frame, placeholder_text="Preço a Detail (Kz)", width=200)
        self.prod_preco_detail.grid(row=2, column=0, padx=5, pady=5)
        self.prod_preco_grosso = ctk.CTkEntry(form_frame, placeholder_text="Preço a Grosso (Kz)", width=200)
        self.prod_preco_grosso.grid(row=2, column=1, padx=5, pady=5)
        self.prod_validade = ctk.CTkEntry(form_frame, placeholder_text="Data de Validade (AAAA-MM-DD)", width=200)
        self.prod_validade.grid(row=3, column=0, padx=5, pady=5)
        self.prod_limite = ctk.CTkEntry(form_frame, placeholder_text="Limite Mínimo", width=200)
        self.prod_limite.grid(row=3, column=1, padx=5, pady=5)
        self.prod_iva = ctk.CTkEntry(form_frame, placeholder_text="IVA (%)", width=200)
        self.prod_iva.grid(row=4, column=0, padx=5, pady=5)
        btn_cadastrar = ctk.CTkButton(form_frame, text="Cadastrar Produto", command=self.cadastrar_produto)
        btn_cadastrar.grid(row=5, column=0, columnspan=2, pady=5)
        self.tree_produtos = ttk.Treeview(frame, columns=("ID", "Nome", "Categoria", "Qtd", "Detail", "Grosso", "Validade", "Limite", "IVA (%)", "Comentário"), show="headings", height=8)
        for col in ("ID", "Nome", "Categoria", "Qtd", "Detail", "Grosso", "Validade", "Limite", "IVA (%)", "Comentário"):
            self.tree_produtos.heading(col, text=col)
            if col in ("IVA (%)", "Comentário"):
                self.tree_produtos.column(col, width=120)
            else:
                self.tree_produtos.column(col, width=100)
        self.tree_produtos.pack(pady=5)
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Editar Selecionado", command=self.editar_produto).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Excluir Selecionado", command=self.excluir_produto).grid(row=0, column=1, padx=5)
        self.refresh_produtos()

    def cadastrar_produto(self):
        nome = self.prod_nome.get()
        desc = self.prod_desc.get()
        cat = self.prod_categoria.get()
        try:
            qtd = int(self.prod_quantidade.get())
        except:
            qtd = 0
        try:
            preco_detail = float(self.prod_preco_detail.get())
        except:
            preco_detail = 0.0
        try:
            preco_grosso = float(self.prod_preco_grosso.get())
        except:
            preco_grosso = 0.0
        validade = self.prod_validade.get().strip() or None
        try:
            limite = int(self.prod_limite.get())
        except:
            limite = 0
        try:
            iva = float(self.prod_iva.get())
        except:
            iva = 0.0
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO produtos (nome, descricao, categoria, quantidade, preco_detail, preco_grosso, data_validade, limite_minimo, iva)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       (nome, desc, cat, qtd, preco_detail, preco_grosso, validade, limite, iva))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Produto cadastrado!")
        self.refresh_produtos()

    def refresh_produtos(self):
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, categoria, quantidade, preco_detail, preco_grosso, data_validade, limite_minimo, iva FROM produtos")
        for row in cursor.fetchall():
            qtd = row[3]
            limite = row[7]
            tag, comentario = get_stock_status(qtd, limite)
            valores = list(row) + [comentario]
            self.tree_produtos.insert("", "end", values=valores, tags=(tag,))
        conn.close()
        self.tree_produtos.tag_configure("verde", background="lightgreen")
        self.tree_produtos.tag_configure("amarelo", background="khaki")
        self.tree_produtos.tag_configure("vermelho", background="tomato")

    def editar_produto(self):
        selecionado = self.tree_produtos.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um produto para editar.")
            return
        valores = self.tree_produtos.item(selecionado, "values")
        prod_id = valores[0]
        edit_win = ctk.CTkToplevel(self)
        edit_win.title("Editar Produto")
        edit_win.iconbitmap('image/mgrace.ico')
        edit_win.geometry("400x550")
        entry_nome = ctk.CTkEntry(edit_win, placeholder_text="Nome", width=300)
        entry_nome.insert(0, valores[1])
        entry_nome.pack(pady=5)
        entry_cat = ctk.CTkEntry(edit_win, placeholder_text="Categoria", width=300)
        entry_cat.insert(0, valores[2])
        entry_cat.pack(pady=5)
        entry_qtd = ctk.CTkEntry(edit_win, placeholder_text="Quantidade", width=300)
        entry_qtd.insert(0, valores[3])
        entry_qtd.pack(pady=5)
        entry_preco_detail = ctk.CTkEntry(edit_win, placeholder_text="Preço a Detail (Kz)", width=300)
        entry_preco_detail.insert(0, valores[4])
        entry_preco_detail.pack(pady=5)
        entry_preco_grosso = ctk.CTkEntry(edit_win, placeholder_text="Preço a Grosso (Kz)", width=300)
        entry_preco_grosso.insert(0, valores[5])
        entry_preco_grosso.pack(pady=5)
        entry_validade = ctk.CTkEntry(edit_win, placeholder_text="Data de Validade", width=300)
        entry_validade.insert(0, valores[6])
        entry_validade.pack(pady=5)
        entry_limite = ctk.CTkEntry(edit_win, placeholder_text="Limite Mínimo", width=300)
        entry_limite.insert(0, valores[7])
        entry_limite.pack(pady=5)
        entry_iva = ctk.CTkEntry(edit_win, placeholder_text="IVA (%)", width=300)
        entry_iva.insert(0, valores[8])
        entry_iva.pack(pady=5)
        def salvar_edicao():
            novo_nome = entry_nome.get()
            novo_cat = entry_cat.get()
            try:
                nova_qtd = int(entry_qtd.get())
            except:
                nova_qtd = 0
            try:
                novo_preco_detail = float(entry_preco_detail.get())
            except:
                novo_preco_detail = 0.0
            try:
                novo_preco_grosso = float(entry_preco_grosso.get())
            except:
                novo_preco_grosso = 0.0
            nova_validade = entry_validade.get().strip() or None
            try:
                novo_limite = int(entry_limite.get())
            except:
                novo_limite = 0
            try:
                novo_iva = float(entry_iva.get())
            except:
                novo_iva = 0.0
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""UPDATE produtos SET nome=?, categoria=?, quantidade=?, preco_detail=?, preco_grosso=?, data_validade=?, limite_minimo=?, iva=?
                              WHERE id=?""",
                           (novo_nome, novo_cat, nova_qtd, novo_preco_detail, novo_preco_grosso, nova_validade, novo_limite, novo_iva, prod_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Produto atualizado!")
            edit_win.destroy()
            self.refresh_produtos()
        ctk.CTkButton(edit_win, text="Salvar Alterações", command=salvar_edicao).pack(pady=20)

    def excluir_produto(self):
        selecionado = self.tree_produtos.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um produto para excluir.")
            return
        valores = self.tree_produtos.item(selecionado, "values")
        prod_id = valores[0]
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE id=?", (prod_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Produto excluído!")
        self.refresh_produtos()

    # --- Usuários ---
    def criar_frame_usuarios(self):
        frame = self.tabview.tab("Usuários")
        lbl = ctk.CTkLabel(frame, text="Cadastro de Usuários", font=("Arial", 18))
        lbl.pack(pady=5)
        form_frame = ctk.CTkFrame(frame)
        form_frame.pack(pady=5)
        self.user_nome = ctk.CTkEntry(form_frame, placeholder_text="Nome do Usuário", width=200)
        self.user_nome.grid(row=0, column=0, padx=5, pady=5)
        self.user_senha = ctk.CTkEntry(form_frame, placeholder_text="Senha", width=200, show="*")
        self.user_senha.grid(row=0, column=1, padx=5, pady=5)
        btn_cadastrar = ctk.CTkButton(form_frame, text="Cadastrar Usuário", command=self.cadastrar_usuario)
        btn_cadastrar.grid(row=1, column=0, columnspan=2, pady=5)
        self.tree_usuarios = ttk.Treeview(frame, columns=("ID", "Nome", "Tipo", "Ativo"), show="headings", height=8)
        for col in ("ID", "Nome", "Tipo", "Ativo"):
            self.tree_usuarios.heading(col, text=col)
            self.tree_usuarios.column(col, width=150)
        self.tree_usuarios.pack(pady=5)
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=5)
        ctk.CTkButton(btn_frame, text="Editar Selecionado", command=self.editar_usuario).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Excluir Selecionado", command=self.excluir_usuario).grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_frame, text="Ativar/Desativar", command=self.alternar_status_usuario).grid(row=0, column=2, padx=5)
        self.refresh_usuarios()

    def cadastrar_usuario(self):
        nome = self.user_nome.get()
        senha = self.user_senha.get()
        tipo = "usuario"
        ativo = 1
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, senha, tipo, ativo) VALUES (?, ?, ?, ?)", (nome, senha, tipo, ativo))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Usuário cadastrado!")
        self.refresh_usuarios()

    def refresh_usuarios(self):
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, tipo, ativo FROM usuarios")
        for row in cursor.fetchall():
            self.tree_usuarios.insert("", "end", values=row)
        conn.close()

    def editar_usuario(self):
        selecionado = self.tree_usuarios.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um usuário para editar.")
            return
        valores = self.tree_usuarios.item(selecionado, "values")
        user_id = valores[0]
        edit_win = ctk.CTkToplevel(self)
        edit_win.title("Editar Usuário")
        edit_win.iconbitmap('image/mgrace.ico')
        edit_win.geometry("400x300")
        entry_nome = ctk.CTkEntry(edit_win, placeholder_text="Novo Nome", width=300)
        entry_nome.insert(0, valores[1])
        entry_nome.pack(pady=5)
        entry_senha = ctk.CTkEntry(edit_win, placeholder_text="Nova Senha", width=300, show="*")
        entry_senha.pack(pady=5)
        def salvar_usuario():
            novo_nome = entry_nome.get()
            nova_senha = entry_senha.get()
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET nome=?, senha=? WHERE id=?", (novo_nome, nova_senha, user_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Usuário atualizado!")
            edit_win.destroy()
            self.refresh_usuarios()
        ctk.CTkButton(edit_win, text="Salvar Alterações", command=salvar_usuario).pack(pady=20)

    def excluir_usuario(self):
        selecionado = self.tree_usuarios.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um usuário para excluir.")
            return
        valores = self.tree_usuarios.item(selecionado, "values")
        user_id = valores[0]
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Usuário excluído!")
        self.refresh_usuarios()

    def alternar_status_usuario(self):
        selecionado = self.tree_usuarios.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um usuário para alterar o status.")
            return
        valores = self.tree_usuarios.item(selecionado, "values")
        user_id = valores[0]
        status_atual = int(valores[3])
        novo_status = 0 if status_atual == 1 else 1
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET ativo=? WHERE id=?", (novo_status, user_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Status alterado!")
        self.refresh_usuarios()

    # --- Empresa ---
    def criar_frame_empresa(self):
        frame = self.tabview.tab("Empresa")
        lbl = ctk.CTkLabel(frame, text="Dados da Empresa", font=("Arial", 18))
        lbl.pack(pady=5)
        form_frame = ctk.CTkFrame(frame)
        form_frame.pack(pady=5)
        self.emp_nome = ctk.CTkEntry(form_frame, placeholder_text="Nome da Empresa", width=300)
        self.emp_nome.grid(row=0, column=0, padx=5, pady=5)
        self.emp_local = ctk.CTkEntry(form_frame, placeholder_text="Localização", width=300)
        self.emp_local.grid(row=0, column=1, padx=5, pady=5)
        self.emp_provincia = ctk.CTkEntry(form_frame, placeholder_text="Província", width=300)
        self.emp_provincia.grid(row=1, column=0, padx=5, pady=5)
        self.emp_nif = ctk.CTkEntry(form_frame, placeholder_text="NIF", width=300)
        self.emp_nif.grid(row=1, column=1, padx=5, pady=5)
        self.emp_tel = ctk.CTkEntry(form_frame, placeholder_text="Telefone", width=300)
        self.emp_tel.grid(row=2, column=0, padx=5, pady=5)
        self.emp_obs = ctk.CTkEntry(form_frame, placeholder_text="Observação", width=300)
        self.emp_obs.grid(row=2, column=1, padx=5, pady=5)
        btn_salvar = ctk.CTkButton(form_frame, text="Salvar Dados", command=self.salvar_empresa)
        btn_salvar.grid(row=3, column=0, columnspan=2, pady=5)
        self.carregar_empresa()

    def salvar_empresa(self):
        nome = self.emp_nome.get()
        local = self.emp_local.get()
        prov = self.emp_provincia.get()
        nif = self.emp_nif.get()
        tel = self.emp_tel.get()
        obs = self.emp_obs.get()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM empresa")
        reg = cursor.fetchone()
        if reg:
            cursor.execute("UPDATE empresa SET nome=?, localizacao=?, provincia=?, nif=?, telefone=?, observacao=? WHERE id=?",
                           (nome, local, prov, nif, tel, obs, reg[0]))
        else:
            cursor.execute("INSERT INTO empresa (nome, localizacao, provincia, nif, telefone, observacao) VALUES (?, ?, ?, ?, ?, ?)",
                           (nome, local, prov, nif, tel, obs))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Dados da empresa salvos!")
        self.carregar_empresa()

    def carregar_empresa(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, localizacao, provincia, nif, telefone, observacao FROM empresa")
        reg = cursor.fetchone()
        conn.close()
        if reg:
            self.emp_nome.delete(0, "end"); self.emp_nome.insert(0, reg[0])
            self.emp_local.delete(0, "end"); self.emp_local.insert(0, reg[1])
            self.emp_provincia.delete(0, "end"); self.emp_provincia.insert(0, reg[2])
            self.emp_nif.delete(0, "end"); self.emp_nif.insert(0, reg[3])
            self.emp_tel.delete(0, "end"); self.emp_tel.insert(0, reg[4])
            self.emp_obs.delete(0, "end"); self.emp_obs.insert(0, reg[5] if reg[5] else "")

    # --- Config Papel ---
    def criar_frame_config_papel(self):
        frame = self.tabview.tab("Config Papel")
        lbl = ctk.CTkLabel(frame, text="Configuração de Papel e Impressora", font=("Arial", 18))
        lbl.pack(pady=5)
        ctk.CTkLabel(frame, text="Tamanho de Papel:").pack(pady=5)
        self.combo_papel = ttk.Combobox(frame, values=PAPER_OPTIONS)
        self.combo_papel.pack(pady=5)
        papel_config = get_config("paper_size")
        if papel_config and papel_config in PAPER_OPTIONS:
            self.combo_papel.set(papel_config)
        else:
            self.combo_papel.set("A5")
        ctk.CTkButton(frame, text="Salvar Tamanho de Papel", command=self.salvar_config_papel).pack(pady=5)
        ctk.CTkLabel(frame, text="Impressora Padrão:").pack(pady=5)
        printers = self.get_printers()
        self.combo_impressora = ttk.Combobox(frame, values=printers)
        self.combo_impressora.pack(pady=5)
        impressora_config = get_config("printer")
        if impressora_config and impressora_config in printers:
            self.combo_impressora.set(impressora_config)
        else:
            if printers:
                self.combo_impressora.set(printers[0])
        ctk.CTkButton(frame, text="Salvar Impressora", command=self.salvar_impressora).pack(pady=5)

    def get_printers(self):
        import win32print
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        printers = win32print.EnumPrinters(flags)
        return [printer[2] for printer in printers]

    def salvar_config_papel(self):
        papel = self.combo_papel.get()
        set_config("paper_size", papel)
        messagebox.showinfo("Sucesso", f"Tamanho de papel '{papel}' configurado com sucesso!")

    def salvar_impressora(self):
        impressora = self.combo_impressora.get()
        set_config("printer", impressora)
        messagebox.showinfo("Sucesso", f"Impressora '{impressora}' configurada com sucesso!")

    # --- Config Email ---
    def criar_frame_config_email(self):
        frame = self.tabview.tab("Config Email")
        lbl = ctk.CTkLabel(frame, text="Configuração de Email (desabilitado)", font=("Arial", 18))
        lbl.pack(pady=5)
        ctk.CTkLabel(frame, text="Esta funcionalidade foi desabilitada.").pack(pady=5)

    def salvar_config_email(self):
        pass

    # --- Contabilidade ---
    def criar_frame_contabilidade(self):
        frame = self.tabview.tab("Contabilidade")
        lbl = ctk.CTkLabel(frame, text="Contabilidade Diária", font=("Arial", 18))
        lbl.pack(pady=5)
        self.calendario_cont = Calendar(frame, date_pattern="yyyy-mm-dd")
        self.calendario_cont.pack(pady=5)
        btn_buscar = ctk.CTkButton(frame, text="Buscar", command=self.buscar_contabilidade)
        btn_buscar.pack(pady=5)
        self.tree_contabilidade = ttk.Treeview(frame, columns=("Data", "Produto", "Quantidade", "Total", "Usuário"), show="headings", height=8)
        for col in ("Data", "Produto", "Quantidade", "Total", "Usuário"):
            self.tree_contabilidade.heading(col, text=col)
            self.tree_contabilidade.column(col, width=120)
        self.tree_contabilidade.pack(pady=10)
        btn_imprimir = ctk.CTkButton(frame, text="Gerar Relatório Contábil (PDF)", command=self.imprimir_relatorio_admin)
        btn_imprimir.pack(pady=5)

    def buscar_contabilidade(self):
        data_sel = self.calendario_cont.get_date()
        for item in self.tree_contabilidade.get_children():
            self.tree_contabilidade.delete(item)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT data_venda, total, detalhes, id_usuario, status FROM vendas WHERE date(data_venda)=?", (data_sel,))
        vendas = cursor.fetchall()
        conn.close()
        for venda in vendas:
            data_venda, total, detalhes, usuario, status = venda
            try:
                itens = json.loads(detalhes)
                for item in itens:
                    self.tree_contabilidade.insert("", "end", values=(data_venda, item.get("nome", ""), item.get("quantidade", ""), f"Kz {float(item.get('subtotal', 0)):.2f}", usuario))
            except Exception as e:
                print("Erro:", e)

    def imprimir_relatorio_admin(self):
        data_sel = self.calendario_cont.get_date()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, data_venda, total, detalhes, id_usuario, status FROM vendas WHERE date(data_venda)=?", (data_sel,))
        vendas = cursor.fetchall()
        conn.close()
        if not vendas:
            messagebox.showinfo("Relatório", "Nenhuma venda encontrada para essa data.")
            return
        total_vendas = sum(float(v[2]) for v in vendas)
        from utils import gerar_pdf_contabilidade
        gerar_pdf_contabilidade(data_sel, vendas, total_vendas, nome_arquivo=f"contabilidade_{data_sel}.pdf")
        messagebox.showinfo("Relatório", f"Relatório contábil gerado para {data_sel}.")

    # --- Estoque RealTime ---
    def criar_frame_estoque_realtime(self):
        frame = self.tabview.tab("Estoque RealTime")
        lbl = ctk.CTkLabel(frame, text="Estoque em Tempo Real", font=("Arial", 18))
        lbl.pack(pady=5)
        self.canvas_frame = ctk.CTkFrame(frame)
        self.canvas_frame.pack(pady=5)
        self.btn_atualizar_estoque = ctk.CTkButton(frame, text="Atualizar Estoque", command=self.atualizar_grafico_estoque)
        self.btn_atualizar_estoque.pack(pady=5)
        self.estoque_label = ctk.CTkLabel(frame, text="(Gráfico atualizado a cada 5 segundos)", font=("Arial", 10))
        self.estoque_label.pack(pady=5)
        self.atualizar_grafico_estoque_periodico()

    def atualizar_grafico_estoque(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, quantidade FROM produtos")
        dados = cursor.fetchall()
        conn.close()
        produtos = [d[0] for d in dados]
        quantidades = [d[1] for d in dados]
        plt.figure(figsize=(6,4))
        plt.bar(produtos, quantidades, color="lightgreen")
        plt.title("Estoque Atual")
        plt.xlabel("Produto")
        plt.ylabel("Quantidade")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        graf_path = "estoque_realtime.png"
        plt.savefig(graf_path)
        plt.close()
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        fig = plt.figure(figsize=(6,4))
        img = plt.imread(graf_path)
        plt.imshow(img)
        plt.axis('off')
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        plt.close(fig)

    def atualizar_grafico_estoque_periodico(self):
        self.atualizar_grafico_estoque()
        self.after(5000, self.atualizar_grafico_estoque_periodico)

    # --- Relatórios ---
    def criar_frame_relatorios(self):
        frame = self.tabview.tab("Relatórios")
        lbl = ctk.CTkLabel(frame, text="Relatórios e Movimentações", font=("Arial", 18))
        lbl.pack(pady=5)
        filtro_frame = ctk.CTkFrame(frame)
        filtro_frame.pack(pady=5)
        ctk.CTkLabel(filtro_frame, text="Selecione a Data:").grid(row=0, column=0, padx=5)
        self.calendario = Calendar(filtro_frame, date_pattern="yyyy-mm-dd")
        self.calendario.grid(row=0, column=1, padx=5)
        ctk.CTkButton(filtro_frame, text="Buscar Vendas", command=self.filtrar_vendas_data).grid(row=0, column=2, padx=5)
        self.tree_vendas_dia = ttk.Treeview(frame, columns=("ID", "Produto", "Qtd", "Preço", "Total"), show="headings", height=8)
        for col in ("ID", "Produto", "Qtd", "Preço", "Total"):
            self.tree_vendas_dia.heading(col, text=col)
            self.tree_vendas_dia.column(col, width=120)
        self.tree_vendas_dia.pack(pady=10)
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Gerar Ficheiro SAF-T (Mês Atual)", command=self.gerar_saft_mensal).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Exportar Vendas para Excel", command=self.exportar_excel_relatorio).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Pré-visualizar Relatório PDF", command=self.previsualizar_relatorio_pdf).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Gerar Gráfico", command=self.exibir_grafico_embutido).grid(row=0, column=3, padx=5, pady=5)
        self.refresh_vendas()

    def filtrar_vendas_data(self):
        data_sel = self.calendario.get_date()
        for item in self.tree_vendas_dia.get_children():
            self.tree_vendas_dia.delete(item)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, detalhes FROM vendas WHERE date(data_venda)=?", (data_sel,))
        vendas = cursor.fetchall()
        conn.close()
        for venda in vendas:
            venda_id, detalhes = venda
            try:
                itens = json.loads(detalhes)
                for item in itens:
                    self.tree_vendas_dia.insert("", "end", values=(venda_id, item.get("nome", ""), item.get("quantidade", ""), f"Kz {float(item.get('preco', 0)):.2f}", f"Kz {float(item.get('subtotal', 0)):.2f}"))
            except Exception as e:
                print("Erro:", e)

    def gerar_saft_mensal(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendas")
        vendas = cursor.fetchall()
        conn.close()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, localizacao, provincia, nif, telefone, observacao FROM empresa")
        emp = cursor.fetchone()
        conn.close()
        empresa_info = {
            "nome": emp[0] if emp else "",
            "localizacao": emp[1] if emp else "",
            "provincia": emp[2] if emp else "",
            "nif": emp[3] if emp else "",
            "telefone": emp[4] if emp else "",
            "observacao": emp[5] if emp and emp[5] else ""
        }
        from utils import gerar_saft
        gerar_saft(vendas, empresa_info)
        messagebox.showinfo("SAFT", "Ficheiro SAF-T gerado com sucesso!")

    def exportar_excel_relatorio(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendas")
        vendas = cursor.fetchall()
        conn.close()
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, localizacao, provincia, nif, telefone, observacao FROM empresa")
        emp = cursor.fetchone()
        conn.close()
        empresa_info = {
            "nome": emp[0] if emp else "",
            "localizacao": emp[1] if emp else "",
            "provincia": emp[2] if emp else "",
            "nif": emp[3] if emp else "",
            "telefone": emp[4] if emp else "",
            "observacao": emp[5] if emp and emp[5] else ""
        }
        from utils import exportar_excel
        exportar_excel(vendas, empresa_info)
        messagebox.showinfo("Excel", "Relatório exportado com sucesso!")

    def previsualizar_relatorio_pdf(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendas")
        vendas = cursor.fetchall()
        conn.close()
        texto = "Relatório de Vendas:\n\n"
        for venda in vendas:
            texto += str(venda) + "\n"
        preview_win = Toplevel(self)
        preview_win.title("Pré-visualização do Relatório PDF")
        preview_win.iconbitmap('image/mgrace.ico')
        txt = Text(preview_win, width=100, height=30)
        txt.pack()
        txt.insert(END, texto)
        txt.configure(state="disabled")

    def exibir_grafico_embutido(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT data_venda, detalhes, total FROM vendas")
        vendas = cursor.fetchall()
        conn.close()
        from utils import gerar_grafico_vendas
        caminho_graf = gerar_grafico_vendas(vendas, periodo="dia", caminho="grafico_embutido.png")
        graf_win = Toplevel(self)
        graf_win.title("Gráfico de Vendas")
        graf_win.iconbitmap('image/mgrace.ico')
        fig = plt.figure(figsize=(5, 4))
        img = plt.imread(caminho_graf)
        plt.imshow(img)
        plt.axis('off')
        canvas = FigureCanvasTkAgg(fig, master=graf_win)
        canvas.draw()
        canvas.get_tk_widget().pack()
        plt.close(fig)

    def refresh_vendas(self):
        # Método opcional para atualizar a árvore de vendas.
        pass

    # --- Cancelar Venda ---
    def criar_frame_cancelar_venda(self):
        frame = self.tabview.tab("Cancelar Venda")
        lbl = ctk.CTkLabel(frame, text="Cancelar Venda", font=("Arial", 18))
        lbl.pack(pady=5)
        self.tree_cancelar = ttk.Treeview(frame, columns=("ID", "Usuário", "Data", "Total"), show="headings", height=8)
        for col in ("ID", "Usuário", "Data", "Total"):
            self.tree_cancelar.heading(col, text=col)
            self.tree_cancelar.column(col, width=150)
        self.tree_cancelar.pack(pady=10)
        self.refresh_vendas_cancelar()
        ctk.CTkButton(frame, text="Cancelar Venda Selecionada", command=self.cancelar_venda).pack(pady=10)

    def refresh_vendas_cancelar(self):
        for item in self.tree_cancelar.get_children():
            self.tree_cancelar.delete(item)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, id_usuario, data_venda, total FROM vendas WHERE status='OK'")
        for row in cursor.fetchall():
            self.tree_cancelar.insert("", "end", values=row)
        conn.close()

    def cancelar_venda(self):
        selecionado = self.tree_cancelar.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma venda para cancelar.")
            return
        valores = self.tree_cancelar.item(selecionado, "values")
        sale_id = valores[0]
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT data_venda, total, detalhes, id_usuario FROM vendas WHERE id=?", (sale_id,))
        registro = cursor.fetchone()
        conn.close()
        if registro:
            data_venda, total, detalhes, usuario = registro
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT nome, localizacao, nif, telefone, observacao FROM empresa")
            emp = cursor.fetchone()
            conn.close()
            empresa_info = {
                "nome": emp[0] if emp else "",
                "localizacao": emp[1] if emp else "",
                "nif": emp[2] if emp else "",
                "telefone": emp[3] if emp else "",
                "observacao": emp[4] if emp and emp[4] else ""
            }
            nome_pdf = f"cancelamento_{sale_id}.pdf"
            from utils import gerar_pdf_cancelamento
            gerar_pdf_cancelamento(sale_id, data_venda, total, detalhes, empresa_info, nome_arquivo=nome_pdf)
            messagebox.showinfo("Cancelamento", f"PDF de cancelamento gerado: {nome_pdf}\nFatura CANCELADA (Registro SAF-T: {sale_id}).")
            try:
                itens = json.loads(detalhes)
                conn = conectar()
                cursor = conn.cursor()
                for item in itens:
                    prod_id = item.get("id")
                    qtd = item.get("quantidade", 0)
                    cursor.execute("SELECT quantidade FROM produtos WHERE id=?", (prod_id,))
                    atual = cursor.fetchone()
                    if atual:
                        novo = atual[0] + qtd
                        cursor.execute("UPDATE produtos SET quantidade=? WHERE id=?", (novo, prod_id))
                conn.commit()
                conn.close()
            except Exception as e:
                print("Erro ao atualizar estoque:", e)
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("UPDATE vendas SET status='cancelado' WHERE id=?", (sale_id,))
            conn.commit()
            conn.close()
            self.refresh_vendas_cancelar()

    # --- Mais Vendidos ---
    def criar_frame_mais_vendidos(self):
        frame = self.tabview.tab("Mais Vendidos")
        lbl = ctk.CTkLabel(frame, text="Produtos Mais Vendidos", font=("Arial", 18))
        lbl.pack(pady=5)
        self.lista_mais_vendidos = ctk.CTkTextbox(frame, width=1000, height=500)
        self.lista_mais_vendidos.pack(pady=10)
        btn_atualizar = ctk.CTkButton(frame, text="Atualizar Lista", command=self.mostrar_mais_vendidos)
        btn_atualizar.pack(pady=5)
        self.mostrar_mais_vendidos()

    def mostrar_mais_vendidos(self):
        contagem = {}
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT detalhes FROM vendas")
        vendas = cursor.fetchall()
        conn.close()
        for venda in vendas:
            try:
                itens = json.loads(venda[0])
                for item in itens:
                    nome = item.get("nome", "Desconhecido")
                    qtd = int(item.get("quantidade", 0))
                    contagem[nome] = contagem.get(nome, 0) + qtd
            except Exception as e:
                print("Erro ao contar:", e)
        lista_ordenada = sorted(contagem.items(), key=lambda x: x[1], reverse=True)
        self.lista_mais_vendidos.delete("0.0", END)
        for prod, total in lista_ordenada:
            self.lista_mais_vendidos.insert(END, f"{prod}: {total} unidades vendidas\n")

    # --- Solicitações ---
    def criar_frame_solicitacoes(self):
        frame = self.tabview.tab("Solicitações")
        lbl = ctk.CTkLabel(frame, text="Solicitações de Produtos", font=("Arial", 18))
        lbl.pack(pady=5)
        self.tree_solicitacoes = ttk.Treeview(frame, columns=("ID", "Usuário", "Produto", "Descrição", "Data"), show="headings", height=10)
        for col in ("ID", "Usuário", "Produto", "Descrição", "Data"):
            self.tree_solicitacoes.heading(col, text=col)
            self.tree_solicitacoes.column(col, width=150)
        self.tree_solicitacoes.pack(pady=10)
        ctk.CTkButton(frame, text="Apagar Solicitação Selecionada", command=self.apagar_solicitacao).pack(pady=5)
        self.refresh_solicitacoes()

    def refresh_solicitacoes(self):
        for item in self.tree_solicitacoes.get_children():
            self.tree_solicitacoes.delete(item)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome_usuario, produto, descricao, data_solicitacao FROM solicitacoes")
        for row in cursor.fetchall():
            self.tree_solicitacoes.insert("", "end", values=row)
        conn.close()

    def apagar_solicitacao(self):
        selecionado = self.tree_solicitacoes.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma solicitação para apagar.")
            return
        valores = self.tree_solicitacoes.item(selecionado, "values")
        solicitacao_id = valores[0]
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM solicitacoes WHERE id=?", (solicitacao_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Solicitação apagada!")
        self.refresh_solicitacoes()

    # --- Sessões ---
    def criar_frame_sessoes(self):
        frame = self.tabview.tab("Sessões")
        lbl = ctk.CTkLabel(frame, text="Registros de Sessões dos Usuários", font=("Arial", 18))
        lbl.pack(pady=5)
        self.tree_sessoes = ttk.Treeview(frame, columns=("ID", "Usuário", "Hora Entrada", "Hora Saída"), show="headings", height=8)
        for col in ("ID", "Usuário", "Hora Entrada", "Hora Saída"):
            self.tree_sessoes.heading(col, text=col)
            self.tree_sessoes.column(col, width=150)
        self.tree_sessoes.pack(pady=10)
        ctk.CTkButton(frame, text="Atualizar Sessões", command=self.refresh_sessoes).pack(pady=5)
        ctk.CTkButton(frame, text="Apagar Sessão Selecionada", command=self.apagar_sessao).pack(pady=5)
        self.refresh_sessoes()

    def refresh_sessoes(self):
        for item in self.tree_sessoes.get_children():
            self.tree_sessoes.delete(item)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome_usuario, hora_entrada, hora_saida FROM sessoes")
        for row in cursor.fetchall():
            self.tree_sessoes.insert("", "end", values=row)
        conn.close()

    def apagar_sessao(self):
        selecionado = self.tree_sessoes.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma sessão para apagar.")
            return
        valores = self.tree_sessoes.item(selecionado, "values")
        sessao_id = valores[0]
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessoes WHERE id=?", (sessao_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Sessão apagada!")
        self.refresh_sessoes()

if __name__ == "__main__":
    app = JanelaAdmin()
    app.mainloop()
