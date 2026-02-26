# Exemplo: lista de cursos. Edite o array.
$base = $PSScriptRoot
Set-Location $base

$cursos = @(
    @{ Nome = "Curso 1"; Url = "https://site.com/cursos/ID/aulas" },
    @{ Nome = "Curso 2"; Url = "https://site.com/cursos/ID/aulas" }
)

$total = $cursos.Count
$atual = 0
foreach ($c in $cursos) {
    $atual++
    if ($atual -gt 1) {
        Write-Host "`n$($c.Nome) inicia em 45 s (curso anterior ja terminou)." -ForegroundColor Yellow
        Start-Sleep -Seconds 45
    }
    New-Item -Path "pdfs\$($c.Nome)" -ItemType Directory -Force | Out-Null
    Write-Host "`n========== [$atual/$total] $($c.Nome) - baixando todas as aulas ==========" -ForegroundColor Cyan
    python bot_pdf.py --curso $c.Url --pasta "pdfs/$($c.Nome)"
    Write-Host "`n$($c.Nome) concluido." -ForegroundColor Green
}

Write-Host "`nConcluido!" -ForegroundColor Green
