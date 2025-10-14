$uri = "http://127.0.0.1:8000/api/review"
$headers = @{
    "Authorization" = "Bearer test-admin-key-12345"
}

# Create multipart form data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"test_file.py`"",
    "Content-Type: text/plain$LF",
    (Get-Content "test_file.py" -Raw),
    "--$boundary--$LF"
) -join $LF

$headers["Content-Type"] = "multipart/form-data; boundary=$boundary"

try {
    $response = Invoke-WebRequest -Uri $uri -Method POST -Headers $headers -Body $bodyLines
    Write-Host "Success! Status: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response Body: $responseBody"
    }
}