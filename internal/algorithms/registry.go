// Package algorithms define el registro de algoritmos disponibles en CamouMacro.
// Equivalente Go de la lista ALGORITHMS[] en main.py.
package algorithms

import (
	"github.com/omegaxo555/camoumacro/internal/browser"
)

// Algorithm representa un algoritmo ejecutable con un ID, etiqueta y handler.
type Algorithm struct {
	ID      string
	Label   string
	Handler func(driver *browser.Handler) error
}

// Registry contiene todos los algoritmos disponibles.
// Para registrar un nuevo algoritmo, agrégalo a esta lista.
var Registry []Algorithm

// Register añade un algoritmo al registry.
func Register(a Algorithm) {
	Registry = append(Registry, a)
}

// FindByID busca un algoritmo por su ID. Devuelve nil si no existe.
func FindByID(id string) *Algorithm {
	for i := range Registry {
		if Registry[i].ID == id {
			return &Registry[i]
		}
	}
	return nil
}

// Labels devuelve los labels de todos los algoritmos registrados.
func Labels() []string {
	labels := make([]string, len(Registry))
	for i, a := range Registry {
		labels[i] = a.Label
	}
	return labels
}
