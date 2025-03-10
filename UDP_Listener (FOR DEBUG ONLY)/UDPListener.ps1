$port = 65432
$endpoint = New-Object System.Net.IPEndPoint([IPAddress]::Any, $port)
$udpClient = New-Object System.Net.Sockets.UdpClient($port)

Write-Host "Listening on UDP port $port..."
while ($true) {
    $bytes = $udpClient.Receive([ref]$endpoint)
    $data = [Text.Encoding]::ASCII.GetString($bytes)
    Write-Host "Received: $data"
}