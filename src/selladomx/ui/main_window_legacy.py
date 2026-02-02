"""Ventana principal de la aplicación"""
import logging
from pathlib import Path
from typing import Optional, List

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QListWidget, QLineEdit, QProgressBar, QTextEdit,
    QLabel, QFileDialog, QMessageBox, QApplication
)

from ..signing.certificate_validator import CertificateValidator
from ..signing.pdf_signer import PDFSigner
from ..signing.tsa import TSAClient
from ..errors import (
    CertificateError, CertificateExpiredError, CertificateRevokedError,
    SigningError, SelladoMXError
)

logger = logging.getLogger(__name__)


class SigningWorker(QThread):
    """Worker thread para firmar PDFs sin bloquear la UI"""

    progress = Signal(int, int)  # current, total
    file_completed = Signal(str, bool, str)  # filename, success, message
    finished = Signal(list)  # Lista de errores

    def __init__(
        self,
        pdf_paths: List[Path],
        cert,
        private_key,
        tsa_client: Optional[TSAClient] = None,
        output_dir: Optional[Path] = None
    ):
        super().__init__()
        self.pdf_paths = pdf_paths
        self.cert = cert
        self.private_key = private_key
        self.tsa_client = tsa_client
        self.output_dir = output_dir
        self.errors = []

    def run(self):
        """Firma todos los PDFs secuencialmente"""
        signer = PDFSigner(self.cert, self.private_key, self.tsa_client)
        total = len(self.pdf_paths)

        for i, pdf_path in enumerate(self.pdf_paths, 1):
            self.progress.emit(i, total)

            try:
                # Calcular output_path si se especificó un directorio de destino
                if self.output_dir:
                    from ..config import SIGNED_SUFFIX
                    output_path = self.output_dir / f"{pdf_path.stem}{SIGNED_SUFFIX}{pdf_path.suffix}"
                else:
                    output_path = None  # Usar default (misma carpeta)

                output_path = signer.sign_pdf(pdf_path, output_path)
                self.file_completed.emit(
                    pdf_path.name,
                    True,
                    f"Firmado exitosamente: {output_path.name}"
                )
            except Exception as e:
                error_msg = str(e)
                self.errors.append(f"{pdf_path.name}: {error_msg}")
                self.file_completed.emit(pdf_path.name, False, error_msg)
                logger.error(f"Error signing {pdf_path.name}: {e}")

        self.finished.emit(self.errors)


