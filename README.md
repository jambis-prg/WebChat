# Chat de Sala Única com UDP - Terceira Etapa

Este projeto implementa a terceira etapa do projeto da disciplina de Infraestrutura de Comunicações - IF678 2025.1, desenvolvendo um sistema de chat de sala única utilizando comunicação UDP com a biblioteca Socket em Python e protocolo RDT (Reliable Data Transfer) implementado na camada de aplicação.

## Objetivo

Desenvolver um sistema cliente-servidor para chat em sala única utilizando o protocolo UDP com **confiabilidade implementada na camada de aplicação**, onde múltiplos clientes podem se conectar ao servidor e trocar mensagens. O sistema implementa funcionalidades como lista de amigos e sistema de banimento por votação

## Estrutura do Projeto

### Arquivos Principais

- **`client.py`**: Implementação do cliente de chat que se conecta ao servidor;
- **`server.py`**: Implementação do servidor que gerencia as conexões e distribui as mensagens;
- **`clienteRDT.py`**: Classe `RDTFull` que implementa o protocolo de transferência confiável para o cliente;
- **`serverRDT.py`**: Classe `RDTServer` que implementa o protocolo de transferência confiável para o servidor;

## Funcionalidades Implementadas

### Primeira Etapa - Transferência de Arquivos
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

### Terceira Etapa - Chat de Sala Única
- ✅ **Sistema de Identificação**: Cadastro de usuários com nomes únicos;
- ✅ **Chat em Sala Única**: Todos os usuários cadastrados podem enviar e receber mensagens;
- ✅ **Lista de Amigos**: Cada usuário pode criar e gerenciar sua lista de contatos;
- ✅ **Identificação de Amigos**: Mensagens de amigos são destacadas com `[amigo]`;
- ✅ **Sistema de Banimento**: Votação para remoção de usuários da sala;
- ✅ **Notificações**: Avisos de entrada e saída de usuários;
- ✅ **Visualização de Usuários**: Comando para listar todos os participantes da sala;

## Requisitos

- **Linguagem**: Python 3.6 ou superior;
- **Bibliotecas**: socket, struct, threading, sys, signal, datetime (bibliotecas padrão do Python);
- **Sistema Operacional**: Linux, Windows;

## Como Executar

### 1. Executar o Servidor

Em um terminal, execute:
```bash
python "server.py"
```
O servidor iniciará e ficará aguardando conexões na porta 12345.

### 2. Executar o Cliente

Em um terminal, execute:
```bash
python "client.py"
```
O cliente solicitará o IP do servidor:
```
Digite o IP do servidor:
```
Verifique o IP do Servidor e digite para prosseguir.

### 3. Identificação no Sistema

Após conectar-se, o servidor solicitará a identificação do usuário:
```bash
Identifique-se com: hi, meu nome eh <nome>
```
Digite a mensagem de identificação com seu nome desejado:

**Exemplo:**
```bash
hi, meu nome eh Renato
```
Caso o nome já esteja em uso, será solicitado outro nome.

### 4. Comandos Disponíveis

No chat, você pode utilizar os seguintes comandos:
- `bye` - Sair do chat;
- `list` - Listar todos os usuários conectados;
- `mylist` - Mostrar sua lista de amigos;
- `addtomylist <nome>` - Adicionar um usuário à sua lista de amigos;
- `rmvfrommylist <nome>` - Remover um usuário da sua lista de amigos;
- `ban <nome>` - Votar para banir um usuário da sala;
Qualquer outra mensagem será enviada para todos os usuários da sala.

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

### Estrutura do Sistema de Chat

- **Identificação do Cliente**:
   - Clientes se identificam com `hi, meu nome eh <nome>`;
   - O servidor verifica se o nome já está em uso;

- **Formato das Mensagens**:
   - As mensagens são exibidas no formato: `IP:PORTA/~[amigo]NOME: MENSAGEM HORA DATA`;
   - Mensagens de amigos são identificadas com o prefixo `[amigo]`;

- **Sistema de Banimento**:
   - A votação para banimento requer maioria simples (50% + 1);
   - O usuário banido é removido da sala imediatamente;

- **Manutenção de Conexões**:
   - O servidor mantém registro de todos os endereços e seus respectivos nomes;
   - Ao sair (`bye`), os registros são removidos automaticamente;

### Classes RDT Implementadas

#### RDTServer
- `send(data, addr)`: Envia dados com garantia de entrega para um endereço;
- `receive()`: Recebe dados garantindo ordem e integridade;
- `broadcast(message, exclude)`: Transmite mensagem para todos os clientes;
- `broadcast_to_registered(message, names, exclude_addr)`: Transmite mensagem para todos os clientes registrados;
#### RDTFull
- `send(data)`: Envia dados com garantia de entrega;
- `receive()`: Recebe dados garantindo ordem e integridade;

## Testes Realizados

O sistema foi testado com:
- ✅ Múltiplas conexões simultâneas (4 conexões simultâneas em máquinas diferentes na mesma rede);
- ✅ Teste de envio e recebimento de mensagens em grupo;
- ✅ Gerenciamento de lista de amigos;
- ✅ Sistema de votação para banimento;
- ✅ Confiabilidade na entrega de mensagens;

## Colaboradores

| [<img src="https://avatars.githubusercontent.com/u/161069298?v=4" width=115><br><sub>Esdras Gabriel</sub>](https://github.com/BlackSardes) | [<img src="https://avatars.githubusercontent.com/u/129231720?v=4" width=115><br><sub>Henrique César</sub>](https://github.com/SapoSopa) | [<img src="https://avatars.githubusercontent.com/u/98539736?v=4" width=115><br><sub>João Victor</sub>](https://github.com/jambis-prg) | [<img src="https://avatars.githubusercontent.com/u/96800329?v=4" width=115><br><sub>Luiz Gustavo</sub>](https://github.com/Zed201) | [<img src="https://avatars.githubusercontent.com/u/123107373?v=4" width=115><br><sub>Márcio Júnior</sub>](https://github.com/MAACJR032) |
| :---: | :---: | :---: | :---: | :---: |