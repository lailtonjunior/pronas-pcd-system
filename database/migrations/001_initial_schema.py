# CRIAR: database/migrations/001_initial_schema.py
"""Initial schema migration

Revision ID: 001
Create Date: 2025-09-10
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Criar extensões PostgreSQL
    op.execute("CREATE EXTENSION IF NOT EXISTS 'uuid-ossp';")
    op.execute("CREATE EXTENSION IF NOT EXISTS 'pg_trgm';")
    
    # Tabela de usuários
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('role', sa.Enum('admin', 'manager', 'user', 'auditor', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_username', 'users', ['username'], unique=True)
    
    # Tabela de instituições
    op.create_table('institutions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cnpj', sa.String(18), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('legal_name', sa.String(255), nullable=False),
        sa.Column('institution_type', sa.Enum('hospital', 'apae', 'ong', 'fundacao', 'associacao', 'instituto', name='institutiontype'), nullable=False),
        sa.Column('cep', sa.String(9), nullable=False),
        sa.Column('address', sa.String(500), nullable=False),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('state', sa.String(2), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('legal_representative', sa.String(255), nullable=False),
        sa.Column('technical_responsible', sa.String(255), nullable=True),
        sa.Column('experience_proof', sa.Text(), nullable=True),
        sa.Column('credential_status', sa.Enum('pending', 'active', 'inactive', 'expired', 'rejected', name='credentialstatus'), default='pending'),
        sa.Column('credential_date', sa.DateTime(), nullable=True),
        sa.Column('credential_expiry', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_institutions_cnpj', 'institutions', ['cnpj'], unique=True)
    op.create_index('idx_institutions_status', 'institutions', ['credential_status'])
    
    # Tabela de áreas prioritárias
    op.create_table('priority_areas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(20), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requirements', postgresql.JSONB(), nullable=True),
        sa.Column('active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_priority_areas_code', 'priority_areas', ['code'], unique=True)
    
    # Inserir áreas prioritárias padrão
    op.execute("""
        INSERT INTO priority_areas (code, name, description, active) VALUES
        ('QSS', 'Qualificação de serviços de saúde', 'Adequação da ambiência de estabelecimentos de saúde', true),
        ('RPD', 'Reabilitação/habilitação da pessoa com deficiência', 'Ações de reabilitação e habilitação', true),
        ('DDP', 'Diagnóstico diferencial da pessoa com deficiência', 'Diagnóstico diferencial', true),
        ('EPD', 'Identificação e estimulação precoce das deficiências', 'Estimulação precoce 0-3 anos', true),
        ('ITR', 'Inserção e reinserção no trabalho', 'Adaptação e inserção no mercado de trabalho', true),
        ('APE', 'Apoio à saúde por meio de práticas esportivas', 'Atividades físicas e esportivas adaptadas', true),
        ('TAA', 'Terapia assistida por animais', 'TAA como complemento terapêutico', true),
        ('APC', 'Apoio à saúde por produção artística e cultural', 'Atividades artísticas e culturais', true);
    """)
    
    # Tabela de projetos
    op.create_table('projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('institution_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('field_of_action', sa.Enum('medico_assistencial', 'formacao', 'pesquisa', name='fieldofaction'), nullable=False),
        sa.Column('priority_area_id', sa.Integer(), nullable=False),
        sa.Column('general_objective', sa.Text(), nullable=False),
        sa.Column('specific_objectives', postgresql.JSONB(), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('target_audience', sa.Text(), nullable=True),
        sa.Column('methodology', sa.Text(), nullable=True),
        sa.Column('expected_results', sa.Text(), nullable=True),
        sa.Column('budget_total', sa.Numeric(12, 2), nullable=False),
        sa.Column('timeline_months', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('draft', 'submitted', 'under_review', 'approved', 'rejected', 'in_execution', 'completed', 'cancelled', name='projectstatus'), default='draft'),
        sa.Column('submission_date', sa.DateTime(), nullable=True),
        sa.Column('approval_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['priority_area_id'], ['priority_areas.id'])
    )
    op.create_index('idx_projects_institution', 'projects', ['institution_id'])
    op.create_index('idx_projects_status', 'projects', ['status'])

def downgrade():
    op.drop_table('projects')
    op.drop_table('priority_areas')
    op.drop_table('institutions')
    op.drop_table('users')
    op.execute("DROP TYPE IF EXISTS projectstatus;")
    op.execute("DROP TYPE IF EXISTS fieldofaction;")
    op.execute("DROP TYPE IF EXISTS credentialstatus;")
    op.execute("DROP TYPE IF EXISTS institutiontype;")
    op.execute("DROP TYPE IF EXISTS userrole;")