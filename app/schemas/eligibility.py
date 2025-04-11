from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


# Esquemas de sub-componentes de entrada
class CertificationInput(BaseModel):
    name: str = Field(..., description="Nome da certificação")
    issuer: str = Field(..., description="Entidade emissora")
    year: int = Field(..., description="Ano de obtenção")
    still_valid: bool = Field(True, description="Se a certificação ainda é válida")

class SpecializedCourseInput(BaseModel):
    name: str = Field(..., description="Nome do curso")
    institution: str = Field(..., description="Instituição")
    year: int = Field(..., description="Ano de conclusão")
    duration_hours: int = Field(..., description="Duração em horas")

# Schemas de sub-componentes detalhados para entrada
class EducationInput(BaseModel):
    highest_degree: str = Field(..., description="Grau acadêmico mais alto (PHD, MASTERS, BACHELORS, OTHER)")
    field_of_study: str = Field(..., description="Área de estudo/especialização")
    university_ranking: Optional[int] = Field(None, description="Ranking da instituição (opcional)")
    years_since_graduation: int = Field(..., description="Anos desde a graduação")
    professional_license: Optional[bool] = Field(False, description="Possui licença profissional")
    license_details: Optional[str] = Field(None, description="Detalhes da licença profissional")
    certifications: Optional[List[CertificationInput]] = Field([], description="Certificações profissionais")
    specialized_courses: Optional[List[SpecializedCourseInput]] = Field([], description="Cursos especializados")

class ExperienceInput(BaseModel):
    years_of_experience: int = Field(..., description="Anos de experiência no campo")
    leadership_roles: bool = Field(False, description="Posições de liderança (sim/não)")
    specialized_experience: bool = Field(False, description="Especialização em área de nicho (sim/não)")
    current_position: str = Field(..., description="Cargo atual")
    past_positions: Optional[List[str]] = Field([], description="Cargos anteriores")
    salary_level: Optional[str] = Field(None, description="Nível salarial (ABOVE_AVERAGE, AVERAGE, BELOW_AVERAGE)")
    salary_percentile: Optional[int] = Field(None, description="Percentil salarial na área")

class AchievementsInput(BaseModel):
    publications_count: int = Field(0, description="Número de publicações científicas/acadêmicas")
    patents_count: int = Field(0, description="Número de patentes")
    projects_led: int = Field(0, description="Projetos significativos liderados")
    notable_contributions: Optional[str] = Field(None, description="Inovações ou contribuições notáveis")
    citations_count: Optional[int] = Field(0, description="Número de citações acadêmicas")
    h_index: Optional[int] = Field(None, description="Índice H acadêmico")
    courses_taught: Optional[int] = Field(0, description="Cursos ministrados")
    industry_standards_contributions: Optional[bool] = Field(False, description="Contribuições para padrões da indústria")

class RecognitionInput(BaseModel):
    awards_count: int = Field(0, description="Número de prêmios/honrarias recebidos")
    speaking_invitations: int = Field(0, description="Convites para palestras/apresentações")
    professional_memberships: int = Field(0, description="Afiliações a associações profissionais")
    media_coverage: Optional[bool] = Field(False, description="Cobertura de mídia do trabalho")
    peer_recognition: Optional[bool] = Field(False, description="Reconhecimento por pares")
    government_recognition: Optional[bool] = Field(False, description="Reconhecimento governamental")
    books_authored: Optional[int] = Field(0, description="Livros/capítulos técnicos publicados")
    mentorship_roles: Optional[int] = Field(0, description="Mentorias formais ou orientações")
    recommendation_letters: Optional[int] = Field(0, description="Número de cartas de recomendação fortes")

class USPlansInput(BaseModel):
    proposed_work: str = Field(..., description="Descrição do trabalho proposto nos EUA")
    field_of_work: str = Field(..., description="Área de atuação pretendida")
    national_importance: str = Field(..., description="Descrição da importância nacional")
    potential_beneficiaries: str = Field(..., description="Beneficiários potenciais")
    standard_process_impracticality: str = Field(..., description="Razões para impraticabilidade do processo padrão")

