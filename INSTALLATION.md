# OpenSuperWhisper Installation Guide

## 📦 Quick Installation

### Windows

1. **Download the latest release**
   - Go to [Releases](https://github.com/Yutaishy/OpenSuperWhisper/releases/latest)
   - Download `opensuperwhisper-v0.7.0-windows-amd64.zip`

2. **Extract and run**
   ```powershell
   # Extract the zip file
   Expand-Archive opensuperwhisper-v0.7.0-windows-amd64.zip -DestinationPath .
   
   # Run the application
   .\opensuperwhisper-v0.7.0-windows-amd64\opensuperwhisper.exe
   ```

3. **Optional: Add to PATH**
   ```powershell
   # Add to system PATH for global access
   $env:PATH += ";$PWD\opensuperwhisper-v0.7.0-windows-amd64"
   ```

### Linux

1. **Download the latest release**
   ```bash
   # For AMD64
   wget https://github.com/Yutaishy/OpenSuperWhisper/releases/download/v0.7.0/opensuperwhisper-v0.7.0-linux-amd64.tar.gz
   
   # For ARM64
   wget https://github.com/Yutaishy/OpenSuperWhisper/releases/download/v0.7.0/opensuperwhisper-v0.7.0-linux-arm64.tar.gz
   ```

2. **Extract and install**
   ```bash
   # Extract
   tar -xzf opensuperwhisper-v0.7.0-linux-amd64.tar.gz
   
   # Make executable
   chmod +x opensuperwhisper-v0.7.0-linux-amd64/opensuperwhisper
   
   # Run
   ./opensuperwhisper-v0.7.0-linux-amd64/opensuperwhisper
   
   # Optional: Install globally
   sudo mv opensuperwhisper-v0.7.0-linux-amd64/opensuperwhisper /usr/local/bin/
   ```

### macOS

1. **Download the latest release**
   ```bash
   # For Intel Mac (AMD64)
   wget https://github.com/Yutaishy/OpenSuperWhisper/releases/download/v0.7.0/opensuperwhisper-v0.7.0-darwin-amd64.tar.gz
   
   # For Apple Silicon (ARM64)
   wget https://github.com/Yutaishy/OpenSuperWhisper/releases/download/v0.7.0/opensuperwhisper-v0.7.0-darwin-arm64.tar.gz
   ```

2. **Extract and install**
   ```bash
   # Extract
   tar -xzf opensuperwhisper-v0.7.0-darwin-amd64.tar.gz
   
   # Make executable
   chmod +x opensuperwhisper-v0.7.0-darwin-amd64/opensuperwhisper
   
   # Remove quarantine attribute (macOS security)
   xattr -d com.apple.quarantine opensuperwhisper-v0.7.0-darwin-amd64/opensuperwhisper
   
   # Run
   ./opensuperwhisper-v0.7.0-darwin-amd64/opensuperwhisper
   ```

## 🐳 Docker Installation

```bash
# Pull the Docker image
docker pull ghcr.io/yutaishy/opensuperwhisper:latest

# Run the container
docker run -d \
  --name opensuperwhisper \
  -p 8000:8000 \
  -v /path/to/data:/app/data \
  ghcr.io/yutaishy/opensuperwhisper:latest
```

## 🐍 Installation from Source

### Prerequisites
- Python 3.11 or higher
- pip
- Git

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Yutaishy/OpenSuperWhisper.git
   cd OpenSuperWhisper
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python src/run_app.py
   ```

## 🔧 Configuration

### Environment Variables

```bash
# Create .env file in the application directory
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=INFO
```

### Configuration File

Create `config.yaml`:
```yaml
app:
  name: OpenSuperWhisper
  version: 0.7.0
  
server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  
audio:
  sample_rate: 16000
  channels: 1
  format: wav
```

## ✅ Verify Installation

```bash
# Check version
opensuperwhisper --version

# Run health check
opensuperwhisper --health

# Start with verbose logging
opensuperwhisper --verbose
```

## 🆘 Troubleshooting

### Windows Issues

**Error: "Windows protected your PC"**
- Click "More info" → "Run anyway"
- Or disable Windows Defender SmartScreen temporarily

**Missing DLL errors**
- Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### Linux Issues

**Permission denied**
```bash
chmod +x opensuperwhisper
```

**Library not found**
```bash
# Install required libraries
sudo apt-get update
sudo apt-get install libgomp1 ffmpeg
```

### macOS Issues

**"Cannot be opened because the developer cannot be verified"**
```bash
# Remove quarantine
xattr -d com.apple.quarantine opensuperwhisper

# Or allow in System Preferences → Security & Privacy
```

## 📚 Additional Resources

- [Documentation](https://github.com/Yutaishy/OpenSuperWhisper/wiki)
- [API Reference](https://github.com/Yutaishy/OpenSuperWhisper/blob/main/docs/API.md)
- [Contributing Guide](https://github.com/Yutaishy/OpenSuperWhisper/blob/main/CONTRIBUTING.md)
- [Support](https://github.com/Yutaishy/OpenSuperWhisper/issues)

## 📄 License

OpenSuperWhisper is released under the MIT License. See [LICENSE](LICENSE) for details.