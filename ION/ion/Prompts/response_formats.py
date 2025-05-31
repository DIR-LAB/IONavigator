from pydantic import BaseModel, Field

class RAGDiagnosis(BaseModel):
    diagnosis: str = Field(description="A detailed description of the I/O performance issues (if any) indicated by the summary information and sources")
    sources: list[int] = Field(description="A list of source IDs from the sources provided")


