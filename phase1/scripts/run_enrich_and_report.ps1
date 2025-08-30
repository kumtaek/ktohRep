Param(
  [int]$Sql = 10000,
  [int]$Method = 10000,
  [int]$Jsp = 10000,
  [string]$DryRun = "true"
)

Write-Host "Seeding JSP files into DB..."
python -m phase1.src.tools.seed_jsp_files || exit 1

Write-Host "Running enrichment passes... (sql=$Sql, method=$Method, jsp=$Jsp, dry_run=$DryRun)"
python -m phase1.src.tools.enrich_run --sql $Sql --method $Method --jsp $Jsp --dry-run $DryRun || exit 1

Write-Host "Collecting metrics and writing 개발내역07.md..."
python -m phase1.src.tools.metrics || exit 1

Write-Host "Done. See 개발내역07.md for the latest report."
