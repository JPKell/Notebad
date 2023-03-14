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
        # Syntax
        syn_red    = '#9E0031',
        syn_orange = '#CC3F0C',
        syn_yellow = '#E4A511',
        syn_green  = '#04724D',
        syn_cyan   = '#379392',
        syn_blue   = '#1D70A2',
        syn_purple = '#573280',
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
        # Syntax
        syn_red    = '#E26D5C',
        syn_orange = '#DC851F',
        syn_yellow = '#FAF2A1',
        syn_green  = '#C3EB78',
        syn_cyan   = '#80DED9',
        syn_blue   = '#3066BE',
        syn_purple = '#665FAB',
    ),
)
