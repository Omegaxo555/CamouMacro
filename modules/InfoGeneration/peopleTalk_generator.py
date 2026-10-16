"""Generador de diálogos naturales, variados y adaptables para hombres y mujeres."""

import random


class PeopleTalkGenerator:
    """Genera mensajes naturales, variados y coherentes para una conversación real.

    Totalmente adaptable según el género objetivo (hombres / mujeres) y tono
    (flirty, casual, premium).
    """

    TONES_BY_GENDER = {
        "women": {
            "flirty": {
                "openers": [
                    "Hey", "Hi", "Hey there", "Hello", "Hi there",
                    "Good evening", "Hey gorgeous", "Well hello", "Hey beautiful",
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
                    "Hey", "Hi", "Hello", "Hey there", "Hi there",
                    "What’s up", "Good to meet you",
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
                    "Good evening", "Hello", "Hi",
                    "It’s a pleasure to meet you", "You caught my attention",
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
        },
        "men": {
            "flirty": {
                "openers": [
                    "Hey handsome", "Well hello handsome", "Hey good-looking",
                    "Hi handsome", "Hey there", "Hello", "Good evening",
                    "Well hello", "Hey",
                ],
                "introductions": [
                    "your profile definitely caught my eye",
                    "you looked really sharp and confident in your photos",
                    "your smile and your style stood out to me right away",
                    "I had to say hello after seeing your pictures",
                    "there’s something very charming and attractive about your vibe",
                    "you seem like a guy with great energy and charisma",
                    "I couldn't help but notice how interesting you seem",
                    "your photos give off a really confident, attractive energy",
                ],
                "hooks": [
                    "I’m usually drawn to a guy who is confident, driven and grounded",
                    "I appreciate a man who knows how to have a genuine conversation",
                    "I like someone with a sharp sense of humor and positive energy",
                    "I enjoy meeting someone who has genuine passion for what he does",
                    "I like conversations that feel natural, exciting and real",
                    "I’ve been hoping to connect with a man with great vibes lately",
                    "I like when someone is direct, charming and easy to talk to",
                ],
                "personal_details": [
                    "I enjoy good conversations much more than endless small talk",
                    "I tend to appreciate a man who is both ambitious and down to earth",
                    "I love good chemistry and spontaneous, fun chats",
                    "I value a man who carries himself with confidence and warmth",
                    "I’m someone who loves good laughs and meaningful connections",
                    "I usually appreciate someone who knows how to make a chat exciting",
                ],
                "questions": [
                    "What kind of things keep you busy and excited outside of work?",
                    "What’s your idea of an ideal weekend to recharge or have fun?",
                    "What kind of energy usually catches your attention in a woman?",
                    "What’s something you’re really passionate about lately?",
                    "What’s a topic you could easily talk about for hours?",
                    "Are you more of an adventurous type or do you prefer relaxing?",
                    "What do you enjoy most when getting to know someone new?",
                ],
                "closers": [
                    "I’d love to hear what you think.",
                    "I’m curious to get to know more about you.",
                    "I think we could have a great conversation.",
                    "I’d love to hear your take on that.",
                    "Looking forward to hearing from you.",
                ],
            },
            "casual": {
                "openers": [
                    "Hey", "Hi", "Hello", "Hey there", "Hi there",
                    "What’s up", "Good to meet you",
                ],
                "introductions": [
                    "your profile caught my eye",
                    "you seem to have a really cool, easygoing vibe",
                    "I liked the photos on your profile",
                    "you looked like an interesting guy to talk to",
                    "you seem like someone who’s fun and easy to chat with",
                    "I liked your style and your relaxed vibe",
                ],
                "hooks": [
                    "I like talking to guys who are genuine and easygoing",
                    "I enjoy meeting people who have a relaxed, positive outlook",
                    "I like a conversation that just flows without being complicated",
                    "I’m always curious to see what someone is like beyond just photos",
                ],
                "personal_details": [
                    "I’m pretty straightforward and enjoy a good, relaxed chat",
                    "I appreciate people with good energy and a quick sense of humor",
                    "I like learning what people are genuinely into",
                ],
                "questions": [
                    "What do you like to do when you have free time?",
                    "What’s something you’ve been getting into lately?",
                    "What was the highlight of your week so far?",
                    "What’s your favorite way to spend a Friday evening?",
                ],
                "closers": [
                    "I’d like to hear more about you.",
                    "I think we’d have a good chat.",
                    "Curious to hear your thoughts.",
                ],
            },
            "premium": {
                "openers": [
                    "Good evening", "Hello", "It’s a pleasure to connect with you",
                    "You caught my attention", "Hi",
                ],
                "introductions": [
                    "your profile carries a very distinguished and confident presence",
                    "you seem like a gentleman with depth and character",
                    "your presence stood out to me as someone truly intriguing",
                    "there is something very memorable and refined about your profile",
                ],
                "hooks": [
                    "I appreciate a man with ambition, intelligence, and a strong sense of purpose",
                    "I find myself drawn to people who have depth and self-assurance",
                    "I value thoughtful conversations that go beyond surface level",
                ],
                "personal_details": [
                    "I value intelligence, charm, and authenticity in a person",
                    "I enjoy conversations with someone who has an interesting point of view",
                    "I appreciate a person who is both successful and down to earth",
                ],
                "questions": [
                    "What drives you most in what you do?",
                    "What kind of qualities do you value most in people you connect with?",
                    "What has been one of your favorite experiences recently?",
                    "What’s a passion or goal you’re currently focused on?",
                ],
                "closers": [
                    "I’d truly enjoy learning more about your perspective.",
                    "I look forward to hearing your thoughts.",
                    "I think this could lead to an exceptional conversation.",
                ],
            },
        },
    }

    # Acceso retrocompatible directo para TONES["flirty"], etc.
    TONES = TONES_BY_GENDER["women"]

    @classmethod
    def normalize_target_gender(cls, target_gender: str | None) -> str:
        """Normaliza el género objetivo a 'women' o 'men'."""
        if not target_gender:
            return "women"
        g = str(target_gender).strip().lower()
        if g in ("men", "man", "male", "m", "hombre", "hombres"):
            return "men"
        return "women"

    @classmethod
    def _get_tone_data(cls, tone: str = "flirty", target_gender: str = "women") -> dict:
        norm_gender = cls.normalize_target_gender(target_gender)
        gender_tones = cls.TONES_BY_GENDER.get(norm_gender, cls.TONES_BY_GENDER["women"])
        tone_key = tone.lower() if tone.lower() in gender_tones else "flirty"
        return gender_tones[tone_key]

    @classmethod
    def build_message(
        cls,
        name: str | None = None,
        age: int | None = None,
        personality: str | None = None,
        tone: str = "flirty",
        target_gender: str = "women",
    ) -> str:
        """Construye un mensaje adaptado al género del objetivo (hombres / mujeres)."""
        tone_data = cls._get_tone_data(tone=tone, target_gender=target_gender)

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
        target_gender: str = "women",
    ) -> list[str]:
        """Genera un hilo natural de mensajes secuenciales adaptados al género del target."""
        tone_data = cls._get_tone_data(tone=tone, target_gender=target_gender)

        count = max(1, count)
        opener_pool = random.sample(tone_data["openers"], min(len(tone_data["openers"]), count))
        intro_pool = random.sample(tone_data["introductions"], min(len(tone_data["introductions"]), count))
        question_pool = random.sample(tone_data["questions"], min(len(tone_data["questions"]), count))

        messages: list[str] = []
        for idx in range(count):
            opener = opener_pool[idx % len(opener_pool)]
            intro = intro_pool[idx % len(intro_pool)]
            hook = random.choice(tone_data["hooks"])
            detail = random.choice(tone_data["personal_details"])
            question = question_pool[idx % len(question_pool)]
            closer = random.choice(tone_data["closers"])

            if idx == 0:
                body = (
                    f"{opener} {name}, {intro}. {hook}. {detail}. {question} {closer}"
                    if name else
                    f"{opener}, {intro}. {hook}. {detail}. {question} {closer}"
                )
            elif idx == 1:
                body = f"I noticed {intro.lower()}. {hook}. {detail}. {question} {closer}"
            elif idx == 2:
                body = f"{hook} {detail}. {question} {closer}"
            else:
                body = f"I’d like to keep this going. {detail}. {question} {closer}"

            messages.append(body.strip())

        return messages

    @classmethod
    def build_message_batch(
        cls,
        count: int = 5,
        include_types: list[str] | None = None,
        target_gender: str = "women",
    ) -> dict[str, list[str]]:
        """Genera un lote con tipos de conversación variados para el género dado."""
        include_types = include_types or ["intro", "story", "question", "follow_up"]
        result: dict[str, list[str]] = {message_type: [] for message_type in include_types}

        for message_type in include_types:
            for _ in range(max(1, count)):
                tone = random.choice(["flirty", "casual", "premium"])
                result[message_type].append(cls.build_message(tone=tone, target_gender=target_gender))

        return result


if __name__ == "__main__":
    generator = PeopleTalkGenerator()
    print("--- Diálogo para MUJERES (target=women) ---")
    print(generator.build_message_set(2, name="Alicia", target_gender="women", tone="flirty"))
    print("\n--- Diálogo para HOMBRES (target=men) ---")
    print(generator.build_message_set(2, name="Lucas", target_gender="men", tone="flirty"))
