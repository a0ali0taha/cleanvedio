python3 'f:\Ahmed\lab\scripts\NoMusic\cleanvedio\server.py'
for /f "tokens=*" %%i in ('python -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print(s.getsockname()[0]); s.close()"') do set IP=%%i
echo Current IP: %IP%
start http://%IP%

pause