from pydantic import BaseModel, ConfigDict


class FromDomainModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
