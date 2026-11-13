# Mini ERP do Mercadinho

Sistema de gestão para um mercadinho de bairro: produtos, estoque, vendas no caixa e relatórios.

## Stack
Python, Django, Django REST Framework, PostgreSQL, Docker Compose. Em breve: Celery e Redis.

## Como rodar
1. `python -m venv .venv` e ative o ambiente
2. `pip install -r requirements.txt`
3. Copie `.env.example` para `.env` e troque a `SECRET_KEY`
4. `docker compose up -d` para ligar o PostgreSQL
5. `python manage.py runserver`

## Etapas
- [x] 0. Fundação: projeto, banco no Docker, variáveis de ambiente
- [ ] 1. Usuários com papéis (Dono, Caixa, Estoquista)
- [ ] 2. Produtos e estoque
- [ ] 3. Vendas
- [ ] 4. API REST
- [ ] 5. Relatórios com Celery
- [ ] 6. Testes e documentação