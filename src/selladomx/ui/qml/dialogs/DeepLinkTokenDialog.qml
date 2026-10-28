import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../design"
import "../components"

// Any web page can open a selladomx:// link, so a token received that way is
// only saved after the user accepts it here.
Dialog {
    id: deepLinkTokenDialog

    property string email: ""
    property int creditsRemaining: 0
    property bool isPrimary: false
    property string tokenAlias: ""
    property string expiresAt: ""
    property bool replacesExisting: false
    property bool decided: false

    function showFor(info) {
        email = info.email || ""
        creditsRemaining = info.credits_remaining || 0
        isPrimary = info.is_primary === true
        tokenAlias = info.alias || ""
        expiresAt = info.expires_at || ""
        replacesExisting = info.replaces_existing === true
        decided = false
        open()
    }

    function formatDate(isoString) {
        if (!isoString)
            return "Sin fecha de expiración"
        var date = new Date(isoString)
        if (isNaN(date.getTime()))
            return isoString
        return date.toLocaleDateString(Qt.locale("es_MX"), "d 'de' MMMM 'de' yyyy")
    }

    title: "Confirmar token"
    modal: true
    closePolicy: Popup.CloseOnEscape

    width: 500
    height: contentColumn.implicitHeight + DesignTokens.xl * 4

    background: Rectangle {
        color: DesignTokens.bgPrimary
        radius: DesignTokens.radiusXl
        border.width: 1
        border.color: DesignTokens.borderDefault
    }

    onClosed: {
        if (!decided)
            mainViewModel.cancelDeepLinkToken()
    }

    ColumnLayout {
        id: contentColumn
        anchors.fill: parent
        spacing: DesignTokens.lg

        Text {
            text: "¿Usar este token en SelladoMX?"
            font.pixelSize: DesignTokens.font2xl
            font.weight: DesignTokens.weightBold
            color: DesignTokens.textPrimary
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }

        Text {
            text: "Un enlace quiere configurar un token en esta aplicación. Acéptalo solo si tú lo solicitaste en selladomx.com: los documentos que firmes con protección mejorada quedarán registrados en esta cuenta."
            font.pixelSize: DesignTokens.fontBase
            color: DesignTokens.textSecondary
            lineHeight: 1.4
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }

        // Token details from the API
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: detailsGrid.implicitHeight + DesignTokens.md * 2
            radius: DesignTokens.radiusLg
            color: DesignTokens.bgSecondary
            border.width: 1
            border.color: DesignTokens.borderDefault

            GridLayout {
                id: detailsGrid
                anchors.fill: parent
                anchors.margins: DesignTokens.md
                columns: 2
                columnSpacing: DesignTokens.md
                rowSpacing: DesignTokens.sm

                Text {
                    visible: deepLinkTokenDialog.email !== ""
                    text: "Cuenta:"
                    font.pixelSize: DesignTokens.fontBase
                    color: DesignTokens.textSecondary
                }
                Text {
                    visible: deepLinkTokenDialog.email !== ""
                    text: deepLinkTokenDialog.email
                    textFormat: Text.PlainText
                    font.pixelSize: DesignTokens.fontBase
                    font.weight: DesignTokens.weightSemiBold
                    color: DesignTokens.textPrimary
                    elide: Text.ElideMiddle
                    Layout.fillWidth: true
                }

                Text {
                    text: "Créditos:"
                    font.pixelSize: DesignTokens.fontBase
                    color: DesignTokens.textSecondary
                }
                Text {
                    text: deepLinkTokenDialog.creditsRemaining + " disponibles"
                    font.pixelSize: DesignTokens.fontBase
                    font.weight: DesignTokens.weightSemiBold
                    color: DesignTokens.textPrimary
                    Layout.fillWidth: true
                }

                Text {
                    text: "Tipo:"
                    font.pixelSize: DesignTokens.fontBase
                    color: DesignTokens.textSecondary
                }
                Text {
                    text: deepLinkTokenDialog.isPrimary
                          ? "Token principal"
                          : "Subtoken" + (deepLinkTokenDialog.tokenAlias !== "" ? " «" + deepLinkTokenDialog.tokenAlias + "»" : "")
                    textFormat: Text.PlainText
                    font.pixelSize: DesignTokens.fontBase
                    font.weight: DesignTokens.weightSemiBold
                    color: DesignTokens.textPrimary
                    elide: Text.ElideRight
                    Layout.fillWidth: true
                }

                Text {
                    text: "Expira:"
                    font.pixelSize: DesignTokens.fontBase
                    color: DesignTokens.textSecondary
                }
                Text {
                    text: deepLinkTokenDialog.formatDate(deepLinkTokenDialog.expiresAt)
                    textFormat: Text.PlainText
                    font.pixelSize: DesignTokens.fontBase
                    font.weight: DesignTokens.weightSemiBold
                    color: DesignTokens.textPrimary
                    Layout.fillWidth: true
                }
            }
        }

        Rectangle {
            visible: deepLinkTokenDialog.replacesExisting
            Layout.fillWidth: true
            Layout.preferredHeight: replaceText.implicitHeight + DesignTokens.md * 2
            radius: DesignTokens.radiusLg
            color: DesignTokens.warningLight
            border.width: 2
            border.color: DesignTokens.warningBorder

            Text {
                id: replaceText
                anchors.fill: parent
                anchors.margins: DesignTokens.md
                text: "Este token reemplazará el que tienes configurado ahora."
                font.pixelSize: DesignTokens.fontSm
                font.weight: DesignTokens.weightMedium
                color: DesignTokens.warningDark
                wrapMode: Text.WordWrap
                verticalAlignment: Text.AlignVCenter
            }
        }

        Item {
            Layout.fillHeight: true
            Layout.minimumHeight: DesignTokens.sm
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: DesignTokens.md

            ModernButton {
                text: "Cancelar"
                variant: "secondary"
                Layout.fillWidth: true
                onClicked: deepLinkTokenDialog.close()
            }

            ModernButton {
                text: deepLinkTokenDialog.replacesExisting ? "Reemplazar token" : "Usar este token"
                variant: "primary"
                Layout.fillWidth: true
                onClicked: {
                    deepLinkTokenDialog.decided = true
                    mainViewModel.confirmDeepLinkToken()
                    deepLinkTokenDialog.close()
                }
            }
        }
    }
}
