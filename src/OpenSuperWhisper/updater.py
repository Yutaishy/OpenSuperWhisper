"""
Auto-update system for OpenSuperWhisper
"""

import json
import hashlib
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import requests
from packaging import version
import logging
import sys
import os


class UpdateChannel(str):
    """Update channels"""
    STABLE = "stable"
    BETA = "beta"
    NIGHTLY = "nightly"


class UpdateInfo:
    """Update information container"""
    
    def __init__(self, data: Dict[str, Any]):
        self.version = data.get('tag_name', '').lstrip('v')
        self.name = data.get('name', '')
        self.body = data.get('body', '')
        self.published_at = data.get('published_at', '')
        self.prerelease = data.get('prerelease', False)
        self.assets = data.get('assets', [])
        self.html_url = data.get('html_url', '')
        
    def get_asset_for_platform(self) -> Optional[Dict[str, Any]]:
        """Get appropriate asset for current platform"""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Map platform to asset patterns
        patterns = {
            ('windows', 'amd64'): ['windows-amd64', 'windows-x64', 'win64'],
            ('linux', 'x86_64'): ['linux-amd64', 'linux-x64'],
            ('linux', 'aarch64'): ['linux-arm64', 'linux-aarch64'],
            ('darwin', 'x86_64'): ['darwin-amd64', 'macos-x64', 'darwin-x64'],
            ('darwin', 'arm64'): ['darwin-arm64', 'macos-arm64'],
        }
        
        # Normalize machine architecture
        if machine in ['amd64', 'x86_64']:
            machine = 'x86_64'
        elif machine in ['aarch64', 'arm64']:
            machine = 'aarch64'
            
        # Find matching asset
        key = (system, machine)
        if key in patterns:
            for asset in self.assets:
                asset_name = asset['name'].lower()
                for pattern in patterns[key]:
                    if pattern in asset_name:
                        return asset
                        
        return None
        
    def is_newer_than(self, current_version: str) -> bool:
        """Check if this update is newer than current version"""
        try:
            return version.parse(self.version) > version.parse(current_version)
        except Exception:
            return False


