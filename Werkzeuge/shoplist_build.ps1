# Builds the shopping-list workbook through Excel (COM), so Excel itself computes and the
# result can be read back and checked. Data comes from shoplist_data.py (JSON).
# Rev. 22.09.2026: prices in the shop's currency (USD or CHF), converted with one rate cell.
param([string]$Json, [string]$Out)

$d = Get-Content -Raw -Encoding UTF8 $Json | ConvertFrom-Json
$order = @('Platine','Bedienfeld','Verbinder','Stromversorgung','Arduino','Mechanik','Abgleich+Reserve','Werkzeug')
$desc = @{
  'Platine'          = 'Bedrahtete Bauteile auf den Platinen - von Hand gelötet. Die SMD-Chips (TL074CDR, OPA1662, 74LVC2G17) bestückt JLCPCB; sie fehlen hier.'
  'Bedienfeld'       = 'Potis, Schalter, Buchsen, Knöpfe - sitzen im Bedienfeld und sind per Kabel mit den Platinen verbunden.'
  'Verbinder'        = 'JST-XH-Stecker (original JST) und Litze für alle Kabel zwischen den Platinen und zum Bedienfeld.'
  'Stromversorgung'  = '12-V-Steckernetzteil ausserhalb des Holzgehäuses; +12 V direkt, −12 V aus einem kleinen DC/DC-Wandler, 12 V für den Arduino.'
  'Arduino'          = 'Oszilloskop mit Display, fest im Gerät.'
  'Mechanik'         = 'Befestigung aller Platinen auf dem Holzboden (Messing-Abstandsbolzen direkt ins Holz).'
  'Abgleich+Reserve' = 'Ausweichwerte zum Feinabstimmen und Ersatzteile für Reparaturen - einmalig, nicht pro Gerät.'
  'Werkzeug'         = 'Einmalig. Lötzinn und Entlötlitze nur, falls nicht vorhanden (dann Menge eintragen).'
}
$hdr = @('Erledigt','Teil','Wert / Typ','Bauform / Spezifikation','Wo (Referenz)','Pro Gerät',
         'Zusätzlich (Reserve / Rundung)','Vorhanden','Bestellmenge','Lieferant',
         'Art.-Nr. im Shop','Preis/Stk. (Warenkorb)','Währung','Summe CHF','Bemerkung')
