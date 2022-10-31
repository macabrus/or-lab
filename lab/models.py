from attr import field, define


@define(kw_only=True)
class Plant:
    id: int = None
    name: str
    petal_count: int
    lifespan_years: float
    soil_ph_min: float
    soil_ph_max: float
    temp_min: float
    temp_max: float
    is_edible: bool
    water_content: float


@define(kw_only=True)
class Genus:
    id: int = None
    name: str
    species: list[Plant] = field(factory=list)
