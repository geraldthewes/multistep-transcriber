from pydantic import BaseModel

class NounList(BaseModel):
    nouns: list[str]

class CorrectedText(BaseModel):
    corrected_text: str

class Speaker_Mapping(BaseModel):
    speaker_mapping: dict[str, str]
