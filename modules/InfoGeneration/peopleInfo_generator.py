import random
from datetime import datetime, timedelta


class PeopleInfoGenerator:
    """Genera perfiles realistas para formularios de dating o registro."""

    MALE_NAMES = [
        "Noah", "Liam", "Lucas", "Mason", "Elijah", "James", "Henry", "Leo",
        "Theo", "Oliver", "Ethan", "Mateo", "Daniel", "Sebastian", "Jack",
        "Aiden", "Samuel", "Wyatt", "Julian", "Benjamin", "Hudson", "Asher",
        "Nathan", "Ezra", "Adrian", "Giovanni", "Oscar", "Marco", "Dylan",
        "Kai", "Javier", "Miguel", "Mateo", "Victor", "Diego", "Rafael", "Levi",
        "Santiago", "Nicolas", "Emiliano", "Alejandro", "Martin", "Felix", "Ian"
    ]

    FEMALE_NAMES = [
        "Ava", "Mia", "Sophia", "Emma", "Olivia", "Charlotte", "Amelia", "Harper",
        "Evelyn", "Abigail", "Ella", "Scarlett", "Grace", "Lily", "Chloe", "Layla",
        "Nora", "Zoey", "Hannah", "Aria", "Luna", "Stella", "Aurora", "Hazel", "Violet",
        "Ruby", "Naomi", "Leah", "Savannah", "Penelope", "Alice", "Elena", "Bella",
        "Mila", "Ivy", "Ariana", "Jade", "Selena", "Rosa", "Cora", "Diana", "Freya",
        "Camila", "Valentina", "Natalia", "Lucía", "Marina", "Alina", "Clara", "Maya",
        "Isla", "Sofia", "Cecilia", "Anita"
    ]

    DOMAINS = [
        "gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "icloud.com",
        "proton.me", "live.com", "mail.com"
    ]

    def __init__(self, seed: int | None = None):
        if seed is not None:
            random.seed(seed)

    @staticmethod
    def _random_date(min_age: int = 25, max_age: int = 65) -> str:
        today = datetime.today()
        min_date = today - timedelta(days=(max_age * 365.25))
        max_date = today - timedelta(days=(min_age * 365.25))
        random_day = random.randint(int(min_date.timestamp()), int(max_date.timestamp()))
        return datetime.fromtimestamp(random_day).strftime("%Y-%m-%d")

    @staticmethod
    def _normalize_name(name: str) -> str:
        return (
            name.lower()
            .replace(" ", "")
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
            .replace("ñ", "n")
            .replace("ü", "u")
        )

    @classmethod
    def generate_name(cls) -> str:
        return random.choice(cls.MALE_NAMES)

    @classmethod
    def generate_female_name(cls) -> str:
        return random.choice(cls.FEMALE_NAMES)

    @classmethod
    def generate_email(cls, name: str | None = None, domain: str | None = None) -> str:
        selected_name = name or cls.generate_name()
        normalized = cls._normalize_name(selected_name)
        suffix = random.randint(10, 999)
        selected_domain = domain or random.choice(cls.DOMAINS)
        return f"{normalized}{suffix}@{selected_domain}"

    @classmethod
    def generate_birthdate(cls, min_age: int = 18, max_age: int = 40) -> str:
        return cls._random_date(min_age=min_age, max_age=max_age)

    @classmethod
    def generate_password(cls, prefix: str = "Pass") -> str:
        number = random.randint(1000, 9999)
        return f"{prefix}{number}!"

    @classmethod
    def generate_profile(cls, name: str | None = None, domain: str | None = None) -> dict:
        selected_name = name or cls.generate_name()
        return {
            "name": selected_name,
            "email": cls.generate_email(selected_name, domain),
            "birthdate": cls.generate_birthdate(),
            "password": cls.generate_password(),
            "gender": "male",
            "looking_for": "female",
            "terms_accepted": True,
        }

    @classmethod
    def generate_profiles(cls, count: int = 10) -> list[dict]:
        return [cls.generate_profile() for _ in range(count)]

    @classmethod
    def build_allfeellove_payload(cls, count: int = 1) -> list[dict]:
        payload = []
        for _ in range(count):
            item = cls.generate_profile()
            payload.append({
                "name": item["name"],
                "email": item["email"],
                "password": item["password"],
                "birthdate": item["birthdate"],
                "gender": "male",
                "looking_for": "female",
                "terms_accepted": True,
            })
        return payload


if __name__ == "__main__":
    generator = PeopleInfoGenerator()
    print(generator.generate_profile())
    print(generator.build_allfeellove_payload(3))



