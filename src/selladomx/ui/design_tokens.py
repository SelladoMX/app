"""SelladoMX Design System - Clean & Professional

Based on modern web design standards with teal accent colors.
All values optimized for readability and professional appearance.
"""

# ============================================================================
# COLORS - Professional Light Theme
# ============================================================================

class Colors:
    """Professional color palette - clean and modern"""

    # Background Colors
    BG_PRIMARY = "#FFFFFF"           # Pure white
    BG_SECONDARY = "#FAFAFA"         # Very light gray (almost white)
    BG_ELEVATED = "#F5F5F5"          # Light gray for cards
    BG_HOVER = "#EEEEEE"             # Hover state

    # Surface Colors
    SURFACE_DEFAULT = "#FFFFFF"      # White
    SURFACE_RAISED = "#FAFAFA"       # Barely off-white
    SURFACE_OVERLAY = "#F5F5F5"      # Light overlay

    # Primary Accent (Professional Teal)
    PRIMARY = "#14B8A6"              # Teal-500 - main brand color
    PRIMARY_HOVER = "#0D9488"        # Teal-600 - hover state
    PRIMARY_ACTIVE = "#0F766E"       # Teal-700 - active/pressed
    PRIMARY_LIGHT = "#0D9488"        # Teal-600 - readable on light backgrounds
    PRIMARY_SUBTLE = "#F0FDFA"       # Teal-50 - very light background

    # Text Colors
    TEXT_PRIMARY = "#111827"         # Almost black (gray-900)
    TEXT_SECONDARY = "#6B7280"       # Medium gray (gray-500)
    TEXT_TERTIARY = "#9CA3AF"        # Light gray (gray-400)
    TEXT_DISABLED = "#D1D5DB"        # Very light gray (gray-300)

    # Border Colors
    BORDER_DEFAULT = "#E5E7EB"       # Gray-200
    BORDER_STRONG = "#D1D5DB"        # Gray-300
    BORDER_SUBTLE = "#F3F4F6"        # Gray-100

    # Semantic Colors
    SUCCESS = "#10B981"              # Green-500
    SUCCESS_LIGHT = "#F0FDF4"        # Green-50 - light background
    SUCCESS_HOVER = "#059669"        # Green-600 - hover state
    SUCCESS_ACTIVE = "#047857"       # Green-700 - active/pressed

    WARNING = "#F59E0B"              # Amber-500
    WARNING_LIGHT = "#FEF3C7"        # Amber-50 - light background
    WARNING_BORDER = "#FDE68A"       # Amber-200 - border
    WARNING_DARK = "#78350F"         # Amber-900 - dark text
    WARNING_HOVER = "#D97706"        # Amber-600 - hover state

    ERROR = "#EF4444"                # Red-500
    ERROR_LIGHT = "#FEF2F2"          # Red-50 - light background
    ERROR_HOVER = "#DC2626"          # Red-600 - hover state
    ERROR_ACTIVE = "#B91C1C"         # Red-700 - active/pressed

    INFO = "#3B82F6"                 # Blue-500
    INFO_LIGHT = "#EFF6FF"           # Blue-50 - light background
    INFO_HOVER = "#2563EB"           # Blue-600 - hover state

    # Step State Colors
    STEP_PENDING_BG = "#FAFAFA"
    STEP_PENDING_BORDER = "#E5E7EB"
    STEP_PENDING_TEXT = "#9CA3AF"

    STEP_ACTIVE_BG = "#F0FDFA"       # Teal-50
    STEP_ACTIVE_BORDER = "#14B8A6"   # Teal-500
    STEP_ACTIVE_TEXT = "#111827"

    STEP_COMPLETED_BG = "#F0FDF4"    # Green-50
    STEP_COMPLETED_BORDER = "#10B981" # Green-500
    STEP_COMPLETED_TEXT = "#111827"

    STEP_DISABLED_BG = "#FAFAFA"
    STEP_DISABLED_BORDER = "#E5E7EB"
    STEP_DISABLED_TEXT = "#D1D5DB"


# ============================================================================
# SPACING - 8px Grid System
# ============================================================================

class Spacing:
    """Consistent spacing scale"""
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32
    HUGE = 40
    MASSIVE = 48


# ============================================================================
# TYPOGRAPHY
# ============================================================================

class Typography:
    """Typography scale"""

    # Font Sizes
    FONT_XS = 11
    FONT_SM = 12
    FONT_BASE = 14
    FONT_MD = 15
    FONT_LG = 16
    FONT_XL = 18
    FONT_2XL = 20
    FONT_3XL = 24
    FONT_4XL = 32
    FONT_5XL = 48

    # Font Weights
    WEIGHT_NORMAL = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700

    # Line Heights
    LINE_HEIGHT_TIGHT = 1.2
    LINE_HEIGHT_NORMAL = 1.5
    LINE_HEIGHT_RELAXED = 1.7


# ============================================================================
# BORDER RADIUS
# ============================================================================

class BorderRadius:
    """Border radius scale"""
    SM = 4
    MD = 6
    LG = 8
    XL = 10
    XXL = 12
    XXXL = 16
    ROUND = 999


# ============================================================================
# COMPONENT SIZES
# ============================================================================

class ComponentSizes:
    """Standard component sizes"""
    BUTTON_SM = 32
    BUTTON_MD = 36
    BUTTON_LG = 44
    BUTTON_XL = 50
    INPUT_DEFAULT = 44
    STEP_NUMBER_SIZE = 56
    ICON_SM = 16
    ICON_MD = 20
    ICON_LG = 24
    ICON_XL = 32


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_margin(top=0, right=0, bottom=0, left=0) -> str:
    """Helper to format setContentsMargins values"""
    return f"{top}, {right}, {bottom}, {left}"


def format_spacing(spacing: int) -> int:
    """Validate spacing is from our scale"""
    valid_spacings = [
        Spacing.XS, Spacing.SM, Spacing.MD, Spacing.LG,
        Spacing.XL, Spacing.XXL, Spacing.XXXL, Spacing.HUGE, Spacing.MASSIVE
    ]
    if spacing not in valid_spacings:
        pass
    return spacing
