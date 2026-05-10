from dataclasses import dataclass, field

@dataclass
class Balance:
    rub: float=0.0
    usd: float=0.0
    eur: float=0.0

@dataclass
class LotInfo:
    name: str
    id: str

@dataclass
class Profile:
    category_ids: list
    lots: list[LotInfo] = field(default_factory=list)

@dataclass
class UserData:
    csrf_token: str
    user_id: str

@dataclass
class Order:
    order_id: str
    order_time: str
    client_name: str
    price: float
    status: str
    name: str
    category: str