class AutoUpdater:
    """Automatic update manager for OpenSuperWhisper"""
    
    GITHUB_API_URL = "https://api.github.com/repos/Yutaishy/OpenSuperWhisper/releases"
    
    def __init__(
        self,
        current_version: str,
        channel: UpdateChannel = UpdateChannel.STABLE,
        check_interval_hours: int = 24,
        auto_download: bool = False,
        auto_install: bool = False
    ):
        """
        Initialize auto-updater
        
        Args:
            current_version: Current application version
            channel: Update channel to use
            check_interval_hours: Hours between update checks
            auto_download: Automatically download updates
            auto_install: Automatically install updates
        """
        self.current_version = current_version.lstrip('v')
        self.channel = channel
        self.check_interval = timedelta(hours=check_interval_hours)
        self.auto_download = auto_download
        self.auto_install = auto_install
        
        self.logger = logging.getLogger(__name__)
        self.config_path = self._get_config_path()
        self.config = self._load_config()
        
    def _get_config_path(self) -> Path:
        """Get configuration file path"""
        system = platform.system()
        
        if system == "Windows":
            base = Path.home() / "AppData" / "Local"
        elif system == "Darwin":  # macOS
            base = Path.home() / "Library" / "Application Support"
        else:  # Linux
            base = Path.home() / ".local" / "share"
            
        config_dir = base / "OpenSuperWhisper"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        return config_dir / "updater.json"
        
    def _load_config(self) -> Dict[str, Any]:
        """Load updater configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
                
        return {
            'last_check': None,
            'pending_update': None,
            'ignored_versions': [],
            'auto_download': self.auto_download,
            'auto_install': self.auto_install
        }
        
    def _save_config(self):
        """Save updater configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            
    def check_for_updates(self, force: bool = False) -> Optional[UpdateInfo]:
        """
        Check for available updates
        
        Args:
            force: Force check even if recently checked
            
        Returns:
            UpdateInfo if update available, None otherwise
        """
        # Check if we should check for updates
        if not force and not self._should_check():
            self.logger.debug("Skipping update check (too recent)")
            return self._get_pending_update()
            
        try:
            # Fetch releases from GitHub
            response = requests.get(
                self.GITHUB_API_URL,
                headers={'Accept': 'application/vnd.github.v3+json'},
                timeout=10
            )
            response.raise_for_status()
            
            releases = response.json()
            
            # Filter based on channel
            if self.channel == UpdateChannel.STABLE:
                releases = [r for r in releases if not r['prerelease']]
            elif self.channel == UpdateChannel.BETA:
                # Include both stable and beta
                pass
            
            # Find latest applicable release
            for release_data in releases:
                update = UpdateInfo(release_data)
                
                # Skip if not newer
                if not update.is_newer_than(self.current_version):
                    continue
                    
                # Skip if ignored
                if update.version in self.config.get('ignored_versions', []):
                    continue
                    
                # Check if platform asset exists
                if not update.get_asset_for_platform():
                    continue
                    
                # Found an update
                self.config['last_check'] = datetime.now().isoformat()
                self.config['pending_update'] = release_data
                self._save_config()
                
                self.logger.info(f"Update available: v{update.version}")
                
                # Auto-download if enabled
                if self.auto_download:
                    self.download_update(update)
                    
                return update
                
            # No updates found
            self.config['last_check'] = datetime.now().isoformat()
            self.config['pending_update'] = None
            self._save_config()
            
            self.logger.info("No updates available")
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return None
            
    def _should_check(self) -> bool:
        """Check if enough time has passed since last check"""
        last_check = self.config.get('last_check')
        if not last_check:
            return True
            
        try:
            last_check_time = datetime.fromisoformat(last_check)
            return datetime.now() - last_check_time > self.check_interval
        except Exception:
            return True
            
    def _get_pending_update(self) -> Optional[UpdateInfo]:
        """Get pending update from config"""
        pending = self.config.get('pending_update')
        if pending:
            return UpdateInfo(pending)
        return None
        
    def download_update(
        self,
        update: UpdateInfo,
        progress_callback: Optional[callable] = None
    ) -> Optional[Path]:
        """
        Download update package
        
        Args:
            update: Update information
            progress_callback: Callback for progress updates
            
        Returns:
            Path to downloaded file or None
        """
        asset = update.get_asset_for_platform()
        if not asset:
            self.logger.error("No suitable asset for platform")
            return None
            
        try:
            # Create download directory
            download_dir = self.config_path.parent / "downloads"
            download_dir.mkdir(exist_ok=True)
            
            # Download file
            download_url = asset['browser_download_url']
            filename = asset['name']
            download_path = download_dir / filename
            
            self.logger.info(f"Downloading update: {filename}")
            
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress, downloaded, total_size)
                            
            # Verify download
            if self._verify_download(download_path, asset):
                self.logger.info(f"Download complete: {download_path}")
                
                # Store download info
                self.config['downloaded_update'] = {
                    'version': update.version,
                    'path': str(download_path),
                    'timestamp': datetime.now().isoformat()
                }
                self._save_config()
                
                # Auto-install if enabled
                if self.auto_install:
                    self.install_update(download_path)
                    
                return download_path
            else:
                self.logger.error("Download verification failed")
                download_path.unlink(missing_ok=True)
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading update: {e}")
            return None
            
    def _verify_download(self, file_path: Path, asset: Dict[str, Any]) -> bool:
        """Verify downloaded file"""
        if not file_path.exists():
            return False
            
        # Check file size
        expected_size = asset.get('size', 0)
        actual_size = file_path.stat().st_size
        
        if expected_size and abs(actual_size - expected_size) > 1024:
            self.logger.error(f"Size mismatch: expected {expected_size}, got {actual_size}")
            return False
            
        # TODO: Add checksum verification if available
        
        return True
        
    def install_update(self, package_path: Path) -> bool:
        """
        Install downloaded update
        
        Args:
            package_path: Path to update package
            
        Returns:
            Success status
        """
        if not package_path.exists():
            self.logger.error("Update package not found")
            return False
            
        try:
            system = platform.system()
            
            # Create update script
            script_path = self._create_update_script(package_path)
            
            if system == "Windows":
                # Launch update script and exit
                subprocess.Popen(
                    ['cmd', '/c', 'start', '', str(script_path)],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                # Unix-like systems
                subprocess.Popen(
                    ['sh', str(script_path)],
                    start_new_session=True
                )
                
            self.logger.info("Update installation started")
            
            # Exit current application
            sys.exit(0)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing update: {e}")
            return False
            
    def _create_update_script(self, package_path: Path) -> Path:
        """Create platform-specific update script"""
        system = platform.system()
        app_path = Path(sys.argv[0]).parent
        
        if system == "Windows":
            script_path = self.config_path.parent / "update.bat"
            script_content = f"""
@echo off
echo Updating OpenSuperWhisper...
timeout /t 3 /nobreak > nul
echo Extracting update...
powershell -Command "Expand-Archive -Path '{package_path}' -DestinationPath '{app_path}' -Force"
echo Update complete!
echo Starting application...
start "" "{app_path}\\opensuperwhisper.exe"
del "%~f0"
"""
        else:
            script_path = self.config_path.parent / "update.sh"
            script_content = f"""
#!/bin/sh
echo "Updating OpenSuperWhisper..."
sleep 3
echo "Extracting update..."
tar -xzf "{package_path}" -C "{app_path}"
echo "Update complete!"
echo "Starting application..."
"{app_path}/opensuperwhisper" &
rm "$0"
"""
            
        script_path.write_text(script_content)
        
        if system != "Windows":
            script_path.chmod(0o755)
            
        return script_path
        
    def ignore_version(self, version_str: str):
        """Add version to ignore list"""
        ignored = self.config.get('ignored_versions', [])
        if version_str not in ignored:
            ignored.append(version_str)
            self.config['ignored_versions'] = ignored
            self._save_config()
            
    def clear_ignored_versions(self):
        """Clear ignored versions list"""
        self.config['ignored_versions'] = []
        self._save_config()
        
    def get_update_status(self) -> Dict[str, Any]:
        """Get current update status"""
        pending = self._get_pending_update()
        downloaded = self.config.get('downloaded_update')
        
        return {
            'current_version': self.current_version,
            'channel': self.channel,
            'last_check': self.config.get('last_check'),
            'pending_update': {
                'version': pending.version,
                'name': pending.name,
                'url': pending.html_url
            } if pending else None,
            'downloaded': downloaded,
            'auto_download': self.config.get('auto_download', False),
            'auto_install': self.config.get('auto_install', False)
        }