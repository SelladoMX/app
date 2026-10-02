# Arquitectura Técnica

## Visión General

```
┌─────────────────────────────────────────┐
│  UI (QML)  src/selladomx/ui/qml/        │
└──────────────┬──────────────────────────┘
               │ context properties / signals
┌──────────────▼──────────────────────────┐
│  Bridge  src/selladomx/ui/qml_bridge/   │
│  MainViewModel, SettingsBridge,         │
│  SigningCoordinator, HistoryViewModel   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Lógica  signing/, api/, utils/         │
│  CertificateValidator, PDFSigner,       │
│  SigningWorker, TSAClient,              │
│  APITimeStamper, SelladoMXAPIClient     │
└─────────────────────────────────────────┘
```

`main.py` crea la aplicación (instancia única vía `QLocalServer`), registra el URL scheme en el primer arranque, expone los view models a QML y carga `ui/qml/main.qml`.

`signing/` no importa PySide6, excepto `worker.py` (`SigningWorker` es un `QThread`).

## Estructura del Proyecto

```
src/selladomx/
├── main.py                 # Entry point
├── config.py               # Constantes y variables de entorno
├── errors.py               # Excepciones de firma/certificado
├── api/                    # Cliente HTTP de la API SelladoMX
├── signing/                # Certificado, firma PAdES, TSA, worker
├── ui/
│   ├── qml/                # main.qml, views/, dialogs/, components/, design/
│   └── qml_bridge/         # View models expuestos a QML
└── utils/                  # QSettings, deep links, URL scheme, updates
```

## Flujo de Firma

```
Paso 1: usuario selecciona PDFs
Paso 2: CertificateValidator.validate_all()
          carga .cer (DER, luego PEM)
          carga .key (DER, PEM o PKCS#12) con contraseña
          valida vigencia (notBefore/notAfter)
Paso 3: SigningCoordinator inicia SigningWorker (QThread)
          por cada PDF, en secuencia:
            PDFSigner firma (PAdES, sin sello visual) con timestamp:
              - TSA gratuita: TSAClient, providers de TSA_FREE_PROVIDERS
              - TSA profesional: APITimeStamper envía el TimeStampReq a la API,
                que lo reenvía a Certum (1 crédito por documento)
            guarda <nombre>_firmado.pdf
            (profesional) envía el SHA-256 del PDF firmado a la API
```

Si falla la TSA profesional por créditos, autenticación o red, el worker detiene el lote.

## Seguridad y Privacidad

- Los PDFs y la clave privada nunca salen de la computadora. Con TSA profesional, la API recibe el TimeStampReq, el nombre y tamaño del archivo, CN y número de serie del firmante, y el hash del PDF firmado.
- No se guardan contraseñas ni claves privadas. QSettings guarda las rutas del último certificado/clave y el token de la API en texto plano.

### Conexiones Externas

- TSAs gratuitas (`TSA_FREE_PROVIDERS` en `config.py`)
- API SelladoMX (`SELLADOMX_API_URL`): saldo, timestamp profesional, historial, tokens
- API de GitHub Releases: verificación de actualizaciones (`utils/update_checker.py`)

## Configuración

Constantes y variables de entorno: `src/selladomx/config.py`.

## Limitaciones Conocidas

1. **Sello visual**: no soportado (solo firma embebida)
2. **Firma secuencial**: los PDFs se firman uno por uno
