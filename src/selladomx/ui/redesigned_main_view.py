"""Redesigned main view with guided workflow (Balena Etcher style)."""
import logging
from pathlib import Path
from typing import Optional, List

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QProgressBar, QTextEdit,
    QLabel, QFileDialog, QMessageBox, QScrollArea
)

from .widgets.step_widget import StepWidget, StepState
from ..signing.certificate_validator import CertificateValidator
from ..signing.pdf_signer import PDFSigner
from ..signing.tsa import TSAClient
from ..errors import (
    CertificateError, CertificateExpiredError, CertificateRevokedError,
)

# Import SigningWorker from main_window_legacy (reuse as-is)
from .main_window_legacy import SigningWorker

logger = logging.getLogger(__name__)


class RedesignedMainView(QMainWindow):
    """Redesigned main window with guided 3-step workflow."""

    def __init__(self):
        """Initialize redesigned main view."""
        super().__init__()
        self.cert = None
        self.private_key = None
        self.signing_worker = None
        self.output_dir = None  # Carpeta de destino para PDFs firmados

        self._setup_ui()
        self._connect_signals()
        self._init_step_states()

        logger.info("RedesignedMainView initialized")

    def _setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("SelladoMX - Firma Digital de PDFs")
        self.resize(950, 750)
        self.setMinimumSize(900, 700)

        # Central widget with scroll area
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        # Scroll area for steps
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        scroll_content = QWidget()
        self.steps_layout = QVBoxLayout(scroll_content)
        self.steps_layout.setSpacing(16)
        self.steps_layout.setContentsMargins(0, 0, 0, 0)

        # STEP 1: Select PDFs
        self.step1 = StepWidget(
            1,
            "Seleccionar PDFs",
            "Agrega los documentos que deseas firmar"
        )
        self._setup_step1_content()
        self.steps_layout.addWidget(self.step1)

        # STEP 2: Load Certificate
        self.step2 = StepWidget(
            2,
            "Cargar Certificado",
            "Selecciona tu certificado e.firma y llave privada"
        )
        self._setup_step2_content()
        self.steps_layout.addWidget(self.step2)

        # STEP 3: Sign
        self.step3 = StepWidget(
            3,
            "Firmar",
            "Inicia el proceso de firma digital"
        )
        self._setup_step3_content()
        self.steps_layout.addWidget(self.step3)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def _setup_step1_content(self):
        """Setup content for step 1 (Select PDFs)."""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # PDF list
        self.list_pdfs = QListWidget()
        self.list_pdfs.setMinimumHeight(150)
        layout.addWidget(self.list_pdfs)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.btn_add_files = QPushButton("Agregar PDFs...")
        self.btn_clear_files = QPushButton("Limpiar lista")
        self.btn_clear_files.setProperty("class", "secondary")

        buttons_layout.addWidget(self.btn_add_files)
        buttons_layout.addWidget(self.btn_clear_files)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        self.step1.set_content(content)

    def _setup_step2_content(self):
        """Setup content for step 2 (Load Certificate)."""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Certificate .cer
        cert_row = QHBoxLayout()
        cert_row.addWidget(QLabel("Certificado (.cer):"))
        self.line_cert_path = QLineEdit()
        self.line_cert_path.setReadOnly(True)
        self.line_cert_path.setPlaceholderText("Selecciona tu certificado...")
        cert_row.addWidget(self.line_cert_path)
        self.btn_browse_cert = QPushButton("Seleccionar")
        self.btn_browse_cert.setMaximumWidth(120)
        cert_row.addWidget(self.btn_browse_cert)
        layout.addLayout(cert_row)

        # Private key .key
        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("Clave privada (.key):"))
        self.line_key_path = QLineEdit()
        self.line_key_path.setReadOnly(True)
        self.line_key_path.setPlaceholderText("Selecciona tu llave privada...")
        key_row.addWidget(self.line_key_path)
        self.btn_browse_key = QPushButton("Seleccionar")
        self.btn_browse_key.setMaximumWidth(120)
        key_row.addWidget(self.btn_browse_key)
        layout.addLayout(key_row)

        # Password
        password_row = QHBoxLayout()
        password_row.addWidget(QLabel("Contraseña:"))
        self.line_password = QLineEdit()
        self.line_password.setEchoMode(QLineEdit.Password)
        self.line_password.setPlaceholderText("Ingresa tu contraseña...")
        password_row.addWidget(self.line_password)
        layout.addLayout(password_row)

        # Validation status
        self.label_cert_status = QLabel("Esperando certificado...")
        self.label_cert_status.setProperty("class", "secondary")
        self.label_cert_status.setWordWrap(True)
        layout.addWidget(self.label_cert_status)

        self.step2.set_content(content)

    def _setup_step3_content(self):
        """Setup content for step 3 (Sign)."""
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(30)
        layout.addWidget(self.progress_bar)

        # Status log
        log_label = QLabel("Registro de actividad:")
        log_label.setProperty("class", "secondary")
        layout.addWidget(log_label)

        self.text_status = QTextEdit()
        self.text_status.setReadOnly(True)
        self.text_status.setMaximumHeight(120)
        layout.addWidget(self.text_status)

        # Output directory selector
        output_row = QHBoxLayout()
        output_row.setSpacing(10)
        output_label = QLabel("Guardar en:")
        output_label.setProperty("class", "secondary")
        output_row.addWidget(output_label)

        self.line_output_dir = QLineEdit()
        self.line_output_dir.setReadOnly(True)
        self.line_output_dir.setPlaceholderText("Misma carpeta que el PDF original (por defecto)")
        output_row.addWidget(self.line_output_dir)

        self.btn_browse_output = QPushButton("Seleccionar carpeta...")
        self.btn_browse_output.setProperty("class", "secondary")
        self.btn_browse_output.setMaximumWidth(160)
        output_row.addWidget(self.btn_browse_output)

        layout.addLayout(output_row)

        # Sign button
        self.btn_sign = QPushButton("Firmar PDFs")
        self.btn_sign.setProperty("class", "success")
        self.btn_sign.setEnabled(False)
        self.btn_sign.setMinimumHeight(50)
        self.btn_sign.setStyleSheet(
            """
            QPushButton {
                font-size: 16px;
                font-weight: 600;
            }
            """
        )
        layout.addWidget(self.btn_sign)

        self.step3.set_content(content)

    def _init_step_states(self):
        """Initialize step states."""
        # Step 1 is active by default
        self.step1.state = StepState.ACTIVE

        # Steps 2 and 3 are disabled
        self.step2.state = StepState.DISABLED
        self.step3.state = StepState.DISABLED

    def _connect_signals(self):
        """Connect widget signals."""
        # Step 1 signals
        self.btn_add_files.clicked.connect(self._on_add_files)
        self.btn_clear_files.clicked.connect(self._on_clear_files)
        self.btn_browse_output.clicked.connect(self._on_browse_output)
        self.list_pdfs.itemSelectionChanged.connect(self._check_step1_completion)

        # Step 2 signals - solo verificar campos llenos, no validar
        self.btn_browse_cert.clicked.connect(self._on_browse_cert)
        self.btn_browse_key.clicked.connect(self._on_browse_key)
        self.line_password.textChanged.connect(self._check_step2_fields)

        # Step 3 signals
        self.btn_sign.clicked.connect(self._on_sign_clicked)

        # Step completion signals
        self.step1.step_completed.connect(self._on_step1_completed)
        self.step2.step_completed.connect(self._on_step2_completed)

    # Step 1 Methods (copied from MainWindow)

    def _on_add_files(self):
        """Add PDF files to the list."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar archivos PDF",
            "",
            "Archivos PDF (*.pdf)"
        )

        for file_path in files:
            self.list_pdfs.addItem(file_path)

        if files:
            self._log_status(f"{len(files)} archivo(s) agregado(s)")
            self._check_step1_completion()

    def _on_clear_files(self):
        """Clear PDF list."""
        self.list_pdfs.clear()
        self._log_status("Lista de archivos limpiada")
        self._check_step1_completion()

    def _on_browse_output(self):
        """Browse for output directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta de destino para PDFs firmados",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if directory:
            self.output_dir = Path(directory)
            self.line_output_dir.setText(directory)
            self._log_status(f"Carpeta de destino: {directory}")
        else:
            # Clear if canceled
            self.output_dir = None
            self.line_output_dir.clear()

    def _check_step1_completion(self):
        """Check if step 1 is completed."""
        if self.list_pdfs.count() > 0:
            if self.step1.state != StepState.COMPLETED:
                self.step1.mark_completed()
                self._log_status("✓ Paso 1 completado: PDFs seleccionados", "green")
        else:
            if self.step1.state == StepState.COMPLETED:
                self.step1.state = StepState.ACTIVE

    def _on_step1_completed(self):
        """Handle step 1 completion."""
        # Activate step 2
        self.step2.activate()

    # Step 2 Methods (copied from MainWindow)

    def _on_browse_cert(self):
        """Select certificate file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar certificado",
            "",
            "Certificados (*.cer *.pem *.crt);;Todos los archivos (*)"
        )

        if file_path:
            self.line_cert_path.setText(file_path)
            self._check_step2_fields()

    def _on_browse_key(self):
        """Select private key file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar clave privada",
            "",
            "Claves privadas (*.key *.pem);;Todos los archivos (*)"
        )

        if file_path:
            self.line_key_path.setText(file_path)
            self._check_step2_fields()

    def _check_step2_fields(self):
        """Check if all step 2 fields are filled (but don't validate yet)."""
        cert_path = self.line_cert_path.text()
        key_path = self.line_key_path.text()
        password = self.line_password.text()

        if all([cert_path, key_path, password]):
            # All fields filled - mark step 2 as completed
            self.label_cert_status.setText("Listo para firmar")
            self.label_cert_status.setStyleSheet("color: #007AFF; font-weight: 500;")

            # Mark step 2 as completed (will trigger _on_step2_completed)
            if self.step2.state != StepState.COMPLETED:
                logger.info("Marking step 2 as completed (all fields filled)")
                self.step2.mark_completed()
        else:
            # Some fields empty - reset if it was completed
            self.label_cert_status.setText("Complete todos los campos")
            self.label_cert_status.setStyleSheet("color: #86868B;")

            if self.step2.state == StepState.COMPLETED:
                self.step2.state = StepState.ACTIVE
                self.step3.state = StepState.DISABLED
                self.btn_sign.setEnabled(False)

    def _validate_certificate(self):
        """Validate certificate and private key.

        Returns:
            bool: True if validation successful, False otherwise
        """
        cert_path = self.line_cert_path.text()
        key_path = self.line_key_path.text()
        password = self.line_password.text()

        # Check all fields are filled
        if not all([cert_path, key_path, password]):
            self.label_cert_status.setText("Complete todos los campos")
            self.label_cert_status.setProperty("class", "secondary")
            self.label_cert_status.setStyleSheet("color: #FF3B30;")
            self.cert = None
            self.private_key = None
            QMessageBox.warning(
                self,
                "Campos incompletos",
                "Por favor complete todos los campos:\n"
                "- Certificado (.cer)\n"
                "- Clave privada (.key)\n"
                "- Contraseña"
            )
            return False

        try:
            # Validate certificate
            validator = CertificateValidator(
                Path(cert_path),
                Path(key_path),
                password
            )

            self.cert, self.private_key = validator.validate_all()

            # Get certificate info
            cert_info = validator.get_certificate_info(self.cert)
            cn = cert_info.get('common_name', 'Desconocido')
            expiry = cert_info['not_after'][:10]

            self.label_cert_status.setText(
                f"✓ Certificado válido: {cn} (Expira: {expiry})"
            )
            self.label_cert_status.setProperty("class", "success")
            self.label_cert_status.setStyleSheet("color: #34C759; font-weight: 500;")
            self._log_status(f"✓ Certificado validado: {cn}", "#34C759")

            return True

        except CertificateExpiredError as e:
            self._show_cert_error(f"Certificado expirado: {e}")
            return False
        except CertificateRevokedError as e:
            self._show_cert_error(f"Certificado revocado: {e}")
            return False
        except CertificateError as e:
            self._show_cert_error(str(e))
            return False
        except Exception as e:
            self._show_cert_error(f"Error: {e}")
            return False

    def _show_cert_error(self, message: str):
        """Show certificate error."""
        self.label_cert_status.setText(f"✗ {message}")
        self.label_cert_status.setProperty("class", "error")
        self.label_cert_status.setStyleSheet("color: #FF3B30; font-weight: 500;")
        self.cert = None
        self.private_key = None
        self._log_status(f"Error de certificado: {message}", "#FF3B30")

        if self.step2.state == StepState.COMPLETED:
            self.step2.state = StepState.ACTIVE
            self.step3.state = StepState.DISABLED

    def _on_step2_completed(self):
        """Handle step 2 completion."""
        logger.info("Step 2 completed - activating step 3")
        # Activate step 3
        self.step3.activate()
        self.btn_sign.setEnabled(True)
        self._log_status("✓ Paso 2 completado: Listo para firmar", "#34C759")

    # Step 3 Methods (copied from MainWindow)

    def _on_sign_clicked(self):
        """Start signing process."""
        # First, validate certificate if not already validated
        if not self.cert or not self.private_key:
            self._log_status("Validando certificado...", "#007AFF")
            if not self._validate_certificate():
                # Validation failed, error already shown
                return

        # Get PDF list
        pdf_paths = []
        for i in range(self.list_pdfs.count()):
            pdf_paths.append(Path(self.list_pdfs.item(i).text()))

        if not pdf_paths:
            return

        # Disable UI
        self._set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(pdf_paths))
        self.progress_bar.setValue(0)
        self.text_status.clear()

        self._log_status(f"Iniciando firma de {len(pdf_paths)} archivo(s)...")

        # Create and configure worker
        tsa_client = TSAClient()
        self.signing_worker = SigningWorker(
            pdf_paths,
            self.cert,
            self.private_key,
            tsa_client,
            self.output_dir  # Pasar carpeta de destino (puede ser None)
        )

        self.signing_worker.progress.connect(self._on_progress)
        self.signing_worker.file_completed.connect(self._on_file_completed)
        self.signing_worker.finished.connect(self._on_signing_finished)

        # Start signing
        self.signing_worker.start()

    def _on_progress(self, current: int, total: int):
        """Update progress bar."""
        self.progress_bar.setValue(current)
        self._log_status(f"Procesando archivo {current}/{total}...")

    def _on_file_completed(self, filename: str, success: bool, message: str):
        """Handle file completion."""
        status = "✓" if success else "✗"
        color = "#34C759" if success else "#FF3B30"
        self._log_status(f"{status} {filename}: {message}", color)

    def _on_signing_finished(self, errors: List[str]):
        """Handle signing completion."""
        self.progress_bar.setVisible(False)
        self._set_ui_enabled(True)

        # Show summary
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

    # Helper Methods

    def _set_ui_enabled(self, enabled: bool):
        """Enable/disable UI controls."""
        self.btn_add_files.setEnabled(enabled)
        self.btn_clear_files.setEnabled(enabled)
        self.btn_browse_output.setEnabled(enabled)
        self.btn_browse_cert.setEnabled(enabled)
        self.btn_browse_key.setEnabled(enabled)
        self.line_password.setEnabled(enabled)
        self.btn_sign.setEnabled(
            enabled and
            self.cert is not None and
            self.step3.state == StepState.ACTIVE
        )

    def _log_status(self, message: str, color: str = "black"):
        """Add message to status log."""
        self.text_status.append(f'<span style="color: {color};">{message}</span>')
        logger.info(message)

    def closeEvent(self, event):
        """Clean sensitive data on close."""
        if hasattr(self, 'private_key'):
            del self.private_key
        if hasattr(self, 'cert'):
            del self.cert
        self.line_password.clear()

        logger.info("RedesignedMainView closed, sensitive data cleared")
        event.accept()
