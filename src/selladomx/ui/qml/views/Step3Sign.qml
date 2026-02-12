// Step3Sign.qml - Signing process step
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../design"
import "../components"
import "../dialogs"

StepIndicator {
    id: step3

    stepNumber: 3
    stepTitle: "Firmar"
    stepDescription: "Inicia el proceso de firma digital"
    stepState: {
        if (!mainViewModel.step2Complete) return "disabled"
        return "active"
    }

    content: ColumnLayout {
        spacing: DesignTokens.lg

        // Benefits Banner (always visible)
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: benefitsLayout.implicitHeight + DesignTokens.md * 2
            radius: DesignTokens.radiusLg
            color: DesignTokens.bgPrimary
            border.width: 2
            border.color: DesignTokens.borderDefault

            RowLayout {
                id: benefitsLayout
                anchors.fill: parent
                anchors.margins: DesignTokens.md
                spacing: DesignTokens.md

                Text {
                    text: "⚖️"
                    font.pixelSize: DesignTokens.font3xl
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: DesignTokens.xs

                    Text {
                        text: "<b>¿Documento legal o empresarial?</b>"
                        textFormat: Text.RichText
                        font.pixelSize: DesignTokens.fontBase
                        color: DesignTokens.textPrimary
                        Layout.fillWidth: true
                    }

                    Text {
                        text: "Obtén validez legal certificada por solo $2 MXN por documento."
                        font.pixelSize: DesignTokens.fontSm
                        color: DesignTokens.textSecondary
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }

                ModernButton {
                    visible: !mainViewModel.hasProfessionalTSA
                    text: "Configurar"
                    variant: "primary"
                    onClicked: mainWindow.showTokenConfigDialog()
                }
            }
        }

        // TSA Professional checkbox
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: tsaCheckLayout.implicitHeight + DesignTokens.lg * 2
            radius: DesignTokens.radiusLg
            color: mainViewModel.useProfessionalTSA ? DesignTokens.primarySubtle : DesignTokens.bgSecondary
            border.width: 2
            border.color: mainViewModel.useProfessionalTSA ? DesignTokens.primary : DesignTokens.borderDefault

            Behavior on color {
                ColorAnimation { duration: DesignTokens.durationNormal }
            }
            Behavior on border.color {
                ColorAnimation { duration: DesignTokens.durationNormal }
            }

            RowLayout {
                id: tsaCheckLayout
                anchors.fill: parent
                anchors.margins: DesignTokens.lg
                spacing: DesignTokens.md

                CheckBox {
                    id: proTsaCheckbox
                    checked: mainViewModel.useProfessionalTSA
                    enabled: mainViewModel.hasProfessionalTSA && !mainViewModel.isSigning
                    onCheckedChanged: {
                        if (checked !== mainViewModel.useProfessionalTSA) {
                            mainViewModel.setUseProfessionalTSA(checked)
                        }
                    }

                    // Sync with model changes
                    Connections {
                        target: mainViewModel
                        function onUseProfessionalTSAChanged() {
                            proTsaCheckbox.checked = mainViewModel.useProfessionalTSA
                        }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: DesignTokens.xs

                    Text {
                        text: "🔒 Usar TSA Profesional"
                        font.pixelSize: DesignTokens.fontLg
                        font.weight: DesignTokens.weightSemiBold
                        color: DesignTokens.textPrimary
                    }

                    Text {
                        text: mainViewModel.hasProfessionalTSA
                            ? "Validez legal garantizada - " + mainViewModel.creditBalance + " créditos disponibles"
                            : "Configura tu token para usar TSA Profesional"
                        font.pixelSize: DesignTokens.fontSm
                        color: mainViewModel.creditBalance > 0 || !mainViewModel.hasProfessionalTSA
                            ? DesignTokens.textSecondary
                            : DesignTokens.error
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }

                // Buy credits button (if balance is 0)
                ModernButton {
                    visible: mainViewModel.hasProfessionalTSA && mainViewModel.creditBalance === 0
                    text: "Comprar"
                    variant: "primary"
                    onClicked: Qt.openUrlExternally("https://selladomx.com/buy-credits")
                }
            }
        }

        // Progress bar
        Rectangle {
            visible: mainViewModel.isSigning
            Layout.fillWidth: true
            Layout.preferredHeight: progressColumn.implicitHeight + DesignTokens.lg * 2
            radius: DesignTokens.radiusLg
            color: DesignTokens.bgSecondary
            border.width: 2
            border.color: DesignTokens.borderDefault

            ColumnLayout {
                id: progressColumn
                anchors.fill: parent
                anchors.margins: DesignTokens.lg
                spacing: DesignTokens.md

                Text {
                    text: "Firmando documentos... " + mainViewModel.currentProgress + " / " + mainViewModel.pdfCount
                    font.pixelSize: DesignTokens.fontBase
                    font.weight: DesignTokens.weightSemiBold
                    color: DesignTokens.textPrimary
                }

                ProgressBar {
                    id: progressBar
                    Layout.fillWidth: true

                    from: 0
                    to: mainViewModel.pdfCount
                    value: mainViewModel.currentProgress

                    background: Rectangle {
                        implicitHeight: 12
                        radius: 6
                        color: DesignTokens.borderDefault
                    }

                    contentItem: Item {
                        implicitHeight: 12

                        Rectangle {
                            width: progressBar.visualPosition * parent.width
                            height: parent.height
                            radius: 6

                            gradient: Gradient {
                                GradientStop { position: 0.0; color: DesignTokens.primary }
                                GradientStop { position: 1.0; color: DesignTokens.primaryActive }
                            }

                            Behavior on width {
                                NumberAnimation {
                                    duration: DesignTokens.durationNormal
                                    easing.type: Easing.OutQuad
                                }
                            }
                        }
                    }
                }
            }
        }

        // Status log
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 180
            color: DesignTokens.surfaceDefault
            radius: DesignTokens.radiusLg
            border.width: 2
            border.color: DesignTokens.borderDefault

            ScrollView {
                anchors.fill: parent
                anchors.margins: DesignTokens.md
                clip: true

                ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                ScrollBar.vertical.policy: ScrollBar.AsNeeded

                TextArea {
                    id: statusLog
                    width: parent.width
                    readOnly: true
                    wrapMode: TextArea.Wrap
                    textFormat: TextArea.RichText
                    text: mainViewModel.statusLog || "<span style='color: " + DesignTokens.textTertiary + ";'>Los mensajes de estado aparecerán aquí...</span>"

                    background: null

                    font.pixelSize: DesignTokens.fontSm
                    font.family: DesignTokens.fontFamilyMono

                    // Auto-scroll to bottom
                    onTextChanged: {
                        cursorPosition = length
                    }
                }
            }
        }

        // Sign button
        ModernButton {
            Layout.fillWidth: true
            Layout.preferredHeight: DesignTokens.buttonXl
            text: mainViewModel.isSigning ? "Firmando..." : ("Firmar " + mainViewModel.pdfCount + " PDF(s)")
            variant: "success"
            loading: mainViewModel.isSigning
            enabled: !mainViewModel.isSigning && mainViewModel.step2Complete
            onClicked: mainViewModel.startSigning()
        }

        // Info text
        Text {
            visible: !mainViewModel.isSigning
            text: {
                if (mainViewModel.useProfessionalTSA) {
                    return "✨ Los documentos serán firmados con TSA Profesional (validez legal garantizada)"
                } else {
                    return "ℹ️ Los documentos serán firmados con TSA Básico"
                }
            }
            font.pixelSize: DesignTokens.fontSm
            color: mainViewModel.useProfessionalTSA ? DesignTokens.primary : DesignTokens.textTertiary
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
    }

    // Handle file completion for potential UI updates
    Connections {
        target: mainViewModel
        function onFileCompleted(filename, success, message, verificationUrl) {
            // Could show individual file success/error indicators here
            if (verificationUrl) {
                console.log("Verification URL for", filename, ":", verificationUrl)
            }
        }

        function onSigningCompleted(successCount, totalCount, usedProfessionalTSA) {
            // Show success dialog with appropriate messaging
            signingSuccessDialog.signedCount = successCount
            signingSuccessDialog.totalCount = totalCount
            signingSuccessDialog.usedProfessionalTSA = usedProfessionalTSA
            signingSuccessDialog.open()
        }
    }

    // Signing success dialog (kept here since it needs signing-specific data)
    SigningSuccessDialog {
        id: signingSuccessDialog
    }
}
