"""
Shared UI Constants, Styles, and Layout Helpers
"""

# Color Palette (Tailwind-inspired)
COLORS = {
    "bg-dark": "#121212",
    "bg-surface": "#1e1e1e",
    "bg-sidebar": "#1a1a1a",
    "border": "#333333",
    "text-dim": "#9ca3af",
    "text-main": "#d1d5db",
    "text-bright": "#ffffff",
    "primary": "#3b82f6",
    "primary-dark": "#2563eb",
    "success": "#4ade80",
    "success-dark": "#22c55e",
    "danger": "#ef4444",
    "danger-dark": "#dc2626",
    "warning": "#facc15",
    "warning-dark": "#eab308",
}

# Common Stylesheets
STYLES = {
    "panel": f"""
        background-color: {COLORS['bg-surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
    """,
    "header": f"""
        background-color: {COLORS['bg-surface']};
        border-bottom: 1px solid {COLORS['border']};
    """,
    "sidebar": f"""
        background-color: {COLORS['bg-sidebar']};
        border-right: 1px solid {COLORS['border']};
    """,
    "title": f"""
        color: {COLORS['text-main']};
        font-weight: 600;
        font-size: 14px;
        border: none;
    """,
    "button-primary": f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: {COLORS['text-bright']};
            border: none;
            border-radius: 4px;
            padding: 6px;
            font-size: 11px;
            font-weight: 700;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary-dark']};
        }}
    """,
    "button-success": f"""
        QPushButton {{
            background-color: {COLORS['success']};
            color: {COLORS['text-bright']};
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {COLORS['success-dark']};
        }}
    """,
    "button-danger": f"""
        QPushButton {{
            background-color: {COLORS['danger']};
            color: {COLORS['text-bright']};
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {COLORS['danger-dark']};
        }}
    """,
}


def apply_style(widget, style_key):
    """Apply a predefined style to a widget."""
    if style_key in STYLES:
        widget.setStyleSheet(STYLES[style_key])


def create_hbox_layout(margins=(0, 0, 0, 0), spacing=0):
    """Create a QHBoxLayout with common defaults."""
    from PySide6.QtWidgets import QHBoxLayout

    layout = QHBoxLayout()
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return layout


def create_vbox_layout(margins=(0, 0, 0, 0), spacing=0):
    """Create a QVBoxLayout with common defaults."""
    from PySide6.QtWidgets import QVBoxLayout

    layout = QVBoxLayout()
    layout.setContentsMargins(*margins)
    layout.setSpacing(spacing)
    return layout
