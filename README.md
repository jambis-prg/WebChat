# Transferência de Arquivos com UDP - Primeira Etapa

Este projeto implementa a primeira etapa do projeto da disciplina de Infraestrutura de Comunicações - IF678 2025.1, desenvolvendo uma ferramenta de transferência de arquivos utilizando comunicação UDP com a biblioteca Socket em Python.

## Objetivo

Desenvolver um sistema cliente-servidor para transferência de arquivos utilizando o protocolo UDP, onde o cliente envia um arquivo ao servidor, que o armazena e o devolve modificado (com nome alterado) ao cliente.

## Estrutura do Projeto

### Arquivos Principais

- **`UDP - Cliente.py`**: Implementação do cliente UDP responsável por enviar arquivos ao servidor e receber a devolução;
- **`UDP - Servidor.py`**: Implementação do servidor UDP que recebe, armazena e devolve arquivos aos clientes;
- **`sample/`**: Diretório contendo arquivos de exemplo para teste (deve ser criado pelo usuário);
- **`Cliente/`**: Diretório criado automaticamente para armazenar arquivos devolvidos pelo servidor;
- **`Servidor/`**: Diretório criado automaticamente para armazenar arquivos recebidos dos clientes;

## Funcionalidades Implementadas

- ✅ Comunicação UDP utilizando a biblioteca Socket do Python;
- ✅ Envio de arquivos em pacotes de até 1024 bytes (buffer_size);
- ✅ Recepção e armazenamento de arquivos no servidor;
- ✅ Devolução do arquivo com nome modificado para o cliente;
- ✅ Suporte a diferentes tipos de arquivo (texto, imagens, etc.);
- ✅ Numeração sequencial de pacotes para controle e ajuste;
- ✅ Detecção de pacotes faltantes no cliente;

## Requisitos

- **Linguagem**: Python 3.6 ou superior;
- **Bibliotecas**: socket, struct, os, sys (bibliotecas padrão do Python);
- **Sistema Operacional**: Linux, Windows;

## Como Executar

### 1. Preparação do Ambiente

Após baixar o repositório, adicione arquivos para teste no diretório `sample/`.Já existem alguns arquivos de teste na pasta `sample/`;

### 2. Executar o Servidor

Em um terminal, execute:
```bash
python "UDP - Servidor.py"
```

O servidor iniciará e ficará aguardando conexões na porta 12345;

### 3. Executar o Cliente

Em outro terminal, execute:
```bash
python "UDP - Cliente.py" <nome_do_arquivo>
```

O arquivo deve ser algum localizado na pasta `sample\`;

**Exemplo:**
```bash
python "UDP - Cliente.py" txtsample1.txt
python "UDP - Cliente.py" jpgsample1.jpg
python "UDP - Cliente.py" pngsample1.png
python "UDP - Cliente.py" pdfsample1.pdf
```

### 4. Verificar os Resultados

- O arquivo enviado será salvo no diretório `Servidor/`, que é criado assim que concluir a etapa anterior;
- O arquivo devolvido será salvo no diretório `Cliente/`, também criado assim que se concluir a etapa anterior, com o prefixo `devolvido_`;

## Detalhes Técnicos

### Protocolo de Comunicação

1. **Envio do Nome**: Cliente envia o nome do arquivo;
2. **Fragmentação**: Arquivo é dividido em pacotes de 1024 bytes;
3. **Numeração**: Cada pacote possui um número sequencial para controle;
4. **Finalização**: Cliente envia sinal `FINAL` ao terminar;
5. **Devolução**: Servidor reenvia o arquivo com numeração sequencial;
6. **Término**: Servidor envia sinal `FIM` ao concluir;

### Estrutura dos Pacotes

- **Cabeçalho**: 4 bytes contendo o número do pacote;
- **Dados**: Até 1020 bytes do conteúdo do arquivo;
- **Buffer Total**: 1024 bytes máximo por pacote;

## Testes Realizados

O sistema foi testado com:
- ✅ Arquivos de texto (.txt);
- ✅ Imagens (.jpg, .png);
- ✅ Documentos (.pdf);

## Colaboradores

| [<img src="https://avatars.githubusercontent.com/u/161069298?v=4" width=115><br><sub>Esdras Gabriel</sub>](https://github.com/BlackSardes) | [<img src="https://avatars.githubusercontent.com/u/129231720?v=4" width=115><br><sub>Henrique César</sub>](https://github.com/SapoSopa) | [<img src="https://avatars.githubusercontent.com/u/98539736?v=4" width=115><br><sub>João Victor</sub>](https://github.com/jambis-prg) | [<img src="https://avatars.githubusercontent.com/u/96800329?v=4" width=115><br><sub>Luiz Gustavo</sub>](https://github.com/Zed201) | [<img src="https://avatars.githubusercontent.com/u/123107373?v=4" width=115><br><sub>Márcio Júnior</sub>](https://github.com/MAACJR032) |
| :---: | :---: | :---: | :---: | :---: |