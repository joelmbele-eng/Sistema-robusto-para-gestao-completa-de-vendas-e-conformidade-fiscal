<!-- Uploading "1.PNG"... -->
# Sistema-robusto-para-gestao-completa-de-vendas-e-conformidade-fiscal
Sistema completo de gestão de vendas e ponto de venda (PDV) desenvolvido em Python com interface gráfica moderna. O sistema oferece funcionalidades completas para controle de vendas, gestão de produtos, usuários e geração de relatórios fiscais.

Sistema de Gestão de Vendas e Ponto de Venda
# Descrição
Sistema completo de gestão de vendas e ponto de venda (PDV) desenvolvido em Python com interface gráfica moderna. O sistema oferece funcionalidades completas para controle de vendas, gestão de produtos, usuários e geração de relatórios fiscais.

#Funcionalidades Principais

🔐 Sistema de Autenticação
Login seguro com diferentes níveis de acesso (Admin/Usuário)
Controle de usuários ativos/inativos
Interface de login com design moderno

👥 #Gestão de Usuários

Criação automática de usuário administrador padrão
Controle de permissões por tipo de usuário
Gestão de status de usuários (ativo/inativo)

📊 Funcionalidades de Vendas

Sistema completo de ponto de venda

Registro detalhado de transações

Diferentes formas de pagamento

Controle de operadores de caixa

📄 Geração de Documentos

Faturas em PDF: Geração automática com informações da empresa e cálculo de IVA

Relatórios de Vendas: Relatórios detalhados em PDF com totalizadores

Comprovantes de Cancelamento: Documentos específicos para vendas canceladas

Ficheiros SAF-T: Geração de arquivos XML para conformidade fiscal

🏢 Gestão Empresarial

Configuração de informações da empresa

Personalização de documentos fiscais

Controle de NIF e dados fiscais

Observações personalizadas em documentos

⚙️ Configurações Avançadas

Configuração de tamanho de papel para impressão

Personalização de layout de documentos

Configurações de empresa editáveis

Tecnologias Utilizadas

Python 3.x

CustomTkinter: Interface gráfica moderna

SQLite: Banco de dados local

ReportLab: Geração de PDFs

PIL (Pillow): Manipulação de imagens

JSON: Estruturação de dados

Estrutura do Projeto

├── main.py          # Arquivo principal com tela de login
├── database.py      # Configuração e conexão com banco de dados
├── admin.py         # Interface administrativa
├── usuario.py       # Interface do usuário comum
├── utils.py         # Utilitários para geração de PDFs e SAF-T
├── api.py          # Funções para relatórios e APIs
└── image/          # Recursos visuais
    ├── mgrace.ico
    ├── xx.png
    └── logg.png