# Schema principal de entrada
class EligibilityAssessmentInput(BaseModel):
    """Dados de entrada para avaliação de elegibilidade."""
    user_id: Optional[str] = None
    
    # Campos detalhados por categoria
    education: EducationInput
    experience: ExperienceInput
    achievements: AchievementsInput
    recognition: RecognitionInput
    us_plans: USPlansInput
    
    # Campos simplificados (para compatibilidade com versão anterior)
    highest_degree: Optional[str] = Field(None, description="Maior nível educacional")
    field_of_study: Optional[str] = Field(None, description="Área de estudo/pesquisa")
    university_ranking: Optional[int] = Field(None, description="Ranking da universidade")
    years_of_experience: Optional[int] = Field(None, description="Anos de experiência na área")
    current_position: Optional[str] = Field(None, description="Cargo atual")
    past_positions: Optional[List[str]] = Field(None, description="Cargos anteriores")
    publication_count: Optional[int] = Field(None, description="Número de publicações")
    citation_count: Optional[int] = Field(None, description="Número de citações")
    h_index: Optional[int] = Field(None, description="Índice H")
    awards: Optional[List[str]] = Field(None, description="Prêmios ou reconhecimentos")
    recommendation_letters: Optional[int] = Field(None, description="Número de cartas de recomendação fortes")
    current_salary: Optional[float] = Field(None, description="Salário anual atual em USD")
    expected_salary: Optional[float] = Field(None, description="Expectativa salarial nos EUA em USD")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "education": {
                    "highest_degree": "PHD",
                    "field_of_study": "Computer Science",
                    "university_ranking": 50,
                    "years_since_graduation": 5,
                    "professional_license": False,
                    "certifications": [
                        {"name": "AWS Solutions Architect", "issuer": "Amazon", "year": 2020, "still_valid": True}
                    ]
                },
                "experience": {
                    "years_of_experience": 8,
                    "leadership_roles": True,
                    "specialized_experience": True,
                    "current_position": "Senior Researcher",
                    "past_positions": ["Assistant Professor", "Research Associate"],
                    "salary_level": "ABOVE_AVERAGE"
                },
                "achievements": {
                    "publications_count": 15,
                    "patents_count": 2,
                    "projects_led": 5,
                    "citations_count": 250,
                    "h_index": 8
                },
                "recognition": {
                    "awards_count": 3,
                    "speaking_invitations": 10,
                    "professional_memberships": 2,
                    "recommendation_letters": 3
                },
                "us_plans": {
                    "proposed_work": "Advanced research in machine learning algorithms for healthcare",
                    "field_of_work": "Artificial Intelligence in Healthcare",
                    "national_importance": "Improve healthcare outcomes and reduce costs",
                    "potential_beneficiaries": "Hospitals, patients, healthcare providers",
                    "standard_process_impracticality": "Specialized expertise not readily available in US workforce"
                }
            }
        }

# Esquemas de saída
class CategoryScores(BaseModel):
    education: float = Field(..., description="Pontuação para educação (0-1)")
    experience: float = Field(..., description="Pontuação para experiência (0-1)")
    achievements: float = Field(..., description="Pontuação para conquistas (0-1)")
    recognition: float = Field(..., description="Pontuação para reconhecimento (0-1)")

class EB2RouteEvaluation(BaseModel):
    recommended_route: str = Field(..., description="Rota recomendada (ADVANCED_DEGREE, EXCEPTIONAL_ABILITY)")
    advanced_degree_score: float = Field(..., description="Pontuação para rota de Grau Avançado (0-1)")
    exceptional_ability_score: float = Field(..., description="Pontuação para rota de Habilidade Excepcional (0-1)")
    route_explanation: str = Field(..., description="Explicação para a rota recomendada")

