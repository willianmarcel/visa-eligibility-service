import pytest
from app.services.scoring_engine import ScoringEngine
from app.schemas.eligibility import (
    EligibilityAssessmentInput, EducationInput, 
    ExperienceInput, AchievementsInput, RecognitionInput,
    USPlansInput
)

class TestEB2NIWScoring:
    """
    Testes unitários para garantir que o algoritmo de pontuação EB2-NIW
    está implementado conforme especificado na documentação.
    """
    
    def setup_method(self):
        """Configuração executada antes de cada teste."""
        self.scoring_engine = ScoringEngine()
    
    # =======================================
    # Testes para a Rota de Grau Avançado
    # =======================================
    
    def test_advanced_degree_route_phd(self):
        """
        Teste para verificar a rota de Grau Avançado com PhD.
        Segundo a documentação, este caso deve receber pontuação 1.0.
        """
        input_data = self._create_basic_assessment_input()
        input_data.education.highest_degree = "PHD"
        input_data.education.field_of_study = "Computer Science"
        
        result = self.scoring_engine.evaluate_advanced_degree_route(input_data)
        assert result >= 0.9, f"PhD deve ter pontuação próxima a 1.0, mas teve {result}"
        
    def test_advanced_degree_route_masters(self):
        """
        Teste para verificar a rota de Grau Avançado com Mestrado.
        Segundo a documentação, este caso deve receber pontuação 0.9.
        """
        input_data = self._create_basic_assessment_input()
        input_data.education.highest_degree = "MASTERS"
        input_data.education.field_of_study = "Computer Science"
        
        result = self.scoring_engine.evaluate_advanced_degree_route(input_data)
        assert 0.8 <= result <= 0.95, f"Mestrado deve ter pontuação próxima a 0.9, mas teve {result}"
        
    def test_advanced_degree_route_bachelors_with_experience(self):
        """
        Teste para verificar a rota de Grau Avançado com Bacharelado + 7 anos de experiência.
        Segundo a documentação, este caso deve receber pontuação 0.85.
        """
        input_data = self._create_basic_assessment_input()
        input_data.education.highest_degree = "BACHELORS"
        input_data.education.field_of_study = "Engineering"
        input_data.experience.years_of_experience = 8
        
        result = self.scoring_engine.evaluate_advanced_degree_route(input_data)
        assert 0.8 <= result <= 0.9, f"Bacharelado + >7 anos deve ter pontuação próxima a 0.85, mas teve {result}"
        
    def test_advanced_degree_route_insufficient(self):
        """
        Teste para verificar a rota de Grau Avançado com apenas Bacharelado e pouca experiência.
        Segundo a documentação, este caso deve receber pontuação baixa.
        """
        input_data = self._create_basic_assessment_input()
        input_data.education.highest_degree = "BACHELORS"
        input_data.education.field_of_study = "Business"
        input_data.experience.years_of_experience = 3  # Menos de 5 anos
        
        result = self.scoring_engine.evaluate_advanced_degree_route(input_data)
        assert result < 0.5, f"Bacharelado + <5 anos deve ter pontuação baixa, mas teve {result}"

    # =======================================
    # Testes para a Rota de Habilidade Excepcional
    # =======================================
    
    def test_exceptional_ability_meets_all_criteria(self):
        """
        Teste para verificar a rota de Habilidade Excepcional quando atende a todos os critérios.
        Segundo a documentação, atender 5-6 critérios deve receber pontuação 1.0.
        """
        input_data = self._create_exceptional_ability_input(
            education=True,
            experience=True,
            license=True,
            salary=True,
            membership=True,
            recognition=True
        )
        
        result = self.scoring_engine.evaluate_exceptional_ability_route(input_data)
        assert result >= 0.9, f"Atender todos os critérios deve ter pontuação próxima a 1.0, mas teve {result}"
        
    def test_exceptional_ability_meets_four_criteria(self):
        """
        Teste para verificar a rota de Habilidade Excepcional quando atende a 4 critérios.
        Segundo a documentação, atender 4 critérios deve receber pontuação 0.9.
        """
        input_data = self._create_exceptional_ability_input(
            education=True,
            experience=True,
            license=True,
            salary=True,
            membership=False,
            recognition=False
        )
        
        result = self.scoring_engine.evaluate_exceptional_ability_route(input_data)
        assert 0.8 <= result <= 0.95, f"Atender 4 critérios deve ter pontuação próxima a 0.9, mas teve {result}"
        
    def test_exceptional_ability_meets_three_criteria(self):
        """
        Teste para verificar a rota de Habilidade Excepcional quando atende a 3 critérios.
        Segundo a documentação, atender 3 critérios deve receber pontuação 0.8.
        """
        input_data = self._create_exceptional_ability_input(
            education=True,
            experience=True,
            license=True,
            salary=False,
            membership=False,
            recognition=False
        )
        
        result = self.scoring_engine.evaluate_exceptional_ability_route(input_data)
        assert 0.7 <= result <= 0.85, f"Atender 3 critérios deve ter pontuação próxima a 0.8, mas teve {result}"
        
    def test_exceptional_ability_insufficient(self):
        """
        Teste para verificar a rota de Habilidade Excepcional quando atende a poucos critérios.
        Segundo a documentação, atender 0-1 critério deve receber pontuação 0.0.
        """
        input_data = self._create_exceptional_ability_input(
            education=True,
            experience=False,
            license=False,
            salary=False,
            membership=False,
            recognition=False
        )
        
        result = self.scoring_engine.evaluate_exceptional_ability_route(input_data)
        assert result < 0.5, f"Atender apenas 1 critério deve ter pontuação baixa, mas teve {result}"

    # =======================================
    # Testes para cálculo do NIW
    # =======================================
    
    def test_niw_criteria_merit_and_importance(self):
        """
        Teste para verificar o cálculo do critério 'mérito e importância nacional' do NIW.
        """
        input_data = self._create_basic_assessment_input()
        # Configurar dados para área de alta relevância nacional
        input_data.us_plans = USPlansInput(
            proposed_work="Pesquisa em cibersegurança para proteção de infraestrutura crítica",
            field_of_work="Cibersegurança",
            national_importance="Proteção contra ameaças cibernéticas a infraestruturas críticas dos EUA",
            potential_beneficiaries="Agências governamentais, empresas de energia, transporte e saúde",
            standard_process_impracticality="Conhecimentos especializados não facilmente disponíveis no mercado de trabalho dos EUA"
        )
        
        result = self.scoring_engine.evaluate_niw_merit_importance(input_data)
        assert result >= 0.8, f"Área crítica deve ter pontuação alta para mérito/importância, mas teve {result}"
        
    def test_niw_criteria_well_positioned(self):
        """
        Teste para verificar o cálculo do critério 'bem posicionado' do NIW.
        """
        input_data = self._create_basic_assessment_input()
        # Configurar perfil com qualificações fortes
        input_data.education.highest_degree = "PHD"
        input_data.experience.years_of_experience = 10
        input_data.achievements.publications_count = 15
        
        result = self.scoring_engine.evaluate_niw_well_positioned(input_data)
        assert result >= 0.8, f"Perfil altamente qualificado deve ter pontuação alta para 'bem posicionado', mas teve {result}"
        
    def test_niw_criteria_waiver_benefit(self):
        """
        Teste para verificar o cálculo do critério 'benefício de dispensa' do NIW.
        """
        input_data = self._create_basic_assessment_input()
        # Configurar dados que justificam a dispensa dos requisitos padrão
        input_data.us_plans = USPlansInput(
            proposed_work="Pesquisa em tratamentos inovadores para doenças raras",
            field_of_work="Biotecnologia Médica",
            national_importance="Avanços no tratamento de doenças raras que afetam milhares de americanos",
            potential_beneficiaries="Pacientes com doenças raras, sistema de saúde americano",
            standard_process_impracticality="Expertise única que não seria viável obter através do processo padrão de certificação de trabalho"
        )
        
        result = self.scoring_engine.evaluate_niw_waiver_benefit(input_data)
        assert result >= 0.7, f"Caso com fortes razões para dispensa deve ter pontuação alta, mas teve {result}"
        
    def test_niw_final_score_calculation(self):
        """
        Teste para verificar o cálculo final do score NIW conforme a fórmula da documentação.
        NIW_score = (merito_e_importancia * 0.35 + bem_posicionado * 0.35 + beneficio_dispensa * 0.30)
        """
        # Valores simulados para teste
        merit_score = 0.9
        well_positioned_score = 0.8
        waiver_benefit_score = 0.7
        
        expected_score = (merit_score * 0.35) + (well_positioned_score * 0.35) + (waiver_benefit_score * 0.30)
        
        result = self.scoring_engine.calculate_niw_score(
            merit_score, well_positioned_score, waiver_benefit_score
        )
        
        assert abs(result - expected_score) < 0.01, f"Score NIW incorreto: esperado {expected_score}, obteve {result}"
    
    def test_overall_score_calculation(self):
        """
        Teste para verificar o cálculo do score geral conforme a fórmula da documentação.
        score_final = (elegibilidadeEB2_score * 0.4) + (NIW_score * 0.6)
        """
        # Valores simulados para teste
        eb2_score = 0.9
        niw_score = 0.8
        
        expected_score = (eb2_score * 0.4) + (niw_score * 0.6)
        expected_percentage = expected_score * 100
        
        result = self.scoring_engine.calculate_final_score(eb2_score, niw_score)
        
        assert abs(result - expected_percentage) < 1.0, f"Score final incorreto: esperado {expected_percentage}, obteve {result}"
        
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
    
    def _create_exceptional_ability_input(self, education=False, experience=False, 
                                         license=False, salary=False, 
                                         membership=False, recognition=False):
        """
        Cria uma entrada para testar a rota de Habilidade Excepcional.
        
        Configura os diferentes critérios conforme os parâmetros:
        1. education: Grau acadêmico relacionado
        2. experience: 10+ anos de experiência
        3. license: Licença/certificação profissional
        4. salary: Salário demonstrando habilidade excepcional
        5. membership: Associação a organizações profissionais
        6. recognition: Reconhecimento por realizações significativas
        """
        input_data = self._create_basic_assessment_input()
        
        # Configurar critérios conforme parâmetros
        if education:
            input_data.education.highest_degree = "MASTERS"
            input_data.education.field_of_study = "Computer Science"
            input_data.education.university_ranking = 50
        else:
            input_data.education.highest_degree = "BACHELORS"
            input_data.education.university_ranking = 200
            
        if experience:
            input_data.experience.years_of_experience = 12
        else:
            input_data.experience.years_of_experience = 4
            
        if license:
            input_data.education.professional_license = True
            input_data.education.license_details = "AWS Certified Solutions Architect Professional"
        else:
            input_data.education.professional_license = False
            
        if salary:
            input_data.experience.salary_level = "ABOVE_AVERAGE"
            input_data.experience.salary_percentile = 85
        else:
            input_data.experience.salary_level = "AVERAGE"
            input_data.experience.salary_percentile = 50
            
        if membership:
            input_data.recognition.professional_memberships = 3
        else:
            input_data.recognition.professional_memberships = 0
            
        if recognition:
            input_data.recognition.awards_count = 4
            input_data.recognition.peer_recognition = True
            input_data.recognition.government_recognition = True
        else:
            input_data.recognition.awards_count = 0
            input_data.recognition.peer_recognition = False
            input_data.recognition.government_recognition = False
            
        return input_data 