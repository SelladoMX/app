// UpdateAvailableDialog.qml - Shown when a newer version is available
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../design"
import "../components"

Dialog {
    id: updateDialog

    property string latestVersion: ""
    property string downloadUrl: ""

    title: "Actualización disponible"
    modal: true

    width: 460
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

        Text {
            text: "Nueva versión disponible"
            font.pixelSize: DesignTokens.font2xl
            font.weight: DesignTokens.weightBold
            color: DesignTokens.textPrimary
            Layout.fillWidth: true
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: versionLayout.implicitHeight + DesignTokens.md * 2
            radius: DesignTokens.radiusLg
            color: DesignTokens.infoLight
            border.width: 1
            border.color: DesignTokens.info

            ColumnLayout {
                id: versionLayout
                anchors.fill: parent
                anchors.margins: DesignTokens.md
                spacing: DesignTokens.xs

                Text {
                    text: "Versión actual: " + appVersion
                    font.pixelSize: DesignTokens.fontBase
                    color: DesignTokens.textSecondary
                }

                Text {
                    text: "Versión disponible: " + updateDialog.latestVersion
                    font.pixelSize: DesignTokens.fontBase
                    font.weight: DesignTokens.weightSemiBold
                    color: DesignTokens.info
                }
            }
        }

        Text {
            text: "Se recomienda actualizar para obtener las últimas mejoras y correcciones."
            font.pixelSize: DesignTokens.fontBase
            color: DesignTokens.textSecondary
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
        }

        Item {
            Layout.fillHeight: true
            Layout.minimumHeight: DesignTokens.sm
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: DesignTokens.md

            ModernButton {
                text: "Ahora no"
                variant: "secondary"
                Layout.fillWidth: true
                onClicked: updateDialog.close()
            }

            ModernButton {
                text: "Descargar"
                variant: "primary"
                Layout.fillWidth: true
                onClicked: {
                    Qt.openUrlExternally(updateDialog.downloadUrl)
                    updateDialog.close()
                }
            }
        }
    }
}
