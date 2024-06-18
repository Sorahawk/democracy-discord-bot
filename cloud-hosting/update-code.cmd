set /p IP=<../../ip.txt
start cmd /c scp -i ../../ec2.pem python-scripts/* ubuntu@%IP%:~/democracy-bot/python-scripts
