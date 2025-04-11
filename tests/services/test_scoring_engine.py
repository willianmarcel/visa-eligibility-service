import pytest
from app.services.scoring_engine import ScoringEngine
from app.schemas.eligibility import (
    EligibilityAssessmentInput, EducationInput, 
    ExperienceInput, AchievementsInput, RecognitionInput
)

class TestScoringEngine:
    """Testes unitários para o motor de pontuação de elegibilidade."""
    
    def setup_method(self):
        """Configuração executada antes de cada teste."""
        self.scoring_engine = ScoringEngine()
    
    def test_calculate_education_score_phd(self, sample_education_data):
        """Teste para calcular pontuação de educação com PhD."""
        # Garantir que o grau é PhD
        sample_education_data["highest_degree"] = "PHD"
        score = self.scoring_engine.calculate_education_score(sample_education_data)
        
        # A pontuação deve ser alta para PhD
        assert score > 0.8, "PhD em uma boa universidade deve ter pontuação alta"
    
    def test_calculate_education_score_bachelors(self, sample_education_data):
        """Teste para calcular pontuação de educação com bacharelado."""
        # Modificar para bacharelado
        sample_education_data["highest_degree"] = "BACHELORS"
        score = self.scoring_engine.calculate_education_score(sample_education_data)
        
        # A pontuação deve ser média para bacharelado
        assert 0.4 < score < 0.7, "Bacharelado deve ter pontuação média"
    
    def test_calculate_experience_score_high(self, sample_experience_data):
        """Teste para calcular pontuação de experiência com muitos anos e liderança."""
        # Garantir experiência sênior
        sample_experience_data["years_of_experience"] = 10
        sample_experience_data["leadership_roles"] = True
        
        score = self.scoring_engine.calculate_experience_score(sample_experience_data)
        
        # A pontuação deve ser alta para experiência sênior
        assert score > 0.7, "10+ anos com liderança deve ter pontuação alta"
    
    def test_calculate_experience_score_low(self, sample_experience_data):
        """Teste para calcular pontuação de experiência com poucos anos e sem liderança."""
        # Configurar experiência júnior
        sample_experience_data["years_of_experience"] = 2
        sample_experience_data["leadership_roles"] = False
        sample_experience_data["specialized_experience"] = False
        
        score = self.scoring_engine.calculate_experience_score(sample_experience_data)
        
        # A pontuação deve ser baixa para experiência júnior
        assert score < 0.5, "Pouca experiência sem liderança deve ter pontuação baixa"
    
    def test_calculate_achievements_score_high(self, sample_achievements_data):
        """Teste para calcular pontuação de realizações com muitas publicações e patentes."""
        # Garantir muitas publicações e patentes
        sample_achievements_data["publications_count"] = 15
        sample_achievements_data["patents_count"] = 4
        
        score = self.scoring_engine.calculate_achievements_score(sample_achievements_data)
        
        # A pontuação deve ser alta para muitas realizações
        assert score > 0.8, "Muitas publicações e patentes deve ter pontuação alta"
    
    def test_calculate_achievements_score_low(self, sample_achievements_data):
        """Teste para calcular pontuação de realizações com poucas publicações e patentes."""
        # Configurar poucas realizações
        sample_achievements_data["publications_count"] = 0
        sample_achievements_data["patents_count"] = 0
        sample_achievements_data["projects_led"] = 0
        
        score = self.scoring_engine.calculate_achievements_score(sample_achievements_data)
        
        # A pontuação deve ser baixa para poucas realizações
        assert score < 0.3, "Sem publicações, patentes ou projetos deve ter pontuação baixa"
    
    def test_calculate_recognition_score_high(self, sample_recognition_data):
        """Teste para calcular pontuação de reconhecimento com muitos prêmios e convites."""
        # Garantir muito reconhecimento
        sample_recognition_data["awards_count"] = 5
        sample_recognition_data["speaking_invitations"] = 8
        sample_recognition_data["professional_memberships"] = 4
        
        score = self.scoring_engine.calculate_recognition_score(sample_recognition_data)
        
        # A pontuação deve ser alta para muito reconhecimento
        assert score > 0.7, "Muito reconhecimento deve ter pontuação alta"
    
    def test_calculate_recognition_score_low(self, sample_recognition_data):
        """Teste para calcular pontuação de reconhecimento com pouco reconhecimento."""
        # Configurar pouco reconhecimento
        sample_recognition_data["awards_count"] = 0
        sample_recognition_data["speaking_invitations"] = 0
        sample_recognition_data["professional_memberships"] = 0
        
        score = self.scoring_engine.calculate_recognition_score(sample_recognition_data)
        
        # A pontuação deve ser baixa para pouco reconhecimento
        assert score < 0.3, "Sem prêmios, convites ou afiliações deve ter pontuação baixa"
    
    def test_calculate_overall_score(self):
        """Teste para calcular pontuação geral com base nas pontuações por categoria."""
        # Configurar pontuações por categoria
        category_scores = {
            "education": 0.9,
            "experience": 0.8,
            "achievements": 0.7,
            "recognition": 0.6
        }
        
        overall_score = self.scoring_engine.calculate_overall_score(category_scores)
        
        # Verificar se a pontuação geral está no intervalo esperado
        assert 75 <= overall_score <= 80, f"Pontuação geral deve estar entre 75 e 80, mas foi {overall_score}"
    
    def test_determine_viability_level_excellent(self):
        """Teste para determinar nível de viabilidade excelente."""
        level = self.scoring_engine.determine_viability_level(90)
        assert level == "EXCELLENT", "Pontuação 90 deve resultar em nível EXCELLENT"
    
    def test_determine_viability_level_strong(self):
        """Teste para determinar nível de viabilidade forte."""
        level = self.scoring_engine.determine_viability_level(75)
        assert level == "STRONG", "Pontuação 75 deve resultar em nível STRONG"
    
    def test_determine_viability_level_promising(self):
        """Teste para determinar nível de viabilidade promissor."""
        level = self.scoring_engine.determine_viability_level(60)
        assert level == "PROMISING", "Pontuação 60 deve resultar em nível PROMISING"
    
    def test_determine_viability_level_challenging(self):
        """Teste para determinar nível de viabilidade desafiador."""
        level = self.scoring_engine.determine_viability_level(45)
        assert level == "CHALLENGING", "Pontuação 45 deve resultar em nível CHALLENGING"
    
    def test_determine_viability_level_insufficient(self):
        """Teste para determinar nível de viabilidade insuficiente."""
        level = self.scoring_engine.determine_viability_level(35)
        assert level == "INSUFFICIENT", "Pontuação 35 deve resultar em nível INSUFFICIENT"
    
    def test_identify_strengths(self):
        """Teste para identificar pontos fortes."""
        category_scores = {
            "education": 0.9,
            "experience": 0.8,
            "achievements": 0.3,
            "recognition": 0.4
        }
        
        strengths = self.scoring_engine.identify_strengths(category_scores)
        
        # Deve identificar educação e experiência como pontos fortes
        assert len(strengths) == 2, f"Deve identificar 2 pontos fortes, mas identificou {len(strengths)}"
        assert any("acadêmica" in s.lower() for s in strengths), "Educação deve ser um ponto forte"
        assert any("experiência" in s.lower() for s in strengths), "Experiência deve ser um ponto forte"
    
    def test_identify_weaknesses(self):
        """Teste para identificar pontos fracos."""
        category_scores = {
            "education": 0.9,
            "experience": 0.8,
            "achievements": 0.3,
            "recognition": 0.4
        }
        
        weaknesses = self.scoring_engine.identify_weaknesses(category_scores)
        
        # Deve identificar realizações e reconhecimento como pontos fracos
        assert len(weaknesses) == 2, f"Deve identificar 2 pontos fracos, mas identificou {len(weaknesses)}"
        assert any("realizações" in s.lower() for s in weaknesses), "Realizações deve ser um ponto fraco"
        assert any("reconhecimento" in s.lower() for s in weaknesses), "Reconhecimento deve ser um ponto fraco"
    
    def test_evaluate_eligibility_excellent(self, sample_assessment_input):
        """Teste para avaliar elegibilidade com perfil excelente."""
        # Configurar perfil excelente
        sample_assessment_input.education.highest_degree = "PHD"
        sample_assessment_input.experience.years_of_experience = 12
        sample_assessment_input.achievements.publications_count = 20
        sample_assessment_input.recognition.awards_count = 5
        
        results = self.scoring_engine.evaluate_eligibility(sample_assessment_input)
        
        assert results["viability_level"] == "EXCELLENT", "Perfil excelente deve resultar em nível EXCELLENT"
        assert results["overall_score"] >= 85, "Perfil excelente deve ter pontuação geral alta"
        assert len(results["strengths"]) > len(results["weaknesses"]), "Deve ter mais pontos fortes que fracos"
    
    def test_evaluate_eligibility_insufficient(self, sample_assessment_input):
        """Teste para avaliar elegibilidade com perfil insuficiente."""
        # Configurar perfil insuficiente
        sample_assessment_input.education.highest_degree = "BACHELORS"
        sample_assessment_input.experience.years_of_experience = 1
        sample_assessment_input.experience.leadership_roles = False
        sample_assessment_input.experience.specialized_experience = False
        sample_assessment_input.achievements.publications_count = 0
        sample_assessment_input.achievements.patents_count = 0
        sample_assessment_input.achievements.projects_led = 0
        sample_assessment_input.recognition.awards_count = 0
        sample_assessment_input.recognition.speaking_invitations = 0
        sample_assessment_input.recognition.professional_memberships = 0
        
        results = self.scoring_engine.evaluate_eligibility(sample_assessment_input)
        
        assert results["viability_level"] == "INSUFFICIENT", "Perfil insuficiente deve resultar em nível INSUFFICIENT"
        assert results["overall_score"] < 40, "Perfil insuficiente deve ter pontuação geral baixa"
        assert len(results["weaknesses"]) > len(results["strengths"]), "Deve ter mais pontos fracos que fortes" 