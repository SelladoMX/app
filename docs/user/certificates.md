# Guía de Certificados e.firma

## Formato de los Certificados e.firma

Los certificados e.firma del SAT típicamente incluyen dos archivos:

- **`.cer`**: Certificado público (formato DER)
- **`.key`**: Clave privada encriptada (formato PKCS#8 DER)

## Formatos Soportados

SelladoMX soporta múltiples formatos de certificados:

- **DER**: Formato binario (extensión .cer/.key)
- **PEM**: Formato texto con marcadores BEGIN/END
- **PKCS#12**: Archivo único con certificado y clave (.p12, .pfx)

## Conversión de Formatos

Si tienes problemas cargando tu certificado e.firma, puedes convertirlo usando OpenSSL:

### Convertir .key de DER a PEM

```bash
openssl pkcs8 -in clave.key -inform DER -out clave.pem -outform PEM
```

### Convertir .cer de DER a PEM

```bash
openssl x509 -in certificado.cer -inform DER -out certificado.pem -outform PEM
```

### Crear archivo PKCS#12 (.pfx)

```bash
# Primero convertir a PEM si es necesario
openssl pkcs8 -in clave.key -inform DER -out clave.pem -outform PEM
openssl x509 -in certificado.cer -inform DER -out certificado.pem -outform PEM

# Luego crear el .pfx
openssl pkcs12 -export -out certificado.pfx -inkey clave.pem -in certificado.pem
```

## Verificación de Certificado

Para verificar la información de tu certificado:

```bash
# Ver detalles del certificado
openssl x509 -in certificado.cer -inform DER -text -noout

# Ver fechas de vigencia
openssl x509 -in certificado.cer -inform DER -noout -dates

# Ver el nombre del titular
openssl x509 -in certificado.cer -inform DER -noout -subject
```

## Seguridad

- **Nunca compartas tu archivo .key con nadie**
- **Nunca compartas tu contraseña**
- Guarda copias de seguridad de tus certificados en un lugar seguro
- Los certificados e.firma tienen el mismo valor legal que una firma autógrafa

## Obtener e.firma del SAT

Si aún no tienes tu e.firma, puedes obtenerla en:

1. En línea: https://www.sat.gob.mx/tramites/operacion/28753/obten-tu-certificado-de-e.firma
2. Presencialmente en las oficinas del SAT
3. Con un Proveedor de Certificación autorizado

## Soporte Técnico

Para problemas con tu certificado e.firma del SAT:
- SAT: 55-627-22-728
- Portal: https://www.sat.gob.mx

Para problemas con SelladoMX:
- Abre un issue en el repositorio del proyecto
