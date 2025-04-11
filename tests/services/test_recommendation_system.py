import pytest
from app.services.recommendation_engine import RecommendationEngine
from app.schemas.eligibility import (
    EligibilityAssessmentInput, EducationInput, 
    ExperienceInput, AchievementsInput, RecognitionInput,
    USPlansInput
)

class TestRecommendationSystem:
    """
    Testes unitários para garantir que o sistema de recomendações
    está implementado conforme especificado na documentação.
    """
    
    def setup_method(self):
        """Configuração executada antes de cada teste."""
        self.recommendation_engine = RecommendationEngine()
    
    def test_recommendations_for_weak_education(self):
        """
        Teste para verificar se o sistema gera recomendações apropriadas para
        um perfil com pontuação baixa em educação.
        """
        # Configurar scores com educação fraca
        category_scores = {
            "education": 0.3,  # Score baixo para educação
            "experience": 0.7,
            "achievements": 0.6,
            "recognition": 0.5
        }
        
        # Criar input de exemplo
        input_data = self._create_basic_assessment_input()
        input_data.education.highest_degree = "BACHELORS"
        
        # Gerar recomendações
        recommendations = self.recommendation_engine.generate_recommendations(
            input_data, category_scores
        )
        
        # Verificar se há recomendações para melhorar educação
        education_recs = [r for r in recommendations if r.category.lower() == "education"]
        
        assert len(education_recs) > 0, "Deve gerar recomendações para melhorar educação"
        
        # Verificar se as recomendações de educação têm alta prioridade
        high_priority_edu_recs = [r for r in education_recs if r.priority <= 2]
        assert len(high_priority_edu_recs) > 0, "Deve haver recomendações de alta prioridade para educação"
        
        # Verificar recomendações específicas conforme documentação
        expected_keywords = ["certificação", "mestrado", "curso", "especializa"]
        assert any(any(kw in r.description.lower() for kw in expected_keywords) for r in education_recs), \
            "Deve recomendar certificações, cursos ou programas educacionais"
    
    def test_recommendations_for_weak_achievements(self):
        """
        Teste para verificar se o sistema gera recomendações apropriadas para
        um perfil com pontuação baixa em realizações.
        """
        # Configurar scores com realizações fracas
        category_scores = {
            "education": 0.8,
            "experience": 0.7,
            "achievements": 0.2,  # Score baixo para realizações
            "recognition": 0.6
        }
        
        # Criar input de exemplo
        input_data = self._create_basic_assessment_input()
        input_data.achievements.publications_count = 0
        input_data.achievements.patents_count = 0
        
        # Gerar recomendações
        recommendations = self.recommendation_engine.generate_recommendations(
            input_data, category_scores
        )
        
        # Verificar se há recomendações para melhorar realizações
        achievement_recs = [r for r in recommendations if r.category.lower() == "achievements"]
        
        assert len(achievement_recs) > 0, "Deve gerar recomendações para melhorar realizações"
        
        # Verificar recomendações específicas conforme documentação
        expected_keywords = ["publica", "artigo", "patent", "projet", "contribu"]
        assert any(any(kw in r.description.lower() for kw in expected_keywords) for r in achievement_recs), \
            "Deve recomendar publicar artigos, buscar patentes ou liderar projetos"
    
    def test_recommendations_for_weak_recognition(self):
        """
        Teste para verificar se o sistema gera recomendações apropriadas para
        um perfil com pontuação baixa em reconhecimento.
        """
        # Configurar scores com reconhecimento fraco
        category_scores = {
            "education": 0.7,
            "experience": 0.8,
            "achievements": 0.6,
            "recognition": 0.3  # Score baixo para reconhecimento
        }
        
        # Criar input de exemplo
        input_data = self._create_basic_assessment_input()
        input_data.recognition.awards_count = 0
        input_data.recognition.speaking_invitations = 0
        
        # Gerar recomendações
        recommendations = self.recommendation_engine.generate_recommendations(
            input_data, category_scores
        )
        
        # Verificar se há recomendações para melhorar reconhecimento
        recognition_recs = [r for r in recommendations if r.category.lower() == "recognition"]
        
        assert len(recognition_recs) > 0, "Deve gerar recomendações para melhorar reconhecimento"
        
        # Verificar recomendações específicas conforme documentação
        expected_keywords = ["prêmio", "palestrar", "associa", "mentor", "profissional"]
        assert any(any(kw in r.description.lower() for kw in expected_keywords) for r in recognition_recs), \
            "Deve recomendar buscar prêmios, palestrar ou associar-se a organizações"
    
    def test_recommendation_priority_based_on_score(self):
        """
        Teste para verificar se as recomendações são priorizadas corretamente
        com base nos scores mais baixos.
        """
        # Configurar scores com várias categorias fracas, mas educação sendo a pior
        category_scores = {
            "education": 0.2,  # Categoria mais fraca
            "experience": 0.5,
            "achievements": 0.4,
            "recognition": 0.6
        }
        
        # Criar input de exemplo básico
        input_data = self._create_basic_assessment_input()
        
        # Gerar recomendações
        recommendations = self.recommendation_engine.generate_recommendations(
            input_data, category_scores
        )
        
        # Verificar se há recomendações para todas as categorias com score baixo
        categories_with_recs = {r.category.lower() for r in recommendations}
        assert "education" in categories_with_recs, "Deve ter recomendações para educação"
        assert "achievements" in categories_with_recs, "Deve ter recomendações para realizações"
        
        # As recomendações de maior prioridade devem ser para educação (categoria mais fraca)
        highest_priority_rec = min(recommendations, key=lambda r: r.priority)
        assert highest_priority_rec.category.lower() == "education", \
            f"Categoria mais fraca deve ter maior prioridade, mas foi {highest_priority_rec.category}"
    
    def test_recommendation_impact_levels(self):
        """
        Teste para verificar se as recomendações incluem diferentes níveis de impacto
        (LOW, MEDIUM, HIGH).
        """
        # Criar input de exemplo com várias áreas para melhorar
        input_data = self._create_basic_assessment_input()
        input_data.education.highest_degree = "BACHELORS"
        input_data.achievements.publications_count = 0
        input_data.recognition.awards_count = 0
        
        # Configurar scores com várias categorias fracas
        category_scores = {
            "education": 0.4,
            "experience": 0.5,
            "achievements": 0.3,
            "recognition": 0.4
        }
        
        # Gerar recomendações
        recommendations = self.recommendation_engine.generate_recommendations(
            input_data, category_scores
        )
        
        # Verificar se há recomendações com diferentes níveis de impacto
        impact_levels = {r.impact for r in recommendations}
        
        assert "HIGH" in impact_levels, "Deve incluir recomendações de alto impacto"
        assert "MEDIUM" in impact_levels or "LOW" in impact_levels, \
            "Deve incluir recomendações de médio ou baixo impacto"
    
    def test_recommendation_count_limit(self):
        """
        Teste para verificar se o sistema limita o número de recomendações
        conforme especificado na documentação (5-7 recomendações).
        """
        # Criar input de exemplo com várias áreas para melhorar
        input_data = self._create_basic_assessment_input()
        
        # Configurar scores com todas as categorias fracas para gerar muitas recomendações potenciais
        category_scores = {
            "education": 0.3,
            "experience": 0.3,
            "achievements": 0.3,
            "recognition": 0.3
        }
        
        # Gerar recomendações
        recommendations = self.recommendation_engine.generate_recommendations(
            input_data, category_scores
        )
        
        # Verificar se o número de recomendações está dentro do limite especificado
        assert 5 <= len(recommendations) <= 8, \
            f"Deve limitar recomendações a 5-7, mas gerou {len(recommendations)}"
    
    def test_recommendation_for_certification(self):
        """
        Teste para verificar se o sistema recomenda certificações específicas
        quando apropriado.
        """
        # Criar input de exemplo com educação fraca mas em área técnica
        input_data = self._create_basic_assessment_input()
        input_data.education.highest_degree = "BACHELORS"
        input_data.education.field_of_study = "Computer Science"
        input_data.experience.current_position = "Software Developer"
        
        # Configurar scores com educação fraca
        category_scores = {
            "education": 0.4,
            "experience": 0.6,
            "achievements": 0.5,
            "recognition": 0.5
        }
        
        # Gerar recomendações
        recommendations = self.recommendation_engine.generate_recommendations(
            input_data, category_scores
        )
        
        # Verificar se há recomendações específicas para certificações
        certification_keywords = ["certificação", "certificado", "curso", "profissional"]
        has_certification_rec = any(
            any(kw in r.description.lower() for kw in certification_keywords)
            for r in recommendations
        )
        
        assert has_certification_rec, "Deve recomendar certificações profissionais específicas"
    
    def test_advanced_degree_vs_exceptional_ability_recommendations(self):
        """
        Teste para verificar se as recomendações indicam qual rota (Grau Avançado
        ou Habilidade Excepcional) é mais fortalecida.
        """
        # Criar input de exemplo
        input_data = self._create_basic_assessment_input()
        
        # Configurar scores médios
        category_scores = {
            "education": 0.5,
            "experience": 0.5,
            "achievements": 0.5,
            "recognition": 0.5
        }
        
        # Gerar recomendações
        recommendations = self.recommendation_engine.generate_recommendations(
            input_data, category_scores
        )
        
        # Verificar se as recomendações indicam qual rota é fortalecida
        routes_mentioned = set()
        for rec in recommendations:
            if hasattr(rec, 'improves_route'):
                routes_mentioned.add(rec.improves_route)
        
        assert routes_mentioned, "Recomendações devem indicar qual rota é fortalecida"
        assert any(r in ["ADVANCED_DEGREE", "EXCEPTIONAL_ABILITY", "BOTH"] for r in routes_mentioned), \
            "Rotas devem incluir ADVANCED_DEGREE, EXCEPTIONAL_ABILITY ou BOTH"
    
    # =======================================
    # Métodos auxiliares
    # =======================================
    
    def _create_basic_assessment_input(self):
        """Cria uma entrada básica para avaliação."""
        return EligibilityAssessmentInput(
            education=EducationInput(
                highest_degree="MASTERS",
                field_of_study="Computer Science",
                university_ranking=100,
                years_since_graduation=5
            ),
            experience=ExperienceInput(
                years_of_experience=5,
                leadership_roles=False,
                specialized_experience=True,
                current_position="Software Engineer"
            ),
            achievements=AchievementsInput(
                publications_count=3,
                patents_count=0,
                projects_led=2
            ),
            recognition=RecognitionInput(
                awards_count=1,
                speaking_invitations=2,
                professional_memberships=1
            ),
            us_plans=USPlansInput(
                proposed_work="Software development for financial services",
                field_of_work="Financial Technology",
                national_importance="Improving security and efficiency of financial systems",
                potential_beneficiaries="Banks, financial institutions, and consumers",
                standard_process_impracticality="Special expertise not readily available"
            )
        ) 