from attr import define, field, fields, make_class


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


skip_fields = {"id"}
CreatePlant = make_class(
    "CreatePlant",
    {"genus_id": field(default=None)}
    | {
        f.name: field(default=None)
        for f in fields(Plant)
        if f.name not in skip_fields
    },
)

UpdatePlant = make_class(
    "UpdatePlant",
    {"genus_id": field(default=None)}
    | {
        f.name: field(default=None)
        for f in fields(Plant)
        if f.name not in skip_fields
    },
)


@define(kw_only=True)
class Genus:
    id: int = None
    name: str
    species: list[Plant] = field(factory=list)
