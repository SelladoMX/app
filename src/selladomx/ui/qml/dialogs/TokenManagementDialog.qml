// TokenManagementDialog.qml - Subtoken management dialog
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../design"
import "../components"

Dialog {
    id: tokenMgmtDialog

    title: "Administrar Subtokens"
    modal: true

    width: 600
    height: 550

    background: Rectangle {
        color: DesignTokens.bgPrimary
        radius: DesignTokens.radiusXl
        border.width: 1
        border.color: DesignTokens.borderDefault
    }

    // State
    property string newTokenValue: ""
    property string newTokenAlias: ""
    property bool isLoading: false
    property string errorMessage: ""

    // Revoke confirmation state
    property string revokeTokenId: ""
    property string revokeTokenAlias: ""

    onOpened: {
        // Clear state and load tokens
        newTokenValue = ""
        newTokenAlias = ""
        errorMessage = ""
        aliasInput.text = ""
        expiryInput.text = ""
        mainViewModel.listTokens()
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: DesignTokens.md

        // Title
        Text {
            text: "Administrar Subtokens"
            font.pixelSize: DesignTokens.font2xl
            font.weight: DesignTokens.weightSemiBold
            color: DesignTokens.textPrimary
            Layout.fillWidth: true
        }

        // Warning banner (not primary token)
        Rectangle {
            visible: !mainViewModel.isPrimaryToken
            Layout.fillWidth: true
            Layout.preferredHeight: warningText.implicitHeight + DesignTokens.md * 2
            radius: DesignTokens.radiusMd
            color: DesignTokens.warningLight
            border.width: 2
            border.color: DesignTokens.warningBorder

            Text {
                id: warningText
                anchors.fill: parent
                anchors.margins: DesignTokens.md
                text: "Solo el token primario puede crear y administrar subtokens"
                font.pixelSize: DesignTokens.fontBase
                color: DesignTokens.warningDark
                wrapMode: Text.WordWrap
                verticalAlignment: Text.AlignVCenter
            }
        }

        // Error message
        Rectangle {
            visible: errorMessage !== ""
            Layout.fillWidth: true
            Layout.preferredHeight: errorText.implicitHeight + DesignTokens.md * 2
            radius: DesignTokens.radiusMd
            color: DesignTokens.errorLight
            border.width: 2
            border.color: DesignTokens.error

            Text {
                id: errorText
                anchors.fill: parent
                anchors.margins: DesignTokens.md
                text: errorMessage
                font.pixelSize: DesignTokens.fontSm
                color: DesignTokens.error
                wrapMode: Text.WordWrap
                verticalAlignment: Text.AlignVCenter
            }
        }

        // Create section
        ColumnLayout {
            visible: mainViewModel.isPrimaryToken
            Layout.fillWidth: true
            spacing: DesignTokens.sm

            Text {
                text: "Crear subtoken"
                font.pixelSize: DesignTokens.fontLg
                font.weight: DesignTokens.weightSemiBold
                color: DesignTokens.textPrimary
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: DesignTokens.sm

                TextField {
                    id: aliasInput
                    Layout.fillWidth: true
                    Layout.preferredHeight: DesignTokens.inputDefault
                    placeholderText: "Nombre del subtoken"
                    font.pixelSize: DesignTokens.fontSm
                    color: DesignTokens.textPrimary
                    placeholderTextColor: DesignTokens.textTertiary

                    background: Rectangle {
                        color: DesignTokens.bgPrimary
                        border.width: 2
                        border.color: aliasInput.activeFocus ? DesignTokens.primary : DesignTokens.borderDefault
                        radius: DesignTokens.radiusMd
                    }
                }

                TextField {
                    id: expiryInput
                    Layout.preferredWidth: 120
                    Layout.preferredHeight: DesignTokens.inputDefault
                    placeholderText: "Días"
                    font.pixelSize: DesignTokens.fontSm
                    color: DesignTokens.textPrimary
                    placeholderTextColor: DesignTokens.textTertiary
                    validator: IntValidator { bottom: 0; top: 3650 }
                    inputMethodHints: Qt.ImhDigitsOnly

                    background: Rectangle {
                        color: DesignTokens.bgPrimary
                        border.width: 2
                        border.color: expiryInput.activeFocus ? DesignTokens.primary : DesignTokens.borderDefault
                        radius: DesignTokens.radiusMd
                    }
                }

                ModernButton {
                    text: "Crear"
                    variant: "success"
                    enabled: aliasInput.text.trim().length > 0 && !isLoading
                    onClicked: {
                        var days = parseInt(expiryInput.text) || 0
                        errorMessage = ""
                        isLoading = true
                        mainViewModel.deriveToken(aliasInput.text.trim(), days)
                    }
                }
            }
        }

        // New token display (shown once after creation)
        Rectangle {
            visible: newTokenValue !== ""
            Layout.fillWidth: true
            Layout.preferredHeight: newTokenColumn.implicitHeight + DesignTokens.md * 2
            radius: DesignTokens.radiusMd
            color: DesignTokens.successLight
            border.width: 2
            border.color: DesignTokens.success

            ColumnLayout {
                id: newTokenColumn
                anchors.fill: parent
                anchors.margins: DesignTokens.md
                spacing: DesignTokens.xs

                Text {
                    text: "Subtoken creado: " + newTokenAlias
                    font.pixelSize: DesignTokens.fontBase
                    font.weight: DesignTokens.weightSemiBold
                    color: DesignTokens.success
                    Layout.fillWidth: true
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: DesignTokens.sm

                    Text {
                        text: newTokenValue
                        font.pixelSize: DesignTokens.fontSm
                        font.family: DesignTokens.fontFamilyMono
                        color: DesignTokens.textPrimary
                        Layout.fillWidth: true
                        wrapMode: Text.WrapAnywhere
                    }

                    ModernButton {
                        text: "Copiar"
                        variant: "secondary"
                        onClicked: {
                            clipboardHelper.text = newTokenValue
                            clipboardHelper.selectAll()
                            clipboardHelper.copy()
                        }
                    }
                }

                Text {
                    text: "Este token solo se muestra una vez. Guárdalo en un lugar seguro."
                    font.pixelSize: DesignTokens.fontXs
                    color: DesignTokens.warning
                    font.weight: DesignTokens.weightSemiBold
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                }
            }
        }

        // Active subtokens header
        Text {
            text: "Subtokens activos"
            font.pixelSize: DesignTokens.fontLg
            font.weight: DesignTokens.weightSemiBold
            color: DesignTokens.textPrimary
            Layout.fillWidth: true
        }

        // Token list
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: DesignTokens.radiusMd
            color: DesignTokens.bgSecondary
            border.width: 1
            border.color: DesignTokens.borderDefault

            ListView {
                id: tokenListView
                anchors.fill: parent
                anchors.margins: DesignTokens.sm
                model: mainViewModel.tokensList
                clip: true
                spacing: DesignTokens.xs

                delegate: Rectangle {
                    width: tokenListView.width
                    height: delegateRow.implicitHeight + DesignTokens.sm * 2
                    radius: DesignTokens.radiusMd
                    color: DesignTokens.bgPrimary
                    border.width: 1
                    border.color: DesignTokens.borderDefault

                    RowLayout {
                        id: delegateRow
                        anchors.fill: parent
                        anchors.margins: DesignTokens.sm
                        spacing: DesignTokens.sm

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2

                            Text {
                                text: modelData.alias || "Sin nombre"
                                font.pixelSize: DesignTokens.fontBase
                                font.weight: DesignTokens.weightSemiBold
                                color: DesignTokens.textPrimary
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }

                            Text {
                                text: {
                                    var token = modelData.token || ""
                                    if (token.length > 12)
                                        return token.substring(0, 8) + "..." + token.substring(token.length - 4)
                                    return token
                                }
                                font.pixelSize: DesignTokens.fontXs
                                font.family: DesignTokens.fontFamilyMono
                                color: DesignTokens.textTertiary
                                Layout.fillWidth: true
                            }

                            RowLayout {
                                spacing: DesignTokens.md

                                Text {
                                    visible: modelData.last_used_at !== undefined && modelData.last_used_at !== null
                                    text: "Último uso: " + (modelData.last_used_at || "Nunca")
                                    font.pixelSize: DesignTokens.fontXs
                                    color: DesignTokens.textTertiary
                                }

                                Text {
                                    visible: modelData.expires_at !== undefined && modelData.expires_at !== null
                                    text: "Expira: " + (modelData.expires_at || "")
                                    font.pixelSize: DesignTokens.fontXs
                                    color: DesignTokens.textTertiary
                                }
                            }
                        }

                        ModernButton {
                            text: "Revocar"
                            variant: "danger"
                            visible: mainViewModel.isPrimaryToken
                            onClicked: {
                                revokeTokenId = modelData.id
                                revokeTokenAlias = modelData.alias || "Sin nombre"
                                revokeConfirmDialog.open()
                            }
                        }
                    }
                }
            }

            // Empty state
            Text {
                visible: mainViewModel.tokensList.length === 0
                anchors.centerIn: parent
                text: "No hay subtokens creados"
                font.pixelSize: DesignTokens.fontBase
                color: DesignTokens.textTertiary
            }
        }

        // Bottom buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: DesignTokens.md

            ModernButton {
                text: "Actualizar"
                variant: "secondary"
                onClicked: mainViewModel.listTokens()
            }

            Item { Layout.fillWidth: true }

            ModernButton {
                text: "Cerrar"
                variant: "secondary"
                onClicked: tokenMgmtDialog.reject()
            }
        }
    }

    // Revoke confirmation dialog
    Dialog {
        id: revokeConfirmDialog
        title: "Confirmar revocación"
        modal: true
        anchors.centerIn: parent
        width: 400
        height: 200

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
                text: "¿Revocar subtoken \"" + revokeTokenAlias + "\"?"
                font.pixelSize: DesignTokens.fontLg
                font.weight: DesignTokens.weightSemiBold
                color: DesignTokens.textPrimary
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }

            Text {
                text: "Esta acción no se puede deshacer. El subtoken dejará de funcionar inmediatamente."
                font.pixelSize: DesignTokens.fontBase
                color: DesignTokens.textSecondary
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }

            Item { Layout.fillHeight: true }

            RowLayout {
                Layout.fillWidth: true
                spacing: DesignTokens.md

                ModernButton {
                    text: "Cancelar"
                    variant: "secondary"
                    Layout.fillWidth: true
                    onClicked: revokeConfirmDialog.reject()
                }

                ModernButton {
                    text: "Revocar"
                    variant: "danger"
                    Layout.fillWidth: true
                    onClicked: {
                        mainViewModel.revokeToken(revokeTokenId)
                        revokeConfirmDialog.accept()
                    }
                }
            }
        }
    }

    // Connect to ViewModel signals
    Connections {
        target: mainViewModel

        function onTokensLoaded(tokens) {
            tokenMgmtDialog.isLoading = false
        }

        function onTokenDerived(tokenInfo) {
            tokenMgmtDialog.isLoading = false
            tokenMgmtDialog.newTokenValue = tokenInfo.token || ""
            tokenMgmtDialog.newTokenAlias = tokenInfo.alias || ""
            aliasInput.text = ""
            expiryInput.text = ""
        }

        function onTokenRevoked(tokenId) {
            tokenMgmtDialog.isLoading = false
        }

        function onTokenError(message) {
            tokenMgmtDialog.isLoading = false
            tokenMgmtDialog.errorMessage = message
        }
    }

    // Hidden TextEdit for clipboard operations
    TextEdit {
        id: clipboardHelper
        visible: false
    }
}
