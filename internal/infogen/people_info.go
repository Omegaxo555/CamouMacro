// Package infogen genera perfiles de personas realistas para formularios de registro.
// Equivalente Go de modules/InfoGeneration/peopleInfo_generator.py.
package infogen

import (
	"fmt"
	"math/rand"
	"strings"
	"time"
	"unicode"

	"golang.org/x/text/transform"
	"golang.org/x/text/unicode/norm"
)

// Profile contiene la información de un perfil generado.
// Equivalente al dict retornado por PeopleInfoGenerator.generate_profile().
type Profile struct {
	Name          string
	Email         string
	Birthdate     string // formato MMDDYYYY
	Password      string
	Gender        string
	LookingFor    string
	TermsAccepted bool
}

// ──────────────────────────────────────────────────────────────────────────────
// Tablas de datos
// ──────────────────────────────────────────────────────────────────────────────

var maleNames = []string{
	"Noah", "Liam", "Lucas", "Mason", "Elijah", "James", "Henry", "Leo",
	"Theo", "Oliver", "Ethan", "Mateo", "Daniel", "Sebastian", "Jack",
	"Aiden", "Samuel", "Wyatt", "Julian", "Benjamin", "Hudson", "Asher",
	"Nathan", "Ezra", "Adrian", "Giovanni", "Oscar", "Marco", "Dylan",
	"Kai", "Javier", "Miguel", "Mateo", "Victor", "Diego", "Rafael", "Levi",
	"Santiago", "Nicolas", "Emiliano", "Alejandro", "Martin", "Felix", "Ian",
}

var femaleNames = []string{
	"Ava", "Mia", "Sophia", "Emma", "Olivia", "Charlotte", "Amelia", "Harper",
	"Evelyn", "Abigail", "Ella", "Scarlett", "Grace", "Lily", "Chloe", "Layla",
	"Nora", "Zoey", "Hannah", "Aria", "Luna", "Stella", "Aurora", "Hazel", "Violet",
	"Ruby", "Naomi", "Leah", "Savannah", "Penelope", "Alice", "Elena", "Bella",
	"Mila", "Ivy", "Ariana", "Jade", "Selena", "Rosa", "Cora", "Diana", "Freya",
	"Camila", "Valentina", "Natalia", "Lucia", "Marina", "Alina", "Clara", "Maya",
	"Isla", "Sofia", "Cecilia", "Anita",
}

var emailDomains = []string{
	"gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "icloud.com",
	"proton.me", "live.com", "mail.com",
}

// ──────────────────────────────────────────────────────────────────────────────
// Funciones públicas
// ──────────────────────────────────────────────────────────────────────────────

// GenerateMaleName elige un nombre masculino aleatorio.
func GenerateMaleName() string {
	return maleNames[rand.Intn(len(maleNames))]
}

// GenerateFemaleName elige un nombre femenino aleatorio.
func GenerateFemaleName() string {
	return femaleNames[rand.Intn(len(femaleNames))]
}

// GenerateEmail genera un email realista basado en el nombre dado.
// Si name es "", usa un nombre masculino aleatorio.
// Equivalente a PeopleInfoGenerator.generate_email().
func GenerateEmail(name, domain string) string {
	if name == "" {
		name = GenerateMaleName()
	}
	normalized := normalizeName(name)
	suffix := 10 + rand.Intn(990)
	if domain == "" {
		domain = emailDomains[rand.Intn(len(emailDomains))]
	}
	return fmt.Sprintf("%s%d@%s", normalized, suffix, domain)
}

// GenerateBirthdate genera una fecha de nacimiento aleatoria en formato MMDDYYYY.
// minAge y maxAge definen el rango de edades.
// Equivalente a PeopleInfoGenerator.generate_birthdate().
func GenerateBirthdate(minAge, maxAge int) string {
	if minAge > maxAge {
		minAge, maxAge = maxAge, minAge
	}
	now := time.Now()

	for range 2000 {
		year := now.Year() - maxAge + rand.Intn(maxAge-minAge+1)
		month := 1 + rand.Intn(12)
		dayMax := daysInMonth(month, year)
		day := 1 + rand.Intn(dayMax)

		// Calcular edad
		age := now.Year() - year
		if now.Month() < time.Month(month) || (now.Month() == time.Month(month) && now.Day() < day) {
			age--
		}
		if age >= minAge && age <= maxAge {
			return fmt.Sprintf("%02d%02d%04d", month, day, year)
		}
	}

	// Fallback
	return fmt.Sprintf("0101%04d", now.Year()-minAge)
}

// GeneratePassword genera una contraseña simple con prefijo y número aleatorio.
// Equivalente a PeopleInfoGenerator.generate_password().
func GeneratePassword(prefix string) string {
	if prefix == "" {
		prefix = "Pass"
	}
	return fmt.Sprintf("%s%d!", prefix, 1000+rand.Intn(9000))
}

// GenerateProfile genera un perfil completo de persona.
// Equivalente a PeopleInfoGenerator.generate_profile().
func GenerateProfile(name, domain string, minAge, maxAge int) Profile {
	if minAge == 0 {
		minAge = 25
	}
	if maxAge == 0 {
		maxAge = 70
	}
	if name == "" {
		name = GenerateMaleName()
	}
	return Profile{
		Name:          name,
		Email:         GenerateEmail(name, domain),
		Birthdate:     GenerateBirthdate(minAge, maxAge),
		Password:      GeneratePassword(""),
		Gender:        "male",
		LookingFor:    "female",
		TermsAccepted: true,
	}
}

// GenerateProfiles genera count perfiles.
// Equivalente a PeopleInfoGenerator.generate_profiles().
func GenerateProfiles(count int) []Profile {
	profiles := make([]Profile, count)
	for i := range profiles {
		profiles[i] = GenerateProfile("", "", 0, 0)
	}
	return profiles
}

// ──────────────────────────────────────────────────────────────────────────────
// Helpers internos
// ──────────────────────────────────────────────────────────────────────────────

// normalizeName convierte un nombre a minúsculas ASCII sin espacios ni acentos.
// Equivalente a PeopleInfoGenerator._normalize_name().
func normalizeName(name string) string {
	// Normalizar a NFD (descompone acentos) y filtrar diacríticos
	t := transform.Chain(norm.NFD, transform.RemoveFunc(func(r rune) bool {
		return unicode.Is(unicode.Mn, r) // elimina marcas de combinación (acentos)
	}), norm.NFC)
	result, _, _ := transform.String(t, name)
	result = strings.ToLower(result)
	result = strings.ReplaceAll(result, " ", "")
	// Mapeos adicionales
	replacer := strings.NewReplacer("ñ", "n", "ü", "u", "ç", "c")
	return replacer.Replace(result)
}

// daysInMonth devuelve los días del mes dado en el año dado.
func daysInMonth(month, year int) int {
	switch month {
	case 1, 3, 5, 7, 8, 10, 12:
		return 31
	case 4, 6, 9, 11:
		return 30
	case 2:
		if year%4 == 0 && (year%100 != 0 || year%400 == 0) {
			return 29
		}
		return 28
	}
	return 30
}
