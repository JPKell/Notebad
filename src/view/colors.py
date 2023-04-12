from types import SimpleNamespace

Themes = SimpleNamespace(
    light = SimpleNamespace(
        # Text
        text_background = '#F9F6F1',
        text_foreground = '#28190E',
        cursor = "#379392",
        # UI elements
        background   = '#FFFFFF',
        bg_highlight = '#FCFCFC',
        foreground   = '#28190E',
        tab_select   = '#ECDBD4',
        tab_unselect = '#E5E0E8',
        scrollbar    = '#DFDBD4',
        # Syntax
        syn_error    = '#ff0000',
        syn_grey     = '#586e75',
        syn_red      = '#dc322f',
        syn_orange   = '#cb4b16',
        syn_yellow   = '#b58900',
        syn_green    = '#859900',
        syn_cyan     = '#2aa198',
        syn_blue     = '#268bd2',
        syn_alt_blue = '#167bc2',
        syn_violet   = '#6c71c4',
        syn_magenta  = '#d33682',
        syn_highlight = '#dc322f',
        syn_highlight_bg = '#FCFCFC',
    ),
    dark = SimpleNamespace(
        # Text
        text_background = '#242526',
        text_foreground = '#E1DEE9',
        cursor = "#B0DED9",
        # UI elements
        background   = '#313131',
        bg_highlight = '#313131',
        foreground   = '#E1DEE9',
        tab_select   = '#38292A',
        tab_unselect = '#32323A',
        scrollbar    = '#2E292A',
        # Syntax
        syn_error    = '#ff0000',
        syn_grey     = '#a3b1b1',
        syn_red      = '#ec423f',
        syn_orange   = '#db5b26',
        syn_yellow   = '#c59910',
        syn_green    = '#95a910',
        syn_cyan     = '#3ab1a8',
        syn_blue     = '#369be2',
        syn_alt_blue = '#C0FDFB',
        syn_violet   = '#7c81d4',
        syn_magenta  = '#e34692',
        syn_highlight = '#ec423f',
        syn_highlight_bg = '#626262',
    ),
)
