import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../design"
import "../components"

Dialog {
    id: benefitsDialog

    title: ""
    modal: true

    width: 680
    height: 650

    background: Rectangle {
        color: DesignTokens.bgPrimary
        radius: DesignTokens.radiusXl
        border.width: 1
        border.color: DesignTokens.borderDefault
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: DesignTokens.lg

        Text {
            text: "🔒 Protege tus documentos con validez legal"
            font.pixelSize: DesignTokens.font3xl
            font.weight: DesignTokens.weightBold
            color: DesignTokens.primary
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }

        // Professional TSA section
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: proContent.implicitHeight + DesignTokens.lg * 2
            radius: DesignTokens.radiusLg
            color: DesignTokens.accentLight
            border.width: 2
            border.color: DesignTokens.accent

            ColumnLayout {
                id: proContent
                anchors.fill: parent
                anchors.margins: DesignTokens.lg
                spacing: DesignTokens.sm

                Text {
                    text: "✓ Protección mejorada"
                    font.pixelSize: DesignTokens.fontLg
                    font.weight: DesignTokens.weightBold
                    color: DesignTokens.accent
                    Layout.fillWidth: true
                }

                Text {
                    text: "• Validez legal respaldada por proveedor europeo certificado\n" +
                          "• Hash registrado y verificable en selladomx.com\n" +
                          "• Fecha y hora certificada por terceros\n" +
                          "• Evidencia admisible en juicios\n" +
                          "• Cumple NOM-151-SCFI-2016 y normas europeas eIDAS"
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
                    text: "⚠️ Firma básica"
                    font.pixelSize: DesignTokens.fontLg
                    font.weight: DesignTokens.weightBold
                    color: DesignTokens.error
                    Layout.fillWidth: true
                }

                Text {
                    text: "• Validez legal básica, sin certificación de terceros\n" +
                          "• Sin registro de hash verificable\n" +
                          "• Aceptación limitada en procesos legales formales\n" +
                          "• Adecuado para documentos internos o de bajo riesgo"
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
            Layout.preferredHeight: priceContent.implicitHeight + DesignTokens.xl * 2
            radius: DesignTokens.radiusLg
            color: DesignTokens.primarySubtle
            border.width: 2
            border.color: DesignTokens.primary

            ColumnLayout {
                id: priceContent
                anchors.fill: parent
                anchors.margins: DesignTokens.xl
                spacing: DesignTokens.sm

                Text {
                    text: creditPriceDisplay + " por documento"
                    font.pixelSize: DesignTokens.font2xl
                    font.weight: DesignTokens.weightBold
                    color: DesignTokens.primary
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                }

                Text {
                    text: "Protege tu patrimonio y negocios con validez legal garantizada."
                    font.pixelSize: DesignTokens.fontBase
                    color: DesignTokens.textSecondary
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                }
            }
        }

        Item { Layout.fillHeight: true }

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
                    Qt.openUrlExternally(buyCreditsUrl)
                    benefitsDialog.accept()
                }
            }
        }
    }
}
