# Arquitectura Técnica

## Visión General

SelladoMX sigue una arquitectura en capas con separación clara de responsabilidades:

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

## Stack Técnico

### Runtime y Lenguaje

- **Python**: ≥3.11, <3.14
- **Gestor de dependencias**: Poetry

### Interfaz de Usuario

- **PySide6**: 6.8.0+ (Qt 6)
  - Framework moderno de UI multiplataforma
  - Soporte completo para widgets personalizados
  - Temas QSS para personalización visual

### Firma Digital y Criptografía

- **pyhanko**: 0.21.0+ (firma PAdES)
  - Creación de firmas digitales en PDFs
  - Formato PAdES compatible con Adobe Reader

- **pyhanko-certvalidator**: 0.26.0+ (validación OCSP/CRL)
  - Validación de certificados contra OCSP
  - Fallback a CRL si OCSP falla

- **cryptography**: 41.0.0+
  - Operaciones criptográficas de bajo nivel
  - Manejo de certificados e.firma del SAT

### Sellado de Tiempo

- **FreeTSA**: Servicio público de timestamp
  - RFC 3161 compliant
  - Sin costo, sin registro

## Estructura del Proyecto

```
client/
├── src/selladomx/
│   ├── main.py              # Entry point y controller
│   ├── config.py            # Configuración global
│   ├── errors.py            # Excepciones personalizadas
│   ├── ui/
│   │   ├── redesigned_main_view.py  # Vista principal (3 pasos)
│   │   ├── main_window_legacy.py    # Backup de UI anterior
│   │   ├── onboarding/              # Pantallas de bienvenida
│   │   │   ├── onboarding_dialog.py
│   │   │   ├── welcome_slide.py
│   │   │   ├── security_slide.py
│   │   │   └── howto_slide.py
│   │   ├── widgets/                 # Componentes personalizados
│   │   │   └── step_widget.py       # Widget de paso con estados
│   │   └── styles/                  # Temas y estilos
│   │       ├── main_theme.qss       # Tema global QSS
│   │       └── colors.py            # Paleta de colores
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

## Componentes Principales

### UI Layer

**redesigned_main_view.py**
- Vista principal con flujo de 3 pasos
- Gestión de estado de cada paso (pending, active, completed)
- Coordinación de eventos entre pasos

**onboarding/**
- Diálogo modal con 3 slides de bienvenida
- Solo se muestra en primera ejecución
- Guardado de estado en QSettings

**widgets/step_widget.py**
- Componente reutilizable para cada paso
- Estados visuales según progreso
- Desactivación/activación automática

**styles/**
- Tema global en QSS (Qt Style Sheets)
- Paleta de colores consistente
- Estilo inspirado en Balena Etcher

### Application Controller

**main.py**
- Entry point de la aplicación
- Inicialización de QApplication
- Carga de temas y configuración
- Gestión del ciclo de vida

**settings_manager.py**
- Wrapper de QSettings para persistencia
- Almacenamiento multiplataforma:
  - macOS: plist
  - Linux: ini
  - Windows: registry
- Gestión de onboarding y preferencias

### Business Logic

**certificate_validator.py**
- Carga de certificados DER/PEM/PKCS#12
- Validación de vigencia
- Verificación OCSP/CRL
- Extracción de información del titular

**pdf_signer.py**
- Firma PAdES con pyhanko
- Integración con TSA
- Generación de nombre de archivo firmado
- Manejo de errores de firma

**tsa.py**
- Cliente RFC 3161 para FreeTSA
- Gestión de timeouts
- Manejo de errores de red

## Flujo de Datos

### Flujo de Firma de PDF

```
Usuario selecciona PDFs
    ↓
Usuario carga certificado + clave
    ↓
CertificateValidator valida certificado (OCSP/CRL)
    ↓
Usuario hace clic en "Firmar"
    ↓
PDFSigner para cada PDF:
    1. Carga PDF original
    2. Crea firma PAdES con certificado
    3. Solicita timestamp a TSA
    4. Embebe firma en PDF
    5. Guarda PDF con sufijo "_firmado"
    ↓
UI muestra progreso y logs
```

### Flujo de Validación de Certificado

```
Usuario selecciona .cer y .key
    ↓
CertificateValidator:
    1. Detecta formato (DER/PEM/PKCS#12)
    2. Carga certificado público
    3. Carga clave privada con contraseña
    4. Verifica que correspondan
    5. Extrae información del certificado
    6. Valida vigencia (notBefore/notAfter)
    7. Valida estado con OCSP
    8. Si OCSP falla, valida con CRL
    ↓
Resultado: Válido/Inválido con detalles
```

## Patrones de Diseño

### Separation of Concerns

Cada capa tiene responsabilidades claramente definidas:
- UI: Solo presentación y manejo de eventos
- Controller: Coordinación y configuración
- Business Logic: Lógica de negocio pura

### Dependency Injection

Los componentes de business logic no dependen de la UI:
```python
# pdf_signer.py no importa nada de PySide6
# Recibe callbacks para reporting
```

### Observer Pattern

UI observa cambios en el estado de la firma:
```python
# Signals de Qt para comunicación asíncrona
progress_signal.emit(percentage)
log_signal.emit(message)
```

## Seguridad y Privacidad

### Principios

1. **Procesamiento local**: Los PDFs nunca salen de la computadora del usuario
2. **Sin almacenamiento**: No se guardan contraseñas ni claves privadas
3. **Limpieza de memoria**: Los datos sensibles se eliminan después de usar
4. **Validación completa**: OCSP/CRL para verificar estado del certificado

### Conexiones Externas

La aplicación solo se conecta a:
- **FreeTSA**: Para obtener timestamps (RFC 3161)
- **OCSP/CRL**: Para validar certificados (estándar PKI)

Ambos son servicios estándar de la infraestructura PKI.

## Configuración

La configuración se centraliza en `config.py`:

```python
# TSA
TSA_URL = "https://freetsa.org/tsr"
TSA_TIMEOUT = 30

# Validación
OCSP_TIMEOUT = 10
CRL_TIMEOUT = 10
ENABLE_CRL_FALLBACK = True

# Firma
SIGNED_SUFFIX = "_firmado"
```

## Limitaciones Conocidas

1. **FreeTSA**: Servicio público sin garantías de disponibilidad
2. **Validación OCSP/CRL**: Requiere conexión a Internet
3. **Sello visual**: No soportado actualmente (solo firma embebida)
4. **Firma secuencial**: Los PDFs se firman uno por uno (no en paralelo)

## Próximas Mejoras

- Sello visual configurable en el PDF
- Soporte para múltiples TSAs con fallback
- Firma de archivos ZIP y XML
- Firma paralela para mejor rendimiento
