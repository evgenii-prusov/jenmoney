from pydantic import BaseModel, ConfigDict


class BaseAPIModel(BaseModel):
    """Base model with shared configuration for all API models."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        from_attributes=True,
        use_enum_values=True,
    )
