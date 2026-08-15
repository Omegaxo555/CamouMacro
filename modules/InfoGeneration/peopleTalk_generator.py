import random


class PeopleTalkGenerator:
    """Genera mensajes naturales, variados y coherentes en inglés para perfiles reales."""

    TONES = {
        "flirty": {
            "openers": [
                "Hey",
                "Hi",
                "Hey there",
                "Hello",
                "Hi there",
                "Good evening",
                "Hey gorgeous",
                "Hey cutie",
                "Hi beautiful",
                "Well hello",
            ],
            "introductions": [
                "I was checking your profile and I had to say something",
                "Your profile really caught my attention",
                "I couldn’t help but notice you",
                "I saw your profile and I had to say hi",
                "I like the vibe you give off",
                "Your photos instantly stood out to me",
                "You seem really interesting from your profile",
                "There’s something about you that feels really attractive",
            ],
            "compliments": [
                "your smile is incredibly charming",
                "your energy feels really warm and fun",
                "you have a really beautiful presence",
                "your vibe is so easy and attractive",
                "you seem genuinely sweet and interesting",
                "your style looks really good",
                "you have a very confident and attractive aura",
                "you seem like someone I would enjoy talking to",
                "your profile feels very refreshing",
                "you look really kind and fun",
            ],
            "flirty_lines": [
                "I think we’d have a great conversation",
                "I like your vibe more than I expected",
                "You seem really easy to talk to",
                "I feel like we’d get along pretty well",
                "There’s something intriguing about you",
                "You have a really attractive energy",
                "I like the way you come across",
                "You seem like someone I’d be interested in knowing better",
                "You look like a lot of fun",
                "There’s a certain charm about you",
            ],
            "closers": [
                "want to chat a little more?",
                "want to keep this conversation going?",
                "want to get to know each other a bit more?",
                "would you be up for a quick chat?",
                "do you want to talk a little more?",
                "want to see where this goes?",
                "interested in talking a bit more?",
                "would you like to continue the conversation?",
                "want to flirt a little with me?",
                "want to share a few thoughts with me?",
            ]
        },
        "casual": {
            "openers": [
                "Hey",
                "Hi",
                "Hey there",
                "Hello",
                "Hi there",
                "What’s up",
                "Hey you",
                "Morning",
                "Good to meet you",
                "Hey handsome",
            ],
            "introductions": [
                "I noticed your profile and wanted to say hi",
                "Your profile stood out to me",
                "I saw your profile and it caught my attention",
                "I thought I’d say hello",
                "You seem really interesting from your profile",
                "I had to reach out because you seem cool",
                "Your vibe looks really good",
                "You looked like someone worth talking to",
            ],
            "compliments": [
                "you seem really easy to talk to",
                "you have a great sense of style",
                "your smile looks super genuine",
                "you seem fun and down to earth",
                "you have a really nice energy",
                "you look like a great person to know",
                "you seem really interesting and kind",
                "your profile feels very authentic",
                "you seem warm and approachable",
                "you have a really good vibe",
            ],
            "flirty_lines": [
                "I like the way you come across",
                "You seem like a lot of fun",
                "I think we could have a good chat",
                "I like your energy",
                "You seem really pleasant to talk to",
                "There’s something refreshing about you",
                "You have a really attractive personality",
                "I feel like we’d get along well",
                "Your vibe is definitely interesting",
                "You seem like someone worth getting to know",
            ],
            "closers": [
                "want to chat sometime?",
                "want to talk a little more?",
                "want to keep this conversation going?",
                "up for a quick conversation?",
                "want to get to know each other a bit?",
                "want to continue chatting?",
                "want to exchange a few words more?",
                "want to see if we click?",
                "interested in talking a bit more?",
                "would be nice to hear from you?",
            ]
        },
        "premium": {
            "openers": [
                "Good evening",
                "Hello",
                "Hi",
                "It’s a pleasure to meet you",
                "How are you doing",
                "You caught my attention",
                "Good to see you",
                "I hope you’re doing well",
                "I’ve been meaning to say hi",
                "You seem quite remarkable",
            ],
            "introductions": [
                "I came across your profile and I had to reach out",
                "Your profile immediately stood out to me",
                "I was drawn to your presence and wanted to say hello",
                "Your elegance and energy are hard to ignore",
                "You seem like someone with a very interesting personality",
                "I couldn’t ignore the impression you gave me",
                "Your profile has a very refined and attractive vibe",
                "You seem genuinely impressive",
            ],
            "compliments": [
                "your presence feels effortlessly elegant",
                "your profile gives off a very polished and confident energy",
                "you seem incredibly classy and intriguing",
                "your smile is very captivating",
                "you have a very refined and attractive style",
                "you seem thoughtful and genuinely lovely",
                "you carry a very charming energy",
                "your look is undeniably impressive",
                "you seem very mature and magnetic",
                "you have an elegant and memorable presence",
            ],
            "flirty_lines": [
                "I feel like we could have an excellent conversation",
                "You have a very captivating aura",
                "There’s something truly memorable about you",
                "I think we’d get along very well",
                "You seem like someone with a lot of depth",
                "Your energy is both attractive and interesting",
                "You seem genuinely special",
                "There’s a lot I’d like to learn about you",
                "You have a very compelling presence",
                "I think you’d be a very interesting person to know",
            ],
            "closers": [
                "would you be open to a more interesting conversation?",
                "want to continue this conversation sometime?",
                "would you like to get to know each other better?",
                "want to talk a little more and see where it goes?",
                "interested in hearing more from you?",
                "would you be open to a nice chat?",
                "want to explore a little more of each other?",
                "want to continue a conversation with someone interesting?",
                "want to share a little more with me?",
                "would you enjoy a more personal conversation?",
            ]
        }
    }

    @staticmethod
    def _pick_unique(items: list[str], count: int) -> list[str]:
        if count <= 0:
            return []
        if len(items) <= count:
            return random.sample(items, len(items))
        return random.sample(items, count)

    @classmethod
    def _build_profile_context(cls, name: str | None = None, age: int | None = None, personality: str | None = None) -> str:
        details = []
        if name:
            details.append(f"{name}")
        if age:
            details.append(f"{age} years old")
        if personality:
            details.append(personality)
        return ", ".join(details) if details else "you"

    @classmethod
    def build_message(cls, name: str | None = None, age: int | None = None, personality: str | None = None, tone: str = "flirty") -> str:
        tone_key = tone.lower() if tone.lower() in cls.TONES else "flirty"
        pool = cls.TONES[tone_key]

        opener = random.choice(pool["openers"])
        intro = random.choice(pool["introductions"])
        compliment = random.choice(pool["compliments"])
        flirty_line = random.choice(pool["flirty_lines"])
        closer = random.choice(pool["closers"])

        profile_context = cls._build_profile_context(name, age, personality)
        open_text = f"{opener}, {intro}."
        if name:
            open_text = f"{opener} {name}, {intro}."

        return f"{open_text} {compliment}. {flirty_line}. {closer}"

    @classmethod
    def build_message_set(
        cls,
        count: int = 5,
        name: str | None = None,
        age: int | None = None,
        personality: str | None = None,
        tone: str = "flirty",
    ) -> list[str]:
        """Genera una lista de mensajes sin repetir partes clave del mensaje."""
        tone_key = tone.lower() if tone.lower() in cls.TONES else "flirty"
        pool = cls.TONES[tone_key]

        messages: list[str] = []
        used_openers: set[str] = set()
        used_intros: set[str] = set()
        used_compliments: set[str] = set()
        used_flirty: set[str] = set()
        used_closers: set[str] = set()

        for _ in range(max(1, count)):
            opener = random.choice(pool["openers"])
            intro = random.choice(pool["introductions"])
            compliment = random.choice(pool["compliments"])
            flirty_line = random.choice(pool["flirty_lines"])
            closer = random.choice(pool["closers"])

            while opener in used_openers and len(used_openers) < len(pool["openers"]):
                opener = random.choice(pool["openers"])
            while intro in used_intros and len(used_intros) < len(pool["introductions"]):
                intro = random.choice(pool["introductions"])
            while compliment in used_compliments and len(used_compliments) < len(pool["compliments"]):
                compliment = random.choice(pool["compliments"])
            while flirty_line in used_flirty and len(used_flirty) < len(pool["flirty_lines"]):
                flirty_line = random.choice(pool["flirty_lines"])
            while closer in used_closers and len(used_closers) < len(pool["closers"]):
                closer = random.choice(pool["closers"])

            used_openers.add(opener)
            used_intros.add(intro)
            used_compliments.add(compliment)
            used_flirty.add(flirty_line)
            used_closers.add(closer)

            subject = cls._build_profile_context(name, age, personality)
            sentence = f"{opener}, {intro}. {compliment}. {flirty_line}. {closer}"
            if name:
                sentence = f"{opener} {name}, {intro}. {compliment}. {flirty_line}. {closer}"
            messages.append(sentence)

        return messages

    @classmethod
    def build_message_batch(cls, count: int = 5, include_types: list[str] | None = None) -> dict[str, list[str]]:
        """Genera mensajes separados por tipo: introduction, compliment, closing, etc."""
        include_types = include_types or ["presentation", "compliment", "flirty", "invitation"]
        result: dict[str, list[str]] = {}

        for message_type in include_types:
            result[message_type] = []

        for message_type in include_types:
            for _ in range(max(1, count)):
                if message_type == "presentation":
                    result[message_type].append(cls.build_message(tone=random.choice(["flirty", "casual", "premium"])))
                elif message_type == "compliment":
                    result[message_type].append(cls.build_message(tone=random.choice(["flirty", "casual", "premium"])))
                elif message_type == "flirty":
                    result[message_type].append(cls.build_message(tone=random.choice(["flirty", "casual", "premium"])))
                else:
                    result[message_type].append(cls.build_message(tone=random.choice(["flirty", "casual", "premium"])))

        return result


if __name__ == "__main__":
    generator = PeopleTalkGenerator()
    print(generator.build_message_set(5, name="Alicia", age=28, personality="sweet and witty", tone="flirty"))
    print(generator.build_message_batch(3, include_types=["presentation", "compliment", "flirty", "invitation"]))