$widths = @(8,22,26,34,32,9,13,10,11,13,14,12,8,11,60)
$DEV  = "'Übersicht'!`$C`$6"          # device count cell
$RATE = "'Übersicht'!`$C`$7"          # USD -> CHF

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
  $ws.Cells.Item(3,1).Value2 = 'Bestellmenge = Pro Gerät × Anzahl Geräte (Übersicht) + Zusätzlich - Vorhanden. Bei 2 Geräten ist das genau die Menge im Warenkorb (Shops runden, z. B. Widerstände in 10er-Schritten).'
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
    $ws.Cells.Item($r,11).NumberFormat = '@'
    $ws.Cells.Item($r,11).Value2 = [string]$it.pn
    $ws.Cells.Item($r,12).Value2 = [double]$it.price
    $ws.Cells.Item($r,13).Value2 = $it.cur
    $ws.Cells.Item($r,14).Formula = "=I$r*L$r*IF(M$r=""USD"",$RATE,1)"
    $ws.Cells.Item($r,15).Value2 = $it.note
    $r++
  }
  $first = 5; $last = $r - 1; $lastRow[$name] = $last
  foreach ($col in 6,7,8,12) { $ws.Range($ws.Cells.Item($first,$col), $ws.Cells.Item($last,$col)).Font.Color = $blue }
  foreach ($col in 8)        { $ws.Range($ws.Cells.Item($first,$col), $ws.Cells.Item($last,$col)).Interior.Color = $yellow }
  $ws.Range($ws.Cells.Item($first,9), $ws.Cells.Item($last,9)).Font.Bold = $true
  $ws.Range($ws.Cells.Item($first,6), $ws.Cells.Item($last,9)).NumberFormat = '0'
  $ws.Range($ws.Cells.Item($first,12), $ws.Cells.Item($last,12)).NumberFormat = '0.00###'
  $ws.Range($ws.Cells.Item($first,14), $ws.Cells.Item($last+1,14)).NumberFormat = '0.00'
  $ws.Range($ws.Cells.Item($first,1), $ws.Cells.Item($last,15)).WrapText = $true
  $ws.Range($ws.Cells.Item($first,1), $ws.Cells.Item($last,15)).VerticalAlignment = -4160   # top
  $sr = $last + 1; $sumRow[$name] = $sr
  $ws.Cells.Item($sr,13).Value2 = 'Summe'; $ws.Cells.Item($sr,13).Font.Bold = $true
  $ws.Cells.Item($sr,14).Formula = "=SUM(N${first}:N$last)"; $ws.Cells.Item($sr,14).Font.Bold = $true
  $ws.Range($ws.Cells.Item(4,1), $ws.Cells.Item($last,15)).Borders.LineStyle = 1
  $ws.Range($ws.Cells.Item(4,1), $ws.Cells.Item($last,15)).Borders.Color = 0xBFBFBF
  [void]$ws.Range($ws.Cells.Item(4,1), $ws.Cells.Item($last,15)).AutoFilter()
  $ws.Activate(); $xl.ActiveWindow.SplitRow = 4; $xl.ActiveWindow.SplitColumn = 0; $xl.ActiveWindow.FreezePanes = $true
  $ws.PageSetup.Orientation = 2; $ws.PageSetup.Zoom = $false; $ws.PageSetup.FitToPagesWide = 1; $ws.PageSetup.FitToPagesTall = $false
}

# ---------------- overview ----------------
$ov.Cells.Font.Name = 'Arial'; $ov.Cells.Font.Size = 10
$ov.Columns.Item(1).ColumnWidth = 3; $ov.Columns.Item(2).ColumnWidth = 36
foreach ($c in 3..7) { $ov.Columns.Item($c).ColumnWidth = 15 }
$ov.Columns.Item(8).ColumnWidth = 70
$ov.Cells.Item(1,2).Value2 = 'Einkaufsliste Synthesizer - sparsame Version'; $ov.Cells.Item(1,2).Font.Size = 16; $ov.Cells.Item(1,2).Font.Bold = $true
$ov.Cells.Item(2,2).Value2 = 'Maturaprojekt · Stand 22.09.2026 · Preise = Warenkorb-Preise vom 22.09.2026 (Tayda, LCSC, Conrad); JLCPCB geschätzt, da nur nach Login'
$ov.Cells.Item(4,2).Value2 = 'Eingabe'; $ov.Cells.Item(4,2).Font.Bold = $true
$ov.Cells.Item(6,2).Value2 = 'Anzahl Geräte'
$ov.Cells.Item(6,3).Value2 = 2
$ov.Cells.Item(6,4).Value2 = 'die Warenkörbe sind für 2 Geräte gefüllt'
$ov.Cells.Item(7,2).Value2 = 'Kurs USD → CHF'
$ov.Cells.Item(7,3).Value2 = 0.84
$ov.Cells.Item(7,4).Value2 = 'Tageskurs 22.09.2026: 0,821 - aufgerundet für die Umrechnungsgebühr von Karte / PayPal'
foreach ($rr in 6,7) { $cc = $ov.Cells.Item($rr,3); $cc.Font.Color = $blue; $cc.Interior.Color = $yellow; $cc.Font.Bold = $true }

