// ModernButton.qml - Modern button component with animations
import QtQuick 2.15
import QtQuick.Controls 2.15
import "../design"

Button {
    id: control

    // Custom properties
    property string variant: "primary"  // primary, secondary, success, danger
    property bool loading: false
    property bool fullWidth: false

    // Sizing
    implicitWidth: fullWidth ? parent.width : Math.max(120, contentItem.implicitWidth + leftPadding + rightPadding)
    implicitHeight: DesignTokens.buttonLg

    leftPadding: DesignTokens.lg
    rightPadding: DesignTokens.lg
    topPadding: 0
    bottomPadding: 0

    // Cursor
    hoverEnabled: true

    // Scale animation on press
    scale: pressed ? 0.97 : 1.0
    Behavior on scale {
        NumberAnimation {
            duration: DesignTokens.durationFast
            easing.type: Easing.OutQuad
        }
    }

    // Content
    contentItem: Item {
        implicitWidth: row.implicitWidth
        implicitHeight: row.implicitHeight

        Row {
            id: row
            anchors.centerIn: parent
            spacing: DesignTokens.sm

            // Loading indicator
            BusyIndicator {
                visible: control.loading
                width: 20
                height: 20
                anchors.verticalCenter: parent.verticalCenter
                running: control.loading
            }

            // Button text
            Text {
                text: control.text
                font.pixelSize: DesignTokens.fontLg
                font.weight: DesignTokens.weightSemiBold
                color: getTextColor()
                verticalAlignment: Text.AlignVCenter
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }

    // Background
    background: Rectangle {
        id: backgroundRect
        radius: DesignTokens.radiusLg
        color: getBackgroundColor()

        border.width: variant === "secondary" ? 2 : 0
        border.color: DesignTokens.borderDefault

        // Gradient for primary/success/danger variants
        gradient: Gradient {
            GradientStop {
                position: 0.0
                color: variant === "secondary" ? getBackgroundColor() : getGradientStart()
            }
            GradientStop {
                position: 1.0
                color: variant === "secondary" ? getBackgroundColor() : getGradientEnd()
            }
        }

        // Hover overlay
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            color: Qt.rgba(0, 0, 0, 1)
            opacity: control.hovered && control.enabled ? 0.1 : 0

            Behavior on opacity {
                NumberAnimation {
                    duration: DesignTokens.durationFast
                    easing.type: Easing.OutQuad
                }
            }
        }

        // Disabled overlay
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            color: DesignTokens.bgPrimary
            opacity: control.enabled ? 0 : 0.6
        }

        // Drop shadow (simplified - Qt 6 compatible)
        layer.enabled: false
    }

    // ========================================================================
    // HELPER FUNCTIONS
    // ========================================================================

    function getTextColor() {
        if (!control.enabled) {
            return DesignTokens.textDisabled
        }
        return variant === "secondary" ? DesignTokens.textPrimary : DesignTokens.bgPrimary
    }

    function getBackgroundColor() {
        if (variant === "secondary") {
            return DesignTokens.bgPrimary
        }
        return "transparent"  // Use gradient instead
    }

    function getGradientStart() {
        if (variant === "primary") return DesignTokens.primary
        if (variant === "success") return DesignTokens.success
        if (variant === "danger") return DesignTokens.error
        return DesignTokens.primary
    }

    function getGradientEnd() {
        if (variant === "primary") return DesignTokens.primaryActive
        if (variant === "success") return Qt.darker(DesignTokens.success, 1.15)
        if (variant === "danger") return Qt.darker(DesignTokens.error, 1.15)
        return DesignTokens.primaryActive
    }
}
