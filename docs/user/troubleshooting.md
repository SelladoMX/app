# Troubleshooting

## Problemas de Certificados

### Error: "No se pudo cargar la clave privada"

1. Verifica que estés usando la contraseña correcta
2. Asegúrate de que el archivo .key corresponda al certificado .cer
3. Intenta convertir el formato (ver [certificates.md](certificates.md#conversión-de-formatos))
4. Verifica que el archivo no esté corrupto

### Error: "Contraseña incorrecta"

- La contraseña de la clave privada debe ser la que estableciste al obtener tu e.firma
- No es la misma contraseña que usas para el portal del SAT
- Verifica que no haya espacios al inicio o final de la contraseña

### Error: "Certificado expirado"

- Los certificados e.firma del SAT tienen vigencia de 4 años
- Necesitas renovar tu e.firma en el SAT
- Visita: https://www.sat.gob.mx/tramites/operacion/28753/obten-tu-certificado-de-e.firma

## Problemas de Firma

### La firma no se muestra en Adobe Reader

Asegúrate de que:
- El PDF original no estaba corrupto
- El proceso de firma se completó sin errores
- Estás usando una versión reciente de Adobe Reader

### Error: "No se pudo firmar el PDF"

- Verifica que el PDF no esté protegido con contraseña
- Asegúrate de que el PDF no esté dañado
- Verifica que tienes permisos de escritura en la carpeta de destino

## Problemas de TSA

### Error al conectar con el servicio TSA o timeout

- Verifica tu conexión a Internet
- El servicio TSA puede estar temporalmente no disponible
- Intenta nuevamente en unos minutos

## Problemas de Instalación

### macOS: "App is damaged and can't be opened"

Ejecuta en la terminal:

```bash
xattr -cr /Applications/SelladoMX.app
```

### Windows: SmartScreen bloquea la aplicación

1. Clic en "Más información"
2. Clic en "Ejecutar de todas formas"

## Problemas de Rendimiento

### La firma de múltiples PDFs es lenta

- Cada PDF se firma secuencialmente y requiere una solicitud de sello de tiempo por Internet
- El proceso puede tardar dependiendo del tamaño de los archivos
