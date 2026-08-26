package ui

import (
	"image/color"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/theme"
)

// DarkCustomTheme tema personalizado oscuro y moderno para CamouMacro.
type DarkCustomTheme struct{}

var _ fyne.Theme = (*DarkCustomTheme)(nil)

func (m *DarkCustomTheme) Color(name fyne.ThemeColorName, variant fyne.ThemeVariant) color.Color {
	switch name {
	case theme.ColorNameBackground:
		return color.NRGBA{R: 15, G: 17, B: 23, A: 255} // #0f1117
	case theme.ColorNameInputBackground:
		return color.NRGBA{R: 26, G: 29, B: 39, A: 255} // #1a1d27
	case theme.ColorNameOverlayBackground:
		return color.NRGBA{R: 34, G: 38, B: 58, A: 255} // #22263a
	case theme.ColorNamePrimary:
		return color.NRGBA{R: 124, G: 106, B: 247, A: 255} // #7c6af7 (Accent)
	case theme.ColorNameFocus:
		return color.NRGBA{R: 157, G: 144, B: 255, A: 255} // #9d90ff
	case theme.ColorNameForeground:
		return color.NRGBA{R: 226, G: 232, B: 240, A: 255} // #e2e8f0
	case theme.ColorNameForegroundOnError:
		return color.NRGBA{R: 255, G: 255, B: 255, A: 255}
	case theme.ColorNameError:
		return color.NRGBA{R: 248, G: 113, B: 113, A: 255} // #f87171
	case theme.ColorNameSuccess:
		return color.NRGBA{R: 52, G: 211, B: 153, A: 255} // #34d399
	case theme.ColorNameWarning:
		return color.NRGBA{R: 251, G: 191, B: 36, A: 255} // #fbbf24
	case theme.ColorNameButton:
		return color.NRGBA{R: 34, G: 38, B: 58, A: 255}
	case theme.ColorNameDisabled:
		return color.NRGBA{R: 74, G: 85, B: 104, A: 255}
	default:
		return theme.DefaultTheme().Color(name, theme.VariantDark)
	}
}

func (m *DarkCustomTheme) Font(style fyne.TextStyle) fyne.Resource {
	return theme.DefaultTheme().Font(style)
}

func (m *DarkCustomTheme) Icon(name fyne.ThemeIconName) fyne.Resource {
	return theme.DefaultTheme().Icon(name)
}

func (m *DarkCustomTheme) Size(name fyne.ThemeSizeName) float32 {
	switch name {
	case theme.SizeNameText:
		return 13
	case theme.SizeNameHeadingText:
		return 20
	case theme.SizeNameSubHeadingText:
		return 16
	case theme.SizeNamePadding:
		return 8
	case theme.SizeNameInputRadius:
		return 6
	default:
		return theme.DefaultTheme().Size(name)
	}
}