class MainWindow(QMainWindow):
    """Ventana principal de SelladoMX"""

    def __init__(self):
        super().__init__()
        self.cert = None
        self.private_key = None
        self.signing_worker = None

        self._setup_ui()
        self._connect_signals()

        logger.info("MainWindow initialized")

    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setWindowTitle("SelladoMX - Firma Digital de PDFs")
        self.resize(900, 700)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Grupo: Archivos PDF
        files_group = QGroupBox("Archivos PDF")
        files_layout = QVBoxLayout()

        self.list_pdfs = QListWidget()
        files_layout.addWidget(self.list_pdfs)

        files_buttons_layout = QHBoxLayout()
        self.btn_add_files = QPushButton("Agregar PDFs...")
        self.btn_clear_files = QPushButton("Limpiar lista")
        files_buttons_layout.addWidget(self.btn_add_files)
        files_buttons_layout.addWidget(self.btn_clear_files)
        files_layout.addLayout(files_buttons_layout)

        files_group.setLayout(files_layout)
        main_layout.addWidget(files_group)

        # Grupo: Certificados
        cert_group = QGroupBox("Certificado e.firma")
        cert_layout = QVBoxLayout()

        # Certificado .cer
        cert_row = QHBoxLayout()
        cert_row.addWidget(QLabel("Certificado (.cer):"))
        self.line_cert_path = QLineEdit()
        self.line_cert_path.setReadOnly(True)
        cert_row.addWidget(self.line_cert_path)
        self.btn_browse_cert = QPushButton("...")
        self.btn_browse_cert.setMaximumWidth(50)
        cert_row.addWidget(self.btn_browse_cert)
        cert_layout.addLayout(cert_row)

        # Clave privada .key
        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("Clave privada (.key):"))
        self.line_key_path = QLineEdit()
        self.line_key_path.setReadOnly(True)
        key_row.addWidget(self.line_key_path)
        self.btn_browse_key = QPushButton("...")
        self.btn_browse_key.setMaximumWidth(50)
        key_row.addWidget(self.btn_browse_key)
        cert_layout.addLayout(key_row)

        # Contraseña
        password_row = QHBoxLayout()
        password_row.addWidget(QLabel("Contraseña:"))
        self.line_password = QLineEdit()
        self.line_password.setEchoMode(QLineEdit.Password)
        password_row.addWidget(self.line_password)
        cert_layout.addLayout(password_row)

        # Estado de validación
        self.label_cert_status = QLabel("Esperando certificado...")
        self.label_cert_status.setStyleSheet("color: gray;")
        cert_layout.addWidget(self.label_cert_status)

        cert_group.setLayout(cert_layout)
        main_layout.addWidget(cert_group)

        # Grupo: Firma
        sign_group = QGroupBox("Firma")
        sign_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        sign_layout.addWidget(self.progress_bar)

        self.text_status = QTextEdit()
        self.text_status.setReadOnly(True)
        self.text_status.setMaximumHeight(150)
        sign_layout.addWidget(self.text_status)

        self.btn_sign = QPushButton("Firmar PDFs")
        self.btn_sign.setEnabled(False)
        self.btn_sign.setStyleSheet("font-weight: bold; padding: 10px;")
        sign_layout.addWidget(self.btn_sign)

        sign_group.setLayout(sign_layout)
        main_layout.addWidget(sign_group)

    def _connect_signals(self):
        """Conecta las señales de los widgets"""
        self.btn_add_files.clicked.connect(self._on_add_files)
        self.btn_clear_files.clicked.connect(self._on_clear_files)
        self.btn_browse_cert.clicked.connect(self._on_browse_cert)
        self.btn_browse_key.clicked.connect(self._on_browse_key)
        self.line_password.textChanged.connect(self._on_password_changed)
        self.btn_sign.clicked.connect(self._on_sign_clicked)

    def _on_add_files(self):
        """Agrega archivos PDF a la lista"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar archivos PDF",
            "",
            "Archivos PDF (*.pdf)"
        )

        for file_path in files:
            self.list_pdfs.addItem(file_path)

        self._update_sign_button_state()
        self._log_status(f"{len(files)} archivo(s) agregado(s)")

    def _on_clear_files(self):
        """Limpia la lista de PDFs"""
        self.list_pdfs.clear()
        self._update_sign_button_state()
        self._log_status("Lista de archivos limpiada")

    def _on_browse_cert(self):
        """Selecciona el archivo de certificado"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar certificado",
            "",
            "Certificados (*.cer *.pem *.crt);;Todos los archivos (*)"
        )

        if file_path:
            self.line_cert_path.setText(file_path)
            self._validate_certificate()

    def _on_browse_key(self):
        """Selecciona el archivo de clave privada"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar clave privada",
            "",
            "Claves privadas (*.key *.pem);;Todos los archivos (*)"
        )

        if file_path:
            self.line_key_path.setText(file_path)
            self._validate_certificate()

    def _on_password_changed(self):
        """Se ejecuta cuando cambia la contraseña"""
        self._validate_certificate()

    def _validate_certificate(self):
        """Valida el certificado y la clave privada"""
        cert_path = self.line_cert_path.text()
        key_path = self.line_key_path.text()
        password = self.line_password.text()

        # Verificar que todos los campos estén llenos
        if not all([cert_path, key_path, password]):
            self.label_cert_status.setText("Esperando certificado...")
            self.label_cert_status.setStyleSheet("color: gray;")
            self.cert = None
            self.private_key = None
            self._update_sign_button_state()
            return

        try:
            # Validar certificado
            validator = CertificateValidator(
                Path(cert_path),
                Path(key_path),
                password
            )

            self.cert, self.private_key = validator.validate_all()

            # Obtener información del certificado
            cert_info = validator.get_certificate_info(self.cert)
            cn = cert_info.get('common_name', 'Desconocido')
            expiry = cert_info['not_after'][:10]

            self.label_cert_status.setText(
                f"✓ Certificado válido: {cn} (Expira: {expiry})"
            )
            self.label_cert_status.setStyleSheet("color: green; font-weight: bold;")
            self._log_status(f"Certificado validado: {cn}")

        except CertificateExpiredError as e:
            self._show_cert_error(f"Certificado expirado: {e}")
        except CertificateRevokedError as e:
            self._show_cert_error(f"Certificado revocado: {e}")
        except CertificateError as e:
            self._show_cert_error(str(e))
        except Exception as e:
            self._show_cert_error(f"Error: {e}")

        self._update_sign_button_state()

    def _show_cert_error(self, message: str):
        """Muestra un error de certificado"""
        self.label_cert_status.setText(f"✗ {message}")
        self.label_cert_status.setStyleSheet("color: red; font-weight: bold;")
        self.cert = None
        self.private_key = None
        self._log_status(f"Error de certificado: {message}")

    def _update_sign_button_state(self):
        """Actualiza el estado del botón de firma"""
        has_files = self.list_pdfs.count() > 0
        has_cert = self.cert is not None and self.private_key is not None

        self.btn_sign.setEnabled(has_files and has_cert)

    def _on_sign_clicked(self):
        """Inicia el proceso de firma"""
        # Obtener lista de PDFs
        pdf_paths = []
        for i in range(self.list_pdfs.count()):
            pdf_paths.append(Path(self.list_pdfs.item(i).text()))

        if not pdf_paths:
            return

        # Deshabilitar UI
        self._set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(pdf_paths))
        self.progress_bar.setValue(0)
        self.text_status.clear()

        self._log_status(f"Iniciando firma de {len(pdf_paths)} archivo(s)...")

        # Crear y configurar worker
        tsa_client = TSAClient()
        self.signing_worker = SigningWorker(
            pdf_paths,
            self.cert,
            self.private_key,
            tsa_client
        )

        self.signing_worker.progress.connect(self._on_progress)
        self.signing_worker.file_completed.connect(self._on_file_completed)
        self.signing_worker.finished.connect(self._on_signing_finished)

        # Iniciar firma
        self.signing_worker.start()

    def _on_progress(self, current: int, total: int):
        """Actualiza la barra de progreso"""
        self.progress_bar.setValue(current)
        self._log_status(f"Procesando archivo {current}/{total}...")

    def _on_file_completed(self, filename: str, success: bool, message: str):
        """Se ejecuta cuando se completa la firma de un archivo"""
        status = "✓" if success else "✗"
        color = "green" if success else "red"
        self._log_status(f"{status} {filename}: {message}", color)

    def _on_signing_finished(self, errors: List[str]):
        """Se ejecuta cuando termina el proceso de firma"""
        self.progress_bar.setVisible(False)
        self._set_ui_enabled(True)

        # Mostrar resumen
        total = self.list_pdfs.count()
        success_count = total - len(errors)

        if errors:
            QMessageBox.warning(
                self,
                "Firma completada con errores",
                f"Se firmaron {success_count} de {total} archivos.\n\n"
                f"Errores:\n" + "\n".join(errors[:5]) +
                (f"\n... y {len(errors) - 5} más" if len(errors) > 5 else "")
            )
        else:
            QMessageBox.information(
                self,
                "Firma completada",
                f"Se firmaron exitosamente {success_count} archivo(s)."
            )

        self._log_status(f"Proceso completado: {success_count}/{total} exitosos")

    def _set_ui_enabled(self, enabled: bool):
        """Habilita/deshabilita los controles de la UI"""
        self.btn_add_files.setEnabled(enabled)
        self.btn_clear_files.setEnabled(enabled)
        self.btn_browse_cert.setEnabled(enabled)
        self.btn_browse_key.setEnabled(enabled)
        self.line_password.setEnabled(enabled)
        self.btn_sign.setEnabled(enabled and self.cert is not None)

    def _log_status(self, message: str, color: str = "black"):
        """Agrega un mensaje al log de estado"""
        self.text_status.append(f'<span style="color: {color};">{message}</span>')
        logger.info(message)

    def closeEvent(self, event):
        """Limpia datos sensibles al cerrar la ventana"""
        if hasattr(self, 'private_key'):
            del self.private_key
        if hasattr(self, 'cert'):
            del self.cert
        self.line_password.clear()

        logger.info("MainWindow closed, sensitive data cleared")
        event.accept()
