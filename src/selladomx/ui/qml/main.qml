// main.qml - Main application window
import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "design"
import "components"
import "views"
import "dialogs"

Window {
    id: mainWindow

    // Window properties
    width: 950
    height: 750
    minimumWidth: 900
    minimumHeight: 700
    visible: true
    title: "SelladoMX - Firma Digital de PDFs"

    color: DesignTokens.bgPrimary

    // Function to show onboarding (called from Python)
    function showOnboarding() {
        onboardingLoader.active = true
    }

    // Global dialog functions (called from child components)
    function showBenefitsDialog() {
        benefitsDialog.open()
    }

    function showTokenConfigDialog() {
        tokenConfigDialog.open()
    }

    // Main layout
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: DesignTokens.xl
        spacing: DesignTokens.lg

        // Header Bar
        HeaderBar {
            id: headerBar
            Layout.fillWidth: true
            Layout.preferredHeight: 60
        }

        // Main Content (3 Steps)
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            ScrollBar.vertical.policy: ScrollBar.AsNeeded

            contentWidth: availableWidth  // Prevent horizontal scrolling

            ColumnLayout {
                width: parent.width
                spacing: DesignTokens.lg

                Step1SelectFiles {
                    id: step1
                    Layout.fillWidth: true
                }

                Step2LoadCertificate {
                    id: step2
                    Layout.fillWidth: true
                }

                Step3Sign {
                    id: step3
                    Layout.fillWidth: true
                }
            }
        }
    }

    // Status message popup (optional - for floating notifications)
    Connections {
        target: mainViewModel
        function onStatusMessage(message, color) {
            // Could show a toast notification here
            console.log("[Status]", message)
        }
    }

    // Onboarding dialog (loaded on demand)
    Loader {
        id: onboardingLoader
        active: false
        anchors.fill: parent
        sourceComponent: OnboardingDialog {
            anchors.centerIn: parent
            onAccepted: {
                // Mark onboarding as completed via settings bridge
                settingsBridge.markOnboardingCompleted()
                onboardingLoader.active = false
            }
            onRejected: {
                // User closed/skipped - still mark as completed
                settingsBridge.markOnboardingCompleted()
                onboardingLoader.active = false
            }
        }

        onLoaded: {
            item.open()
        }
    }

    // Centralized dialogs (shared across all components)
    BenefitsDialog {
        id: benefitsDialog
        anchors.centerIn: parent
    }

    TokenConfigDialog {
        id: tokenConfigDialog
        anchors.centerIn: parent
    }
}
