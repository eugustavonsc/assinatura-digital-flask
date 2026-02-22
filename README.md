# Sistema de Assinatura Digital - Campanha Acessório 0KM 🏍️

Este projeto foi desenvolvido para automatizar e profissionalizar o processo de confirmação de entrega de brindes (capacetes) da campanha **Acessório 0KM** no Grupo Cajueiro. 

A aplicação permite que o vendedor faça o upload de um documento em PDF e gere um link único para o cliente. O cliente, por sua vez, pode visualizar o documento e realizar a assinatura digital diretamente na tela do seu dispositivo móvel.

## 🚀 Funcionalidades

- **Painel Administrativo:** Área restrita para upload de documentos e gestão de arquivos.
- **Assinatura Digital Mobile-Friendly:** Interface otimizada para assinatura em telas touch.
- **Integração com WhatsApp:** Geração automática de mensagens personalizadas para envio do link ao cliente.
- **Segurança Blindada:** - Variáveis de ambiente (`.env`) para proteção de chaves e senhas.
  - Validação rigorosa de IDs para prevenir acessos maliciosos (Path Traversal).
  - Sanitização de arquivos no upload.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python com o framework Flask.
- **Manipulação de PDF:** PyMuPDF (fitz) para inserção da assinatura no documento original.
- **Frontend:** HTML5, CSS3 e JavaScript (utilizando a API Canvas para captura da assinatura).
- **Hospedagem:** PythonAnywhere.
- **Controle de Versão:** Git e GitHub.

## 🔒 Segurança

O projeto segue boas práticas de segurança, mantendo credenciais sensíveis e dados de clientes fora do controle de versão através de arquivos `.gitignore` e configuração de variáveis de ambiente no servidor.

---
Desenvolvido por **Gustavo Augusto** como parte da digitalização de processos do balcão de peças genuínas Honda.