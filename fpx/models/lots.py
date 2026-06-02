from dataclasses import dataclass, field


@dataclass
class CurrentLotInfo:
    short_desc: str
    description: str
    price: float

@dataclass
class LotEditor:
    csrf_token: str
    form_created_at: str
    offer_id: str
    node_id: str
    location: str
    deleted: str
    fields: dict = field(default_factory=dict)

@dataclass
class LotInfo:
    name: str
    id: str

@dataclass
class CategoryLastLot:
    category_id: str
    filtration: str
    price: float
    offer_id: str
    owner_username: str