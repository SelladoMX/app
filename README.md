# SelladoMX

Aplicación de escritorio para firmar PDFs con certificados e.firma del SAT.

## Características Principales

- Firma PAdES compatible con Adobe Reader
- Sellado de tiempo (TSA)
- Procesamiento 100% local (sin custodia)
- Validación completa de certificados (OCSP/CRL)
- Interfaz moderna con flujo guiado
- Firma por lotes

## Seguridad y Privacidad

- Los archivos PDF nunca salen de tu computadora
- No se almacenan contraseñas ni certificados
- No hay conexiones a servidores externos (excepto TSA y validación OCSP/CRL)
- Limpieza automática de datos sensibles en memoria

## Quick Start

### Para Usuarios

Descarga el ejecutable para tu plataforma: [Releases](releases)

### Para Desarrolladores

```bash
# Instalar dependencias
poetry install

# Ejecutar
poetry run selladomx
```

## Documentación

### Usuario
- [Instalación y Uso](docs/user/installation.md)
- [Guía de Certificados](docs/user/certificates.md)
- [Troubleshooting](docs/user/troubleshooting.md)

### Desarrollador
- [Desarrollo](docs/developer/development.md)
- [Packaging](docs/developer/packaging.md)
- [Arquitectura](docs/developer/architecture.md)

## Tecnologías

**Runtime**: Python 3.11+

**UI**: PySide6 (Qt 6)

**Firma**: pyhanko · pyhanko-certvalidator

**Criptografía**: cryptography

**TSA**: FreeTSA

## Arquitectura

```
┌─────────────────────────────────────────┐
│      UI Layer (PySide6)                 │
│   - redesigned_main_view.py (3 pasos)  │
│   - onboarding (3 slides)               │
│   - widgets (step_widget)               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Application Controller (main.py)       │
│  - Settings Manager (QSettings)         │
│  - Theme Loader (QSS)                   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Business Logic                         │
│   - CertificateValidator                 │
│   - PDFSigner (pyhanko)                  │
│   - TSAClient                            │
└─────────────────────────────────────────┘
```

## Estructura del Proyecto

```
client/
├── src/selladomx/
│   ├── main.py              # Entry point
│   ├── config.py            # Configuración
│   ├── errors.py            # Excepciones
│   ├── ui/
│   │   ├── redesigned_main_view.py  # Vista principal (3 pasos)
│   │   ├── onboarding/              # Pantallas de bienvenida
│   │   ├── widgets/                 # Componentes personalizados
│   │   └── styles/                  # Temas y estilos
│   ├── utils/
│   │   └── settings_manager.py      # Persistencia con QSettings
│   └── signing/
│       ├── certificate_validator.py  # Validación de certificados
│       ├── pdf_signer.py             # Firma de PDFs
│       └── tsa.py                    # Cliente TSA
├── tests/
├── pyproject.toml
└── README.md
```

## Licencia

MIT

## Filosofía del Proyecto

> "La confianza del usuario está en que el documento nunca sale de su computadora."

SelladoMX está diseñado con seguridad y privacidad como prioridades. Nunca enviamos tus documentos o certificados a ningún servidor externo (excepto para validación OCSP/CRL y timestamp, que son servicios estándar).
