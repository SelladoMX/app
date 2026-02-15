// ConfirmSigningDialog.qml - Confirmation dialog before signing starts
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../design"
import "../components"

Dialog {
    id: confirmDialog

    property int fileCount: 0
    property bool useProfessionalTSA: false
    property int creditBalance: 0

    title: "Confirmar firma"
    modal: true

    width: 500
    height: contentColumn.implicitHeight + DesignTokens.xl * 4

    background: Rectangle {
        color: DesignTokens.bgPrimary
        radius: DesignTokens.radiusXl
        border.width: 1
        border.color: DesignTokens.borderDefault
    }

    ColumnLayout {
        id: contentColumn
        anchors.fill: parent
        spacing: DesignTokens.lg

        // Header
        Text {
            text: "Confirmar firma de documentos"
            font.pixelSize: DesignTokens.font2xl
            font.weight: DesignTokens.weightBold
            color: DesignTokens.textPrimary
            Layout.fillWidth: true
        }

        // File count
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: fileInfoLayout.implicitHeight + DesignTokens.md * 2
            radius: DesignTokens.radiusLg
            color: DesignTokens.bgSecondary
            border.width: 1
            border.color: DesignTokens.borderDefault

            RowLayout {
                id: fileInfoLayout
                anchors.fill: parent
                anchors.margins: DesignTokens.md
                spacing: DesignTokens.md

                Text {
                    text: confirmDialog.fileCount + " documento(s)"
                    font.pixelSize: DesignTokens.fontLg
                    font.weight: DesignTokens.weightSemiBold
                    color: DesignTokens.textPrimary
                }
            }
        }

        // TSA Tier info
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: tsaTierLayout.implicitHeight + DesignTokens.md * 2
            radius: DesignTokens.radiusLg
            color: confirmDialog.useProfessionalTSA ? DesignTokens.primarySubtle : DesignTokens.bgSecondary
            border.width: 2
            border.color: confirmDialog.useProfessionalTSA ? DesignTokens.primary : DesignTokens.borderDefault

            ColumnLayout {
                id: tsaTierLayout
                anchors.fill: parent
                anchors.margins: DesignTokens.md
                spacing: DesignTokens.sm

                Text {
                    text: confirmDialog.useProfessionalTSA ? "Protección mejorada" : "Firma básica"
                    font.pixelSize: DesignTokens.fontLg
                    font.weight: DesignTokens.weightBold
                    color: DesignTokens.textPrimary
                }

                Text {
                    visible: confirmDialog.useProfessionalTSA
                    text: "Costo: " + confirmDialog.fileCount + " crédito(s)\nBalance actual: " + confirmDialog.creditBalance + " créditos"
                    font.pixelSize: DesignTokens.fontBase
                    color: confirmDialog.creditBalance >= confirmDialog.fileCount ? DesignTokens.textSecondary : DesignTokens.error
                    lineHeight: 1.6
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }

                Text {
                    visible: confirmDialog.useProfessionalTSA && confirmDialog.creditBalance < confirmDialog.fileCount
                    text: "No tienes créditos suficientes. La firma fallará."
                    font.pixelSize: DesignTokens.fontSm
                    font.weight: DesignTokens.weightSemiBold
                    color: DesignTokens.error
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }

                Text {
                    visible: !confirmDialog.useProfessionalTSA
                    text: "Gratis - validez legal básica"
                    font.pixelSize: DesignTokens.fontBase
                    color: DesignTokens.textSecondary
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }
            }
        }

        Item {
            Layout.fillHeight: true
            Layout.minimumHeight: DesignTokens.sm
        }

        // Buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: DesignTokens.md

            ModernButton {
                text: "Cancelar"
                variant: "secondary"
                Layout.fillWidth: true
                onClicked: confirmDialog.reject()
            }

            ModernButton {
                text: "Firmar " + confirmDialog.fileCount + " documento(s)"
                variant: "success"
                Layout.fillWidth: true
                onClicked: {
                    confirmDialog.accept()
                    mainViewModel.startSigning()
                }
            }
        }
    }
}
