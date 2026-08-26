// Package infogen genera mensajes de conversación naturales y variados.
// Equivalente Go de modules/InfoGeneration/peopleTalk_generator.py.
package infogen

import (
	"fmt"
	"math/rand"
)

// Tone representa un tono de conversación con sus plantillas de texto.
type Tone struct {
	Openers        []string
	Introductions  []string
	Hooks          []string
	PersonalDetails []string
	Questions      []string
	Closers        []string
}

// tones contiene los tres tonos disponibles: flirty, casual, premium.
// Equivalente a PeopleTalkGenerator.TONES.
var tones = map[string]Tone{
	"flirty": {
		Openers: []string{
			"Hey", "Hi", "Hey there", "Hello", "Hi there",
			"Good evening", "Hey gorgeous", "Well hello",
		},
		Introductions: []string{
			"your profile caught my attention",
			"your vibe stood out to me",
			"I had to say hi after seeing your profile",
			"I was curious about you from your photos",
			"there is something really appealing about you",
			"your energy feels easy and attractive",
			"I liked the way you come across",
			"I couldn't ignore how interesting you seem",
		},
		Hooks: []string{
			"I'm usually drawn to people who have a warm, fun energy",
			"I like people who seem genuine and easy to talk to",
			"I'm always curious about what makes someone interesting in person",
			"I like the way your profile feels relaxed and confident",
			"I enjoy talking to people who seem fun and grounded",
			"I've been trying to meet someone with a good vibe lately",
			"I like conversations that feel natural instead of forced",
		},
		PersonalDetails: []string{
			"I enjoy good conversations more than small talk",
			"I like people who can make a simple chat feel interesting",
			"I tend to enjoy people with a confident but easygoing energy",
			"I'm a big believer in good chemistry and natural conversation",
			"I usually appreciate someone who knows how to make a conversation flow",
			"I like meeting people who are both fun and thoughtful",
		},
		Questions: []string{
			"What do you usually do when you want to relax?",
			"What kind of vibe do you usually go for in people?",
			"What's something you're really into lately?",
			"What would make a perfect weekend for you?",
			"What's your idea of a really good conversation?",
			"What kind of people usually catch your attention?",
			"What do you enjoy most about meeting new people?",
			"What's a place or activity that always makes you happy?",
		},
		Closers: []string{
			"I'd love to hear more about you.",
			"I'm curious to know more.",
			"I'd be interested in hearing your take on that.",
			"I'd like to know more about that side of you.",
			"I think we could have a really good chat.",
		},
	},
	"casual": {
		Openers: []string{
			"Hey", "Hi", "Hello", "Hey there", "Hi there",
			"What's up", "Good to meet you",
		},
		Introductions: []string{
			"your profile caught my eye",
			"your vibe felt really easygoing",
			"I had to say hello after seeing your profile",
			"I liked the overall energy you give off",
			"you looked like someone worth talking to",
			"I liked the way your profile felt natural",
			"there's something about you that feels approachable",
			"you seem like someone with a fun personality",
		},
		Hooks: []string{
			"I like people who seem genuine and easy to talk to",
			"I enjoy meeting people who have a relaxed, positive energy",
			"I always find it interesting to get to know people through conversation",
			"I like a chat that feels natural and not rehearsed",
			"I'm always curious about what kind of person someone is outside the obvious stuff",
			"I like how a real conversation can tell you a lot about someone",
		},
		PersonalDetails: []string{
			"I'm usually someone who likes straightforward, easygoing conversations",
			"I enjoy talking to people who can make a simple chat feel fun",
			"I appreciate people with good energy and a sense of humor",
			"I like learning what makes people interesting in a real way",
			"I tend to enjoy people who are warm and easy to connect with",
		},
		Questions: []string{
			"What's something you really enjoy doing in your free time?",
			"What kind of people usually click with you?",
			"What makes you feel most relaxed?",
			"What's a topic you could talk about for hours?",
			"What do you like doing on weekends?",
			"What kind of energy do you usually look for in someone?",
			"What's something you've been getting into lately?",
			"What's the best part of your week?",
		},
		Closers: []string{
			"I'd like to hear more about you.",
			"I'd enjoy hearing your perspective.",
			"I think we could have a good chat.",
			"I'm curious to know more about that.",
			"I'd like to keep this conversation going.",
		},
	},
	"premium": {
		Openers: []string{
			"Good evening", "Hello", "Hi",
			"It's a pleasure to meet you", "You caught my attention",
		},
		Introductions: []string{
			"your profile immediately stood out to me",
			"your presence feels very intriguing",
			"I had to reach out after seeing your profile",
			"I was drawn to the energy you give off",
			"there is something very memorable about your profile",
			"your profile feels polished and confident",
			"you seem like someone with a very interesting perspective",
			"you have a very attractive and refined presence",
		},
		Hooks: []string{
			"I enjoy conversations with people who have depth and personality",
			"I appreciate people who can be both confident and easy to talk to",
			"I'm always attracted to someone with a strong sense of self",
			"I like a conversation that feels thoughtful and genuine",
			"I enjoy meeting people who have an interesting point of view",
			"I think chemistry often starts with a natural, easy conversation",
		},
		PersonalDetails: []string{
			"I tend to be drawn to people who have a sense of charm and intelligence",
			"I enjoy talking to people who are both interesting and easy to connect with",
			"I usually appreciate people with great energy and a lot of personality",
			"I like conversations that go beyond the obvious and feel real",
			"I value people who seem thoughtful, confident, and warm",
		},
		Questions: []string{
			"What makes you feel most like yourself?",
			"What kind of experiences usually stay with you?",
			"What's a conversation topic you always enjoy?",
			"What do you value most in the people you connect with?",
			"What's something that really excites you lately?",
			"What kind of energy do you look for in people?",
			"What do you enjoy most about spending time with someone you like?",
			"What do you think makes a person genuinely interesting?",
		},
		Closers: []string{
			"I'd really like to hear more about that.",
			"I think this could turn into a great conversation.",
			"I'm curious to know more about your perspective.",
			"I'd enjoy learning more about that side of you.",
			"I'd love to keep talking and hear more.",
		},
	},
}

