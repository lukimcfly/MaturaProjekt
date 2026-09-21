# Builds the shopping-list workbook through Excel (COM), so Excel itself computes and the
# result can be read back and checked. Data comes from shoplist_data.py (JSON).
param([string]$Json, [string]$Out)

$d = Get-Content -Raw -Encoding UTF8 $Json | ConvertFrom-Json
$order = @('Platine','Bedienfeld','Verbinder','Stromversorgung','Arduino','Mechanik','Abgleich+Reserve','Werkzeug')
$desc = @{
  'Platine'          = 'Bedrahtete Bauteile auf den Platinen - von Hand gelötet. Die SMD-Chips (OPA4196, OPA1662, 74LVC2G17) bestückt JLCPCB; sie fehlen hier.'
  'Bedienfeld'       = 'Potis, Schalter, Buchsen, Knöpfe - sitzen im Bedienfeld und sind per Kabel mit den Platinen verbunden.'
  'Verbinder'        = 'JST-XH-Stecker und Litze für alle Kabel zwischen den Platinen und zum Bedienfeld.'
  'Stromversorgung'  = '12-V-Netzteil ausserhalb des Holzgehäuses; im Gerät ±12 V für den Synthesizer und 12 V für den Arduino.'
  'Arduino'          = 'Oszilloskop mit Display, fest im Gerät.'
  'Mechanik'         = 'Befestigung aller Platinen auf dem Holzboden (Einschraubmuffen + Abstandsbolzen).'
  'Abgleich+Reserve' = 'Ausweichwerte zum Feinabstimmen und Ersatzteile für Reparaturen - einmalig, nicht pro Gerät.'
  'Werkzeug'         = 'Einmalig und nur, falls nicht vorhanden.'
}
$hdr = @('Erledigt','Teil','Wert / Typ','Bauform / Spezifikation','Wo (Referenz)','Pro Gerät',
         'Zusätzlich (Reserve / einmalig)','Vorhanden','Bestellmenge','Lieferant (Vorschlag)',
         'Art.-Nr. / Suchbegriff','Preis/Stk. CHF (Schätzung)','Summe CHF','Bemerkung')
$widths = @(8,22,24,34,34,9,13,10,11,17,34,13,11,60)
$DEV = "'Übersicht'!`$C`$6"          # device count cell

$yellow = 0x99FFFF; $headFill = 0x5A3A1F; $blue = 0xFF0000   # Excel colours are BGR

$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false; $xl.DisplayAlerts = $false
$wb = $xl.Workbooks.Add()
while ($wb.Worksheets.Count -lt ($order.Count + 1)) { [void]$wb.Worksheets.Add([Type]::Missing, $wb.Worksheets.Item($wb.Worksheets.Count)) }
$ov = $wb.Worksheets.Item(1); $ov.Name = 'Übersicht'
$sumRow = @{}; $lastRow = @{}

