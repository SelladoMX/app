// HeaderBar.qml - Header with app title and credit balance
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../design"
import "../components"

Rectangle {
    id: header

    color: "transparent"
    implicitHeight: 60

    RowLayout {
        anchors.fill: parent
        spacing: DesignTokens.lg

        // App Logo/Title
        RowLayout {
            spacing: DesignTokens.md

            // App icon
            Image {
                source: appIconSource
                width: 40
                height: 40
                sourceSize.width: 40
                sourceSize.height: 40
                smooth: true
                mipmap: true
            }

            ColumnLayout {
                spacing: 0

                Text {
                    text: "SelladoMX"
                    font.pixelSize: DesignTokens.font2xl
                    font.weight: DesignTokens.weightBold
                    color: DesignTokens.textPrimary
                }

                Text {
                    text: "Firma Digital de PDFs"
                    font.pixelSize: DesignTokens.fontSm
                    color: DesignTokens.textSecondary
                }
            }
        }

        // Spacer
        Item {
            Layout.fillWidth: true
        }

        // Free tier upgrade prompt (when no token)
        Button {
            id: upgradeButton
            flat: true
            visible: !mainViewModel.hasProfessionalTSA

            contentItem: Text {
                text: "Usando TSA Básico • Mejorar validez legal →"
                font.pixelSize: DesignTokens.fontSm
                color: DesignTokens.textPrimary
                font.underline: true
            }

            background: Item {}

            onClicked: mainWindow.showBenefitsDialog()

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                acceptedButtons: Qt.NoButton
            }
        }

        // Credits display (when has token)
        Button {
            id: creditsButton
            flat: true
            visible: mainViewModel.hasProfessionalTSA

            contentItem: Rectangle {
                implicitWidth: creditLayout.implicitWidth + DesignTokens.lg * 2
                implicitHeight: 44
                radius: DesignTokens.radiusLg
                color: DesignTokens.primarySubtle
                border.width: 2
                border.color: DesignTokens.primary

                RowLayout {
                    id: creditLayout
                    anchors.centerIn: parent
                    spacing: DesignTokens.sm

                    Text {
                        text: "💰"
                        font.pixelSize: DesignTokens.fontXl
                    }

                    ColumnLayout {
                        spacing: 0

                        Text {
                            text: mainViewModel.creditBalance + " créditos"
                            font.pixelSize: DesignTokens.fontBase
                            font.weight: DesignTokens.weightSemiBold
                            color: DesignTokens.textPrimary
                        }

                        Text {
                            text: "TSA Profesional"
                            font.pixelSize: DesignTokens.fontXs
                            color: DesignTokens.textSecondary
                        }
                    }

                    ToolButton {
                        text: "↻"
                        font.pixelSize: DesignTokens.fontXl
                        onClicked: mainViewModel.refreshCreditBalance()

                        ToolTip.visible: hovered
                        ToolTip.text: "Actualizar balance"
                        ToolTip.delay: 500
                    }
                }
            }

            background: Item {}

            onClicked: {
                if (mainViewModel.creditBalance < 5) {
                    Qt.openUrlExternally(buyCreditsUrl)
                }
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: mainViewModel.creditBalance < 5 ? Qt.PointingHandCursor : Qt.ArrowCursor
                acceptedButtons: Qt.NoButton
            }
        }

        // Buy credits button (if no credits or low)
        ModernButton {
            visible: mainViewModel.hasProfessionalTSA && mainViewModel.creditBalance < 5
            text: mainViewModel.creditBalance === 0 ? "Comprar Créditos" : "💳 Comprar más"
            variant: mainViewModel.creditBalance === 0 ? "primary" : "secondary"
            onClicked: Qt.openUrlExternally(buyCreditsUrl)
        }

        // Configure token button (if no token)
        ModernButton {
            visible: !mainViewModel.hasProfessionalTSA
            text: "Configurar Token"
            variant: "secondary"
            onClicked: mainWindow.showTokenConfigDialog()
        }

        // Settings button (if has token)
        Button {
            visible: mainViewModel.hasProfessionalTSA
            text: "⚙️"
            font.pixelSize: DesignTokens.fontXl

            background: Rectangle {
                color: parent.hovered ? DesignTokens.bgHover : "transparent"
                radius: DesignTokens.radiusMd
            }

            onClicked: settingsMenu.open()

            Menu {
                id: settingsMenu
                y: parent.height

                MenuItem {
                    text: "Configurar token"
                    onTriggered: mainWindow.showTokenConfigDialog()
                }

                MenuItem {
                    text: "Administrar subtokens"
                    enabled: mainViewModel.hasProfessionalTSA && mainViewModel.isPrimaryToken
                    onTriggered: mainWindow.showTokenManagementDialog()
                }

                MenuSeparator {}

                MenuItem {
                    text: "Comprar créditos"
                    onTriggered: Qt.openUrlExternally(buyCreditsUrl)
                }
            }
        }
    }
}
