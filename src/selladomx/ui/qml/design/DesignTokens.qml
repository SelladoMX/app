// DesignTokens.qml - Design System Singleton
// Based on design_tokens.py and selladomx.com website styling
pragma Singleton
import QtQuick 2.15

QtObject {
    id: tokens

    // ========================================================================
    // COLORS - Professional Light Theme
    // ========================================================================

    // Background Colors
    readonly property color bgPrimary: "#FFFFFF"
    readonly property color bgSecondary: "#FAFAFA"
    readonly property color bgElevated: "#F5F5F5"
    readonly property color bgHover: "#EEEEEE"

    // Surface Colors
    readonly property color surfaceDefault: "#FFFFFF"
    readonly property color surfaceRaised: "#FAFAFA"
    readonly property color surfaceOverlay: "#F5F5F5"

    // Primary Accent (Professional Teal) - Main brand color
    readonly property color primary: "#14B8A6"           // Teal-500
    readonly property color primaryHover: "#0D9488"      // Teal-600
    readonly property color primaryActive: "#0F766E"     // Teal-700
    readonly property color primaryLight: "#0D9488"      // Teal-600
    readonly property color primarySubtle: "#F0FDFA"     // Teal-50

    // Text Colors
    readonly property color textPrimary: "#111827"       // Gray-900
    readonly property color textSecondary: "#6B7280"     // Gray-500
    readonly property color textTertiary: "#9CA3AF"      // Gray-400
    readonly property color textDisabled: "#D1D5DB"      // Gray-300

    // Border Colors
    readonly property color borderDefault: "#E5E7EB"     // Gray-200
    readonly property color borderStrong: "#D1D5DB"      // Gray-300
    readonly property color borderSubtle: "#F3F4F6"      // Gray-100

    // Semantic Colors
    readonly property color success: "#10B981"           // Green-500
    readonly property color successLight: "#F0FDF4"      // Green-50
    readonly property color successHover: "#059669"      // Green-600
    readonly property color successActive: "#047857"     // Green-700

    readonly property color warning: "#F59E0B"           // Amber-500
    readonly property color warningLight: "#FEF3C7"      // Amber-50
    readonly property color warningBorder: "#FDE68A"     // Amber-200
    readonly property color warningDark: "#78350F"       // Amber-900
    readonly property color warningHover: "#D97706"      // Amber-600

    readonly property color error: "#EF4444"             // Red-500
    readonly property color errorLight: "#FEF2F2"        // Red-50
    readonly property color errorHover: "#DC2626"        // Red-600
    readonly property color errorActive: "#B91C1C"       // Red-700

    readonly property color info: "#3B82F6"              // Blue-500
    readonly property color infoLight: "#EFF6FF"         // Blue-50
    readonly property color infoHover: "#2563EB"         // Blue-600

    // Step State Colors
    readonly property color stepPendingBg: "#FAFAFA"
    readonly property color stepPendingBorder: "#E5E7EB"
    readonly property color stepPendingText: "#9CA3AF"

    readonly property color stepActiveBg: "#F0FDFA"      // Teal-50
    readonly property color stepActiveBorder: "#14B8A6"  // Teal-500
    readonly property color stepActiveText: "#111827"

    readonly property color stepCompletedBg: "#F0FDF4"   // Green-50
    readonly property color stepCompletedBorder: "#10B981" // Green-500
    readonly property color stepCompletedText: "#111827"

    readonly property color stepDisabledBg: "#FAFAFA"
    readonly property color stepDisabledBorder: "#E5E7EB"
    readonly property color stepDisabledText: "#D1D5DB"

    // ========================================================================
    // SPACING - 8px Grid System
    // ========================================================================

    readonly property int xs: 4
    readonly property int sm: 8
    readonly property int md: 12
    readonly property int lg: 16
    readonly property int xl: 20
    readonly property int xxl: 24
    readonly property int xxxl: 32
    readonly property int huge: 40
    readonly property int massive: 48

    // ========================================================================
    // TYPOGRAPHY
    // ========================================================================

    // Font Sizes
    readonly property int fontXs: 11
    readonly property int fontSm: 12
    readonly property int fontBase: 14
    readonly property int fontMd: 15
    readonly property int fontLg: 16
    readonly property int fontXl: 18
    readonly property int font2xl: 20
    readonly property int font3xl: 24
    readonly property int font4xl: 32
    readonly property int font5xl: 48

    // Font Weights
    readonly property int weightNormal: Font.Normal    // 400
    readonly property int weightMedium: Font.Medium    // 500
    readonly property int weightSemiBold: Font.DemiBold // 600
    readonly property int weightBold: Font.Bold        // 700

    // Line Heights
    readonly property real lineHeightTight: 1.2
    readonly property real lineHeightNormal: 1.5
    readonly property real lineHeightRelaxed: 1.7

    // ========================================================================
    // BORDER RADIUS
    // ========================================================================

    readonly property int radiusSm: 4
    readonly property int radiusMd: 6
    readonly property int radiusLg: 8
    readonly property int radiusXl: 10
    readonly property int radiusXxl: 12
    readonly property int radiusXxxl: 16
    readonly property int radiusRound: 999

    // ========================================================================
    // COMPONENT SIZES
    // ========================================================================

    readonly property int buttonSm: 32
    readonly property int buttonMd: 36
    readonly property int buttonLg: 44
    readonly property int buttonXl: 50

    readonly property int inputDefault: 44
    readonly property int stepNumberSize: 56

    readonly property int iconSm: 16
    readonly property int iconMd: 20
    readonly property int iconLg: 24
    readonly property int iconXl: 32

    // ========================================================================
    // ANIMATION DURATIONS (milliseconds)
    // ========================================================================

    readonly property int durationFast: 150
    readonly property int durationNormal: 200
    readonly property int durationSlow: 300

    // ========================================================================
    // SHADOWS
    // ========================================================================

    readonly property color shadowColor: "#10000000"    // 10% black
    readonly property int shadowRadius: 8
    readonly property int shadowVerticalOffset: 4

    readonly property color shadowColorLight: "#08000000"  // 5% black
    readonly property int shadowRadiusLight: 4
    readonly property int shadowVerticalOffsetLight: 2

    // ========================================================================
    // OVERLAYS
    // ========================================================================

    readonly property color overlayDark: Qt.rgba(0, 0, 0, 0.1)
    readonly property color overlayLight: Qt.rgba(1, 1, 1, 0.6)

    // ========================================================================
    // BADGE/STATUS SIZES
    // ========================================================================

    readonly property int badgeSize: 56
    readonly property int statusDotSize: 14

    // ========================================================================
    // FONT FAMILIES
    // ========================================================================

    readonly property string fontFamilyMono: "Monaco, Courier New, monospace"
}
