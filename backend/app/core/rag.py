import logging
from typing import List, Tuple
from uuid import UUID
from sqlmodel import select, Session
from sqlalchemy import text as sa_text
from app.models import ContractChunk, PolicyChunk
from app.llm import get_llm_client
from app.database import get_session

logger = logging.getLogger(__name__)

class RAGService:
    """
    Service for Handling Retrieval Augmented Generation (RAG) operations.
    
    Responsibilities:
    1. Chunking text content.
    2. Generating embeddings via LLM service.
    3. Storing vectors in Postgres (pgvector).
    4. Retrieving relevant chunks by semantic similarity.
    """

    def __init__(self):
        self.llm = get_llm_client()

    def _split_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Simple recursive character splitting strategy.
        
        Args:
            text (str): Input text.
            chunk_size (int): Target characters per chunk.
            overlap (int): Overlap characters.
        
        Returns:
            List[str]: List of text chunks.
        """
        if not text:
            return []
            
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += (chunk_size - overlap)
        return chunks

    async def ingest_contract(self, session: Session, contract_id: UUID, content: str):
        """
        Process a contract text: split, embed, and store chunks.

        Args:
            session: DB Session.
            contract_id: UUID of the parent contract.
            content: Full text of the contract.
        """
        # 1. Split
        chunks = self._split_text(content)
        logger.info(f"Splitting contract {contract_id} into {len(chunks)} chunks.")

        # 2. Embed & Store
        for i, chunk_text in enumerate(chunks):
            try:
                embedding = await self.llm.generate_embedding(chunk_text)
                
                db_chunk = ContractChunk(
                    contract_id=contract_id,
                    chunk_index=i,
                    content=chunk_text,
                    embedding=embedding
                )
                session.add(db_chunk)
                
            except Exception as e:
                logger.error(f"Failed to embed chunk {i} for contract {contract_id}: {e}")
                # Continue processing other chunks? Or fail hard? 
                # For robust ingestion, we might want to fail hard or implement retry.
                raise e
        
        await session.commit()

    async def search(self, session: Session, query: str, limit: int = 5) -> List[ContractChunk]:
        """
        Semantic search for contract chunks.

        Args:
            session: DB Session.
            query: User question or search phrase.
            limit: Number of results.

        Returns:
            List[ContractChunk]: Relevant chunks.
        """
        # 1. Embed Query
        query_embedding = await self.llm.generate_embedding(query)

        # 2. Search via pgvector (L2 distance via <-> operator)
        # Note: SQLModel doesn't native support vector ops easily in pythonic select yet, 
        # usually requires `order_by(ContractChunk.embedding.l2_distance(query_embedding))`
        
        stmt = select(ContractChunk).order_by(
            ContractChunk.embedding.l2_distance(query_embedding)
        ).limit(limit)
        
        results = await session.exec(stmt)
        return results.all()

    async def ingest_policy(self, session: Session, policy_id: UUID, content: str):
        """
        Process a policy text: split, embed, and store chunks.
        """
        chunks = self._split_text(content)
        logger.info(f"Splitting policy {policy_id} into {len(chunks)} chunks.")

        for i, chunk_text in enumerate(chunks):
            try:
                embedding = await self.llm.generate_embedding(chunk_text)
                db_chunk = PolicyChunk(
                    policy_id=policy_id,
                    chunk_index=i,
                    content=chunk_text,
                    embedding=embedding
                )
                session.add(db_chunk)
            except Exception as e:
                logger.error(f"Failed to embed chunk {i} for policy {policy_id}: {e}")
                raise e
        
        await session.commit()

    async def search_policies(self, session: Session, query: str, limit: int = 5) -> List[PolicyChunk]:
        """
        Semantic search for policy chunks.
        """
        query_embedding = await self.llm.generate_embedding(query)
        
        stmt = select(PolicyChunk).order_by(
            PolicyChunk.embedding.l2_distance(query_embedding)
        ).limit(limit)
        
        results = await session.exec(stmt)
        return results.all()
