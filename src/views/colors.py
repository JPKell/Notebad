from types import SimpleNamespace

Themes = SimpleNamespace(
    light = SimpleNamespace(
        # Text
        text_background = '#FBF6F1',
        text_foreground = '#28190E',
        cursor = "#379392",
        # UI elements
        background   = '#ECEBE4',
        bg_highlight = '#FBF6F1',
        foreground   = '#28190E',
        tab_select   = '#ECDBD4',
        tab_unselect = '#E5E0E8',
        scrollbar    = '#DFDBD4',
        # Syntax
        syn_grey   = '#586e75',
        syn_red    = '#dc322f',
        syn_orange = '#cb4b16',
        syn_yellow = '#b58900',
        syn_green  = '#859900',
        syn_cyan   = '#2aa198',
        syn_blue   = '#268bd2',
        syn_violet = '#6c71c4',
        syn_magenta = '#d33682',
    ),
    dark = SimpleNamespace(
        # Text
        text_background = '#242526',
        text_foreground = '#E1DEE9',
        cursor = "#B0DED9",
        # UI elements
        background   = '#202122',
        bg_highlight = '#28292A',
        foreground   = '#E1DEE9',
        tab_select   = '#38292A',
        tab_unselect = '#32323A',
        scrollbar    = '#2E292A',
        # Syntax
        syn_grey   = '#93a1a1',
        syn_red    = '#dc322f',
        syn_orange = '#cb4b16',
        syn_yellow = '#b58900',
        syn_green  = '#859900',
        syn_cyan   = '#2aa198',
        syn_blue   = '#268bd2',
        syn_violet = '#6c71c4',
        syn_magenta = '#d33682',
    ),
)
