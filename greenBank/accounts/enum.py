from enum import Enum

class CardType(Enum):
    Visa = "visa"
    MasterCard = "masterCard"
    
class CardCurrencyType(Enum):
    AMD = "AMD"
    RUR = "RUB"
    EUR = "EUR"
    USD = "USD"
    
class AccountType(Enum):
    Current = "current"
    Saving = "saving"

class QRType(Enum):
    QR_card = "QR-card"
    QR_account = "QR-account"

class TransverType(Enum):
    Phone = "phone"
    Account = "account"
    Card = "card"
    QR_card = "QR-card"
    QR_account = "QR-account"