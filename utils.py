# utils.py
import datetime
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4, A5, LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import json
import win32api
from database import get_config

# Mapeia os tamanhos de papel
PAPER_SIZES = {
    "A4": A4,
    "A5": A5,
    "Letter": LETTER
}

def gerar_pdf(dados, nome_arquivo="fatura.pdf"):
    """Gera a fatura em PDF com informações da venda, incluindo o cálculo do IVA e uma assinatura digital."""
    papel = get_config("paper_size")
    tamanho = PAPER_SIZES.get(papel, A5)
    doc = SimpleDocTemplate(nome_arquivo, pagesize=tamanho)
    styles = getSampleStyleSheet()
    elementos = []
    
    fatura_num = dados.get("fatura_numero", "0000")
    elementos.append(Paragraph(f"<b>Fatura Nº: {fatura_num}</b>", styles["Title"]))
    elementos.append(Spacer(1, 8))
    
    empresa = dados.get("empresa", {})
    emp_text = f"{empresa.get('nome', 'Empresa')}\n{empresa.get('localizacao', '')}\nNIF: {empresa.get('nif', '')}"
    elementos.append(Paragraph(emp_text, styles["Normal"]))
    if empresa.get("observacao", ""):
        elementos.append(Paragraph(f"<i>FACTURA / RECIBO</i>", styles["Normal"]))
    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph(f"<i>: {empresa.get('observacao')}</i>", styles["Normal"]))
    
    info = f"Operador de caixa: {dados.get('usuario', '')}<br/>Data: {dados.get('data', '')}<br/>Forma de Pagamento: {dados.get('forma_pagamento', '')}"
    elementos.append(Paragraph(info, styles["Normal"]))
    elementos.append(Spacer(1, 12))
    
    table_data = [["Produto", "Quantidade", "Preço (Kz)", "Subtotal (Kz)"]]
    for item in dados.get("itens", []):
        table_data.append([
            item.get("nome", ""),
            str(item.get("quantidade", "")),
            f"Kz {float(item.get('preco', 0)):.2f}",
            f"Kz {float(item.get('subtotal', 0)):.2f}"
        ])
    table = Table(table_data, colWidths=[120, 50, 70, 70])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black)
    ]))
    elementos.append(table)
    elementos.append(Spacer(1, 12))
    
    iva_total = dados.get("iva_total", 0)
    if iva_total > 0:
        elementos.append(Paragraph(f"<b>Total Imposto IVA(5%): Kz {iva_total:.2f}</b>", styles["Normal"]))
        elementos.append(Spacer(1, 6))
        total_com_iva = dados.get("total_com_iva", dados.get("total", 0))
        elementos.append(Paragraph(f"<b>Total Produto: Kz {total_com_iva:.2f}</b>", styles["Normal"]))
    else:
        total_text = f"<b>Total: Kz {float(dados.get('total', 0)):.2f}</b>"
        elementos.append(Paragraph(total_text, styles["Normal"]))
    
    # Adiciona a assinatura digital (calculada com SHA256)
    assinatura = hashlib.sha256((dados.get("fatura_numero", "0000") + dados.get("data", "")).encode("utf-8")).hexdigest()
    elementos.append(Spacer(1, 12))
    elementos.append(Paragraph(f"Assinatura Digital: {assinatura}", styles["Normal"]))
    elementos.append(Spacer(1, 12)) 
    elementos.append(Paragraph(f"M.GRACE SOFTWARE-Processado por programa válido n31.1/AGT20: ", styles["Normal"]))
    
    doc.build(elementos)
    print(f"Fatura gerada: {nome_arquivo}")

def gerar_pdf_cancelamento(sale_id, data_venda, total, detalhes, empresa_info, nome_arquivo="cancelamento.pdf"):
    """
    Gera um PDF de cancelamento com título em vermelho “Fatura Cancelada”, 
    informações da empresa, dados da venda (data, total e referência para o SAF-T)
    e a lista dos produtos cancelados.
    """
    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []
    
    titulo = Paragraph("<font color='red'><b>Fatura Cancelada</b></font>", styles["Title"])
    elementos.append(titulo)
    elementos.append(Spacer(1, 12))
    
    emp_text = f"{empresa_info.get('nome', 'Empresa')}\n{empresa_info.get('localizacao', '')}\nNIF: {empresa_info.get('nif', '')}\nTelefone: {empresa_info.get('telefone', '')}"
    if empresa_info.get("observacao", ""):
        emp_text += f"\nObservação: {empresa_info.get('observacao')}"
    elementos.append(Paragraph(emp_text, styles["Normal"]))
    elementos.append(Spacer(1, 12))
    
    info_venda = f"Data da Venda: {data_venda}<br/>Total da Venda: Kz {float(total):.2f}<br/><b>Registro SAF-T: {sale_id}</b>"
    elementos.append(Paragraph(info_venda, styles["Normal"]))
    elementos.append(Spacer(1, 12))
    
    try:
        itens = json.loads(detalhes)
        table_data = [["Produto", "Quantidade", "Preço (Kz)", "Subtotal (Kz)"]]
        for item in itens:
            table_data.append([
                item.get("nome", ""),
                str(item.get("quantidade", "")),
                f"Kz {float(item.get('preco', 0)):.2f}",
                f"Kz {float(item.get('subtotal', 0)):.2f}"
            ])
        table = Table(table_data, colWidths=[150, 60, 100, 100])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black)
        ]))
        elementos.append(table)
    except Exception as e:
        elementos.append(Paragraph("Erro ao ler os itens da venda cancelada.", styles["Normal"]))
        print("Erro:", e)
    
    doc.build(elementos)
    print(f"PDF de cancelamento gerado: {nome_arquivo}")
    return nome_arquivo