$ov.Cells.Item(9,2).Value2 = 'Bauteile pro Blatt (CHF)'; $ov.Cells.Item(9,2).Font.Bold = $true
$row = 10
foreach ($name in $order) {
  $ov.Cells.Item($row,2).Value2 = $name
  $ov.Cells.Item($row,3).Formula = "='$name'!N$($sumRow[$name])"
  $ov.Cells.Item($row,3).Font.Color = 0x008000; $ov.Cells.Item($row,3).NumberFormat = '0.00'
  $row++
}
$ov.Cells.Item($row,2).Value2 = 'Total Bauteile (ohne Platinen, ohne Versand)'; $ov.Cells.Item($row,2).Font.Bold = $true
$ov.Cells.Item($row,3).Formula = "=SUM(C10:C$($row-1))"; $ov.Cells.Item($row,3).Font.Bold = $true; $ov.Cells.Item($row,3).NumberFormat = '0.00'
$totalRow = $row

$row += 2
$ov.Cells.Item($row,2).Value2 = 'Pro Lieferant (CHF)'; $ov.Cells.Item($row,2).Font.Bold = $true
$row++
$sh = @('Lieferant','Ware','Versand','Total','Versand in Shop-Währung','Versandart')
for ($c = 0; $c -lt $sh.Count; $c++) { $h = $ov.Cells.Item($row, $c + 2); $h.Value2 = $sh[$c]; $h.Font.Bold = $true; $h.Font.Color = 0xFFFFFF; $h.Interior.Color = $headFill }
$supTop = $row + 1
foreach ($sp in $d.shipping) {
  $row++
  $sup = $sp[0]; $cost = [double]$sp[1]; $cur = $sp[2]; $what = $sp[3]
  $ov.Cells.Item($row,2).Value2 = $sup
  $parts = foreach ($name in $order) { "SUMIF('$name'!`$J`$5:`$J`$$($lastRow[$name]),`$B$row,'$name'!`$N`$5:`$N`$$($lastRow[$name]))" }
  $ov.Cells.Item($row,3).Formula = '=' + ($parts -join '+')
  $ov.Cells.Item($row,6).Value2 = "$cost $cur"
  $cs = ([string]$cost).Replace(',', '.')
  if ($cur -eq 'USD') { $ov.Cells.Item($row,4).Formula = "=$cs*`$C`$7" } else { $ov.Cells.Item($row,4).Formula = "=$cs" }
  $ov.Cells.Item($row,5).Formula = "=C$row+D$row"; $ov.Cells.Item($row,5).Font.Bold = $true
  $ov.Cells.Item($row,7).Value2 = $what
  foreach ($c in 3,4,5) { $ov.Cells.Item($row,$c).NumberFormat = '0.00' }
}
$supBot = $row
$row++
$ov.Cells.Item($row,2).Value2 = 'Kontrolle: Summe Lieferanten = Total Bauteile'
$ov.Cells.Item($row,3).Formula = "=IF(ABS(SUM(C${supTop}:C$supBot)-C$totalRow)<0.005,""stimmt"",""FEHLT: Lieferant prüfen"")"
$checkRow = $row
$ov.Range($ov.Cells.Item($supTop-1,2), $ov.Cells.Item($supBot,7)).Borders.LineStyle = 1

$row += 2
$ov.Cells.Item($row,2).Value2 = 'Platinen bei JLCPCB (Schätzung in USD - der genaue Preis erscheint erst nach dem Login)'; $ov.Cells.Item($row,2).Font.Bold = $true
$row++
$jh = @('Platine','pro Gerät','benötigt','bestellen','davon bestückt','SMD-Chips (JLCPCB)')
for ($c = 0; $c -lt $jh.Count; $c++) { $h = $ov.Cells.Item($row, $c + 2); $h.Value2 = $jh[$c]; $h.Font.Bold = $true; $h.Font.Color = 0xFFFFFF; $h.Interior.Color = $headFill }
$jt = $row
$boards = @(@('Oszillator',3,10,10,'U102 SN74LVC2G17DBVR (C10429), U103 TL074CDR (C12594), U104 OPA1662AIDR (C882794)'),
            @('Filter',4,10,10,'U401 TL074CDR (C12594)'),
            @('Hauptplatine',1,5,0,'keine - ohne Bestückung'))
