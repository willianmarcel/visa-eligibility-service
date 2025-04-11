#!/usr/bin/env python3
"""
Script para executar todos os testes do serviço de elegibilidade.
Inclui testes unitários e de integração.
"""

import subprocess
import sys
import os

def print_header(message):
    """Imprime cabeçalho formatado para mensagens."""
    line = "-" * 80
    print(f"\n{line}")
    print(f" {message}")
    print(f"{line}\n")

def run_tests():
    """Executa todos os testes e retorna o status de sucesso."""
    tests_passed = True
    
    # Definir variáveis de ambiente para teste
    test_env = os.environ.copy()
    test_env["TESTING"] = "True"
    test_env["DATABASE_URL"] = "sqlite:///./test.db"
    
    try:
        # Testes unitários
        print_header("Executando testes do EB2 Route Evaluator")
        result = subprocess.run(["pytest", "-xvs", "tests/services/test_eb2_route_evaluator.py"], env=test_env)
        tests_passed = tests_passed and result.returncode == 0
        
        print_header("Executando testes do NIW Evaluator")
        result = subprocess.run(["pytest", "-xvs", "tests/services/test_niw_evaluator.py"], env=test_env)
        tests_passed = tests_passed and result.returncode == 0
        
        print_header("Executando testes do Recommendation Engine")
        result = subprocess.run(["pytest", "-xvs", "tests/services/test_recommendation_engine.py"], env=test_env)
        tests_passed = tests_passed and result.returncode == 0
        
        print_header("Executando testes do Scoring Engine")
        result = subprocess.run(["pytest", "-xvs", "tests/services/test_scoring_engine.py"], env=test_env)
        tests_passed = tests_passed and result.returncode == 0
        
        # Testes de integração
        print_header("Executando testes de integração")
        result = subprocess.run(["pytest", "-xvs", "tests/services/test_eligibility_integration.py"], env=test_env)
        tests_passed = tests_passed and result.returncode == 0
        
        # Testes de migração
        print_header("Executando testes de migração")
        result = subprocess.run(["pytest", "-xvs", "tests/db/test_migration_add_detailed_recommendations.py"], env=test_env)
        tests_passed = tests_passed and result.returncode == 0
        
        # Relatório de cobertura
        print_header("Gerando relatório de cobertura de código")
        result = subprocess.run([
            "pytest", "--cov=app.services", "--cov-report=term", "--cov-report=html:coverage_report",
            "tests/"
        ], env=test_env)
        tests_passed = tests_passed and result.returncode == 0
        
        if tests_passed:
            print_header("Todos os testes foram executados com sucesso!")
        else:
            print_header("Alguns testes falharam. Verifique os logs acima.")
        
        return tests_passed
    
    except Exception as e:
        print(f"Erro ao executar os testes: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 