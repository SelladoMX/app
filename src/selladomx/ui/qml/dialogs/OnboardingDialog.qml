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
    height: 520

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

                    Item { Layout.preferredHeight: DesignTokens.xl }

                    Image {
                        source: appIconSource
                        Layout.preferredWidth: 72
                        Layout.preferredHeight: 72
                        sourceSize.width: 72
                        sourceSize.height: 72
                        smooth: true
                        mipmap: true
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
                        text: "Firma tus PDFs sin subir archivos a la nube"
                        font.pixelSize: DesignTokens.fontLg
                        color: DesignTokens.textSecondary
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                    }

                    Item { Layout.preferredHeight: DesignTokens.xl }

                    Text {
                        text: "Firma tus documentos PDF con certificados digitales de forma segura.\n\nLa firma se aplica localmente en tu computadora. Tus documentos nunca se envían a servidores externos."
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

            // Slide 3: Choose protection level
            Item {
                ColumnLayout {
                    anchors.centerIn: parent
                    width: parent.width - 80
                    spacing: DesignTokens.md

                    Text {
                        text: "Elige tu nivel de protección"
                        font.pixelSize: DesignTokens.font3xl
                        font.weight: DesignTokens.weightBold
                        color: DesignTokens.textPrimary
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                    }

                    Text {
                        text: "Ambas opciones firman tus documentos. La diferencia es el respaldo legal."
                        font.pixelSize: DesignTokens.fontMd
                        color: DesignTokens.textSecondary
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                    }

                    Item { Layout.preferredHeight: DesignTokens.sm }

                    // Comparison boxes
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: DesignTokens.md

                        // Professional TSA
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: proContent.implicitHeight + DesignTokens.md * 2
                            radius: DesignTokens.radiusLg
                            color: DesignTokens.accentLight
                            border.width: 2
                            border.color: DesignTokens.accent

                            ColumnLayout {
                                id: proContent
                                anchors.fill: parent
                                anchors.margins: DesignTokens.md
                                spacing: DesignTokens.xs

                                Text {
                                    text: "Protección mejorada"
                                    font.pixelSize: DesignTokens.fontBase
                                    font.weight: DesignTokens.weightBold
                                    color: DesignTokens.accent
                                }

                                Repeater {
                                    model: [
                                        "✓ Máxima validez legal",
                                        "✓ Cumple NOM-151 y eIDAS",
                                        "✓ Evidencia admisible en juicios",
                                        "✓ Proveedor europeo certificado",
                                        "✓ " + creditPriceDisplay + " por documento"
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

                        // Basic TSA
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: freeContent.implicitHeight + DesignTokens.md * 2
                            radius: DesignTokens.radiusLg
                            color: DesignTokens.bgSecondary
                            border.width: 1
                            border.color: DesignTokens.borderDefault

                            ColumnLayout {
                                id: freeContent
                                anchors.fill: parent
                                anchors.margins: DesignTokens.md
                                spacing: DesignTokens.xs

                                Text {
                                    text: "Firma básica"
                                    font.pixelSize: DesignTokens.fontBase
                                    font.weight: DesignTokens.weightBold
                                    color: DesignTokens.textSecondary
                                }

                                Repeater {
                                    model: [
                                        "• Validez legal básica",
                                        "• Sello de tiempo de proveedor público",
                                        "• Adecuado para uso personal",
                                        "• Aceptación limitada en procesos formales",
                                        "• Gratis"
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

                    Item { Layout.preferredHeight: DesignTokens.xs }

                    Text {
                        text: "💡 Recomendamos protección mejorada para contratos, facturas y trámites oficiales"
                        font.pixelSize: DesignTokens.fontSm
                        font.weight: DesignTokens.weightMedium
                        color: DesignTokens.primary
                        Layout.fillWidth: true
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                    }
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

                ModernButton {
                    text: "Anterior"
                    variant: "secondary"
                    visible: currentSlide > 0
                    onClicked: currentSlide--
                }

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