for ($s = 0; $s -lt $order.Count; $s++) {
  $name = $order[$s]
  $ws = $wb.Worksheets.Item($s + 2); $ws.Name = $name
  $ws.Cells.Font.Name = 'Arial'; $ws.Cells.Font.Size = 10
  $ws.Cells.Item(1,1).Value2 = $name; $ws.Cells.Item(1,1).Font.Size = 14; $ws.Cells.Item(1,1).Font.Bold = $true
  $ws.Cells.Item(2,1).Value2 = $desc[$name]
  $ws.Cells.Item(3,1).Value2 = 'Gelb = selbst ausfüllen (Vorhanden, echter Preis). Bestellmenge = Pro Gerät × Anzahl Geräte (Übersicht) + Zusätzlich - Vorhanden.'
  $ws.Cells.Item(3,1).Font.Italic = $true
  for ($c = 0; $c -lt $hdr.Count; $c++) {
    $h = $ws.Cells.Item(4, $c + 1); $h.Value2 = $hdr[$c]
    $h.Font.Bold = $true; $h.Font.Color = 0xFFFFFF; $h.Interior.Color = $headFill; $h.WrapText = $true
    $ws.Columns.Item($c + 1).ColumnWidth = $widths[$c]
  }
  $ws.Rows.Item(4).RowHeight = 30
  $r = 5
  foreach ($it in $d.sheets.$name) {
    $ws.Cells.Item($r,1).Value2 = ''
    $ws.Cells.Item($r,2).Value2 = $it.part
    $ws.Cells.Item($r,3).Value2 = $it.value
    $ws.Cells.Item($r,4).Value2 = $it.spec
    $ws.Cells.Item($r,5).Value2 = $it.refs
    $ws.Cells.Item($r,6).Value2 = [double]$it.per
    $ws.Cells.Item($r,7).Value2 = [double]$it.extra
    $ws.Cells.Item($r,8).Value2 = [double]$it.have
    $ws.Cells.Item($r,9).Formula = "=MAX(0,F$r*$DEV+G$r-H$r)"
    $ws.Cells.Item($r,10).Value2 = $it.supplier
    $ws.Cells.Item($r,11).Value2 = $it.pn
    $ws.Cells.Item($r,12).Value2 = [double]$it.price
    $ws.Cells.Item($r,13).Formula = "=I$r*L$r"
    $ws.Cells.Item($r,14).Value2 = $it.note
    $r++
  }
  $first = 5; $last = $r - 1; $lastRow[$name] = $last
  foreach ($col in 6,7,8,12) { $ws.Range($ws.Cells.Item($first,$col), $ws.Cells.Item($last,$col)).Font.Color = $blue }
  foreach ($col in 8,12)     { $ws.Range($ws.Cells.Item($first,$col), $ws.Cells.Item($last,$col)).Interior.Color = $yellow }
  $ws.Range($ws.Cells.Item($first,9), $ws.Cells.Item($last,9)).Font.Bold = $true
  $ws.Range($ws.Cells.Item($first,6), $ws.Cells.Item($last,9)).NumberFormat = '0'
  $ws.Range($ws.Cells.Item($first,12), $ws.Cells.Item($last+1,13)).NumberFormat = '#,##0.00'
  $ws.Range($ws.Cells.Item($first,1), $ws.Cells.Item($last,14)).WrapText = $true
  $ws.Range($ws.Cells.Item($first,1), $ws.Cells.Item($last,14)).VerticalAlignment = -4160   # top
  $sr = $last + 1; $sumRow[$name] = $sr
  $ws.Cells.Item($sr,12).Value2 = 'Summe'; $ws.Cells.Item($sr,12).Font.Bold = $true
  $ws.Cells.Item($sr,13).Formula = "=SUM(M${first}:M$last)"; $ws.Cells.Item($sr,13).Font.Bold = $true
  $ws.Range($ws.Cells.Item(4,1), $ws.Cells.Item($last,14)).Borders.LineStyle = 1
  $ws.Range($ws.Cells.Item(4,1), $ws.Cells.Item($last,14)).Borders.Color = 0xBFBFBF
  [void]$ws.Range($ws.Cells.Item(4,1), $ws.Cells.Item($last,14)).AutoFilter()
  $ws.Activate(); $xl.ActiveWindow.SplitRow = 4; $xl.ActiveWindow.SplitColumn = 0; $xl.ActiveWindow.FreezePanes = $true
  $ws.PageSetup.Orientation = 2; $ws.PageSetup.Zoom = $false; $ws.PageSetup.FitToPagesWide = 1; $ws.PageSetup.FitToPagesTall = $false
}

# ---------------- overview ----------------
$ov.Cells.Font.Name = 'Arial'; $ov.Cells.Font.Size = 10
$ov.Columns.Item(1).ColumnWidth = 3; $ov.Columns.Item(2).ColumnWidth = 34
foreach ($c in 3..7) { $ov.Columns.Item($c).ColumnWidth = 16 }
$ov.Columns.Item(8).ColumnWidth = 60
$ov.Cells.Item(1,2).Value2 = 'Einkaufsliste Synthesizer'; $ov.Cells.Item(1,2).Font.Size = 16; $ov.Cells.Item(1,2).Font.Bold = $true
$ov.Cells.Item(2,2).Value2 = 'Maturaprojekt · Stand 21.09.2026 · abgeleitet aus SynthesizerFinal Rev. 4.0 (Stückliste) plus Bedienfeld, Kabel, Stromversorgung, Arduino, Mechanik'
$ov.Cells.Item(4,2).Value2 = 'Eingabe'; $ov.Cells.Item(4,2).Font.Bold = $true
$ov.Cells.Item(6,2).Value2 = 'Anzahl Geräte'
$ov.Cells.Item(6,3).Value2 = 2; $ov.Cells.Item(6,3).Font.Color = $blue; $ov.Cells.Item(6,3).Interior.Color = $yellow; $ov.Cells.Item(6,3).Font.Bold = $true
$ov.Cells.Item(6,4).Value2 = 'alle Bestellmengen rechnen sich daraus (Vorgabe: 2 Geräte, Angabe von Timo)'