foreach ($bd in $boards) {
  $row++
  $ov.Cells.Item($row,2).Value2 = $bd[0]
  $ov.Cells.Item($row,3).Value2 = [double]$bd[1]
  $ov.Cells.Item($row,4).Formula = "=C$row*`$C`$6"
  $ov.Cells.Item($row,5).Value2 = [double]$bd[2]
  $ov.Cells.Item($row,6).Value2 = [double]$bd[3]
  $ov.Cells.Item($row,7).Value2 = $bd[4]
}
$ov.Range($ov.Cells.Item($jt,2), $ov.Cells.Item($row,7)).Borders.LineStyle = 1
$row += 2
$jc = @(@('Oszillator-Platine 108 × 108 mm, 10 Stück',15.30,'Preis aus dem Angebot vom 22.09.2026'),
        @('Filter-Platine 80 × 68 mm, 10 Stück',5.00,'Sonderangebot bis 100 × 100 mm'),
        @('Hauptplatine 96 × 98 mm, 5 Stück',4.00,'Sonderangebot bis 100 × 100 mm'),
        @('Bestückung Oszillator: Einrichtung 8, Schablone ~1.5, 3 Extended-Teile à 3, Chips 10 × 1.42',33.00,'Schätzung'),
        @('Bestückung Filter: Einrichtung 8, Schablone ~1.5, 1 Extended-Teil 3, Chips 10 × 0.29',15.50,'Schätzung'),
        @('Versand DHL Express DDP (MWST inbegriffen)',35.00,'Schätzung für ~1 kg; für 0,5 kg zeigte JLCPCB 28 USD'))
$ov.Cells.Item($row,2).Value2 = 'Posten'; $ov.Cells.Item($row,3).Value2 = 'USD'; $ov.Cells.Item($row,4).Value2 = 'CHF'
foreach ($c in 2,3,4) { $ov.Cells.Item($row,$c).Font.Bold = $true }
$jcTop = $row + 1
foreach ($j in $jc) {
  $row++
  $ov.Cells.Item($row,2).Value2 = $j[0]; $ov.Cells.Item($row,3).Value2 = [double]$j[1]
  $ov.Cells.Item($row,4).Formula = "=C$row*`$C`$7"; $ov.Cells.Item($row,5).Value2 = $j[2]
  foreach ($c in 3,4) { $ov.Cells.Item($row,$c).NumberFormat = '0.00' }
}
$row++
$ov.Cells.Item($row,2).Value2 = 'JLCPCB total (Schätzung)'; $ov.Cells.Item($row,2).Font.Bold = $true
$ov.Cells.Item($row,3).Formula = "=SUM(C${jcTop}:C$($row-1))"; $ov.Cells.Item($row,4).Formula = "=SUM(D${jcTop}:D$($row-1))"
foreach ($c in 3,4) { $ov.Cells.Item($row,$c).NumberFormat = '0.00'; $ov.Cells.Item($row,$c).Font.Bold = $true }
$jlcRow = $row

$row += 2
$ov.Cells.Item($row,2).Value2 = 'GESAMTKOSTEN für 2 Geräte (CHF, inkl. Versand und MWST)'; $ov.Cells.Item($row,2).Font.Bold = $true; $ov.Cells.Item($row,2).Font.Size = 12
$ov.Cells.Item($row,3).Formula = "=SUM(E${supTop}:E$supBot)+D$jlcRow"; $ov.Cells.Item($row,3).Font.Bold = $true; $ov.Cells.Item($row,3).Font.Size = 12
$ov.Cells.Item($row,3).NumberFormat = '0.00'; $ov.Cells.Item($row,3).Interior.Color = 0xCCFFCC
$grandRow = $row
$row++
$ov.Cells.Item($row,2).Value2 = 'pro Gerät'
$ov.Cells.Item($row,3).Formula = "=C$grandRow/`$C`$6"; $ov.Cells.Item($row,3).NumberFormat = '0.00'