class NIWEvaluation(BaseModel):
    merit_importance_score: float = Field(..., description="Pontuação para mérito e importância nacional (0-1)")
    well_positioned_score: float = Field(..., description="Pontuação para estar bem posicionado (0-1)")
    benefit_waiver_score: float = Field(..., description="Pontuação para benefício da dispensa (0-1)")
    niw_overall_score: float = Field(..., description="Pontuação geral NIW (0-1)")

class RecommendationDetail(BaseModel):
    category: str = Field(..., description="Categoria da recomendação")
    description: str = Field(..., description="Descrição detalhada")
    impact: str = Field(..., description="Impacto (LOW, MEDIUM, HIGH)")
    priority: int = Field(..., description="Prioridade (1-5)")
    improves_route: str = Field(..., description="Rota melhorada (ADVANCED_DEGREE, EXCEPTIONAL_ABILITY, BOTH, NIW)")

# Alias para manter compatibilidade com o código existente
Recommendation = RecommendationDetail

class EligibilityScore(BaseModel):
    """Pontuação de elegibilidade por categoria."""
    education: float = Field(..., description="Pontuação para educação (0-1)")
    experience: float = Field(..., description="Pontuação para experiência profissional (0-1)")
    achievements: float = Field(..., description="Pontuação para conquistas (0-1)")
    recognition: float = Field(..., description="Pontuação para reconhecimento (0-1)")
    overall: float = Field(..., description="Pontuação geral (0-1)")

class EligibilityAssessmentOutput(BaseModel):
    """Resultado da avaliação de elegibilidade."""
    id: str = Field(..., description="ID único da avaliação")
    user_id: Optional[str] = Field(None, description="ID do usuário (se disponível)")
    created_at: datetime = Field(..., description="Data e hora da avaliação")
    
    # Pontuações
    score: EligibilityScore = Field(..., description="Pontuações por categoria")
    
    # Avaliação EB2 (novo)
    eb2_route: Optional[EB2RouteEvaluation] = Field(None, description="Avaliação das rotas EB2")
    
    # Avaliação NIW (novo)
    niw_evaluation: Optional[NIWEvaluation] = Field(None, description="Avaliação dos critérios NIW")
    
    # Classificação
    viability_level: str = Field(..., description="Classificação da viabilidade (EXCELLENT, STRONG, PROMISING, CHALLENGING, INSUFFICIENT)")
    viability: str = Field(..., description="Classificação da viabilidade legada (Low, Moderate, Good, Strong)")
    probability: float = Field(..., description="Probabilidade estimada de aprovação (0-1)")
    
    # Feedback
    strengths: List[str] = Field(..., description="Pontos fortes da petição")
    weaknesses: List[str] = Field(..., description="Áreas que precisam de melhoria")
    recommendations: List[str] = Field(..., description="Recomendações específicas")
    
    # Recomendações detalhadas (novo)
    detailed_recommendations: Optional[List[RecommendationDetail]] = Field(None, description="Recomendações detalhadas")
    
    # Próximos passos
    next_steps: Optional[List[str]] = Field(None, description="Próximos passos recomendados")
    
    # Mensagem personalizada
    message: Optional[str] = Field(None, description="Mensagem personalizada")
    
    # Dados adicionais
    estimated_processing_time: Optional[int] = Field(None, description="Tempo estimado de processamento em meses")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
                "user_id": "user123",
                "created_at": "2023-05-20T14:30:15.123Z",
                "score": {
                    "education": 0.85,
                    "experience": 0.75,
                    "achievements": 0.70,
                    "recognition": 0.65,
                    "overall": 0.75
                },
                "eb2_route": {
                    "recommended_route": "ADVANCED_DEGREE",
                    "advanced_degree_score": 0.85,
                    "exceptional_ability_score": 0.65,
                    "route_explanation": "Seu doutorado em ciência da computação proporciona uma base forte para a rota de Grau Avançado"
                },
                "niw_evaluation": {
                    "merit_importance_score": 0.80,
                    "well_positioned_score": 0.65,
                    "benefit_waiver_score": 0.55,
                    "niw_overall_score": 0.68
                },
                "viability_level": "STRONG",
                "viability": "Good",
                "probability": 0.72,
                "strengths": [
                    "PhD de universidade bem classificada",
                    "Forte experiência em pesquisa",
                    "Publicações em conferências reconhecidas"
                ],
                "weaknesses": [
                    "Número limitado de citações",
                    "Poucos prêmios de reconhecimento",
                    "Experiência concentrada em apenas uma área"
                ],
                "recommendations": [
                    "Obter mais cartas de recomendação de especialistas reconhecidos",
                    "Aumentar citações através de colaborações",
                    "Documentar impacto específico do seu trabalho"
                ],
                "detailed_recommendations": [
                    {
                        "category": "recognition",
                        "description": "Obter mais cartas de recomendação de especialistas reconhecidos na área",
                        "impact": "HIGH",
                        "priority": 1,
                        "improves_route": "BOTH"
                    }
                ],
                "next_steps": [
                    "Complete seu perfil com mais detalhes sobre publicações",
                    "Upload de documentos comprobatórios de prêmios"
                ],
                "message": "Seu perfil é promissor, com forte base educacional que o posiciona bem para o EB2-NIW",
                "estimated_processing_time": 8
            }
        }

