#!/usr/bin/env python3

import logging
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar engine SQLite em memória
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    echo=True
)

# Criar base para modelos
Base = declarative_base()

# Definir modelo de teste
class TestModel(Base):
    __tablename__ = 'test_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))

# Criar tabelas
Base.metadata.create_all(engine)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def test_sqlite():
    """Teste de funcionamento do SQLite em memória"""
    try:
        # Criar registro
        logger.info("Inserindo dados de teste...")
        db.add(TestModel(name="Test Entry"))
        db.commit()
        
        # Consultar registro
        logger.info("Consultando dados inseridos...")
        result = db.query(TestModel).first()
        
        if result and result.name == "Test Entry":
            logger.info(f"✅ Registro encontrado com ID: {result.id}, Nome: {result.name}")
        else:
            logger.error("❌ Não foi possível recuperar o registro")
            return False
            
        # Executar consulta direta
        logger.info("Executando consulta direta...")
        count_result = db.execute(text("SELECT COUNT(*) as count FROM test_table")).fetchone()
        logger.info(f"Contagem de registros: {count_result.count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("=== TESTANDO SQLITE EM MEMÓRIA COMO FALLBACK ===")
    
    success = test_sqlite()
    
    if success:
        print("\n✅ SUCESSO: SQLite em memória funcionando corretamente como fallback!")
    else:
        print("\n❌ FALHA: Problemas com o SQLite em memória!") 