$row += 2
$notes = @(
 'Wichtig und leicht zu übersehen',
 '• Vier Bestellungen: JLCPCB (Platinen), LCSC (JST-Stecker, Sonderteile), Tayda (fast alles Übrige), Conrad (Netzteile, Litze). Anleitung: Einkauf/BESTELLEN.md.',
 '• Chinesische Feiertage 25.09.-07.10.2026: JLCPCB und LCSC arbeiten eingeschränkt. Wer bis 24.09. bestellt, bekommt die Platinen deutlich früher.',
 '• JLCPCB: Bestückung geht nur für ALLE Platinen einer Bestellung (10 von 10). Die überzähligen bestückten Platinen sind Reserve.',
 '• Vierfach-Op-Amp auf Oszillator und Filter ist jetzt ein TL074CDR statt OPA4196: gleiche Anschlüsse, Simulation deckungsgleich, 0.29 statt 3.62 USD.',
 '• Tonhöhe- und Cutoff-Potis mit Kennlinie C (umgekehrt logarithmisch) - so wie sie verdrahtet sind, verteilt nur C die Oktaven gleichmässig.',
 '• Zeitkondensatoren (56 nF, 15 nF) müssen Folie sein - der Keramik-"104" vom Steckbrett lag 56 % neben dem aufgedruckten Wert.',
 '• Stromversorgung neu: +12 V direkt vom Netzteil, −12 V aus dem DC/DC-Wandler B1212S (+Vo an Masse). Gemeinsame Masse mit dem Arduino ist damit automatisch gegeben.',
 '• Frontplatte höchstens ca. 3 mm dick (Klinkenbuchsen haben ein kurzes Gewinde) - bei dickerem Holz die Löcher von hinten aussenken.',
 '• Arduino nie direkt an ein Audiosignal: die Signale schwingen um 0 V (auch negativ). Immer über die Eingangsstufe (Blatt Arduino), Abgriff FILT_B_OUT an J817.'
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
Write-Output ("parts CHF: " + $ov.Cells.Item($totalRow,3).Value2 + "   supplier check: " + $ov.Cells.Item($checkRow,3).Text)
for ($i = $supTop; $i -le $supBot; $i++) { Write-Output ("  " + $ov.Cells.Item($i,2).Text + ": goods " + $ov.Cells.Item($i,3).Text + " + ship " + $ov.Cells.Item($i,4).Text + " = " + $ov.Cells.Item($i,5).Text) }
Write-Output ("JLC CHF: " + $ov.Cells.Item($jlcRow,4).Text + "   GRAND TOTAL CHF: " + $ov.Cells.Item($grandRow,3).Text + "   per device: " + $ov.Cells.Item($grandRow+1,3).Text)
$p = $wb.Worksheets.Item('Platine')
for ($i = 5; $i -le $lastRow['Platine']; $i++) { if ($p.Cells.Item($i,3).Text -eq '10kΩ') { Write-Output ("check 10k: per " + $p.Cells.Item($i,6).Text + " extra " + $p.Cells.Item($i,7).Text + " -> order " + $p.Cells.Item($i,9).Text + " (" + $p.Cells.Item($i,11).Text + ")") } }
$a = $wb.Worksheets.Item('Arduino')
Write-Output ("check Arduino Uno: per " + $a.Cells.Item(5,6).Text + " have " + $a.Cells.Item(5,8).Text + " -> order " + $a.Cells.Item(5,9).Text)
foreach ($name in $order) { Write-Output ("sheet " + $name + " sum " + $wb.Worksheets.Item($name).Cells.Item($sumRow[$name],14).Value2) }
$wb.Save()
$wb.Close($false); $xl.Quit()
[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl)
