# Prueba el webhook del agente iBanu con las cuatro consultas de la rubrica.
# Uso:  .\probar_webhook.ps1 -Codigo U00112048
#       .\probar_webhook.ps1 -Codigo U00112048 -Consulta proyeccion
param(
    [Parameter(Mandatory = $true)][string]$Codigo,
    [ValidateSet('todas', 'matricula', 'estado', 'proyeccion', 'recomendaciones')][string]$Consulta = 'todas',
    [string]$Url = 'https://ksaavedra363.app.n8n.cloud/webhook/ibanu/orientador',
    [string]$Token = 'ibk_7f3c9a1e5d2b48c6a0e4f9b1d3c7a5e2',
    [int]$TimeoutSeg = 90
)

$preguntas = [ordered]@{
    matricula       = 'Quiero matricularme el proximo semestre. Que asignaturas puedo inscribir segun mis prerrequisitos y mi avance, y que debo tener en cuenta del reglamento (creditos maximos, fechas y requisitos)?'
    estado          = 'Muestrame mi estado academico actual: asignaturas aprobadas, en curso y pendientes, mi promedio, mis creditos cursados y si tengo alguna alerta o riesgo academico.'
    proyeccion      = 'Hazme una proyeccion de mi carrera: cuantos semestres me faltan, que asignaturas deberia cursar en cada uno y cual seria mi fecha estimada de graduacion si sigo este ritmo.'
    recomendaciones = 'Dame recomendaciones personalizadas para tener exito en el programa segun mi desempeno: estrategias de estudio, recursos de autoaprendizaje, opciones de investigacion y acciones concretas para este semestre.'
}

$sesion = "prueba-$([guid]::NewGuid().ToString('N').Substring(0, 8))"
$claves = if ($Consulta -eq 'todas') { $preguntas.Keys } else { @($Consulta) }
$tmp = New-TemporaryFile

foreach ($k in $claves) {
    $cuerpo = @{ codigo_estudiante = $Codigo; mensaje = $preguntas[$k]; sesion_id = $sesion } | ConvertTo-Json -Compress
    [System.IO.File]::WriteAllText($tmp.FullName, $cuerpo, (New-Object System.Text.UTF8Encoding($false)))

    Write-Host "`n=== Consulta: $k ===" -ForegroundColor Cyan
    $salida = curl.exe -s -S --max-time $TimeoutSeg -w "`nHTTP %{http_code}  tiempo %{time_total}s" `
        -X POST $Url `
        -H "Content-Type: application/json; charset=utf-8" `
        -H "X-Ibanu-Token: $Token" `
        --data-binary "@$($tmp.FullName)"
    $lineas = $salida -split "`n"
    $json = ($lineas[0..($lineas.Count - 2)]) -join "`n"
    try { ($json | ConvertFrom-Json) | ConvertTo-Json -Depth 8 } catch { Write-Host $json }
    Write-Host $lineas[-1] -ForegroundColor Yellow
}
Remove-Item $tmp.FullName -ErrorAction SilentlyContinue
