# Guia de Integração Frontend - Serviço de Eligibilidade

Este documento fornece orientações para desenvolvedores frontend que precisam integrar com o serviço de avaliação de elegibilidade para vistos EB2-NIW.

## Visão Geral

O serviço de elegibilidade fornece APIs para avaliação de perfis de candidatos para imigração através da categoria EB2 com National Interest Waiver (NIW). A API analisa os dados fornecidos e retorna uma avaliação detalhada da elegibilidade do candidato, incluindo pontuações por categoria, recomendações e próximos passos.

## URL Base da API

```
http://localhost:8080/api/v1
```

Em produção, substitua pela URL apropriada.

## Endpoints Principais

### 1. Avaliação de Elegibilidade

**Endpoint:** `POST /eligibility/assess`

Este endpoint realiza uma avaliação completa da elegibilidade do candidato com base nos dados fornecidos.

**Limite de taxa:** 5 requisições por minuto

#### Payload (Entrada)

```typescript
interface EligibilityAssessmentInput {
  user_id?: string;
  
  // Informações educacionais
  education: {
    highest_degree: string; // "PHD", "MASTERS", "BACHELORS", "OTHER"
    field_of_study: string;
    university_ranking?: number;
    years_since_graduation: number;
    professional_license: boolean;
    license_details?: string;
    certifications?: Array<{
      name: string;
      issuer: string;
      year: number;
      still_valid: boolean;
    }>;
    specialized_courses?: Array<{
      name: string;
      institution: string;
      year: number;
      duration_hours: number;
    }>;
  };
  
  // Informações de experiência profissional
  experience: {
    years_of_experience: number;
    leadership_roles: boolean;
    specialized_experience: boolean;
    current_position: string;
    past_positions?: string[];
    salary_level?: string; // "ABOVE_AVERAGE", "AVERAGE", "BELOW_AVERAGE"
    salary_percentile?: number;
  };
  
  // Realizações e conquistas
  achievements: {
    publications_count: number;
    patents_count: number;
    projects_led: number;
    notable_contributions?: string;
    citations_count?: number;
    h_index?: number;
    courses_taught?: number;
    industry_standards_contributions?: boolean;
  };
  
  // Reconhecimento
  recognition: {
    awards_count: number;
    speaking_invitations: number;
    professional_memberships: number;
    media_coverage?: boolean;
    peer_recognition?: boolean;
    government_recognition?: boolean;
    books_authored?: number;
    mentorship_roles?: number;
    recommendation_letters?: number;
  };
  
  // Planos para os EUA
  us_plans: {
    proposed_work: string;
    field_of_work: string;
    national_importance: string;
    potential_beneficiaries: string;
    standard_process_impracticality: string;
  };
}
```

#### Resposta

```typescript
interface EligibilityAssessmentOutput {
  id: string;
  user_id?: string;
  created_at: string; // ISO 8601 datetime
  
  // Pontuações por categoria (0.0 a 1.0)
  score: {
    education: number;
    experience: number;
    achievements: number;
    recognition: number;
    overall: number;
  };
  
  // Avaliação da rota EB2
  eb2_route?: {
    recommended_route: string; // "ADVANCED_DEGREE" ou "EXCEPTIONAL_ABILITY"
    advanced_degree_score: number;
    exceptional_ability_score: number;
    route_explanation: string;
  };
  
  // Avaliação dos critérios NIW
  niw_evaluation?: {
    merit_importance_score: number;
    well_positioned_score: number;
    benefit_waiver_score: number;
    niw_overall_score: number;
  };
  
  // Classificação da viabilidade
  viability_level: string; // "EXCELLENT", "STRONG", "PROMISING", "CHALLENGING", "INSUFFICIENT"
  viability: string; // Legado: "Low", "Moderate", "Good", "Strong"
  probability: number; // 0.0 a 1.0
  
  // Feedback e recomendações
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  
  // Recomendações detalhadas
  detailed_recommendations?: Array<{
    category: string;
    description: string;
    impact: string; // "LOW", "MEDIUM", "HIGH"
    priority: number; // 1-5
    improves_route: string; // "ADVANCED_DEGREE", "EXCEPTIONAL_ABILITY", "BOTH", "NIW"
  }>;
  
  // Próximos passos
  next_steps?: string[];
  
  // Mensagem personalizada
  message?: string;
  
  // Tempo estimado de processamento em meses
  estimated_processing_time?: number;
}
```

#### Exemplo de Uso (React)

```typescript
import { useState } from 'react';
import axios from 'axios';

function EligibilityForm() {
  const [formData, setFormData] = useState({
    // Inicialize com valores padrão...
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(
        'http://localhost:8080/api/v1/eligibility/assess',
        formData,
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );
      
      setResult(response.data);
    } catch (err) {
      setError(err.message || 'Erro ao processar a solicitação');
    } finally {
      setLoading(false);
    }
  };
  
  // Renderização do formulário...
}
```

### 2. Histórico de Avaliações

**Endpoint:** `GET /eligibility/history/{user_id}`

Retorna o histórico de avaliações para um usuário específico.

**Limite de taxa:** 10 requisições por minuto

#### Parâmetros

