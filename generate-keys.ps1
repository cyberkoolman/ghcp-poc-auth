#!/usr/bin/env pwsh
# Generates an RSA-2048 key pair and prints PEM strings for use in appsettings or secrets.
# Usage: ./generate-keys.ps1

$rsa = [System.Security.Cryptography.RSA]::Create(2048)

$privatePem = $rsa.ExportRSAPrivateKeyPem()
$publicPem  = $rsa.ExportRSAPublicKeyPem()

Write-Host ""
Write-Host "=== PRIVATE KEY (PrivateKeyPem) — keep secret, never commit ==="
Write-Host $privatePem
Write-Host ""
Write-Host "=== PUBLIC KEY (PublicKeyPem) — safe to distribute ==="
Write-Host $publicPem
Write-Host ""
Write-Host "Store the private key in 'dotnet user-secrets' or your secrets manager."
Write-Host "  dotnet user-secrets set 'Jwt:PrivateKeyPem' '<paste key here>'"
Write-Host "  dotnet user-secrets set 'Jwt:PublicKeyPem'  '<paste key here>'"
