from flask import Flask, jsonify, render_template_string, request, send_file
from flask_cors import CORS
from database import conectar, get_config
import json
import os
from datetime import datetime
import tempfile
from reportlab.lib.pagesizes import A4, A5, LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

app = Flask(__name__, static_folder='static')
CORS(app)

# Mapeia os tamanhos de papel
PAPER_SIZES = {
    "A4": A4,
    "A5": A5,
    "Letter": LETTER
}

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PCK Software</title>
    <style>
        :root {
            --primary-color: #2196F3;
            --secondary-color: #FFC107;
            --success-color: #4CAF50;
            --danger-color: #F44336;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .logo-header {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .logo {
            width: 100px;
            height: auto;
        }
        
        .company-name {
            font-size: 32px;
            color: var(--primary-color);
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: var(--primary-color);
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 10px;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .card.primary {
            border-left: 4px solid var(--primary-color);
        }
        
        .card.success {
            border-left: 4px solid var(--success-color);
        }
        
        .table-container {
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        th {
            background: var(--primary-color);
            color: white;
            padding: 12px;
            text-align: left;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .produto-item {
            background: #f8f9fa;
            margin: 5px 0;
            padding: 10px;
            border-radius: 4px;
            border-left: 3px solid var(--secondary-color);
        }
        
        .data-selector {
            margin: 20px 0;
            text-align: center;
        }
        
        input[type="date"] {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        
        button {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        
        button:hover {
            background: #1976D2;
        }
        
        .total {
            font-size: 24px;
            font-weight: bold;
            color: var(--success-color);
        }
        
        .button-container {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo-header">
                <img src="/static/logg.png" alt="M.Grace Logo" class="logo">
                <div class="company-name">PCK Software</div>
            </div>
            <h2>Relatório de Vendas - {{data}}</h2>
        </div>
        
        <div class="data-selector">
            <form action="/api/vendas/data" method="get">
                <input type="date" name="data" value="{{data}}">
                <input type="hidden" name="format" value="html">
                <button type="submit">Buscar Vendas</button>
            </form>
            <div class="button-container">
                <a href="/api/vendas/data/pdf?data={{data}}">
                    <button style="background-color: var(--success-color);">Exportar PDF</button>
                </a>
            </div>
        </div>

        <div class="dashboard">
            <div class="card primary">
                <h3>Total de Vendas</h3>
                <div class="total">{{total_vendas}}</div>
            </div>
            <div class="card success">
                <h3>Valor Total</h3>
                <div class="total">{{valor_total}} Kz</div>
            </div>
        </div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Hora</th>
                        <th>Produtos</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {% for venda in vendas %}
                    <tr>
                        <td>{{venda.data.split()[1]}}</td>
                        <td>
                            {% for item in venda.detalhes %}
                                <div class="produto-item">
                                    {{item.nome}} - {{item.quantidade}}x - {{item.preco}} Kz
                                </div>
                            {% endfor %}
                        </td>
                        <td>{{venda.total}} Kz</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
'''

def gerar_relatorio_pdf(dados, nome_arquivo="relatorio.pdf"):
    """Gera um relatório de vendas em PDF."""
    papel = get_config("paper_size") or "A4"
    tamanho = PAPER_SIZES.get(papel, A4)
    doc = SimpleDocTemplate(nome_arquivo, pagesize=tamanho)
    styles = getSampleStyleSheet()
    elementos = []
    
    # Cabeçalho
    elementos.append(Paragraph(f"<b>RELATÓRIO DE VENDAS</b>", styles["Title"]))
    elementos.append(Spacer(1, 8))
    
    # Informações da empresa
    empresa = dados.get("empresa", {})
    emp_text = f"{empresa.get('nome', 'Empresa')}\n{empresa.get('localizacao', '')}\nNIF: {empresa.get('nif', '')}"
    elementos.append(Paragraph(emp_text, styles["Normal"]))
    elementos.append(Spacer(1, 12))
    
    # Data do relatório
    elementos.append(Paragraph(f"<b>Data do Relatório:</b> {dados.get('data', '')}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Total de Vendas:</b> {dados.get('total_vendas', 0)}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Valor Total:</b> {dados.get('valor_total', 0):,.2f} Kz", styles["Normal"]))
    elementos.append(Spacer(1, 12))
    
    # Tabela de produtos vendidos
    table_data = [["Produto", "Quantidade", "Preço (Kz)", "Subtotal (Kz)"]]
    for item in dados.get("itens", []):
        table_data.append([
            item.get("nome", ""),
            str(item.get("quantidade", "")),
            f"{float(item.get('preco', 0)):,.2f}",
            f"{float(item.get('subtotal', 0)):,.2f}"
        ])
    
    # Adicionar linha com total
    table_data.append(["", "", "<b>TOTAL</b>", f"<b>{float(dados.get('valor_total', 0)):,.2f}</b>"])
    
    # Criar tabela
    tabela = Table(table_data, colWidths=[doc.width*0.4, doc.width*0.2, doc.width*0.2, doc.width*0.2])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('SPAN', (0, -1), (2, -1)),
    ]))
    elementos.append(tabela)
    
    # Rodapé
    elementos.append(Spacer(1, 20))
    elementos.append(Paragraph(f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles["Normal"]))
    
    # Construir o PDF
    doc.build(elementos)
    return nome_arquivo

@app.route('/api/vendas/data')
def get_vendas_por_data():
    data_consulta = request.args.get('data', datetime.now().strftime('%Y-%m-%d'))
    format_html = request.args.get('format', 'json') == 'html'
    
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT data_venda, detalhes, total 
            FROM vendas 
            WHERE date(data_venda) = ?
            ORDER BY data_venda DESC
        """, (data_consulta,))
        
        vendas = cursor.fetchall()
        vendas_formatadas = []
        valor_total = 0
        
        for venda in vendas:
            detalhes_venda = json.loads(venda[1])
            valor_total += float(venda[2])
            
            vendas_formatadas.append({
                'data': venda[0],
                'detalhes': detalhes_venda,
                'total': venda[2]
            })

        if format_html:
            return render_template_string(
                TEMPLATE,
                data=data_consulta,
                total_vendas=len(vendas),
                valor_total=f"{valor_total:,.2f}",
                vendas=vendas_formatadas
            )
        
        return jsonify({
            'status': 'success',
            'data': data_consulta,
            'total_vendas': len(vendas),
            'valor_total': valor_total,
            'vendas': vendas_formatadas
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/vendas/data/pdf')
def get_vendas_pdf():
    data_consulta = request.args.get('data', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        # Obter informações da empresa
        cursor.execute("SELECT nome, localizacao, nif, observacao FROM empresa LIMIT 1")
        empresa_info = cursor.fetchone()
        empresa = {
            "nome": empresa_info[0] if empresa_info else "M.Grace Software",
            "localizacao": empresa_info[1] if empresa_info else "",
            "nif": empresa_info[2] if empresa_info else "",
            "observacao": empresa_info[3] if empresa_info else ""
        }
        
        # Obter vendas da data selecionada
        cursor.execute("""
            SELECT data_venda, detalhes, total, id_usuario
            FROM vendas 
            WHERE date(data_venda) = ? AND status = 'OK'
            ORDER BY data_venda DESC
        """, (data_consulta,))
        
        vendas = cursor.fetchall()
        
        # Preparar dados para o PDF
        itens_relatorio = []
        valor_total = 0
        
        for venda in vendas:
            detalhes_venda = json.loads(venda[1])
            valor_total += float(venda[2])
            
            for item in detalhes_venda:
                itens_relatorio.append({
                    "nome": item["nome"],
                    "quantidade": item["quantidade"],
                    "preco": item["preco"],
                    "subtotal": float(item["quantidade"]) * float(item["preco"])
                })
        
        # Criar dados para o PDF
        dados_pdf = {
            "empresa": empresa,
            "data": data_consulta,
            "usuario": "Relatório Administrativo",
            "itens": itens_relatorio,
            "total_vendas": len(vendas),
            "valor_total": valor_total,
            "forma_pagamento": "Diversos",
            "fatura_numero": f"REL-{data_consulta.replace('-', '')}"
        }
        
        # Gerar PDF em arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()
        
        gerar_relatorio_pdf(dados_pdf, temp_file.name)
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f"relatorio_vendas_{data_consulta}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