- `user_id`: ID do usuário (na URL)

#### Resposta

Array de objetos `EligibilityAssessmentOutput` (mesmo formato da resposta de avaliação).

### 3. Informações sobre Critérios

**Endpoint:** `GET /eligibility/info`

Retorna informações sobre os critérios de avaliação e seus pesos.

**Limite de taxa:** 20 requisições por minuto

#### Resposta

```typescript
interface EligibilityCriteria {
  criteria: {
    education: string;
    experience: string;
    achievements: string;
    recognition: string;
  };
  weights: {
    education: number;
    experience: number;
    achievements: number;
    recognition: number;
  };
  viability_levels: {
    [key: string]: string;
  };
}
```

### 4. Configuração do Sistema

**Endpoint:** `GET /eligibility/config`

Retorna a configuração detalhada usada pelo sistema de avaliação, incluindo todos os pesos, thresholds e parâmetros.

#### Resposta

Um objeto JSON contendo as configurações detalhadas do sistema:

```typescript
interface EligibilityConfig {
  category_weights: Record<string, number>;
  education_criteria: Record<string, any>;
  experience_criteria: Record<string, any>;
  achievements_criteria: Record<string, any>;
  recognition_criteria: Record<string, any>;
  viability_thresholds: Record<string, number>;
  strength_threshold: number;
  weakness_threshold: number;
  eb2_config: Record<string, any>;
  niw_config: Record<string, any>;
  max_recommendations: number;
}
```

## Códigos de Status HTTP

- **200 OK**: A requisição foi bem-sucedida
- **201 Created**: Um novo recurso foi criado com sucesso
- **400 Bad Request**: A requisição contém parâmetros inválidos
- **401 Unauthorized**: Autenticação necessária
- **403 Forbidden**: O cliente não tem permissão para acessar o recurso
- **404 Not Found**: O recurso solicitado não foi encontrado
- **422 Unprocessable Entity**: Erro de validação nos dados enviados
- **429 Too Many Requests**: Limite de taxa excedido
- **500 Internal Server Error**: Erro interno do servidor

## Melhores Práticas para Integração

### Tratamento de Erros

Sempre implemente tratamento de erros robusto, incluindo:

1. Timeout para requisições (recomendado: 10s)
2. Lógica de retry para falhas temporárias
3. Feedback amigável para o usuário

```typescript
// Exemplo de função de retry
async function fetchWithRetry(url, options, maxRetries = 3, delay = 1000) {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fetch(url, options);
    } catch (err) {
      if (attempt === maxRetries) throw err;
      await new Promise(resolve => setTimeout(resolve, delay));
      // Aumentar o delay exponencialmente para backoff
      delay *= 2;
    }
  }
}
```

### Cache

Para reduzir carga no servidor e melhorar performance, considere:

1. Armazenar temporariamente o resultado mais recente (localStorage/sessionStorage)
2. Implementar cache com TTL para endpoints como `/info` e `/config`

```typescript
// Exemplo de cache simples
function getCachedOrFetch(key, fetchFn, ttlMs = 300000) {
  const cached = localStorage.getItem(key);
  if (cached) {
    const { data, timestamp } = JSON.parse(cached);
    if (Date.now() - timestamp < ttlMs) {
      return Promise.resolve(data);
    }
  }
  
  return fetchFn().then(data => {
    localStorage.setItem(key, JSON.stringify({
      data,
      timestamp: Date.now()
    }));
    return data;
  });
}
```

### Validação de Dados

Implemente validação de dados no cliente antes de enviar para a API:

1. Verifique campos obrigatórios
2. Valide formatos e intervalos de valores
3. Forneça feedback imediato para o usuário

## Recomendações de UI/UX

### 1. Formulário em Etapas

Divida o formulário de avaliação em seções lógicas:
- Informações Educacionais
- Experiência Profissional
- Realizações e Conquistas
- Reconhecimento
- Planos para os EUA

### 2. Visualização de Resultados

Apresente os resultados em formato visual:
- Gráficos radar/spider para pontuações por categoria
- Barras de progresso para pontuações individuais
- Sistema de cores para indicar níveis (vermelho, amarelo, verde)
- Organização de recomendações por prioridade e impacto

### 3. Histórico e Comparação

Permita que os usuários:
- Visualizem seu histórico de avaliações
- Comparem avaliações diferentes
- Identifiquem melhorias ao longo do tempo

## Considerações de Desempenho

1. A avaliação completa pode levar alguns segundos para ser processada
2. Implemente indicadores de carregamento apropriados
3. Considere processar avaliações em segundo plano para formulários extensos

## Exemplos de Interfaces Recomendadas

### Formulário de Avaliação
- Wizard com múltiplas etapas
- Campos agrupados por categoria
- Dicas e tooltips para explicar cada critério
- Validação em tempo real

### Resultados da Avaliação
- Dashboard com pontuação geral destacada
- Cartões separados para cada categoria
- Seção de recomendações organizadas por prioridade
- Call-to-actions para próximos passos
- Opção para baixar/compartilhar resultados (PDF/Email)

## Suporte e Contatos

Para questões relacionadas à API, entre em contato com a equipe de desenvolvimento. 