from enum import Enum

class UpdateResult(Enum):
    NEW_LISTING = "new_listing"
    PRICE_CHANGE = "price_change"
    NO_CHANGE = "no_change"