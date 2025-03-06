<#
    .SYNOPSIS
    Converts Condor 2 landscapes to Condor 3 compatibilty when the conversion archive download is available

    .DESCRIPTION
    Extracts Condor landscape conversion files and links directories

    .PARAMETER Condor2
    Path to the Condor 2 install folder

    .PARAMETER Condor3
    Path to the Condor 3 install folder

    .PARAMETER Downloads
    Path to the folder containing the conversion file downloads

    .INPUTS
    None. You cannot pipe objects to Convert-Landscape.

    .OUTPUTS
    None.

  #>

param(
    [Parameter()]
    $Condor2 = 'C:\Condor2',

    [Parameter()]
    $Condor3 = 'C:\Condor3',

	[Parameter()]
	$Downloads = (New-Object -ComObject Shell.Application).NameSpace('shell:Downloads').Self.Path  # [Environment]::GetFolderPath()
)

$conversions = Get-ChildItem -Path $Downloads -File -Filter '*_to_C3.7z'
if (-not $conversions)
{
	Write-Error "No conversion files found in $($Downloads)"
}
else
{
	$landscapes2 = [IO.DirectoryInfo][IO.Path]::Combine($Condor2, 'Landscapes')
	$landscapes3 = [IO.DirectoryInfo][IO.Path]::Combine($Condor3, 'Landscapes')
	$conversions | %{
		$conv = $_
		$name = [IO.Path]::GetFileName($_) -replace '_to_C3\.7z$', ''
		$c2l = [IO.DirectoryInfo][IO.Path]::Combine($landscapes2, $name)
		if (-not $c2l.Exists)
		{
			Write-Warning "Condor2 landscape $($name) not present"
		}
		else
		{
			if (-not $c2l.GetFiles('*.tm3'))
			{
				Write-Host -ForegroundColor Yellow "Converting $($name)..."
				# Extract conversion files
				& 'C:\Program Files\7-Zip\7z.exe' x -t7z "-o$($landscapes2)" $conv.FullName
				$c2t = [IO.DirectoryInfo][IO.Path]::Combine($landscapes2, "$($name)_to_C3")
				try
				{
					if ($c2t.Exists)
					{
						Get-ChildItem -Path $c2t.FullName -File -Recurse | %{
							$to = [IO.Path]::Combine($c2l.FullName, $_.FullName.Remove(0, $c2t.FullName.Length + 1))
							Move-Item -Path $_ -Destination $to -Force
						}
					}
					else
					{
						Write-Error "Extraction error"
					}
				}
				finally
				{
					$c2t.Delete($true)
				}

				# Create directory link
				$c3l = [IO.DirectoryInfo][IO.Path]::Combine($landscapes3, $name)
				if (-not $c3l.Exists)
				{
					New-Item -ItemType SymbolicLink -Path $c3l.FullName -Target $c2l.FullName
				}
			}
		}
	} | Out-Null
}
