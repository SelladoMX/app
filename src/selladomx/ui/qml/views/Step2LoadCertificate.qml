// Step2LoadCertificate.qml - Certificate and private key loading step
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs
import QtCore
import "../design"
import "../components"

StepIndicator {
    id: step2

    stepNumber: 2
    stepTitle: "Cargar Certificado"
    stepDescription: "Selecciona tu certificado e.firma y llave privada"
    stepState: {
        if (!mainViewModel.step1Complete) return "disabled"
        if (mainViewModel.step2Complete) return "completed"
        return "active"
    }

    content: ColumnLayout {
        spacing: DesignTokens.lg

        // Certificate file (.cer)
        RowLayout {
            spacing: DesignTokens.md
            Layout.fillWidth: true

            Text {
                text: "Certificado (.cer):"
                font.pixelSize: DesignTokens.fontBase
                color: DesignTokens.textPrimary
                Layout.preferredWidth: 140
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: DesignTokens.inputDefault
                radius: DesignTokens.radiusLg
                color: DesignTokens.surfaceDefault
                border.width: 2
                border.color: certPathField.activeFocus ? DesignTokens.primary : DesignTokens.borderDefault

                Behavior on border.color {
                    ColorAnimation { duration: DesignTokens.durationFast }
                }

                TextInput {
                    id: certPathField
                    anchors.fill: parent
                    anchors.margins: DesignTokens.md
                    verticalAlignment: TextInput.AlignVCenter
                    font.pixelSize: DesignTokens.fontBase
                    color: DesignTokens.textPrimary
                    readOnly: true
                    text: {
                        var path = mainViewModel.certPath
                        if (!path) return ""
                        var lastSlash = Math.max(path.lastIndexOf("/"), path.lastIndexOf("\\"))
                        return lastSlash >= 0 ? path.substring(lastSlash + 1) : path
                    }

                    Text {
                        visible: !parent.text
                        anchors.fill: parent
                        verticalAlignment: Text.AlignVCenter
                        text: "Selecciona tu certificado..."
                        color: DesignTokens.textTertiary
                        font.pixelSize: DesignTokens.fontBase
                    }
                }
            }

            ModernButton {
                text: "Seleccionar"
                variant: "secondary"
                onClicked: certDialog.open()
            }
        }

        // Private key file (.key)
        RowLayout {
            spacing: DesignTokens.md
            Layout.fillWidth: true

            Text {
                text: "Clave privada (.key):"
                font.pixelSize: DesignTokens.fontBase
                color: DesignTokens.textPrimary
                Layout.preferredWidth: 140
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: DesignTokens.inputDefault
                radius: DesignTokens.radiusLg
                color: DesignTokens.surfaceDefault
                border.width: 2
                border.color: keyPathField.activeFocus ? DesignTokens.primary : DesignTokens.borderDefault

                Behavior on border.color {
                    ColorAnimation { duration: DesignTokens.durationFast }
                }

                TextInput {
                    id: keyPathField
                    anchors.fill: parent
                    anchors.margins: DesignTokens.md
                    verticalAlignment: TextInput.AlignVCenter
                    font.pixelSize: DesignTokens.fontBase
                    color: DesignTokens.textPrimary
                    readOnly: true
                    text: {
                        var path = mainViewModel.keyPath
                        if (!path) return ""
                        var lastSlash = Math.max(path.lastIndexOf("/"), path.lastIndexOf("\\"))
                        return lastSlash >= 0 ? path.substring(lastSlash + 1) : path
                    }

                    Text {
                        visible: !parent.text
                        anchors.fill: parent
                        verticalAlignment: Text.AlignVCenter
                        text: "Selecciona tu llave privada..."
                        color: DesignTokens.textTertiary
                        font.pixelSize: DesignTokens.fontBase
                    }
                }
            }

            ModernButton {
                text: "Seleccionar"
                variant: "secondary"
                onClicked: keyDialog.open()
            }
        }

        // Password field
        RowLayout {
            spacing: DesignTokens.md
            Layout.fillWidth: true

            Text {
                text: "Contraseña:"
                font.pixelSize: DesignTokens.fontBase
                color: DesignTokens.textPrimary
                Layout.preferredWidth: 140
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: DesignTokens.inputDefault
                radius: DesignTokens.radiusLg
                color: DesignTokens.surfaceDefault
                border.width: 2
                border.color: passwordField.activeFocus ? DesignTokens.primary : DesignTokens.borderDefault

                Behavior on border.color {
                    ColorAnimation { duration: DesignTokens.durationFast }
                }

                TextInput {
                    id: passwordField
                    anchors.fill: parent
                    anchors.margins: DesignTokens.md
                    verticalAlignment: TextInput.AlignVCenter
                    font.pixelSize: DesignTokens.fontBase
                    color: DesignTokens.textPrimary
                    echoMode: TextInput.Password
                    enabled: mainViewModel.certPath && mainViewModel.keyPath

                    onTextChanged: {
                        // Auto-validate when password is entered and both files are selected
                        if (mainViewModel.certPath && mainViewModel.keyPath && text.length > 0) {
                            validateTimer.restart()
                        }
                    }

                    Text {
                        visible: !parent.text && parent.enabled
                        anchors.fill: parent
                        verticalAlignment: Text.AlignVCenter
                        text: "Ingresa tu contraseña..."
                        color: DesignTokens.textTertiary
                        font.pixelSize: DesignTokens.fontBase
                    }

                    // Timer to debounce validation
                    Timer {
                        id: validateTimer
                        interval: 500
                        repeat: false
                        onTriggered: {
                            mainViewModel.loadCertificate(
                                mainViewModel.certPath,
                                mainViewModel.keyPath,
                                passwordField.text
                            )
                        }
                    }
                }
            }

            // Show/hide password button
            ToolButton {
                text: passwordField.echoMode === TextInput.Password ? "👁" : "👁‍🗨"
                font.pixelSize: DesignTokens.fontXl
                onClicked: {
                    passwordField.echoMode = passwordField.echoMode === TextInput.Password
                        ? TextInput.Normal
                        : TextInput.Password
                }

                ToolTip.visible: hovered
                ToolTip.text: passwordField.echoMode === TextInput.Password ? "Mostrar" : "Ocultar"
                ToolTip.delay: 500
            }
        }

        // Validation status
        Rectangle {
            visible: mainViewModel.certStatus !== "No se ha cargado certificado"
            Layout.fillWidth: true
            Layout.preferredHeight: statusText.implicitHeight + DesignTokens.md * 2
            radius: DesignTokens.radiusLg
            color: mainViewModel.step2Complete ? DesignTokens.successLight : DesignTokens.errorLight
            border.width: 2
            border.color: mainViewModel.step2Complete ? DesignTokens.success : DesignTokens.error

            Behavior on color {
                ColorAnimation { duration: DesignTokens.durationNormal }
            }
            Behavior on border.color {
                ColorAnimation { duration: DesignTokens.durationNormal }
            }

            Text {
                id: statusText
                anchors.fill: parent
                anchors.margins: DesignTokens.md
                text: mainViewModel.certStatus
                font.pixelSize: DesignTokens.fontBase
                color: mainViewModel.certStatusColor
                wrapMode: Text.WordWrap
                verticalAlignment: Text.AlignVCenter
            }
        }

        // Info text
        Text {
            text: "🔒 Tu contraseña es procesada localmente y nunca se envía a ningún servidor"
            font.pixelSize: DesignTokens.fontSm
            color: DesignTokens.textTertiary
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
    }

    // File dialogs
    FileDialog {
        id: certDialog
        title: "Seleccionar certificado"
        currentFolder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
        fileMode: FileDialog.OpenFile
        nameFilters: ["Certificados (*.cer *.pem *.crt)", "Todos los archivos (*)"]

        onAccepted: {
            mainViewModel.setCertPath(selectedFile.toString())
        }
    }

    FileDialog {
        id: keyDialog
        title: "Seleccionar clave privada"
        currentFolder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
        fileMode: FileDialog.OpenFile
        nameFilters: ["Claves privadas (*.key *.pem)", "Todos los archivos (*)"]

        onAccepted: {
            mainViewModel.setKeyPath(selectedFile.toString())
        }
    }
}