# Manter classes de compatibilidade com a implementação anterior    
class AssessmentCreate(BaseModel):
    """Schema para criação de uma avaliação rápida de elegibilidade."""
    user_id: Optional[str] = None
    education_level: str = Field(..., description="Nível de educação (ex: 'PhD', 'Master', 'Bachelor')")
    field_of_study: str = Field(..., description="Área de estudo/especialização")
    years_of_experience: int = Field(..., description="Anos de experiência na área")
    publications_count: int = Field(0, description="Número de publicações acadêmicas")
    citations_count: int = Field(0, description="Número de citações de trabalhos publicados")
    awards_count: int = Field(0, description="Número de prêmios ou reconhecimentos")
    recommendation_letters: int = Field(0, description="Número de cartas de recomendação fortes")
    annual_salary: Optional[float] = None
    current_position: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "education_level": "PhD",
                "field_of_study": "Computer Science",
                "years_of_experience": 5,
                "publications_count": 7,
                "citations_count": 120,
                "awards_count": 2,
                "recommendation_letters": 3,
                "annual_salary": 95000,
                "current_position": "Senior Researcher"
            }
        }

class AssessmentResponse(BaseModel):
    """Schema para resposta de uma avaliação de elegibilidade."""
    id: str
    overall_score: float = Field(..., description="Pontuação geral de viabilidade (0.0 a 1.0)")
    viability_level: str = Field(..., description="Nível de viabilidade textual (ex: 'Strong', 'Promising')")
    education_score: float = Field(..., description="Pontuação do fator educação (0.0 a 1.0)")
    experience_score: float = Field(..., description="Pontuação do fator experiência (0.0 a 1.0)")
    achievements_score: float = Field(..., description="Pontuação do fator conquistas (0.0 a 1.0)")
    recognition_score: float = Field(..., description="Pontuação do fator reconhecimento (0.0 a 1.0)")
    strengths: List[str] = Field(..., description="Pontos fortes identificados")
    weaknesses: List[str] = Field(..., description="Pontos fracos identificados")
    recommendations: List[str] = Field(..., description="Recomendações para melhorar a petição")
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "overall_score": 0.78,
                "viability_level": "Promising",
                "education_score": 0.9,
                "experience_score": 0.7,
                "achievements_score": 0.6,
                "recognition_score": 0.8,
                "strengths": [
                    "Forte formação acadêmica",
                    "Experiência relevante na área"
                ],
                "weaknesses": [
                    "Poucas publicações em journals de alto impacto",
                    "Número limitado de citações"
                ],
                "recommendations": [
                    "Publicar mais artigos em journals de alto impacto",
                    "Obter mais cartas de recomendação de especialistas reconhecidos"
                ],
                "created_at": "2023-01-15T13:45:30Z"
            }
        }
    
    class Config:
        orm_mode = True 