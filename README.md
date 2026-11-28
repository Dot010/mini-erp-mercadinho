# Mini ERP do Mercadinho

Sistema de gestão para um mercadinho de bairro: produtos, estoque, vendas no caixa, totem de autoatendimento, painel do dono e relatórios por período.

## Stack
- **Back-end:** Python, Django, Django REST Framework, PostgreSQL
- **Tarefas em segundo plano:** Celery e Redis
- **Front-end:** React, TypeScript, Vite
- **Infra:** Docker Compose

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
`python manage.py test`

Os testes não precisam do Redis ligado: a fila é substituída por um mock.

## Etapas
- [x] 0. Fundação: projeto, banco no Docker, variáveis de ambiente
- [x] 1. Usuários com papéis (Dono, Caixa, Estoquista)
- [x] 2. Produtos e estoque
- [x] 3. Vendas
- [x] 4. API REST
- [x] 5. Front-end React (tela do caixa)
- [x] 6. Totem de autoatendimento com liberação para maiores de 18
- [x] 7. Painel do dono e relatórios por período com Celery, Redis e CSV
- [ ] 8. Testes automatizados no CI e documentação
- [ ] 9. CPF na nota
- [ ] 10. Produtos por peso (balança)
- [ ] 11. Assistente com IA (LangChain)