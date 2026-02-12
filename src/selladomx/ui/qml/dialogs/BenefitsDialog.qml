// BenefitsDialog.qml - TSA Professional benefits comparison dialog
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../design"
import "../components"

Dialog {
    id: benefitsDialog

    title: "Mejora tu Seguridad Legal"
    modal: true

    width: 600
    height: 650

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

        // Header
        Text {
            text: "🔒 TSA Profesional - Máxima Seguridad Legal"
            font.pixelSize: DesignTokens.font3xl
            font.weight: DesignTokens.weightBold
            color: DesignTokens.primary
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }

        Text {
            text: "¿Por qué necesitas TSA Profesional?"
            font.pixelSize: DesignTokens.fontLg
            font.weight: DesignTokens.weightSemiBold
            color: DesignTokens.textPrimary
            Layout.fillWidth: true
        }

        // Comparison table
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            ColumnLayout {
                width: parent.width
                spacing: DesignTokens.md

                // Professional TSA section
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: proContent.implicitHeight + DesignTokens.lg * 2
                    radius: DesignTokens.radiusLg
                    color: DesignTokens.successLight
                    border.width: 2
                    border.color: DesignTokens.success

                    ColumnLayout {
                        id: proContent
                        anchors.fill: parent
                        anchors.margins: DesignTokens.lg
                        spacing: DesignTokens.sm

                        Text {
                            text: "✓ TSA Profesional"
                            font.pixelSize: DesignTokens.fontLg
                            font.weight: DesignTokens.weightBold
                            color: DesignTokens.success
                            Layout.fillWidth: true
                        }

                        Text {
                            text: "• Validez legal garantizada por DigitalSign\n" +
                                  "• Certificación oficial RFC 3161\n" +
                                  "• Hash registrado y verificable en selladomx.com\n" +
                                  "• Fecha y hora certificada por terceros\n" +
                                  "• Evidencia admisible en juicios\n" +
                                  "• Cumplimiento NOM-151-SCFI-2016"
                            font.pixelSize: DesignTokens.fontSm
                            color: DesignTokens.textSecondary
                            lineHeight: 1.6
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }
                    }
                }

                // Free TSA section
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: freeContent.implicitHeight + DesignTokens.lg * 2
                    radius: DesignTokens.radiusLg
                    color: DesignTokens.errorLight
                    border.width: 2
                    border.color: DesignTokens.error

                    ColumnLayout {
                        id: freeContent
                        anchors.fill: parent
                        anchors.margins: DesignTokens.lg
                        spacing: DesignTokens.sm

                        Text {
                            text: "⚠️ TSA Gratuito"
                            font.pixelSize: DesignTokens.fontLg
                            font.weight: DesignTokens.weightBold
                            color: DesignTokens.error
                            Layout.fillWidth: true
                        }

                        Text {
                            text: "• ⚠️ Sin registro de hash\n" +
                                  "• ⚠️ Validez limitada (sin garantía)\n" +
                                  "• ❌ No certificado por terceros\n" +
                                  "• ❌ Fecha no verificable por terceros\n" +
                                  "• ⚠️ Aceptación limitada en procesos legales\n" +
                                  "• Recomendado para documentos internos"
                            font.pixelSize: DesignTokens.fontSm
                            color: DesignTokens.textSecondary
                            lineHeight: 1.6
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }
                    }
                }

                // Pricing highlight
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: priceContent.implicitHeight + DesignTokens.lg * 2
                    radius: DesignTokens.radiusLg
                    color: DesignTokens.primarySubtle
                    border.width: 2
                    border.color: DesignTokens.primary

                    ColumnLayout {
                        id: priceContent
                        anchors.fill: parent
                        anchors.margins: DesignTokens.lg
                        spacing: DesignTokens.xs

                        Text {
                            text: "💰 Solo $2 MXN por documento"
                            font.pixelSize: DesignTokens.fontXl
                            font.weight: DesignTokens.weightBold
                            color: DesignTokens.primary
                            Layout.fillWidth: true
                        }

                        Text {
                            text: "Protege tu patrimonio y negocios con la máxima seguridad."
                            font.pixelSize: DesignTokens.fontSm
                            color: DesignTokens.textSecondary
                            Layout.fillWidth: true
                            wrapMode: Text.WordWrap
                        }
                    }
                }
            }
        }

        // Buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: DesignTokens.md

            ModernButton {
                text: "Ahora No"
                variant: "secondary"
                Layout.fillWidth: true
                onClicked: benefitsDialog.reject()
            }

            ModernButton {
                text: "Comprar Créditos"
                variant: "primary"
                Layout.fillWidth: true
                onClicked: {
                    Qt.openUrlExternally("https://selladomx.com/buy-credits")
                    benefitsDialog.accept()
                }
            }
        }
    }
}
