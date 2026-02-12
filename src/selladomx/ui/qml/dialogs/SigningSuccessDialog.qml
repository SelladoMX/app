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

    title: usedProfessionalTSA ? "✅ Firma Completa" : "Firmados " + signedCount + " documento(s)"
    modal: true

    width: 550
    height: usedProfessionalTSA ? 450 : 500

    anchors.centerIn: parent

    background: Rectangle {
        color: DesignTokens.bgPrimary
        radius: DesignTokens.radiusXl
        border.width: 1
        border.color: DesignTokens.borderDefault
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: DesignTokens.lg

        // Success with Professional TSA
        ColumnLayout {
            visible: usedProfessionalTSA
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
                text: "• ✓ Hash registrado y verificable en selladomx.com\n" +
                      "• ✓ Sello de tiempo certificado RFC 3161\n" +
                      "• ✓ Fecha verificable por terceros confiables\n" +
                      "• ✓ Evidencia admisible en procesos legales"
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
                    text: "💳 Créditos restantes: " + mainViewModel.creditBalance
                    font.pixelSize: DesignTokens.fontBase
                    font.weight: DesignTokens.weightBold
                    color: DesignTokens.primaryActive
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }

        // Success with Free TSA (with upsell)
        ColumnLayout {
            visible: !usedProfessionalTSA
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
                text: "⚠️ Documentos firmados con TSA Gratuito (validez limitada, sin registro de hash)."
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
                        text: "💡 ¿Necesitas validez legal garantizada?"
                        font.pixelSize: DesignTokens.fontLg
                        font.weight: DesignTokens.weightSemiBold
                        color: DesignTokens.warningDark
                        Layout.fillWidth: true
                    }

                    Text {
                        text: "TSA Profesional te da registro de hash verificable, certificación oficial RFC 3161 y fecha verificable por terceros por solo $2 MXN por documento."
                        font.pixelSize: DesignTokens.fontBase
                        color: DesignTokens.warningDark
                        lineHeight: 1.6
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                    }

                    Text {
                        text: "<b>Ideal para:</b> Contratos, facturas, actas, y cualquier documento legal o empresarial."
                        textFormat: Text.RichText
                        font.pixelSize: DesignTokens.fontBase
                        color: DesignTokens.warningDark
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
                visible: usedProfessionalTSA
                text: "Entendido"
                variant: "primary"
                Layout.fillWidth: true
                onClicked: successDialog.accept()
            }

            ModernButton {
                visible: !usedProfessionalTSA
                text: "Entendido"
                variant: "secondary"
                Layout.fillWidth: true
                onClicked: successDialog.accept()
            }

            ModernButton {
                visible: !usedProfessionalTSA
                text: "Ver TSA Profesional"
                variant: "primary"
                Layout.fillWidth: true
                onClicked: {
                    successDialog.accept()
                    benefitsDialog.open()
                }
            }
        }
    }

    // Benefits dialog (for upsell)
    BenefitsDialog {
        id: benefitsDialog
    }
}
