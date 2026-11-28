# Mini ERP do Mercadinho

[![CI](https://github.com/Dot010/mini-erp-mercadinho/actions/workflows/ci.yml/badge.svg)](https://github.com/Dot010/mini-erp-mercadinho/actions/workflows/ci.yml)

Sistema de gestão para um mercadinho de bairro: produtos, estoque, vendas no caixa, totem de autoatendimento, painel do dono e relatórios por período.

## O que o sistema faz

| Papel | Pode fazer |
|---|---|
| **Dono** | tudo, mais o painel do dia, os relatórios por período e o download em CSV |
| **Caixa** | vender, ver as próprias vendas e liberar compras de produtos +18 no totem |
| **Estoquista** | cadastrar produtos e registrar entradas e saídas de estoque |
| **Totem** | autoatendimento: o cliente passa os produtos e paga; produtos +18 pedem liberação de um funcionário |

## Stack    
- **Back-end:** Python, Django, Django REST Framework, PostgreSQL
- **Tarefas em segundo plano:** Celery e Redis
- **Front-end:** React, TypeScript, Vite
- **Infra:** Docker Compose e GitHub Actions

## Decisões técnicas
- **Estoque sem venda duplicada:** a venda trava a linha do produto no banco (`select_for_update` dentro de `transaction.atomic`), então duas vendas ao mesmo tempo não deixam o estoque negativo.
- **Permissões por papel:** cada rota da API confere o papel do usuário (403 quando não pode).
- **Relatórios fora da requisição:** o pedido é salvo como pendente e o Celery calcula em segundo plano. A task recebe só o id e entra na fila com `transaction.on_commit`, para o worker nunca procurar um relatório que ainda não foi salvo.
- **Venda de produto +18 no totem:** a compra só é finalizada depois que um caixa ou o dono libera; a liberação vale para uma compra só.
- **CSV para o Excel brasileiro:** separador `;`, vírgula decimal e BOM UTF-8.
- **Login protegido:** o endpoint de login limita a 5 tentativas por minuto (429).

## Primeira vez (instalação)

### Back-end
1. `python -m venv .venv` e ative o ambiente
2. `pip install -r requirements.txt`
3. Copie `.env.example` para `.env` e troque a `SECRET_KEY`
4. `docker compose up -d` para ligar o PostgreSQL e o Redis
5. `python manage.py migrate`

### Front-end
1. `cd frontend`
2. `npm install`

## Dia a dia (ligar o sistema)

Abra o Docker Desktop e use 3 terminais na pasta do projeto:

| Terminal | Comando | O que liga |
|---|---|---|
| 1 | `docker compose up -d` e `python manage.py runserver` | banco, Redis e API (porta 8000) |
| 2 | `celery -A config worker --pool=solo -l info` | o worker que gera os relatórios |
| 3 | `cd frontend` e `npm run dev` | a tela (porta 5173) |

Depois, abra http://localhost:5173.

> O `--pool=solo` é necessário no Windows. Nos terminais 1 e 2, o `(.venv)` precisa estar ativo.

## Testes
`python manage.py test` roda os 74 testes do back-end. Eles não precisam do Redis ligado: a fila é substituída por um mock.

A cada push na `main` e em todo pull request, o GitHub Actions roda os testes com um PostgreSQL de verdade, confere se não falta nenhuma migration e faz o lint e o build do front-end.

## Etapas
- [x] 0. Fundação: projeto, banco no Docker, variáveis de ambiente
- [x] 1. Usuários com papéis (Dono, Caixa, Estoquista)
- [x] 2. Produtos e estoque
- [x] 3. Vendas
- [x] 4. API REST
- [x] 5. Front-end React (tela do caixa)
- [x] 6. Totem de autoatendimento com liberação para maiores de 18
- [x] 7. Painel do dono e relatórios por período com Celery, Redis e CSV
- [x] 8. Testes automatizados no CI e documentação
- [ ] 9. CPF na nota
- [ ] 10. Produtos por peso (balança)
- [ ] 11. Assistente com IA (LangChain)