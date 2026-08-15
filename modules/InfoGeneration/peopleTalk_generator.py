import random


class PeopleTalkGenerator:
    """Genera mensajes naturales, variados y coherentes para una conversación real."""

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
                "Well hello",
            ],
            "introductions": [
                "your profile caught my attention",
                "your vibe stood out to me",
                "I had to say hi after seeing your profile",
                "I was curious about you from your photos",
                "there is something really appealing about you",
                "your energy feels easy and attractive",
                "I liked the way you come across",
                "I couldn’t ignore how interesting you seem",
            ],
            "hooks": [
                "I’m usually drawn to people who have a warm, fun energy",
                "I like people who seem genuine and easy to talk to",
                "I’m always curious about what makes someone interesting in person",
                "I like the way your profile feels relaxed and confident",
                "I enjoy talking to people who seem fun and grounded",
                "I’ve been trying to meet someone with a good vibe lately",
                "I like conversations that feel natural instead of forced",
            ],
            "personal_details": [
                "I enjoy good conversations more than small talk",
                "I like people who can make a simple chat feel interesting",
                "I tend to enjoy people with a confident but easygoing energy",
                "I’m a big believer in good chemistry and natural conversation",
                "I usually appreciate someone who knows how to make a conversation flow",
                "I like meeting people who are both fun and thoughtful",
            ],
            "questions": [
                "What do you usually do when you want to relax?",
                "What kind of vibe do you usually go for in people?",
                "What’s something you’re really into lately?",
                "What would make a perfect weekend for you?",
                "What’s your idea of a really good conversation?",
                "What kind of people usually catch your attention?",
                "What do you enjoy most about meeting new people?",
                "What’s a place or activity that always makes you happy?",
            ],
            "closers": [
                "I’d love to hear more about you.",
                "I’m curious to know more.",
                "I’d be interested in hearing your take on that.",
                "I’d like to know more about that side of you.",
                "I think we could have a really good chat.",
            ],
        },
        "casual": {
            "openers": [
                "Hey",
                "Hi",
                "Hello",
                "Hey there",
                "Hi there",
                "What’s up",
                "Good to meet you",
            ],
            "introductions": [
                "your profile caught my eye",
                "your vibe felt really easygoing",
                "I had to say hello after seeing your profile",
                "I liked the overall energy you give off",
                "you looked like someone worth talking to",
                "I liked the way your profile felt natural",
                "there’s something about you that feels approachable",
                "you seem like someone with a fun personality",
            ],
            "hooks": [
                "I like people who seem genuine and easy to talk to",
                "I enjoy meeting people who have a relaxed, positive energy",
                "I always find it interesting to get to know people through conversation",
                "I like a chat that feels natural and not rehearsed",
                "I’m always curious about what kind of person someone is outside the obvious stuff",
                "I like how a real conversation can tell you a lot about someone",
            ],
            "personal_details": [
                "I’m usually someone who likes straightforward, easygoing conversations",
                "I enjoy talking to people who can make a simple chat feel fun",
                "I appreciate people with good energy and a sense of humor",
                "I like learning what makes people interesting in a real way",
                "I tend to enjoy people who are warm and easy to connect with",
            ],
            "questions": [
                "What’s something you really enjoy doing in your free time?",
                "What kind of people usually click with you?",
                "What makes you feel most relaxed?",
                "What’s a topic you could talk about for hours?",
                "What do you like doing on weekends?",
                "What kind of energy do you usually look for in someone?",
                "What’s something you’ve been getting into lately?",
                "What’s the best part of your week?",
            ],
            "closers": [
                "I’d like to hear more about you.",
                "I’d enjoy hearing your perspective.",
                "I think we could have a good chat.",
                "I’m curious to know more about that.",
                "I’d like to keep this conversation going.",
            ],
        },
        "premium": {
            "openers": [
                "Good evening",
                "Hello",
                "Hi",
                "It’s a pleasure to meet you",
                "You caught my attention",
            ],
            "introductions": [
                "your profile immediately stood out to me",
                "your presence feels very intriguing",
                "I had to reach out after seeing your profile",
                "I was drawn to the energy you give off",
                "there is something very memorable about your profile",
                "your profile feels polished and confident",
                "you seem like someone with a very interesting perspective",
                "you have a very attractive and refined presence",
            ],
            "hooks": [
                "I enjoy conversations with people who have depth and personality",
                "I appreciate people who can be both confident and easy to talk to",
                "I’m always attracted to someone with a strong sense of self",
                "I like a conversation that feels thoughtful and genuine",
                "I enjoy meeting people who have an interesting point of view",
                "I think chemistry often starts with a natural, easy conversation",
            ],
            "personal_details": [
                "I tend to be drawn to people who have a sense of charm and intelligence",
                "I enjoy talking to people who are both interesting and easy to connect with",
                "I usually appreciate people with great energy and a lot of personality",
                "I like conversations that go beyond the obvious and feel real",
                "I value people who seem thoughtful, confident, and warm",
            ],
            "questions": [
                "What makes you feel most like yourself?",
                "What kind of experiences usually stay with you?",
                "What’s a conversation topic you always enjoy?",
                "What do you value most in the people you connect with?",
                "What’s something that really excites you lately?",
                "What kind of energy do you look for in people?",
                "What do you enjoy most about spending time with someone you like?",
                "What do you think makes a person genuinely interesting?",
            ],
            "closers": [
                "I’d really like to hear more about that.",
                "I think this could turn into a great conversation.",
                "I’m curious to know more about your perspective.",
                "I’d enjoy learning more about that side of you.",
                "I’d love to keep talking and hear more.",
            ],
        },
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
        tone_data = cls.TONES[tone_key]

        opener = random.choice(tone_data["openers"])
        intro = random.choice(tone_data["introductions"])
        hook = random.choice(tone_data["hooks"])
        detail = random.choice(tone_data["personal_details"])
        question = random.choice(tone_data["questions"])
        closer = random.choice(tone_data["closers"])

        if name:
            sentence = (
                f"{opener} {name}, {intro}. {hook}. {detail}. "
                f"{question} {closer}"
            )
        else:
            sentence = (
                f"{opener}, {intro}. {hook}. {detail}. "
                f"{question} {closer}"
            )

        return sentence

    @classmethod
    def build_message_set(
        cls,
        count: int = 5,
        name: str | None = None,
        age: int | None = None,
        personality: str | None = None,
        tone: str = "flirty",
    ) -> list[str]:
        """Genera mensajes que encajan entre sí en una sola conversación."""
        tone_key = tone.lower() if tone.lower() in cls.TONES else "flirty"
        tone_data = cls.TONES[tone_key]

        messages: list[str] = []
        used_openers: set[str] = set()
        used_intros: set[str] = set()
        used_questions: set[str] = set()

        for _ in range(max(1, count)):
            opener = random.choice(tone_data["openers"])
            intro = random.choice(tone_data["introductions"])
            hook = random.choice(tone_data["hooks"])
            detail = random.choice(tone_data["personal_details"])
            question = random.choice(tone_data["questions"])
            closer = random.choice(tone_data["closers"])

            while opener in used_openers and len(used_openers) < len(tone_data["openers"]):
                opener = random.choice(tone_data["openers"])
            while intro in used_intros and len(used_intros) < len(tone_data["introductions"]):
                intro = random.choice(tone_data["introductions"])
            while question in used_questions and len(used_questions) < len(tone_data["questions"]):
                question = random.choice(tone_data["questions"])

            used_openers.add(opener)
            used_intros.add(intro)
            used_questions.add(question)

            if name:
                message = (
                    f"{opener} {name}, {intro}. {hook}. {detail}. "
                    f"{question} {closer}"
                )
            else:
                message = (
                    f"{opener}, {intro}. {hook}. {detail}. "
                    f"{question} {closer}"
                )
            messages.append(message)

        return messages

    @classmethod
    def build_message_batch(cls, count: int = 5, include_types: list[str] | None = None) -> dict[str, list[str]]:
        """Genera un lote con tipos de conversación: intro, opinion, question y closing."""
        include_types = include_types or ["intro", "story", "question", "follow_up"]
        result: dict[str, list[str]] = {message_type: [] for message_type in include_types}

        for message_type in include_types:
            for _ in range(max(1, count)):
                tone = random.choice(["flirty", "casual", "premium"])
                if message_type == "intro":
                    result[message_type].append(cls.build_message(tone=tone))
                elif message_type == "story":
                    result[message_type].append(cls.build_message(tone=tone))
                elif message_type == "question":
                    result[message_type].append(cls.build_message(tone=tone))
                else:
                    result[message_type].append(cls.build_message(tone=tone))

        return result


if __name__ == "__main__":
    generator = PeopleTalkGenerator()
    print(generator.build_message_set(5, name="Alicia", age=28, personality="sweet and witty", tone="flirty"))
