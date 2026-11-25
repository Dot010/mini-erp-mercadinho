# Mini ERP do Mercadinho

Sistema de gestão para um mercadinho de bairro: produtos, estoque, vendas no caixa, totem de autoatendimento e painel do dono.

## Stack
- **Back-end:** Python, Django, Django REST Framework, PostgreSQL
- **Front-end:** React, TypeScript, Vite
- **Infra:** Docker Compose
- **Em breve:** Celery e Redis

## Como rodar

### Back-end
1. `python -m venv .venv` e ative o ambiente
2. `pip install -r requirements.txt`
3. Copie `.env.example` para `.env` e troque a `SECRET_KEY`
4. `docker compose up -d` para ligar o PostgreSQL
5. `python manage.py migrate`
6. `python manage.py runserver`

### Front-end
1. `cd frontend`
2. `npm install`
3. `npm run dev`

### Testes
`python manage.py test`

## Etapas
- [x] 0. Fundação: projeto, banco no Docker, variáveis de ambiente
- [x] 1. Usuários com papéis (Dono, Caixa, Estoquista)
- [x] 2. Produtos e estoque
- [x] 3. Vendas
- [x] 4. API REST
- [x] 5. Front-end React (tela do caixa)
- [x] 6. Totem de autoatendimento com liberação para maiores de 18
- [ ] 7. Painel do dono e relatórios com Celery *(em andamento)*
- [ ] 8. Testes automatizados no CI e documentação
- [ ] 9. CPF na nota
- [ ] 10. Produtos por peso (balança)
- [ ] 11. Assistente com IA (LangChain)