// OnboardingDialog.qml - Modern onboarding wizard
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../design"
import "../components"

Dialog {
    id: onboardingDialog

    property int currentSlide: 0
    property int totalSlides: 4

    title: "Bienvenido a SelladoMX"
    modal: true
    closePolicy: Popup.NoAutoClose

    width: 700
    height: 500

    anchors.centerIn: parent

    background: Rectangle {
        color: DesignTokens.bgPrimary
        radius: DesignTokens.radiusXxl
        border.width: 1
        border.color: DesignTokens.borderDefault
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Slides container
        StackLayout {
            id: slidesStack
            currentIndex: currentSlide
            Layout.fillWidth: true
            Layout.fillHeight: true

            // Slide 1: Welcome
            Item {
                ColumnLayout {
                    anchors.centerIn: parent
                    width: parent.width - 100
                    spacing: DesignTokens.lg

                    Item { Layout.preferredHeight: DesignTokens.xxl }

                    Text {
                        text: "🔐"
                        font.pixelSize: 56
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Text {
                        text: "Bienvenido a SelladoMX"
                        font.pixelSize: DesignTokens.font3xl
                        font.weight: DesignTokens.weightSemiBold
                        color: DesignTokens.textPrimary
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                    }

                    Text {
                        text: "Firma digital 100% local"
                        font.pixelSize: DesignTokens.fontLg
                        color: DesignTokens.textSecondary
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                    }

                    Item { Layout.preferredHeight: DesignTokens.xxl }

                    Text {
                        text: "Firma tus documentos PDF con certificados digitales sin enviar datos a servidores externos.\n\nTodo el procesamiento ocurre localmente en tu computadora."
                        font.pixelSize: DesignTokens.fontMd
                        color: DesignTokens.textPrimary
                        lineHeight: 1.5
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                    }

                    Item { Layout.fillHeight: true }
                }
            }

            // Slide 2: Security
            Item {
                ColumnLayout {
                    anchors.centerIn: parent
                    width: parent.width - 100
                    spacing: DesignTokens.lg

                    Item { Layout.preferredHeight: DesignTokens.xl }

                    Text {
                        text: "🔒"
                        font.pixelSize: 56
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Text {
                        text: "Tu privacidad es nuestra prioridad"
                        font.pixelSize: DesignTokens.font3xl
                        font.weight: DesignTokens.weightSemiBold
                        color: DesignTokens.textPrimary
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                    }

                    Item { Layout.preferredHeight: DesignTokens.xxl }

                    // Security features
                    Repeater {
                        model: [
                            "Tus claves privadas nunca salen de tu computadora",
                            "Código 100% open source y auditable",
                            "Procesamiento completamente local",
                            "Los datos se limpian de memoria al cerrar"
                        ]

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: DesignTokens.md
                            Layout.leftMargin: DesignTokens.xl
                            Layout.rightMargin: DesignTokens.xl

                            Text {
                                text: "•"
                                font.pixelSize: DesignTokens.fontXl
                                color: DesignTokens.primary
                                Layout.preferredWidth: DesignTokens.xl
                            }

                            Text {
                                text: modelData
                                font.pixelSize: DesignTokens.fontMd
                                color: DesignTokens.textPrimary
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                            }
                        }
                    }

                    Item { Layout.fillHeight: true }
                }
            }

            // Slide 3: Professional TSA
            Item {
                ColumnLayout {
                    anchors.centerIn: parent
                    width: parent.width - 100
                    spacing: DesignTokens.lg

                    Item { Layout.preferredHeight: DesignTokens.sm }

                    Text {
                        text: "⚖️"
                        font.pixelSize: 72
                        Layout.alignment: Qt.AlignHCenter
                    }

                    Text {
                        text: "¿Necesitas Validez Legal?"
                        font.pixelSize: DesignTokens.font4xl
                        font.weight: DesignTokens.weightBold
                        color: DesignTokens.textPrimary
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                        lineHeight: 1.2
                    }

                    Item { Layout.preferredHeight: DesignTokens.xl }

                    // Comparison boxes
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: DesignTokens.lg

                        // Professional TSA
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: proContent.implicitHeight + DesignTokens.lg * 2
                            radius: DesignTokens.radiusLg
                            color: DesignTokens.successLight
                            border.width: 2
                            border.color: DesignTokens.primary

                            ColumnLayout {
                                id: proContent
                                anchors.fill: parent
                                anchors.margins: DesignTokens.lg
                                spacing: DesignTokens.sm

                                Text {
                                    text: "TSA Profesional"
                                    font.pixelSize: DesignTokens.fontLg
                                    font.weight: DesignTokens.weightBold
                                    color: DesignTokens.primary
                                }

                                Repeater {
                                    model: [
                                        "✓ Certificación oficial RFC 3161",
                                        "✓ Evidencia admisible en juicios",
                                        "✓ Cumplimiento NOM-151-SCFI-2016",
                                        "✓ Solo $2 MXN por documento"
                                    ]

                                    Text {
                                        text: modelData
                                        font.pixelSize: DesignTokens.fontSm
                                        color: DesignTokens.textPrimary
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }
                                }
                            }
                        }

                        // Free TSA
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: freeContent.implicitHeight + DesignTokens.lg * 2
                            radius: DesignTokens.radiusLg
                            color: DesignTokens.bgSecondary
                            border.width: 2
                            border.color: DesignTokens.borderDefault

                            ColumnLayout {
                                id: freeContent
                                anchors.fill: parent
                                anchors.margins: DesignTokens.lg
                                spacing: DesignTokens.sm

                                Text {
                                    text: "TSA Gratuito (Limitado)"
                                    font.pixelSize: DesignTokens.fontLg
                                    font.weight: DesignTokens.weightBold
                                    color: DesignTokens.textTertiary
                                }

                                Repeater {
                                    model: [
                                        "• Solo para uso personal e informal",
                                        "• ⚠️ Sin garantía de validez legal",
                                        "• ❌ No aceptado en procesos legales",
                                        "• No recomendado para negocios"
                                    ]

                                    Text {
                                        text: modelData
                                        font.pixelSize: DesignTokens.fontSm
                                        color: DesignTokens.textSecondary
                                        wrapMode: Text.WordWrap
                                        Layout.fillWidth: true
                                    }
                                }
                            }
                        }
                    }

                    Text {
                        text: "💡 Recomendación: Usa TSA Profesional para documentos importantes como contratos, facturas o trámites oficiales"
                        font.pixelSize: DesignTokens.fontMd
                        font.weight: DesignTokens.weightMedium
                        color: DesignTokens.primary
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                    }

                    Item { Layout.fillHeight: true }
                }
            }

            // Slide 4: How To
            Item {
                ColumnLayout {
                    anchors.centerIn: parent
                    width: parent.width - 100
                    spacing: DesignTokens.lg

                    Item { Layout.preferredHeight: DesignTokens.xl }

                    Text {
                        text: "Cómo funciona"
                        font.pixelSize: DesignTokens.font3xl
                        font.weight: DesignTokens.weightSemiBold
                        color: DesignTokens.textPrimary
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                    }

                    Text {
                        text: "3 pasos simples"
                        font.pixelSize: DesignTokens.fontLg
                        color: DesignTokens.textSecondary
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                    }

                    Item { Layout.preferredHeight: DesignTokens.xxl }

                    // Steps
                    Repeater {
                        model: [
                            { number: "1.", text: "Selecciona los PDFs que deseas firmar" },
                            { number: "2.", text: "Carga tu certificado e.firma (.cer y .key)" },
                            { number: "3.", text: "Haz clic en 'Firmar' y listo" }
                        ]

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: DesignTokens.md
                            Layout.leftMargin: DesignTokens.xl
                            Layout.rightMargin: DesignTokens.xl

                            Text {
                                text: modelData.number
                                font.pixelSize: DesignTokens.fontXl
                                font.weight: DesignTokens.weightSemiBold
                                color: DesignTokens.primary
                                Layout.preferredWidth: DesignTokens.xxl
                            }

                            Text {
                                text: modelData.text
                                font.pixelSize: DesignTokens.fontMd
                                color: DesignTokens.textPrimary
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                            }
                        }
                    }

                    Item { Layout.preferredHeight: DesignTokens.xl }

                    Text {
                        text: "Tus documentos nunca salen de tu computadora."
                        font.pixelSize: DesignTokens.fontMd
                        font.italic: true
                        color: DesignTokens.textSecondary
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                    }

                    Item { Layout.fillHeight: true }
                }
            }
        }

        // Navigation footer
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: navLayout.implicitHeight + DesignTokens.lg * 2
            color: DesignTokens.bgSecondary
            radius: DesignTokens.radiusXxl

            Rectangle {
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: 1
                color: DesignTokens.borderDefault
            }

            RowLayout {
                id: navLayout
                anchors.fill: parent
                anchors.margins: DesignTokens.lg
                spacing: DesignTokens.md

                // Skip button
                Button {
                    text: "Omitir"
                    flat: true
                    visible: currentSlide < totalSlides - 1

                    contentItem: Text {
                        text: parent.text
                        font.pixelSize: DesignTokens.fontBase
                        color: DesignTokens.textTertiary
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        color: "transparent"
                    }

                    onClicked: onboardingDialog.accept()
                }

                Item { Layout.fillWidth: true }

                // Dots indicator
                RowLayout {
                    spacing: DesignTokens.xs

                    Repeater {
                        model: totalSlides

                        Rectangle {
                            width: 8
                            height: 8
                            radius: 4
                            color: index === currentSlide ? DesignTokens.primary : DesignTokens.borderDefault

                            Behavior on color {
                                ColorAnimation { duration: DesignTokens.durationFast }
                            }
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                // Previous button
                ModernButton {
                    text: "Anterior"
                    variant: "secondary"
                    visible: currentSlide > 0
                    onClicked: currentSlide--
                }

                // Next/Finish button
                ModernButton {
                    text: currentSlide < totalSlides - 1 ? "Siguiente" : "Comenzar"
                    variant: "primary"
                    onClicked: {
                        if (currentSlide < totalSlides - 1) {
                            currentSlide++
                        } else {
                            onboardingDialog.accept()
                        }
                    }
                }
            }
        }
    }
}
