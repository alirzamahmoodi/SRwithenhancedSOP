# Installation Guide

## System Requirements
- Windows 10/11 or Windows Server 2019/22/25 64-bit
- Miniconda3
- Oracle Instant Client 19c+ (if not using thick client, which is included in the Oracle 12c in PACS Server)
- 4GB+ free disk space

## Development Setup

1. **Clone Repository**
```bash
git clone https://github.com/alirzamahmoodi/SRwithenhancedSOP.git
cd SRwithenhancedSOP
```

2. **Create Conda Environment**
```bash
conda env create -f environment.yml
```

3. **Activate Environment**
```bash
conda activate google-ai
```

4. **Oracle Client Configuration**
```bash
# From <mcfile name="main.py" path="e:\SRwithenhancedSOP\main.py"></mcfile>
set ORACLE_HOME=C:\Oracle\instantclient_19_20
set PATH=%ORACLE_HOME%;%PATH%
```

## Production Deployment

1. **Build Executable**
```bash
pyinstaller audio_transcriber.spec
```

2. **Deploy Application**
```bash
xcopy /E /I dist "C:\Program Files\SRTranscriber"
```
3. **Copu config.yaml to C:\Program Files\SRTranscriber**

4. **Configure Services**
```bash
# From <mcfile name="readme.md" path="e:\SRwithenhancedSOP\readme.md"></mcfile>
sc create SRTranscriber binPath= "C:\Program Files\SRTranscriber\audio_transcriber.exe --monitor"
```

## Verification

1. **Test Environment**
```bash
python -c "import oracledb; print(oracledb.__version__)"
```

2. **Validate Installation**
```bash
audio_transcriber.exe --version
```

## Post-Install Configuration

**Edit Configuration File**
```yaml
# From <mcfile name="config.yaml" path="e:\SRwithenhancedSOP\config.yaml"></mcfile>
ORACLE_HOST: "172.31.100.60" # for example
GEMINI_API_KEY: "your-api-key"
```

```

## Troubleshooting
- **Environment Issues**: Validate with `conda list --export`
- **Oracle Errors**: Check `ORACLE_HOME` path in system variables
- **API Failures**: Verify network access to `generativeai.googleapis.com:443`

## Cross References
- [Architecture Overview](architecture.md)
- [Configuration Guide](../config/config_reference.md)
```