import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../design"
import "../components"

Dialog {
    id: tokenDialog

    title: "Configurar Token de Autenticación"
    modal: true

    width: 500
    height: 450

    background: Rectangle {
        color: DesignTokens.bgPrimary
        radius: DesignTokens.radiusXl
        border.width: 1
        border.color: DesignTokens.borderDefault
    }

    property bool isValidating: false
    property bool validationSuccess: false
    property string validationMessage: ""
    property string tokenValue: ""

    ColumnLayout {
        anchors.fill: parent
        spacing: DesignTokens.lg

        Text {
            text: "Configurar Token de Autenticación"
            font.pixelSize: DesignTokens.font2xl
            font.weight: DesignTokens.weightSemiBold
            color: DesignTokens.textPrimary
            Layout.fillWidth: true
        }

        Text {
            text: "Ingresa tu token de SelladoMX para acceder a TSA profesional.\nFormato esperado: smx_xxxxxxxxxxxxx"
            font.pixelSize: DesignTokens.fontBase
            color: DesignTokens.textSecondary
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        TextField {
            id: tokenInput
            Layout.fillWidth: true
            Layout.preferredHeight: DesignTokens.inputDefault
            placeholderText: "Pega tu token aquí (smx_xxxxx...)"
            font.family: DesignTokens.fontFamilyMono
            font.pixelSize: DesignTokens.fontSm
            color: DesignTokens.textPrimary
            placeholderTextColor: DesignTokens.textTertiary

            background: Rectangle {
                color: DesignTokens.bgPrimary
                border.width: 2
                border.color: tokenInput.activeFocus ? DesignTokens.primary : DesignTokens.borderDefault
                radius: DesignTokens.radiusLg
            }

            onTextChanged: {
                validationSuccess = false
                validationMessage = ""
            }
        }

        Rectangle {
            visible: validationMessage !== ""
            Layout.fillWidth: true
            Layout.preferredHeight: resultText.implicitHeight + DesignTokens.md * 2
            radius: DesignTokens.radiusMd
            color: validationSuccess ? DesignTokens.successLight : DesignTokens.errorLight
            border.width: 2
            border.color: validationSuccess ? DesignTokens.success : DesignTokens.error

            Text {
                id: resultText
                anchors.fill: parent
                anchors.margins: DesignTokens.md
                text: validationMessage
                font.pixelSize: DesignTokens.fontBase
                color: validationSuccess ? DesignTokens.success : DesignTokens.error
                wrapMode: Text.WordWrap
                verticalAlignment: Text.AlignVCenter
            }
        }

        Item {
            Layout.fillHeight: true
        }

        Text {
            text: "💡 Consigue tu token en <a href='" + buyCreditsUrl + "' style='color: " + DesignTokens.primary + ";'>selladomx.com/precios</a>"
            font.pixelSize: DesignTokens.fontSm
            color: DesignTokens.textTertiary
            textFormat: Text.RichText
            wrapMode: Text.WordWrap
            Layout.fillWidth: true

            onLinkActivated: Qt.openUrlExternally(link)

            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.NoButton
                cursorShape: parent.hoveredLink ? Qt.PointingHandCursor : Qt.ArrowCursor
            }
        }

        // Buttons
        RowLayout {
            Layout.fillWidth: true
            spacing: DesignTokens.md

            ModernButton {
                text: "Cancelar"
                variant: "secondary"
                Layout.fillWidth: true
                onClicked: tokenDialog.reject()
            }

            ModernButton {
                text: isValidating ? "Validando..." : "Guardar"
                variant: "primary"
                enabled: tokenInput.text.length > 0 && !isValidating
                loading: isValidating
                Layout.fillWidth: true
                onClicked: {
                    validateAndSaveToken()
                }
            }
        }
    }

    function validateAndSaveToken() {
        var token = tokenInput.text.trim()

        if (token.length === 0) {
            validationMessage = "Por favor ingresa un token"
            validationSuccess = false
            return
        }

        var isValidFormat = /^(smx_[A-Za-z0-9]{5,}|[0-9a-fA-F]{64})$/.test(token)
        if (!isValidFormat) {
            validationMessage = "Formato de token inválido. Debe comenzar con 'smx_' o ser un hash de 64 caracteres."
            validationSuccess = false
            return
        }

        isValidating = true
        validationMessage = "Validando token con el servidor..."

        mainViewModel.validateAndSaveToken(token)
    }

    Connections {
        target: mainViewModel
        function onTokenValidationResult(success, message) {
            tokenDialog.isValidating = false
            tokenDialog.validationSuccess = success
            tokenDialog.validationMessage = message

            if (success) {
                closeTimer.start()
            }
        }
    }

    Timer {
        id: closeTimer
        interval: 1500
        onTriggered: tokenDialog.accept()
    }
}
