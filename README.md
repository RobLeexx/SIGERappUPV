# SIGERappUPV
An report app for ISI (Ingeniería de Sistemas de Información)

## Local SonarQube analysis

With SonarQube running at http://localhost:9000, run from this directory in Bash:

```bash
read -rsp 'SonarQube token: ' SONAR_TOKEN; printf '\n'
export SONAR_TOKEN
sonar-scanner
unset SONAR_TOKEN
```

Results: http://localhost:9000/dashboard?id=SIGER. Keep tokens out of project files.
