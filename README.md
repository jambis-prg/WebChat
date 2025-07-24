# Transferência de Arquivos com UDP - Segunda Etapa

Este projeto implementa a segunda etapa do projeto da disciplina de Infraestrutura de Comunicações - IF678 2025.1, desenvolvendo uma ferramenta de transferência de arquivos utilizando comunicação UDP com a biblioteca Socket em Python.

## Objetivo

Desenvolver um sistema cliente-servidor para transferência de arquivos utilizando o protocolo UDP com **confiabilidade implementada na camada de aplicação**, onde o cliente envia um arquivo ao servidor, que o armazena e o devolve modificado (com nome alterado) ao cliente. Essa etapa adiciona mecanismos de confiabilidade como controle de sequência, acknowledgments (ACKs), timeouts e retransmissões.

## Estrutura do Projeto

### Arquivos Principais

- **`UDP - Cliente.py`**: Implementação do cliente UDP responsável por enviar arquivos ao servidor e receber a devolução utilizando RDT;
- **`UDP - Servidor.py`**: Implementação do servidor UDP que recebe, armazena e devolve arquivos aos clientes utilizando RDT;
- **`sender.py`**: Classe `RDTSender` que implementa o protocolo de transferência confiável no lado do remetente;
- **`receiver.py`**: Classe `RDTReceiver` que implementa o protocolo de transferência confiável no lado do receptor;
- **`Simulador_de_rede.py`**: Classe `Simulador_de_Perdas` para simulação configurável de condições de rede (perda de pacotes);
- **`sample/`**: Diretório contendo arquivos de exemplo para teste (deve ser criado pelo usuário);
- **`Cliente/`**: Diretório criado automaticamente para armazenar arquivos devolvidos pelo servidor;
- **`Servidor/`**: Diretório criado automaticamente para armazenar arquivos recebidos dos clientes;

## Funcionalidades Implementadas

### Primeira Etapa
- ✅ Comunicação UDP utilizando a biblioteca Socket do Python;
- ✅ Envio de arquivos em pacotes de até 1024 bytes (buffer_size);
- ✅ Recepção e armazenamento de arquivos no servidor;
- ✅ Devolução do arquivo com nome modificado para o cliente;
- ✅ Suporte a diferentes tipos de arquivo (texto, imagens, PDF, etc.);

### Segunda Etapa - RDT (Reliable Data Transfer)
- ✅ **Protocolo Stop-and-Wait**: Implementação do protocolo RDT 3.0;
- ✅ **Numeração Sequencial**: Pacotes numerados alternadamente (0 e 1, conforme a máquina de estados);
- ✅ **Sistema de ACK**: Acknowledgments para confirmação de recebimento;
- ✅ **Timeout e Retransmissão**: Retransmissão automática em caso de perda;
- ✅ **Detecção de Duplicatas**: Identificação e descarte de pacotes duplicados;
- ✅ **Simulação de Perda**: Simulação configurável de perda de pacotes via linha de comando com taxa fixa ou aleatória;
- ✅ **Confiabilidade sobre UDP**: Transferência confiável utilizando protocolo não-confiável;

## Requisitos

- **Linguagem**: Python 3.6 ou superior;
- **Bibliotecas**: socket, struct, os, sys (bibliotecas padrão do Python);
- **Sistema Operacional**: Linux, Windows;

## Como Executar

### 1. Preparação do Ambiente

Após baixar o repositório, adicione arquivos para teste no diretório `sample/`. Já existem alguns arquivos de teste na pasta `sample/`;

### 2. Executar o Servidor

Em um terminal, execute:
```bash
python "UDP - Servidor.py"
```

Para configurar uma taxa específica de perda de pacotes:
```bash
python "UDP - Servidor.py" --loss-rate=0.05          # Taxa fixa de 5%
python "UDP - Servidor.py" --loss 0.1                # Taxa fixa de 10%
python "UDP - Servidor.py" --random-range=0.02-0.08  # Taxa aleatória entre 2%-8%
```

Por padrão a taxa de perda é um valor aleatório entre 0% e 2%; O servidor iniciará e ficará aguardando conexões na porta 12345;

### 3. Executar o Cliente

Em outro terminal, execute:
```bash
python "UDP - Cliente.py" <nome_do_arquivo>
```

Para configurar uma taxa específica de perda de pacotes:
```bash
python "UDP - Cliente.py" arquivo.txt --loss-rate=0.03          # Taxa fixa de 3%
python "UDP - Cliente.py" arquivo.txt --loss 0.08               # Taxa fixa de 8%
python "UDP - Cliente.py" arquivo.txt --random-range=0.01-0.12  # Taxa aleatória entre 1%-12%
```

