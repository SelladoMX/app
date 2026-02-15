// SigningSuccessDialog.qml - Success dialog with TSA tier messaging
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../design"
import "../components"

Dialog {
    id: successDialog

    property int signedCount: 0
    property int totalCount: 0
    property bool usedProfessionalTSA: false
    property var verificationUrls: []

    title: signedCount === 0 ? "Error en la Firma" : (usedProfessionalTSA ? "Firma Completa" : "Firmados " + signedCount + " documento(s)")
    modal: true

    width: 550
    height: Math.min(700, contentColumn.implicitHeight + DesignTokens.xl * 4)

    background: Rectangle {
        color: DesignTokens.bgPrimary
        radius: DesignTokens.radiusXl
        border.width: 1
        border.color: DesignTokens.borderDefault
    }

    onClosed: {
        var hadSignedDocs = signedCount > 0
        // Reset all dialog state
        verificationUrls = []
        signedCount = 0
        totalCount = 0
        usedProfessionalTSA = false
        // Reset form after a short delay to allow dialog animation to finish
        if (hadSignedDocs) {
            resetFormTimer.start()
        }
    }

    ColumnLayout {
        id: contentColumn
        anchors.fill: parent
        spacing: DesignTokens.lg

        // Error state - no documents were signed
        ColumnLayout {
            visible: signedCount === 0
            spacing: DesignTokens.md
            Layout.fillWidth: true

            Text {
                text: "No se pudo completar la firma"
                font.pixelSize: DesignTokens.font2xl
                font.weight: DesignTokens.weightBold
                color: DesignTokens.error
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: errorContent.implicitHeight + DesignTokens.lg * 2
                radius: DesignTokens.radiusLg
                color: "#FEF2F2"
                border.width: 2
                border.color: DesignTokens.error

                ColumnLayout {
                    id: errorContent
                    anchors.fill: parent
                    anchors.margins: DesignTokens.lg
                    spacing: DesignTokens.sm

                    Text {
                        text: "El servicio de sellado de tiempo no está disponible en este momento."
                        font.pixelSize: DesignTokens.fontBase
                        font.weight: DesignTokens.weightMedium
                        color: DesignTokens.error
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                    }

                    Text {
                        text: "• No se consumieron créditos\n• Tus documentos no fueron modificados\n• Intenta de nuevo más tarde"
                        font.pixelSize: DesignTokens.fontBase
                        color: DesignTokens.textPrimary
                        lineHeight: 1.8
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                    }
                }
            }
        }

        // Success with Professional TSA
        ColumnLayout {
            visible: usedProfessionalTSA && signedCount > 0
            spacing: DesignTokens.md
            Layout.fillWidth: true

            Text {
                text: "Firmados " + signedCount + " documento(s) con validez legal"
                font.pixelSize: DesignTokens.font2xl
                font.weight: DesignTokens.weightBold
                color: DesignTokens.success
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
            }

            Text {
                text: "Tus documentos tienen:"
                font.pixelSize: DesignTokens.fontLg
                font.weight: DesignTokens.weightSemiBold
                color: DesignTokens.textPrimary
                Layout.fillWidth: true
            }

            Text {
                text: "• Hash registrado y verificable en selladomx.com\n" +
                      "• Sello de tiempo certificado\n" +
                      "• Fecha verificable por terceros\n" +
                      "• Evidencia admisible en procesos legales"
                font.pixelSize: DesignTokens.fontBase
                color: DesignTokens.textPrimary
                lineHeight: 1.8
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: creditsText.implicitHeight + DesignTokens.md * 2
                radius: DesignTokens.radiusLg
                color: DesignTokens.primarySubtle
                border.width: 2
                border.color: DesignTokens.primary

                Text {
                    id: creditsText
                    anchors.fill: parent
                    anchors.margins: DesignTokens.md
                    text: "Créditos restantes: " + mainViewModel.creditBalance
                    font.pixelSize: DesignTokens.fontBase
                    font.weight: DesignTokens.weightBold
                    color: DesignTokens.primaryActive
                    verticalAlignment: Text.AlignVCenter
                }
            }

            // Verification URLs section
            ColumnLayout {
                visible: successDialog.verificationUrls.length > 0
                spacing: DesignTokens.sm
                Layout.fillWidth: true

                Text {
                    text: "URLs de verificación"
                    font.pixelSize: DesignTokens.fontLg
                    font.weight: DesignTokens.weightSemiBold
                    color: DesignTokens.textPrimary
                    Layout.fillWidth: true
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: urlsColumn.implicitHeight + DesignTokens.md * 2
                    radius: DesignTokens.radiusLg
                    color: DesignTokens.bgSecondary
                    border.width: 1
                    border.color: DesignTokens.borderDefault

                    ColumnLayout {
                        id: urlsColumn
                        anchors.fill: parent
                        anchors.margins: DesignTokens.md
                        spacing: DesignTokens.xs

                        Repeater {
                            model: successDialog.verificationUrls

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2

                                Text {
                                    text: modelData.filename
                                    font.pixelSize: DesignTokens.fontSm
                                    font.weight: DesignTokens.weightSemiBold
                                    color: DesignTokens.textPrimary
                                    elide: Text.ElideMiddle
                                    Layout.fillWidth: true
                                }

                                Text {
                                    text: "<a href='" + modelData.url + "'>" + modelData.url + "</a>"
                                    textFormat: Text.RichText
                                    font.pixelSize: DesignTokens.fontSm
                                    font.family: DesignTokens.fontFamilyMono
                                    color: DesignTokens.info
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                    onLinkActivated: function(link) {
                                        Qt.openUrlExternally(link)
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: parent.hoveredLink ? Qt.PointingHandCursor : Qt.ArrowCursor
                                        acceptedButtons: Qt.NoButton
                                    }
                                }
                            }
                        }
                    }
                }

                Text {
                    text: "Se envió un correo de confirmación por cada documento firmado"
                    font.pixelSize: DesignTokens.fontSm
                    color: DesignTokens.textSecondary
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }
            }
        }

        // Success with Free TSA (with upsell)
        ColumnLayout {
            visible: !usedProfessionalTSA && signedCount > 0
            spacing: DesignTokens.md
            Layout.fillWidth: true

            Text {
                text: "Firmados " + signedCount + " documento(s)"
                font.pixelSize: DesignTokens.font2xl
                font.weight: DesignTokens.weightBold
                color: DesignTokens.primary
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
            }

            Text {
                text: "Documentos firmados con sello de tiempo básico (validez legal básica)."
                font.pixelSize: DesignTokens.fontBase
                font.weight: DesignTokens.weightMedium
                color: DesignTokens.warning
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: upsellContent.implicitHeight + DesignTokens.lg * 2
                radius: DesignTokens.radiusXl
                color: DesignTokens.warningLight
                border.width: 2
                border.color: DesignTokens.warningBorder

                ColumnLayout {
                    id: upsellContent
                    anchors.fill: parent
                    anchors.margins: DesignTokens.lg
                    spacing: DesignTokens.sm

                    Text {
                        text: "¿Necesitas la mayor validez legal?"
                        font.pixelSize: DesignTokens.fontLg
                        font.weight: DesignTokens.weightSemiBold
                        color: DesignTokens.warningDark
                        Layout.fillWidth: true
                    }

                    Text {
                        text: "Con protección mejorada obtienes hash verificable, fecha certificada por terceros y evidencia admisible en juicios " + creditPriceDisplay + " por documento."
                        font.pixelSize: DesignTokens.fontBase
                        color: DesignTokens.warningDark
                        lineHeight: 1.6
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                    }
                }
            }
        }

        Item {
            Layout.fillHeight: true
        }

        // Buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: DesignTokens.md

            ModernButton {
                visible: signedCount === 0
                text: "Cerrar"
                variant: "secondary"
                Layout.fillWidth: true
                onClicked: successDialog.accept()
            }

            ModernButton {
                visible: usedProfessionalTSA && signedCount > 0
                text: "Entendido"
                variant: "primary"
                Layout.fillWidth: true
                onClicked: successDialog.accept()
            }

            ModernButton {
                visible: !usedProfessionalTSA && signedCount > 0
                text: "Entendido"
                variant: "secondary"
                Layout.fillWidth: true
                onClicked: successDialog.accept()
            }

            ModernButton {
                visible: !usedProfessionalTSA && signedCount > 0
                text: "Ver protección mejorada"
                variant: "primary"
                Layout.fillWidth: true
                onClicked: {
                    successDialog.accept()
                    mainWindow.showBenefitsDialog()
                }
            }
        }
    }

    // Timer to reset form after dialog closes
    Timer {
        id: resetFormTimer
        interval: 300
        repeat: false
        onTriggered: mainViewModel.resetForm()
    }
}
