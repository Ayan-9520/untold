"""pgvector extension and vector_store_documents table."""

from typing import Sequence, Union

from alembic import op

revision: str = "027_vector_store_pgvector"
down_revision: Union[str, None] = "026_ai_publishing_agent"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS vector_store_documents (
            id SERIAL PRIMARY KEY,
            collection VARCHAR(128) NOT NULL,
            document_id VARCHAR(128) NOT NULL,
            content TEXT NOT NULL,
            embedding vector(384) NOT NULL,
            metadata JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(collection, document_id)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_vector_store_documents_collection "
        "ON vector_store_documents (collection)"
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_vector_store_documents_embedding_hnsw
        ON vector_store_documents
        USING hnsw (embedding vector_cosine_ops)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_vector_store_documents_embedding_hnsw")
    op.execute("DROP INDEX IF EXISTS ix_vector_store_documents_collection")
    op.execute("DROP TABLE IF EXISTS vector_store_documents")
