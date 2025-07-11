import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog, Toplevel
import datetime
import json
from database import conectar, get_config
from utils import gerar_pdf, imprimir_pdf
from tkcalendar import Calendar
from PIL import Image, ImageTk

class JanelaUsuario(ctk.CTk):
    def __init__(self, nome_usuario):
        super().__init__()
        self.title("Ponto de Venda - Usuário")
        self.iconbitmap('image/mgrace.ico')
        self.geometry("1100x750")
        self.resizable(False, False)
        
        # Carregando a imagem de fundo
        self.bg_image = Image.open("image/tt.png")  # Substitua pelo caminho correto da sua imagem
        self.bg_image = self.bg_image.resize((1100, 750), Image.LANCZOS)  # Redimensiona para o tamanho da janela
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        
        # Criando um label para exibir a imagem de fundo
        self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Posiciona o label para cobrir toda a janela
        
        self.nome_usuario = nome_usuario
        self.horario_entrada = datetime.datetime.now().strftime("%H:%M:%S")
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sessoes (nome_usuario, hora_entrada) VALUES (?, ?)", (self.nome_usuario, self.horario_entrada))
        conn.commit()
        self.sessao_id = cursor.lastrowid
        conn.close()
        self.carrinho = []  # Cada item: dict com id, nome, quantidade, preco, iva e subtotal
        
        self.lbl_usuario = ctk.CTkLabel(self, text=f"Usuário: {self.nome_usuario} | Entrou às: {self.horario_entrada}", font=("Arial", 12))    
        self.lbl_usuario.pack(pady=5)
        
        self.btn_logout = ctk.CTkButton(self, text="Trocar Sessão", command=self.trocar_sessao)
        self.btn_logout.pack(pady=5)
        
        self.label_data_hora = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.label_data_hora.pack(pady=5)
        self.atualizar_data_hora()
        
        # Frame de Produtos
        frame_esquerda = ctk.CTkFrame(self, width=550, height=680)
        frame_esquerda.pack(side="left", padx=10, pady=10)
        
        lbl_busca = ctk.CTkLabel(frame_esquerda, text="Produtos Disponíveis", font=("Arial", 18))
        lbl_busca.pack(pady=5)
        
        busca_frame = ctk.CTkFrame(frame_esquerda)
        busca_frame.pack(pady=5)
        
        self.entry_busca_nome = ctk.CTkEntry(busca_frame, placeholder_text="Buscar por Nome", width=200)
        self.entry_busca_nome.grid(row=0, column=0, padx=5)
        
        self.entry_busca_categoria = ctk.CTkEntry(busca_frame, placeholder_text="Buscar por Categoria", width=200)
        self.entry_busca_categoria.grid(row=0, column=1, padx=5)
        
        ctk.CTkButton(frame_esquerda, text="Buscar", command=self.buscar_produtos).pack(pady=5)
        
        self.tree_produtos = ttk.Treeview(frame_esquerda, columns=("ID", "Nome", "Categoria", "Detail", "Grosso", "Estoque", "IVA (%)"), show="headings", height=15)
        for col in ("ID", "Nome", "Categoria", "Detail", "Grosso", "Estoque", "IVA (%)"):
            self.tree_produtos.heading(col, text=col)
            self.tree_produtos.column(col, width=100)
        self.tree_produtos.pack(pady=10)
        self.refresh_produtos()
        
        self.label_modo = ctk.CTkLabel(frame_esquerda, text="Modo de Venda:")
        self.label_modo.pack(pady=2)
        
        self.combo_modo = ttk.Combobox(frame_esquerda, values=["Detail", "Grosso"])
        self.combo_modo.pack(pady=2)
        self.combo_modo.current(0)
        
        ctk.CTkButton(frame_esquerda, text="Solicitar Produto", command=self.solicitar_produto).pack(pady=5)
        
        # Frame de Carrinho
        frame_direita = ctk.CTkFrame(self, width=520, height=680)
        frame_direita.pack(side="right", padx=10, pady=10)
        
        lbl_carrinho = ctk.CTkLabel(frame_direita, text="Carrinho de Venda", font=("Arial", 18))
        lbl_carrinho.pack(pady=5)
        
        self.tree_carrinho = ttk.Treeview(frame_direita, columns=("Nome", "Qtd", "Preço", "Subtotal"), show="headings", height=10)
        for col in ("Nome", "Qtd", "Preço", "Subtotal"):
            self.tree_carrinho.heading(col, text=col)
            self.tree_carrinho.column(col, width=100)
        self.tree_carrinho.pack(pady=5)
        
        self.label_total = ctk.CTkLabel(frame_direita, text="Total: Kz 0.00", font=("Arial", 16))
        self.label_total.pack(pady=5)
        
        self.label_pagamento = ctk.CTkLabel(frame_direita, text="Forma de Pagamento:")
        self.label_pagamento.pack(pady=5)
        
        self.combo_pagamento = ttk.Combobox(frame_direita, values=["Dinheiro", "Cartão", "Pix", "Transferência"])
        self.combo_pagamento.pack(pady=5)
        self.combo_pagamento.current(0)
        
        btn_frame = ctk.CTkFrame(frame_direita)
        btn_frame.pack(pady=5)
        
        ctk.CTkButton(btn_frame, text="Adicionar Produto", command=self.adicionar_produto).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="Remover Selecionado", command=self.remover_item).grid(row=0, column=1, padx=5)
        
        ctk.CTkButton(frame_direita, text="Finalizar Venda", command=self.finalizar_venda).pack(pady=10)

    def trocar_sessao(self):
        hora_saida = datetime.datetime.now().strftime("%H:%M:%S")
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE sessoes SET hora_saida=? WHERE id=?", (hora_saida, self.sessao_id))
        conn.commit()
        conn.close()
        self.destroy()
        import main
        main.tela_login()

    def atualizar_data_hora(self):
        agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.label_data_hora.configure(text=agora)
        self.after(1000, self.atualizar_data_hora)

    def refresh_produtos(self):
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, categoria, preco_detail, preco_grosso, quantidade, iva FROM produtos")
        for row in cursor.fetchall():
            self.tree_produtos.insert("", "end", values=row)
        conn.close()

    def buscar_produtos(self):
        nome = self.entry_busca_nome.get()
        categoria = self.entry_busca_categoria.get()
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        conn = conectar()
        cursor = conn.cursor()
        query = "SELECT id, nome, categoria, preco_detail, preco_grosso, quantidade, iva FROM produtos WHERE 1=1"
        params = []
        if nome:
            query += " AND nome LIKE ?"
            params.append(f"%{nome}%")
        if categoria:
            query += " AND categoria LIKE ?"
            params.append(f"%{categoria}%")
        cursor.execute(query, tuple(params))
        for row in cursor.fetchall():
            self.tree_produtos.insert("", "end", values=row)
        conn.close()

    def adicionar_produto(self):
        selecionado = self.tree_produtos.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um produto para adicionar.")
            return
        valores = self.tree_produtos.item(selecionado, "values")
        prod_id, nome, categoria, preco_detail, preco_grosso, estoque, iva = valores
        modo = self.combo_modo.get()
        if modo == "Detail":
            preco = float(preco_detail)
        else:
            preco = float(preco_grosso)
        qtd = simpledialog.askinteger("Quantidade", f"Informe a quantidade para {nome} (Disponível: {estoque}):", minvalue=1, maxvalue=int(estoque))
        if not qtd:
            return
        for item in self.carrinho:
            if item["id"] == prod_id:
                item["quantidade"] += qtd
                item["subtotal"] = item["quantidade"] * preco
                break
        else:
            self.carrinho.append({
                "id": prod_id,
                "nome": nome,
                "quantidade": qtd,
                "preco": preco,
                "iva": float(iva),
                "subtotal": qtd * preco
            })
        self.atualizar_carrinho()
        novo_estoque = int(estoque) - qtd
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE produtos SET quantidade=? WHERE id=?", (novo_estoque, prod_id))
        conn.commit()
        conn.close()
        self.refresh_produtos()
        if novo_estoque <= 5:
            messagebox.showwarning("Atenção", f"O estoque do produto '{nome}' está baixo (atual: {novo_estoque}).")

    def atualizar_carrinho(self):
        for item in self.tree_carrinho.get_children():
            self.tree_carrinho.delete(item)
        total = 0.0
        total_iva = 0.0
        for item in self.carrinho:
            total += item["subtotal"]
            iva_valor = item["preco"] * item["quantidade"] * (item["iva"]/100)
            total_iva += iva_valor
            self.tree_carrinho.insert("", "end", values=(item["nome"], item["quantidade"], f"Kz {item['preco']:.2f}", f"Kz {item['subtotal']:.2f}"))
        self.label_total.configure(text=f"Total: Kz {total:.2f}")
        self.total_venda = total
        self.total_iva = total_iva

    def remover_item(self):
        selecionado = self.tree_carrinho.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um item para remover.")
            return
        indice = self.tree_carrinho.index(selecionado)
        item = self.carrinho[indice]
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT quantidade FROM produtos WHERE id=?", (item["id"],))
        estoque = cursor.fetchone()[0]
        novo_estoque = estoque + item["quantidade"]
        cursor.execute("UPDATE produtos SET quantidade=? WHERE id=?", (novo_estoque, item["id"]))
        conn.commit()
        conn.close()
        del self.carrinho[indice]
        self.atualizar_carrinho()
        self.refresh_produtos()

    def finalizar_venda(self):
        if not self.carrinho:
            messagebox.showwarning("Atenção", "O carrinho está vazio.")
            return
        total = sum(item["subtotal"] for item in self.carrinho)
        total_iva = sum(item["preco"] * item["quantidade"] * (item["iva"]/100) for item in self.carrinho)
        total_com_iva = total
        data_venda = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        detalhes = json.dumps(self.carrinho, ensure_ascii=False)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO vendas (id_usuario, data_venda, total, detalhes) VALUES (?, ?, ?, ?)",
                       (self.nome_usuario, data_venda, total_com_iva, detalhes))
        conn.commit()
        conn.close()
        fatura_numero = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, localizacao, nif, observacao FROM empresa")
        emp = cursor.fetchone()
        conn.close()
        empresa = {"nome": emp[0] if emp else "Empresa",
                   "localizacao": emp[1] if emp else "",
                   "nif": emp[2] if emp else "",
                   "observacao": emp[3] if emp and emp[3] else ""}
        dados_fatura = {
            "fatura_numero": fatura_numero,
            "empresa": empresa,
            "usuario": self.nome_usuario,
            "data": data_venda,
            "itens": self.carrinho,
            "total": total,
            "iva_total": total_iva,
            "total_com_iva": total_com_iva,
            "forma_pagamento": self.combo_pagamento.get()
        }
        self.visualizar_fatura(dados_fatura)
        nome_pdf = f"fatura_{self.nome_usuario}_{fatura_numero}.pdf"
        from utils import gerar_pdf
        gerar_pdf(dados_fatura, nome_arquivo=nome_pdf)
        impressora = get_config("printer")
        if impressora:
            from utils import imprimir_pdf
            imprimir_pdf(nome_pdf, impressora)
            imprimir_pdf(nome_pdf, impressora)
        else:
            messagebox.showwarning("Aviso", "Nenhuma impressora configurada! Verifique na aba 'Config Papel'.")
        messagebox.showinfo("Venda", f"Venda finalizada com sucesso!\nFatura gerada: {nome_pdf}")
        self.carrinho = []
        self.atualizar_carrinho()

    def visualizar_fatura(self, dados):
        preview_win = Toplevel(self)
        preview_win.title("Pré-visualização da Fatura")
        preview_win.iconbitmap('image/mgrace.ico')
        preview_win.geometry("600x700")
        empresa = dados.get("empresa", {})
        header = f"Fatura Nº: {dados.get('fatura_numero', '')}\n{empresa.get('nome', 'Empresa')}\n{empresa.get('localizacao', '')}\nNIF: {empresa.get('nif', '')}"
        if empresa.get("observacao", ""):
            header += f"\nObservação: {empresa.get('observacao')}"
        header += f"\nOperador de Caixa: {dados.get('usuario', '')}"
        lbl_header = ctk.CTkLabel(preview_win, text=header, font=("Arial", 16), justify="center")
        lbl_header.pack(pady=10)
        info_venda = f"Data: {dados.get('data', '')}\nForma de Pagamento: {dados.get('forma_pagamento', '')}"
        lbl_info = ctk.CTkLabel(preview_win, text=info_venda, font=("Arial", 12), justify="left")
        lbl_info.pack(pady=10)
        txt_itens = ctk.CTkTextbox(preview_win, width=550, height=300)
        txt_itens.pack(pady=10)
        txt_itens.insert("end", "Produto\tQuantidade\tPreço (Kz)\tSubtotal (Kz)\n")
        txt_itens.insert("end", "-"*60 + "\n")
        for item in dados.get("itens", []):
            linha = f"{item.get('nome', '')}\t{item.get('quantidade', '')}\tKz {float(item.get('preco', 0)):.2f}\tKz {float(item.get('subtotal', 0)):.2f}\n"
            txt_itens.insert("end", linha)
        txt_itens.configure(state="disabled")
        lbl_total = ctk.CTkLabel(preview_win, text=f"Total: Kz {float(dados.get('total', 0)):.2f}", font=("Arial", 14, "bold"))
        lbl_total.pack(pady=10)
        if dados.get("iva_total", 0) > 0:
            lbl_iva = ctk.CTkLabel(preview_win, text=f"% IVA: Kz {float(dados.get('iva_total', 0)):.2f}", font=("Arial", 14))
            lbl_iva.pack(pady=5)
            lbl_total_iva = ctk.CTkLabel(preview_win, text=f"Total vendas: Kz {float(dados.get('total_com_iva', 0)):.2f}", font=("Arial", 14, "bold"))
            lbl_total_iva.pack(pady=5)

    def solicitar_produto(self):
        solic_win = Toplevel(self)
        solic_win.title("Solicitar Produto")
        solic_win.iconbitmap('image/mgrace.ico')
        solic_win.geometry("400x300")
        lbl = ctk.CTkLabel(solic_win, text="Cadastrar Solicitação", font=("Arial", 16))
        lbl.pack(pady=10)
        lbl_produto = ctk.CTkLabel(solic_win, text="Nome do Produto:")
        lbl_produto.pack(pady=5)
        entry_produto = ctk.CTkEntry(solic_win, width=300)
        entry_produto.pack(pady=5)
        lbl_desc = ctk.CTkLabel(solic_win, text="Descrição:")
        lbl_desc.pack(pady=5)
        entry_desc = ctk.CTkEntry(solic_win, width=300)
        entry_desc.pack(pady=5)
        def salvar_solicitacao():
            produto = entry_produto.get()
            descricao = entry_desc.get()
            data_solicitacao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO solicitacoes (nome_usuario, produto, descricao, data_solicitacao) VALUES (?, ?, ?, ?)",
                           (self.nome_usuario, produto, descricao, data_solicitacao))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Solicitação cadastrada!")
            solic_win.destroy()
        ctk.CTkButton(solic_win, text="Salvar Solicitação", command=salvar_solicitacao).pack(pady=10)

    def refresh_vendas(self):
        # Método opcional para atualizar a árvore de vendas.
        pass

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
    #app = JanelaAdmin()
    #app.mainloop()
    pass