$ov.Cells.Item(8,2).Value2 = 'Kosten pro Blatt (Schätzung, CHF)'; $ov.Cells.Item(8,2).Font.Bold = $true
$row = 9
foreach ($name in $order) {
  $ov.Cells.Item($row,2).Value2 = $name
  $ov.Cells.Item($row,3).Formula = "='$name'!M$($sumRow[$name])"
  $ov.Cells.Item($row,3).Font.Color = 0x008000; $ov.Cells.Item($row,3).NumberFormat = '#,##0.00'
  $row++
}
$ov.Cells.Item($row,2).Value2 = 'Total Bauteile (ohne Platinen)'; $ov.Cells.Item($row,2).Font.Bold = $true
$ov.Cells.Item($row,3).Formula = "=SUM(C9:C$($row-1))"; $ov.Cells.Item($row,3).Font.Bold = $true; $ov.Cells.Item($row,3).NumberFormat = '#,##0.00'
$totalRow = $row

$row += 2
$ov.Cells.Item($row,2).Value2 = 'Kosten pro Lieferant (Schätzung, CHF)'; $ov.Cells.Item($row,2).Font.Bold = $true
$row++
$suppliers = @('Distrelec (CH)','Musikding (DE)','Bastelgarage (CH)','Galaxus (CH)')
foreach ($sup in $suppliers) {
  $ov.Cells.Item($row,2).Value2 = $sup
  $parts = foreach ($name in $order) { "SUMIF('$name'!`$J`$5:`$J`$$($lastRow[$name]),`$B`$$row,'$name'!`$M`$5:`$M`$$($lastRow[$name]))" }
  $ov.Cells.Item($row,3).Formula = '=' + ($parts -join '+')
  $ov.Cells.Item($row,3).NumberFormat = '#,##0.00'
  $row++
}
$ov.Cells.Item($row,2).Value2 = 'Kontrolle: Summe Lieferanten = Total'
$ov.Cells.Item($row,3).Formula = "=IF(ABS(SUM(C$($row-$suppliers.Count):C$($row-1))-C$totalRow)<0.005,""stimmt"",""FEHLT: Lieferant prüfen"")"
$checkRow = $row

