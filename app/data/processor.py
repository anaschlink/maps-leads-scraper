import re

class DataProcessor:

    REQUIRED_FIELDS = ["name", "address"]

    def validate_required_fields(self, data: dict):
        for field in self.REQUIRED_FIELDS:
            if not data.get(field):
                raise ValueError(f"Missing required field: {field}")

    def normalize_text(self, text: str):
        if not text:
            return None
        return text.strip()

    def normalize_rating(self, rating):
        if not rating:
            return None
        return float(rating.replace(",", "."))

    def normalize_phone(self, phone: str):
        if not phone:
            return None
        return re.sub(r"\D", "", phone)

    def normalize_address(self, address: str):
        if not address:
            return None
        return address.strip()

    def split_address(self, address: str):
        if not address:
            return None, None
        parts = address.split(",")
        return parts[0].strip(), parts[-1].strip()