// pickOne selecciona un elemento aleatorio de un slice de strings.
func pickOne(items []string) string {
	if len(items) == 0 {
		return ""
	}
	return items[rand.Intn(len(items))]
}

// BuildMessage genera un mensaje único con el tono dado.
// Equivalente a PeopleTalkGenerator.build_message().
func BuildMessage(name string, tone string) string {
	t, ok := tones[tone]
	if !ok {
		t = tones["flirty"]
	}

	opener := pickOne(t.Openers)
	intro := pickOne(t.Introductions)
	hook := pickOne(t.Hooks)
	detail := pickOne(t.PersonalDetails)
	question := pickOne(t.Questions)
	closer := pickOne(t.Closers)

	if name != "" {
		return fmt.Sprintf("%s %s, %s. %s. %s. %s %s", opener, name, intro, hook, detail, question, closer)
	}
	return fmt.Sprintf("%s, %s. %s. %s. %s %s", opener, intro, hook, detail, question, closer)
}

// BuildMessageSet genera un hilo de count mensajes variados sin repetir saludo/intro.
// Equivalente a PeopleTalkGenerator.build_message_set().
func BuildMessageSet(count int, name, tone string) []string {
	if count < 1 {
		count = 1
	}
	t, ok := tones[tone]
	if !ok {
		t = tones["flirty"]
	}

	// Mezclar pools
	openerPool := shuffledSlice(t.Openers)
	introPool := shuffledSlice(t.Introductions)
	questionPool := shuffledSlice(t.Questions)

	messages := make([]string, 0, count)
	for idx := range count {
		opener := openerPool[idx%len(openerPool)]
		intro := introPool[idx%len(introPool)]
		hook := pickOne(t.Hooks)
		detail := pickOne(t.PersonalDetails)
		question := questionPool[idx%len(questionPool)]
		closer := pickOne(t.Closers)

		var body string
		switch idx {
		case 0:
			if name != "" {
				body = fmt.Sprintf("%s %s, %s. %s. %s. %s %s", opener, name, intro, hook, detail, question, closer)
			} else {
				body = fmt.Sprintf("%s, %s. %s. %s. %s %s", opener, intro, hook, detail, question, closer)
			}
		case 1:
			body = fmt.Sprintf("I noticed %s. %s. %s. %s %s", intro, hook, detail, question, closer)
		case 2:
			body = fmt.Sprintf("%s %s. %s %s", hook, detail, question, closer)
		default:
			body = fmt.Sprintf("I'd like to keep this going. %s. %s %s", detail, question, closer)
		}
		messages = append(messages, body)
	}
	return messages
}

// RandomTone devuelve un tono aleatorio entre los disponibles.
func RandomTone() string {
	keys := make([]string, 0, len(tones))
	for k := range tones {
		keys = append(keys, k)
	}
	return keys[rand.Intn(len(keys))]
}

// shuffledSlice devuelve una copia mezclada del slice.
func shuffledSlice(s []string) []string {
	cp := make([]string, len(s))
	copy(cp, s)
	rand.Shuffle(len(cp), func(i, j int) { cp[i], cp[j] = cp[j], cp[i] })
	return cp
}
