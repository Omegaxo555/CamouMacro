"""Generador de perfiles de usuario adaptables para masculino y femenino."""

import random
from datetime import datetime


class PeopleInfoGenerator:
    """Genera perfiles realistas para formularios de dating o registro, adaptables por género."""

    MALE_NAMES = [
        "Noah", "Liam", "Lucas", "Mason", "Elijah", "James", "Henry", "Leo",
        "Theo", "Oliver", "Ethan", "Mateo", "Daniel", "Sebastian", "Jack",
        "Aiden", "Samuel", "Wyatt", "Julian", "Benjamin", "Hudson", "Asher",
        "Nathan", "Ezra", "Adrian", "Giovanni", "Oscar", "Marco", "Dylan",
        "Kai", "Javier", "Miguel", "Victor", "Diego", "Rafael", "Levi",
        "Santiago", "Nicolas", "Emiliano", "Alejandro", "Martin", "Felix", "Ian",
        "Carlos", "Gabriel", "David", "Christian", "Alex", "Marcus", "Thomas",
        "Aaron", "Abel", "Abraham", "Adam", "Alan", "Albert", "Amir", "Andrew",
        "Angel", "Anthony", "Antonio", "Arlo", "Arthur", "Ashton", "Austin", "Axel",
        "Beau", "Blake", "Brandon", "Brayden", "Brian", "Brody", "Caleb", "Calvin",
        "Cameron", "Carter", "Charles", "Chase", "Christopher", "Cole", "Colin",
        "Connor", "Cooper", "Damian", "Darius", "Dominic", "Elias", "Evan", "George",
        "Graham", "Isaac", "Isaiah", "Jaxon", "Jeremiah", "Enzo", "Francisco", "Hugo",
        "Ivan", "Jason", "Jose"
    ]

    FEMALE_NAMES = [
        "Ava", "Mia", "Sophia", "Emma", "Olivia", "Charlotte", "Amelia", "Harper",
        "Evelyn", "Abigail", "Ella", "Scarlett", "Grace", "Lily", "Chloe", "Layla",
        "Nora", "Zoey", "Hannah", "Aria", "Luna", "Stella", "Aurora", "Hazel", "Violet",
        "Ruby", "Naomi", "Leah", "Savannah", "Penelope", "Alice", "Elena", "Bella",
        "Mila", "Ivy", "Ariana", "Jade", "Selena", "Rosa", "Cora", "Diana", "Freya",
        "Camila", "Valentina", "Natalia", "Lucía", "Marina", "Alina", "Clara", "Maya",
        "Isla", "Sofia", "Cecilia", "Anita", "Carmen", "Julia", "Eva", "Laura",
        "Adeline", "Adriana", "Aisha", "Alexandra", "Alexis", "Alyssa", "Amara",
        "Andrea", "Angela", "Annabelle", "Ashley", "Athena", "Audrey", "Autumn",
        "Beatrice", "Bianca", "Brooke", "Carolina", "Catalina", "Celeste", "Daisy",
        "Daniela", "Delilah", "Emilia", "Esme", "Estella", "Gabriella", "Georgia",
        "Gianna", "Giselle", "Isabel", "Jasmine", "Josephine", "Juliette", "Kiara",
        "Liliana", "Lola", "Madeline", "Maeve", "Melanie", "Nina", "Noelle", "Phoebe",
        "Serena", "Sophie", "Talia", "Alana", "Ana", "Ariella", "Blair"
    ]

    DOMAINS = [
        "gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "icloud.com",
        "proton.me", "live.com", "mail.com"
    ]

    def __init__(self, seed: int | None = None):
        if seed is not None:
            random.seed(seed)

    @staticmethod
    def _random_date(min_age: int = 25, max_age: int = 70) -> str:
        today = datetime.today()

        if min_age > max_age:
            min_age, max_age = max_age, min_age

        for _ in range(2000):
            year = random.randint(today.year - max_age, today.year - min_age)
            month = random.randint(1, 12)

            if month in (1, 3, 5, 7, 8, 10, 12):
                day_max = 31
            elif month == 2:
                day_max = 29 if year % 4 == 0 else 28
            else:
                day_max = 30

            day = random.randint(1, day_max)
            candidate = f"{month:02d}{day:02d}{year:04d}"

            age = today.year - year - ((today.month, today.day) < (month, day))
            if min_age <= age <= max_age:
                return candidate

        return f"0101{today.year - min_age:04d}"

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
    def normalize_gender(cls, gender: str | None, default: str = "male") -> str:
        """Normaliza el género a 'male' o 'female'."""
        if not gender:
            return default
        g = str(gender).strip().lower()
        if g in ("female", "women", "woman", "f", "mujer", "mujeres", "femenina", "femenino"):
            return "female"
        if g in ("male", "men", "man", "m", "hombre", "hombres", "masculino"):
            return "male"
        if g == "random":
            return random.choice(["male", "female"])
        return default

    @classmethod
    def generate_male_name(cls) -> str:
        return random.choice(cls.MALE_NAMES)

    @classmethod
    def generate_female_name(cls) -> str:
        return random.choice(cls.FEMALE_NAMES)

    @classmethod
    def generate_name(cls, gender: str = "random") -> str:
        """Genera un nombre según el género especificado ('male', 'female', 'random')."""
        norm = cls.normalize_gender(gender, default="random")
        if norm == "female":
            return cls.generate_female_name()
        if norm == "male":
            return cls.generate_male_name()
        return random.choice([cls.generate_male_name(), cls.generate_female_name()])

    @classmethod
    def generate_email(cls, name: str | None = None, domain: str | None = None, gender: str = "male") -> str:
        selected_name = name or cls.generate_name(gender=gender)
        normalized = cls._normalize_name(selected_name)
        suffix = random.randint(10, 999)
        selected_domain = domain or random.choice(cls.DOMAINS)
        return f"{normalized}{suffix}@{selected_domain}"

    @classmethod
    def generate_birthdate(cls, min_age: int = 25, max_age: int = 70) -> str:
        return cls._random_date(min_age=min_age, max_age=max_age)

    @classmethod
    def generate_password(cls, prefix: str = "Pass") -> str:
        number = random.randint(1000, 9999)
        return f"{prefix}{number}!"

    @classmethod
    def generate_profile(
        cls,
        name: str | None = None,
        domain: str | None = None,
        min_age: int = 25,
        max_age: int = 70,
        gender: str = "male",
        looking_for: str | None = None,
    ) -> dict:
        """Genera un perfil completo y adaptable para hombre o mujer.

        Args:
            name: Nombre opcional personalizado. Si no se indica, se genera según el género.
            domain: Dominio de email opcional.
            min_age: Edad mínima.
            max_age: Edad máxima.
            gender: 'male', 'female', 'men', 'women' o 'random'.
            looking_for: 'female', 'male', 'women', 'men' o None (se auto-asigna el opuesto).
        """
        norm_gender = cls.normalize_gender(gender, default="male")

        if looking_for:
            norm_looking_for = cls.normalize_gender(looking_for, default="female" if norm_gender == "male" else "male")
        else:
            norm_looking_for = "female" if norm_gender == "male" else "male"

        selected_name = name or cls.generate_name(gender=norm_gender)

        return {
            "name": selected_name,
            "email": cls.generate_email(selected_name, domain, gender=norm_gender),
            "birthdate": cls.generate_birthdate(min_age=min_age, max_age=max_age),
            "password": cls.generate_password(),
            "gender": norm_gender,
            "looking_for": norm_looking_for,
            "terms_accepted": True,
        }

    @classmethod
    def generate_profiles(cls, count: int = 10, gender: str = "male", looking_for: str | None = None) -> list[dict]:
        return [cls.generate_profile(gender=gender, looking_for=looking_for) for _ in range(count)]

    @classmethod
    def build_allfeellove_payload(cls, count: int = 1, gender: str = "male", looking_for: str | None = None) -> list[dict]:
        payload = []
        for _ in range(count):
            item = cls.generate_profile(gender=gender, looking_for=looking_for)
            payload.append({
                "name": item["name"],
                "email": item["email"],
                "password": item["password"],
                "birthdate": item["birthdate"],
                "gender": item["gender"],
                "looking_for": item["looking_for"],
                "terms_accepted": True,
            })
        return payload


if __name__ == "__main__":
    generator = PeopleInfoGenerator()
    print("Perfil masculino:", generator.generate_profile(gender="male"))
    print("Perfil femenino:", generator.generate_profile(gender="female"))
