#!/usr/bin/env python3
"""
OpenSuperWhisper Web Server Entry Point
Docker container entry point for the Web API server
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Ensure OpenSuperWhisper module is importable
sys.path.insert(0, str(Path(__file__).parent / 'OpenSuperWhisper'))

def setup_environment():
    """Setup environment for Docker deployment"""

    # Set default values for environment variables
    os.environ.setdefault('HOST', '0.0.0.0')
    os.environ.setdefault('PORT', '8000')

    # Disable GUI-related Qt environment variables
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    os.environ['DISPLAY'] = ':99'  # Dummy display for any Qt imports

    # Set logging configuration
    os.environ.setdefault('PYTHONUNBUFFERED', '1')

    # Create necessary directories
    os.makedirs('/tmp/opensuperwhisper', exist_ok=True)
    os.makedirs('/app/logs', exist_ok=True)

    print("🚀 OpenSuperWhisper Web API Server")
    print("===================================")
    print("Version: 0.6.13")
    print(f"Host: {os.getenv('HOST', '0.0.0.0')}")
    print(f"Port: {os.getenv('PORT', '8000')}")

    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  WARNING: OPENAI_API_KEY not set!")
        print("   API calls will fail without a valid OpenAI API key.")
        print("   Set the environment variable:")
        print("   docker run -e OPENAI_API_KEY=your_key_here ...")
        print()
    else:
        api_key = os.getenv('OPENAI_API_KEY', '')
        masked_key = api_key[:10] + '*' * (len(api_key) - 14) + api_key[-4:] if len(api_key) > 14 else 'sk-***'
        print(f"✅ OpenAI API Key: {masked_key}")

    print("\n📚 Available Endpoints:")
    print("   GET  / - Health check and available models")
    print("   POST /transcribe - Transcribe audio file")
    print("   POST /format-text - Format text only")
    print(f"\n🌐 API Documentation: http://localhost:{os.getenv('PORT', '8000')}/docs")
    print("===================================\n")

def main():
    """Main entry point"""

    # Setup environment
    setup_environment()

    try:
        # Import after environment setup
        import uvicorn

        from OpenSuperWhisper.web_api import app

        # Get configuration
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', '8000'))
        workers = int(os.getenv('WORKERS', '1'))

        # Production server configuration
        if os.getenv('ENVIRONMENT') == 'production':
            # Use Gunicorn for production
            from gunicorn.app.wsgiapp import WSGIApplication

            class StandaloneApplication(WSGIApplication):
                def __init__(self, app, options=None):
                    self.options = options or {}
                    self.application = app
                    super().__init__()

                def load_config(self):
                    for key, value in self.options.items():
                        self.cfg.set(key.lower(), value)

                def load(self):
                    return self.application

            options = {
                'bind': f'{host}:{port}',
                'workers': workers,
                'worker_class': 'uvicorn.workers.UvicornWorker',
                'max_requests': 1000,
                'max_requests_jitter': 100,
                'preload_app': True,
                'access_log_format': '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s',
                'timeout': 120,
            }

            StandaloneApplication(app, options).run()
        else:
            # Development server
            uvicorn.run(
                app,
                host=host,
                port=port,
                log_level="info",
                access_log=True,
                reload=False  # Disabled for Docker
            )

    except KeyboardInterrupt:
        print("\n👋 Shutting down OpenSuperWhisper Web API Server...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
