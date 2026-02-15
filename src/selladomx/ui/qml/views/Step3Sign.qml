// Step3Sign.qml - Signing process step
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs
import QtCore
import "../design"
import "../components"
import "../dialogs"

StepIndicator {
    id: step3

    stepNumber: 3
    stepTitle: "Firmar"
    stepDescription: "Inicia el proceso de firma digital"
    stepState: {
        if (!mainViewModel.step1Complete || !mainViewModel.step2Complete) return "disabled"
        return "active"
    }

    content: ColumnLayout {
        spacing: DesignTokens.lg

        // Enhanced protection toggle
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
                        text: "Usar protección mejorada"
                        font.pixelSize: DesignTokens.fontLg
                        font.weight: DesignTokens.weightSemiBold
                        color: DesignTokens.textPrimary
                    }

                    Text {
                        text: mainViewModel.hasProfessionalTSA
                            ? "Recomendado para documentos legales o empresariales"
                            : "Configura tu token para habilitar esta opción"
                        font.pixelSize: DesignTokens.fontSm
                        color: DesignTokens.textSecondary
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }

                // Configure button (when no token)
                ModernButton {
                    visible: !mainViewModel.hasProfessionalTSA
                    text: "Configurar"
                    variant: "primary"
                    onClicked: mainWindow.showTokenConfigDialog()
                }

                // Buy credits button (if balance is 0)
                ModernButton {
                    visible: mainViewModel.hasProfessionalTSA && mainViewModel.creditBalance === 0
                    text: "Comprar"
                    variant: "primary"
                    onClicked: Qt.openUrlExternally(buyCreditsUrl)
                }
            }
        }

        // Output directory selector
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: outputDirLayout.implicitHeight + DesignTokens.sm * 2
            radius: DesignTokens.radiusMd
            color: DesignTokens.bgSecondary
            border.width: 1
            border.color: DesignTokens.borderDefault

            RowLayout {
                id: outputDirLayout
                anchors.fill: parent
                anchors.margins: DesignTokens.sm
                spacing: DesignTokens.md

                Text {
                    text: "Guardar en:"
                    font.pixelSize: DesignTokens.fontBase
                    font.weight: DesignTokens.weightMedium
                    color: DesignTokens.textSecondary
                }

                Text {
                    text: mainViewModel.outputDirDisplay
                    font.pixelSize: DesignTokens.fontBase
                    color: DesignTokens.textPrimary
                    elide: Text.ElideMiddle
                    Layout.fillWidth: true
                }

                ModernButton {
                    text: "Cambiar"
                    variant: "secondary"
                    onClicked: folderDialog.open()
                }

                ModernButton {
                    visible: mainViewModel.outputDir !== ""
                    text: "Restablecer"
                    variant: "secondary"
                    onClicked: mainViewModel.clearOutputDir()
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

        // Status log (only visible in debug mode)
        Rectangle {
            visible: mainViewModel.isDebugMode
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
            text: mainViewModel.signingSuccessful ? "Firmado exitosamente ✓" : mainViewModel.isSigning ? "Firmando..." : ("Firmar " + mainViewModel.pdfCount + " PDF(s)")
            variant: "success"
            loading: mainViewModel.isSigning
            enabled: !mainViewModel.isSigning && !mainViewModel.signingSuccessful && mainViewModel.step1Complete && mainViewModel.step2Complete
            onClicked: mainViewModel.confirmSigning()
        }

        // Info text
        Text {
            visible: !mainViewModel.isSigning
            text: {
                if (mainViewModel.useProfessionalTSA) {
                    return "Los documentos serán firmados con protección mejorada (sello de tiempo certificado)"
                } else {
                    return "Los documentos serán firmados con sello de tiempo básico"
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
        }

        function onShowConfirmSigningDialog(fileCount, useProfessionalTSA, creditBalance) {
            confirmSigningDialog.fileCount = fileCount
            confirmSigningDialog.useProfessionalTSA = useProfessionalTSA
            confirmSigningDialog.creditBalance = creditBalance
            confirmSigningDialog.open()
        }

        function onVerificationUrlsReady(urls) {
            signingSuccessDialog.verificationUrls = urls
        }

        function onSigningCompleted(successCount, totalCount, usedProfessionalTSA) {
            signingSuccessDialog.signedCount = successCount
            signingSuccessDialog.totalCount = totalCount
            signingSuccessDialog.usedProfessionalTSA = usedProfessionalTSA
            signingSuccessDialog.open()
        }
    }

    // Confirmation dialog (shown before signing starts)
    ConfirmSigningDialog {
        id: confirmSigningDialog
        parent: Overlay.overlay
        anchors.centerIn: parent
    }

    // Signing success dialog (kept here since it needs signing-specific data)
    SigningSuccessDialog {
        id: signingSuccessDialog
        parent: Overlay.overlay
        anchors.centerIn: parent
    }

    // Folder selection dialog for output directory
    FolderDialog {
        id: folderDialog
        title: "Seleccionar carpeta destino"
        currentFolder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)

        onAccepted: {
            mainViewModel.setOutputDir(selectedFolder)
        }
    }
}
