# Serviço de Avaliação de Elegibilidade

Este serviço é responsável pela avaliação de elegibilidade para vistos EB2-NIW, fornecendo uma análise preliminar das chances de sucesso em uma petição baseada no perfil do usuário.

## Arquitetura

Este serviço é parte da arquitetura de microserviços da plataforma Visa Platform, utilizando:

- **FastAPI**: Framework para criação de APIs
- **PostgreSQL**: Banco de dados principal
- **SQLAlchemy**: ORM para acesso ao banco de dados
- **Pydantic**: Validação de modelos de dados
- **Redis**: Cache de dados e filas de mensagens
- **Docker**: Containerização para desenvolvimento e produção

## Estrutura do Código

```
eligibility-service/
├── app/
│   ├── api/            # Rotas da API
│   ├── core/           # Configurações e utilitários core
│   ├── db/             # Camada de banco de dados
│   ├── models/         # Modelos SQLAlchemy
│   ├── schemas/        # Schemas Pydantic
│   └── services/       # Lógica de negócio
├── tests/              # Testes automatizados
│   ├── api/            # Testes da API
│   └── services/       # Testes dos serviços
├── scripts/            # Scripts de utilidade e deploy
└── alembic/            # Migrações de banco de dados
```

## Principais Melhorias Implementadas

1. **Configuração Parametrizada**:
   - Extração de todos os parâmetros, pesos e limiares para arquivos de configuração
   - Eliminação de valores hardcoded no código
   - Centralização de configurações para fácil ajuste e manutenção

2. **Sistema de Logging Abrangente**:
   - Implementação de logs estruturados em formato JSON
   - Diferentes níveis de log (DEBUG, INFO, WARNING, ERROR)
   - Logs específicos para cada componente (API, scoring, recomendação)
   - Suporte para logging para console em desenvolvimento e para arquivo em produção
   - Registro de métricas para monitoramento

3. **Testes Automatizados**:
   - Testes unitários para os principais componentes
   - Testes de integração para APIs
   - Fixtures para facilitar configuração de testes
   - Testes para diferentes tipos de perfil (forte, fraco, etc.)
   - Validação completa do algoritmo de scoring

4. **Tratamento de Erros**:
   - Captura e log de exceções
   - Respostas de erro padronizadas
   - Mensagens de erro informativas

5. **Rastreabilidade**:
   - IDs de requisição únicos para cada solicitação
   - Medição de tempo de processamento
   - Correlação entre logs de diferentes componentes

## Desenvolvimento Local

### Pré-requisitos

- Python 3.8+
- Docker e Docker Compose
- Git

### Configuração do Ambiente

1. Clone o repositório:
```bash
git clone [repo-url]
cd visa-platform/eligibility-service
```

2. Configure o ambiente Python:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou 
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. Inicie o PostgreSQL com Docker:
```bash
docker-compose up -d postgres
```

4. Configure as variáveis de ambiente (ou use o arquivo .env existente):
```bash
# Exemplo .env
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/visadev"
```

5. Execute o serviço:
```bash
python run_dev.py
```

A API estará disponível em http://localhost:8000

### Testes

Execute os testes com:
```bash
pytest
```

## Endpoints API

### Avaliação de Elegibilidade

- `POST /api/v1/eligibility/evaluate`: Avalia a elegibilidade para visto EB2-NIW

Para mais detalhes, acesse a documentação OpenAPI em http://localhost:8000/docs quando o servidor estiver rodando.

## Implantação

### Docker

Para construir e executar o contêiner:

```bash
docker build -t eligibility-service .
docker run -p 8000:8000 eligibility-service
```

### Docker Compose (ambiente completo)

Para executar o ambiente completo com banco de dados:

```bash
docker-compose up -d
```

## Ambiente de Produção

Para o ambiente de produção, certifique-se de:

1. Definir variáveis de ambiente seguras
2. Usar HTTPS/TLS
3. Configurar autenticação adequada
4. Configurar monitoramento e logs

## Migrações de Banco de Dados

Para criar uma nova migração:

```bash
alembic revision --autogenerate -m "descrição da mudança"
```

Para aplicar migrações:

```bash
alembic upgrade head
```

## Integração com Azure

O serviço está preparado para integração com serviços Azure:

- **Azure SQL Database**: Para persistência de dados
- **Azure Cache for Redis**: Para caching
- **Azure Monitor/Application Insights**: Para logging e monitoramento

Configurar as variáveis de ambiente apropriadas ao implantar na Azure.