$row += 2
$ov.Cells.Item($row,2).Value2 = 'Platinen bei JLCPCB'; $ov.Cells.Item($row,2).Font.Bold = $true
$row++
$jh = @('Platine','pro Gerät','benötigt','bestellen (5er-Schritte)','davon bestückt','SMD-Chips (JLCPCB)')
for ($c = 0; $c -lt $jh.Count; $c++) { $h = $ov.Cells.Item($row, $c + 2); $h.Value2 = $jh[$c]; $h.Font.Bold = $true; $h.Font.Color = 0xFFFFFF; $h.Interior.Color = $headFill }
$jt = $row
$boards = @(@('Oszillator',3,1,'U102 74LVC2G17, U103 OPA4196, U104 OPA1662'), @('Filter',4,1,'U401 OPA4196'), @('Hauptplatine',1,0,'keine'))
foreach ($bd in $boards) {
  $row++
  $ov.Cells.Item($row,2).Value2 = $bd[0]
  $ov.Cells.Item($row,3).Value2 = [double]$bd[1]; $ov.Cells.Item($row,3).Font.Color = $blue
  $ov.Cells.Item($row,4).Formula = "=C$row*`$C`$6"
  $ov.Cells.Item($row,5).Formula = "=CEILING(D$row,5)"
  if ($bd[2] -eq 1) { $ov.Cells.Item($row,6).Formula = "=D$row" } else { $ov.Cells.Item($row,6).Value2 = [double]0 }
  $ov.Cells.Item($row,7).Value2 = $bd[3]
}
$ov.Range($ov.Cells.Item($jt,2), $ov.Cells.Item($row,7)).Borders.LineStyle = 1
$row += 2
$notes = @(
 'Wichtig und leicht zu übersehen',
 '• Mit 2 Geräten ändert sich die Bestellung bei JLCPCB: Oszillator 10 Stück (6 bestückt), Filter 10 (8 bestückt), Hauptplatine 5 - siehe Tabelle oben.',
 '• Preise sind grobe Schätzungen (Stand Sept. 2026, nicht einzeln geprüft) - beim Bestellen den echten Preis in die gelbe Spalte eintragen, dann stimmen die Summen.',
 '• Frequenz- und Cutoff-Potis logarithmisch (A) kaufen: mit linearen liegt die höchste Oktave auf dem ersten 1 % des Drehwegs.',
 '• Zeitkondensatoren (56 nF, 15 nF) müssen Folie sein - der Keramik-"104" vom Steckbrett lag 56 % neben dem aufgedruckten Wert.',
 '• Stromversorgung: den 0-V-Ausgang des TRACO-Wandlers mit dem Minus des 12-V-Netzteils verbinden - sonst misst der Arduino ohne gemeinsame Masse.',
 '• Achsen: Potis und Drehknöpfe vom selben Händler, damit Achse (6 mm oder 1/4") und Knopf zusammenpassen.',
 '• Bestellung aus Deutschland (Musikding): ab ca. CHF 62 Warenwert fällt Schweizer MWST an, dazu eine Gebühr des Paketdienstes. Eine gesammelte Bestellung ist günstiger als mehrere kleine.',
 '• Die Eingangsstufe des Arduino (Blatt Arduino, "VORLÄUFIG") ist noch nicht gezeichnet - die Teile sind bereits eingeplant.'
)
foreach ($n in $notes) { $ov.Cells.Item($row,2).Value2 = $n; $row++ }
$ov.Cells.Item($row - $notes.Count,2).Font.Bold = $true
$ov.Activate()

$wb.SaveAs($Out, 51)
$xl.Calculate()

# ---------------- read back and check ----------------
$errs = 0
foreach ($w in $wb.Worksheets) {
  $ur = $w.UsedRange
  foreach ($cell in $ur.Cells) { if ($cell.Text -like '#*') { $errs++; Write-Output ("ERROR " + $w.Name + '!' + $cell.Address(0,0) + ' ' + $cell.Text) } }
}
Write-Output "formula errors: $errs"
Write-Output ("sheet names: " + (($wb.Worksheets | ForEach-Object { $_.Name }) -join ' | '))
Write-Output ("total CHF: " + $ov.Cells.Item($totalRow,3).Value2 + "   supplier check: " + $ov.Cells.Item($checkRow,3).Text)
for ($i = $jt + 1; $i -le $jt + 3; $i++) { Write-Output ("JLC " + $ov.Cells.Item($i,2).Text + ": need " + $ov.Cells.Item($i,4).Text + ", order " + $ov.Cells.Item($i,5).Text + ", assembled " + $ov.Cells.Item($i,6).Text) }
$p = $wb.Worksheets.Item('Platine')
for ($i = 5; $i -le $lastRow['Platine']; $i++) { if ($p.Cells.Item($i,3).Text -eq '10kΩ') { Write-Output ("check 10k: per " + $p.Cells.Item($i,6).Text + " extra " + $p.Cells.Item($i,7).Text + " -> order " + $p.Cells.Item($i,9).Text) } }
$a = $wb.Worksheets.Item('Arduino')
Write-Output ("check Arduino Uno: per " + $a.Cells.Item(5,6).Text + " have " + $a.Cells.Item(5,8).Text + " -> order " + $a.Cells.Item(5,9).Text)
foreach ($name in $order) { Write-Output ("sheet " + $name + " sum " + $wb.Worksheets.Item($name).Cells.Item($sumRow[$name],13).Value2) }
$wb.Save()
$wb.Close($false); $xl.Quit()
[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)
