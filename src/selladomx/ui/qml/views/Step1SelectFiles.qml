import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs
import QtCore
import "../design"
import "../components"

StepIndicator {
    id: step1

    stepNumber: 1
    stepTitle: "Seleccionar PDFs"
    stepDescription: "Agrega los documentos que deseas firmar"
    stepState: mainViewModel.step1Complete ? "completed" : "active"

    content: ColumnLayout {
        spacing: DesignTokens.md

        // File list with drag & drop area
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 200
            color: DesignTokens.surfaceDefault
            radius: DesignTokens.radiusXl
            border.width: 2
            border.color: dropArea.containsDrag ? DesignTokens.primary : DesignTokens.borderDefault

            Behavior on border.color {
                ColorAnimation { duration: DesignTokens.durationFast }
            }

            ListView {
                id: fileListView
                anchors.fill: parent
                anchors.margins: DesignTokens.md
                clip: true
                spacing: DesignTokens.xs

                model: mainViewModel.pdfFiles

                delegate: Rectangle {
                    width: fileListView.width
                    height: 40
                    radius: DesignTokens.radiusMd
                    color: mouseArea.containsMouse ? DesignTokens.bgHover : "transparent"

                    Behavior on color {
                        ColorAnimation { duration: DesignTokens.durationFast }
                    }

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: DesignTokens.sm
                        spacing: DesignTokens.sm

                        Text {
                            text: "📄"
                            font.pixelSize: DesignTokens.fontXl
                        }

                        // Filename
                        Text {
                            Layout.fillWidth: true
                            text: {
                                var path = modelData
                                var lastSlash = Math.max(path.lastIndexOf("/"), path.lastIndexOf("\\"))
                                return lastSlash >= 0 ? path.substring(lastSlash + 1) : path
                            }
                            color: DesignTokens.textPrimary
                            elide: Text.ElideMiddle
                            font.pixelSize: DesignTokens.fontBase
                        }

                        ToolButton {
                            text: "✕"
                            font.pixelSize: DesignTokens.fontLg
                            onClicked: mainViewModel.removePdfAt(index)

                            ToolTip.visible: hovered
                            ToolTip.text: "Eliminar"
                            ToolTip.delay: 500
                        }
                    }

                    MouseArea {
                        id: mouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        acceptedButtons: Qt.NoButton  // Don't intercept clicks
                    }
                }

                // Empty state
                Item {
                    visible: fileListView.count === 0
                    anchors.fill: parent

                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: DesignTokens.md

                        Text {
                            text: "📂"
                            font.pixelSize: DesignTokens.font4xl
                            Layout.alignment: Qt.AlignHCenter
                        }

                        Text {
                            text: "Arrastra PDFs aquí o haz clic en Agregar"
                            color: DesignTokens.textSecondary
                            font.pixelSize: DesignTokens.fontBase
                            Layout.alignment: Qt.AlignHCenter
                        }
                    }
                }
            }

            DropArea {
                id: dropArea
                anchors.fill: parent

                onDropped: {
                    if (drop.hasUrls) {
                        var pdfUrls = []
                        for (var i = 0; i < drop.urls.length; i++) {
                            var url = drop.urls[i].toString()
                            if (url.toLowerCase().endsWith('.pdf')) {
                                pdfUrls.push(url)
                            }
                        }
                        if (pdfUrls.length > 0) {
                            mainViewModel.addPdfFiles(pdfUrls)
                        }
                    }
                }

                // Visual feedback
                Rectangle {
                    anchors.fill: parent
                    color: DesignTokens.primary
                    opacity: dropArea.containsDrag ? 0.1 : 0
                    radius: DesignTokens.radiusXl

                    Behavior on opacity {
                        NumberAnimation { duration: DesignTokens.durationFast }
                    }
                }
            }
        }

        // File count and cost estimation
        Rectangle {
            visible: mainViewModel.pdfCount > 0
            Layout.fillWidth: true
            Layout.preferredHeight: costLayout.implicitHeight + DesignTokens.sm * 2
            radius: DesignTokens.radiusMd
            color: DesignTokens.primarySubtle
            border.width: 1
            border.color: DesignTokens.primary

            RowLayout {
                id: costLayout
                anchors.fill: parent
                anchors.margins: DesignTokens.sm
                spacing: DesignTokens.md

                Text {
                    text: "📊"
                    font.pixelSize: DesignTokens.fontXl
                }

                Text {
                    text: mainViewModel.pdfCount + " archivo(s) seleccionado(s)"
                    font.pixelSize: DesignTokens.fontBase
                    color: DesignTokens.textPrimary
                    font.weight: DesignTokens.weightMedium
                }

                Item { Layout.fillWidth: true }

                Text {
                    visible: mainViewModel.pdfCount > 0
                    text: "💰 Costo con protección mejorada: " + mainViewModel.pdfCount + " × $2 = $" + (mainViewModel.pdfCount * 2) + " MXN"
                    font.pixelSize: DesignTokens.fontSm
                    color: DesignTokens.primary
                    font.weight: DesignTokens.weightSemiBold
                }
            }
        }

        // Action buttons
        RowLayout {
            spacing: DesignTokens.md

            ModernButton {
                text: "Agregar PDFs..."
                variant: "primary"
                onClicked: fileDialog.open()
            }

            ModernButton {
                text: "Limpiar lista"
                variant: "secondary"
                enabled: mainViewModel.pdfCount > 0
                onClicked: mainViewModel.clearPdfList()
            }
        }

        Text {
            text: "💡 Puedes seleccionar múltiples archivos o arrastrarlos a la lista"
            font.pixelSize: DesignTokens.fontSm
            color: DesignTokens.textTertiary
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }
    }

    FileDialog {
        id: fileDialog
        title: "Seleccionar archivos PDF"
        currentFolder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
        fileMode: FileDialog.OpenFiles
        nameFilters: ["Archivos PDF (*.pdf)", "Todos los archivos (*)"]

        onAccepted: {
            mainViewModel.addPdfFiles(selectedFiles)
        }
    }

}
