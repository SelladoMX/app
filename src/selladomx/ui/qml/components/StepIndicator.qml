// StepIndicator.qml - Step container for guided workflow
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../design"

Rectangle {
    id: step

    // Properties
    property int stepNumber: 1
    property string stepTitle: ""
    property string stepDescription: ""
    property string stepState: "pending"  // pending, active, completed, disabled
    property alias content: contentLoader.sourceComponent

    // Signals
    signal completed()

    // Sizing
    implicitHeight: mainLayout.implicitHeight + (DesignTokens.xxxl * 2)
    implicitWidth: parent.width

    // Styling
    radius: DesignTokens.radiusXxl
    color: getBackgroundColor()
    border.width: 3
    border.color: getBorderColor()

    // Transitions
    Behavior on border.color {
        ColorAnimation { duration: DesignTokens.durationNormal }
    }
    Behavior on color {
        ColorAnimation { duration: DesignTokens.durationNormal }
    }

    // Main layout
    ColumnLayout {
        id: mainLayout
        anchors.fill: parent
        anchors.margins: DesignTokens.xxxl
        spacing: DesignTokens.xl

        // Header
        RowLayout {
            id: headerLayout
            spacing: DesignTokens.lg
            Layout.fillWidth: true

            // Number badge
            Rectangle {
                id: numberBadge
                width: DesignTokens.stepNumberSize
                height: DesignTokens.stepNumberSize
                radius: DesignTokens.stepNumberSize / 2

                gradient: Gradient {
                    GradientStop {
                        position: 0.0
                        color: getNumberBackground()
                    }
                    GradientStop {
                        position: 1.0
                        color: Qt.darker(getNumberBackground(), 1.1)
                    }
                }

                // Pulse animation when active
                SequentialAnimation on scale {
                    running: step.stepState === "active"
                    loops: Animation.Infinite

                    NumberAnimation {
                        from: 1.0
                        to: 1.05
                        duration: 1000
                        easing.type: Easing.InOutSine
                    }
                    NumberAnimation {
                        from: 1.05
                        to: 1.0
                        duration: 1000
                        easing.type: Easing.InOutSine
                    }
                }

                Text {
                    anchors.centerIn: parent
                    text: step.stepState === "completed" ? "✓" : step.stepNumber
                    font.pixelSize: step.stepState === "completed" ? 36 : 32
                    font.weight: DesignTokens.weightBold
                    color: DesignTokens.bgPrimary
                }
            }

            // Title & Description
            ColumnLayout {
                Layout.fillWidth: true
                spacing: DesignTokens.xs

                Text {
                    text: step.stepTitle
                    font.pixelSize: DesignTokens.font3xl
                    font.weight: DesignTokens.weightBold
                    color: DesignTokens.textPrimary
                    Layout.fillWidth: true
                }

                Text {
                    text: step.stepDescription
                    font.pixelSize: DesignTokens.fontBase
                    color: DesignTokens.textSecondary
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }

            // Status dot
            Rectangle {
                width: DesignTokens.statusDotSize
                height: DesignTokens.statusDotSize
                radius: DesignTokens.statusDotSize / 2
                color: getStatusColor()

                Behavior on color {
                    ColorAnimation { duration: DesignTokens.durationNormal }
                }
            }
        }

        // Content container
        Loader {
            id: contentLoader
            Layout.fillWidth: true
            Layout.fillHeight: true

            enabled: step.stepState === "active" || step.stepState === "completed"
            opacity: enabled ? 1.0 : 0.5

            Behavior on opacity {
                NumberAnimation {
                    duration: DesignTokens.durationNormal
                    easing.type: Easing.OutQuad
                }
            }
        }
    }

    // ========================================================================
    // HELPER FUNCTIONS
    // ========================================================================

    function getBorderColor() {
        if (stepState === "active") return DesignTokens.stepActiveBorder
        if (stepState === "completed") return DesignTokens.stepCompletedBorder
        if (stepState === "disabled") return DesignTokens.stepDisabledBorder
        return DesignTokens.stepPendingBorder
    }

    function getBackgroundColor() {
        if (stepState === "active") return DesignTokens.stepActiveBg
        if (stepState === "completed") return DesignTokens.stepCompletedBg
        if (stepState === "disabled") return DesignTokens.stepDisabledBg
        return DesignTokens.stepPendingBg
    }

    function getNumberBackground() {
        if (stepState === "active") return DesignTokens.primary
        if (stepState === "completed") return DesignTokens.success
        if (stepState === "disabled") return DesignTokens.textDisabled
        return DesignTokens.textTertiary
    }

    function getStatusColor() {
        if (stepState === "active") return DesignTokens.primary
        if (stepState === "completed") return DesignTokens.success
        if (stepState === "disabled") return DesignTokens.borderDefault
        return DesignTokens.textTertiary
    }
}
