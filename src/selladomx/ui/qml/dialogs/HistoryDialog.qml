// HistoryDialog.qml - Document history dialog with pagination
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../design"
import "../components"

Dialog {
    id: historyDialog

    title: "Historial de Documentos Firmados"
    modal: true
    width: 900
    height: 700

    background: Rectangle {
        color: DesignTokens.bgPrimary
        radius: DesignTokens.radiusXl
        border.width: 1
        border.color: DesignTokens.borderDefault
    }

    property var viewModel: mainViewModel.historyViewModel

    onOpened: {
        if (viewModel && !viewModel.isLoading) {
            viewModel.loadHistory()
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: DesignTokens.lg

        // Header with refresh button
        RowLayout {
            Layout.fillWidth: true

            Text {
                text: "Documentos Firmados (" + (viewModel ? viewModel.totalCount : 0) + ")"
                font.pixelSize: DesignTokens.fontXl
                font.weight: DesignTokens.weightBold
                color: DesignTokens.textPrimary
                Layout.fillWidth: true
            }

            ModernButton {
                text: "Actualizar"
                variant: "secondary"
                enabled: viewModel && !viewModel.isLoading
                onClicked: viewModel.refresh()
            }
        }

        // Loading indicator
        BusyIndicator {
            visible: viewModel && viewModel.isLoading
            Layout.alignment: Qt.AlignHCenter
        }

        // Empty state
        ColumnLayout {
            visible: viewModel && !viewModel.isLoading && viewModel.totalCount === 0
            spacing: DesignTokens.md
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignCenter

            Text {
                text: "No hay documentos firmados"
                font.pixelSize: DesignTokens.fontLg
                color: DesignTokens.textSecondary
                Layout.alignment: Qt.AlignHCenter
            }

            Text {
                text: "Los documentos que firmes con TSA Profesional aparecerán aquí"
                font.pixelSize: DesignTokens.fontBase
                color: DesignTokens.textTertiary
                Layout.alignment: Qt.AlignHCenter
            }
        }

        // History table
        ScrollView {
            visible: viewModel && !viewModel.isLoading && viewModel.totalCount > 0
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            ListView {
                id: historyList
                model: viewModel ? viewModel.historyItems : []
                spacing: DesignTokens.sm

                delegate: Rectangle {
                    width: historyList.width
                    height: delegateColumn.implicitHeight + DesignTokens.md * 2
                    radius: DesignTokens.radiusLg
                    color: DesignTokens.bgSecondary
                    border.width: 1
                    border.color: DesignTokens.borderDefault

                    ColumnLayout {
                        id: delegateColumn
                        anchors.fill: parent
                        anchors.margins: DesignTokens.md
                        spacing: DesignTokens.xs

                        // Filename
                        Text {
                            text: modelData.filename || "Sin nombre"
                            font.pixelSize: DesignTokens.fontBase
                            font.weight: DesignTokens.weightSemiBold
                            color: DesignTokens.textPrimary
                            elide: Text.ElideMiddle
                            Layout.fillWidth: true
                        }

                        // Timestamp & size
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: DesignTokens.md

                            Text {
                                text: formatTimestamp(modelData.timestamp_utc)
                                font.pixelSize: DesignTokens.fontSm
                                color: DesignTokens.textSecondary
                            }

                            Text {
                                text: formatFileSize(modelData.file_size)
                                font.pixelSize: DesignTokens.fontSm
                                color: DesignTokens.textSecondary
                                visible: modelData.file_size > 0
                            }
                        }

                        // Signer info
                        Text {
                            text: "Firmado por: " + (modelData.signer_cn || "Sin información del firmante")
                            font.pixelSize: DesignTokens.fontSm
                            color: DesignTokens.textTertiary
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                            visible: modelData.signer_cn
                        }

                        // Verification URL
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: DesignTokens.sm

                            Text {
                                property string verifyUrl: "https://www.selladomx.com/verify/" + modelData.verification_token
                                text: "<a href='" + verifyUrl + "'>Ver certificado de validez</a>"
                                textFormat: Text.RichText
                                font.pixelSize: DesignTokens.fontSm
                                color: DesignTokens.info
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

                            ModernButton {
                                text: "Copiar"
                                variant: "secondary"
                                onClicked: {
                                    var verifyUrl = "https://www.selladomx.com/verify/" + modelData.verification_token
                                    clipboardHelper.text = verifyUrl
                                    clipboardHelper.selectAll()
                                    clipboardHelper.copy()
                                }
                            }
                        }
                    }
                }
            }
        }

        // Pagination controls
        RowLayout {
            visible: viewModel && viewModel.totalPages > 1
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignHCenter
            spacing: DesignTokens.md

            ModernButton {
                text: "← Anterior"
                variant: "secondary"
                enabled: viewModel && viewModel.currentPage > 1
                onClicked: viewModel.previousPage()
            }

            Text {
                text: "Página " + (viewModel ? viewModel.currentPage : 1) + " de " + (viewModel ? viewModel.totalPages : 1)
                font.pixelSize: DesignTokens.fontBase
                color: DesignTokens.textPrimary
            }

            ModernButton {
                text: "Siguiente →"
                variant: "secondary"
                enabled: viewModel && viewModel.currentPage < viewModel.totalPages
                onClicked: viewModel.nextPage()
            }
        }

        // Close button
        ModernButton {
            text: "Cerrar"
            variant: "primary"
            Layout.fillWidth: true
            onClicked: historyDialog.close()
        }
    }

    // Hidden TextEdit for clipboard operations
    TextEdit {
        id: clipboardHelper
        visible: false
    }

    // Error handling
    Connections {
        target: viewModel
        function onErrorOccurred(message) {
            errorText.text = message
            errorText.visible = true
            errorTimer.start()
        }
    }

    // Error message display
    Rectangle {
        id: errorMessage
        visible: errorText.visible
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: DesignTokens.md
        width: parent.width - DesignTokens.lg * 2
        height: errorText.implicitHeight + DesignTokens.md * 2
        radius: DesignTokens.radiusMd
        color: DesignTokens.errorLight
        border.width: 2
        border.color: DesignTokens.error
        z: 1000

        Text {
            id: errorText
            anchors.fill: parent
            anchors.margins: DesignTokens.md
            visible: false
            font.pixelSize: DesignTokens.fontBase
            color: DesignTokens.error
            wrapMode: Text.WordWrap
            verticalAlignment: Text.AlignVCenter
        }

        Timer {
            id: errorTimer
            interval: 5000
            onTriggered: errorText.visible = false
        }
    }

    // Helper functions
    function formatTimestamp(timestamp) {
        if (!timestamp) return "Sin fecha"
        var date = new Date(timestamp)
        return Qt.formatDateTime(date, "dd/MM/yyyy hh:mm")
    }

    function formatFileSize(bytes) {
        if (!bytes || bytes === 0) return ""
        return "Tamaño: " + (bytes / 1024).toFixed(1) + " KB"
    }
}