def gerar_pdf_contabilidade(data_sel, vendas, total_vendas, nome_arquivo="contabilidade.pdf"):
    """
    Gera um PDF de contabilidade para um dia (data_sel) listando todas as vendas e o total.
    """
    from reportlab.platypus import Table
    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []
    elementos.append(Paragraph(f"<b>Relatório de Vendas - {data_sel}</b>", styles["Title"]))
    elementos.append(Spacer(1,12))
    
    table_data = [["Venda ID", "Data", "Usuário", "Total (Kz)", "Status"]]
    for venda in vendas:
        venda_id, data_venda, total, detalhes, usuario, status = venda
        table_data.append([str(venda_id), data_venda, usuario, f"Kz {float(total):.2f}", status])
    table = Table(table_data, colWidths=[70, 100, 100, 100, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black)
    ]))
    elementos.append(table)
    elementos.append(Spacer(1,12))
    elementos.append(Paragraph(f"<b>Total de Vendas: Kz {total_vendas:.2f}</b>", styles["Normal"]))
    doc.build(elementos)
    print(f"Relatório de contabilidade gerado: {nome_arquivo}")

def exportar_excel(dados, empresa_info, nome_arquivo="vendas.xlsx"):
    df_empresa = pd.DataFrame([empresa_info])
    df_vendas = pd.DataFrame(dados)
    with pd.ExcelWriter(nome_arquivo) as writer:
        df_empresa.to_excel(writer, sheet_name="Empresa", index=False)
        df_vendas.to_excel(writer, sheet_name="Vendas", index=False)
    print(f"Arquivo Excel gerado: {nome_arquivo}")

def gerar_saft(vendas, empresa_info, nome_arquivo=None):
    """
    Gera um ficheiro SAF-T em XML com todos os registros de vendas (incluindo os cancelados).
    """
    if nome_arquivo is None:
        nome_arquivo = f"SAFT_{datetime.datetime.now().strftime('%Y%m')}.xml"
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write("<SAFT>\n")
        f.write("  <Empresa>\n")
        f.write(f"    <Nome>{empresa_info.get('nome', '')}</Nome>\n")
        f.write(f"    <Localizacao>{empresa_info.get('localizacao', '')}</Localizacao>\n")
        f.write(f"    <NIF>{empresa_info.get('nif', '')}</NIF>\n")
        f.write(f"    <Telefone>{empresa_info.get('telefone', '')}</Telefone>\n")
        if empresa_info.get("observacao", ""):
            f.write(f"    <Observacao>{empresa_info.get('observacao')}</Observacao>\n")
        f.write("  </Empresa>\n")
        f.write("  <Vendas>\n")
        for venda in vendas:
            f.write(f"    <Venda>{str(venda)}</Venda>\n")
        f.write("  </Vendas>\n")
        f.write("</SAFT>")
    print(f"Ficheiro SAF-T gerado: {nome_arquivo}")

def gerar_grafico_vendas(vendas, periodo="dia", caminho="grafico.png"):
    vendas_produtos = {}
    for venda in vendas:
        data_venda = venda[0]
        detalhes = venda[1]
        try:
            itens = json.loads(detalhes)
            for item in itens:
                nome = item.get("nome", "Desconhecido")
                subtotal = float(item.get("subtotal", 0))
                chave = (data_venda, nome)
                vendas_produtos[chave] = vendas_produtos.get(chave, 0) + subtotal
        except Exception as e:
            print("Erro no parse dos detalhes:", e)
    datas = {}
    for (data, prod), total in vendas_produtos.items():
        datas.setdefault(data, []).append((prod, total))
    if periodo == "mes":
        meses = {}
        for data_str, lista in datas.items():
            mes = data_str[:7]
            for prod, total in lista:
                key = (mes, prod)
                meses[key] = meses.get(key, 0) + total
        datas = {}
        for (mes, prod), total in meses.items():
            datas.setdefault(mes, []).append((prod, total))
    if not datas:
        print("Nenhum dado para gerar gráfico.")
        return caminho
    periodo_chave = list(datas.keys())[0]
    produtos, totals = zip(*datas[periodo_chave])
    plt.figure(figsize=(8, 4))
    plt.bar(produtos, totals, color="skyblue")
    plt.title(f"Vendas em {periodo_chave} ({periodo})")
    plt.xlabel("Produto")
    plt.ylabel("Total Vendido (Kz)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()
    print(f"Gráfico gerado: {caminho}")
    return caminho

def imprimir_pdf(nome_arquivo, printer):
    try:
        win32api.ShellExecute(0, "print", nome_arquivo, None, ".", 0)
        print(f"Enviado para impressão: {nome_arquivo} na impressora {printer}")
    except Exception as e:
        print("Erro ao imprimir PDF:", e)