Por padrão a taxa de perda é um valor aleatório entre 0% e 2%; O arquivo deve ser algum localizado na pasta `sample\`;

**Exemplo:**
```bash
python "UDP - Cliente.py" txtsample1.txt                           # Taxa aleatória
python "UDP - Cliente.py" jpgsample1.jpg --loss-rate=0.05          # Taxa fixa de 5%
python "UDP - Cliente.py" pngsample1.png --loss 0.02               # Taxa fixa de 2%
python "UDP - Cliente.py" pdfsample1.pdf --random-range=0.03-0.15  # Taxa aleatória 3%-15%
```

### 4. Verificar os Resultados

- O arquivo enviado será salvo no diretório `Servidor/`, que é criado assim que executar o Servidor;
- O arquivo devolvido será salvo no diretório `Cliente/`, também criado assim que executar o Cliente, com o prefixo `servidor_`;

### 5. Monitorar Logs RDT

Durante a execução, o sistema exibirá logs detalhados do protocolo RDT:
```
[RDT] Pacote 0 enviado.
[RDT] ACK 0 recebido corretamente.
[RDT] Pacote 1 enviado.
[RDT] Timeout expirado. Retransmitindo...
[RDT] Pacote 1 enviado.
[RDT] ACK 1 recebido corretamente.
```

Estes logs ajudam a monitorar:
- Envio e recebimento de pacotes;
- Timeouts e retransmissões;
- Simulação de perdas;
- Detecção de duplicatas;

## Detalhes Técnicos

### Protocolo de Comunicação RDT

1. **Inicialização**: Cliente e servidor inicializam com sequência 0;
2. **Envio de Dados**: 
   - Remetente envia pacote com número de sequência atual;
   - Aguarda ACK correspondente dentro do timeout configurado;
3. **Recebimento**:
   - Receptor verifica número de sequência esperado;
   - Envia ACK com o número de sequência recebido;
   - Entrega dados à aplicação apenas se sequência correta;
4. **Tratamento de Erros**:
   - **Timeout**: Retransmite o último pacote enviado;
   - **ACK Duplicado**: Ignora ACKs de sequências antigas;
   - **Pacote Duplicado**: Reenvia último ACK sem entregar dados;
5. **Simulação de Perdas**: Taxa configurável via linha de comando (padrão: aleatória entre 0%-10%);

### Estrutura dos Pacotes RDT

- **Cabeçalho RDT**: 1 byte contendo o número de sequência (0 ou 1);
- **Cabeçalho Aplicação**: 5 bytes identificando tipo do pacote (BEGIN, CHUNK, FINAL);
- **ACK**: 1 byte contendo número de sequência confirmado;
- **Dados**: Restante do payload (até 1018 bytes para dados de arquivo);

### Classes RDT Implementadas

#### RDTSender
- `send(data)`: Envia dados com garantia de entrega;
- `_make_packet(seq, payload)`: Cria pacote com número de sequência;
- `_parse_ack(data)`: Analisa pacotes de ACK recebidos;

#### RDTReceiver  
- `receive()`: Recebe dados garantindo ordem e integridade;
- `_make_ack(seq)`: Cria pacote de acknowledgment;
- `_parse_packet(pkt)`: Analisa pacotes recebidos;

#### Simulador_de_rede
- `__init__(loss_rate)`: Inicializa simulador com taxa de perda especificada;
- `drop_packet()`: Determina aleatoriamente se um pacote deve ser descartado;
- `simula_perda_de_pacote(info)`: Simula perda e exibe logs de debug;
- `recolher_taxa_dos_argumentos()`: Extrai taxa de perda dos argumentos ou gera valor aleatório;

### Simulação de Perda Aleatória

O sistema possui três modos de simulação de perda:

1. **Taxa Aleatória (Padrão)**: Se nenhum parâmetro for especificado, gera uma taxa aleatória entre 0% e 2%
2. **Taxa Fixa**: Especificada via `--loss-rate=X.XX` ou `--loss X.XX`
3. **Faixa Aleatória Personalizada**: Especificada via `--random-range=X.XX-Y.YY`

**Características da aleatoriedade:**
- Cada execução gera uma taxa diferente (exceto se especificada)
- A decisão de perda para cada pacote é independente e aleatória
- Distribuição uniforme dentro da faixa especificada

## Testes Realizados

O sistema foi testado com:
- ✅ Arquivos de texto (.txt);
- ✅ Imagens (.jpg, .png);
- ✅ Documentos (.pdf);
- ✅ **Simulação de Perda de Pacotes**: Testado com perda artificial de 2%;
- ✅ **Timeout e Retransmissão**: Verificado comportamento com diferentes valores de timeout;
- ✅ **Transferência Confiável**: Garantia de integridade dos arquivos transferidos;
- ✅ **Detecção de Duplicatas**: Tratamento correto de pacotes duplicados;

## Colaboradores

| [<img src="https://avatars.githubusercontent.com/u/161069298?v=4" width=115><br><sub>Esdras Gabriel</sub>](https://github.com/BlackSardes) | [<img src="https://avatars.githubusercontent.com/u/129231720?v=4" width=115><br><sub>Henrique César</sub>](https://github.com/SapoSopa) | [<img src="https://avatars.githubusercontent.com/u/98539736?v=4" width=115><br><sub>João Victor</sub>](https://github.com/jambis-prg) | [<img src="https://avatars.githubusercontent.com/u/96800329?v=4" width=115><br><sub>Luiz Gustavo</sub>](https://github.com/Zed201) | [<img src="https://avatars.githubusercontent.com/u/123107373?v=4" width=115><br><sub>Márcio Júnior</sub>](https://github.com/MAACJR032) |
| :---: | :---: | :---: | :---: | :---: |