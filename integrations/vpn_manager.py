#!/usr/bin/env python3
"""
VPN Connection Manager for Cybersecurity AI Agent
Supports multiple VPN providers including TryHackMe, HackTheBox, and custom OpenVPN configs
"""

import asyncio
import json
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import re
import signal
from datetime import datetime, timedelta

import psutil
import requests
from loguru import logger
import yaml

from shared_utils import ConfigManager, LoggerManager, DirectoryManager

class VPNManager:
    """Manage VPN connections for penetration testing environments"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or ConfigManager.get_instance().config
        self.logger = LoggerManager.setup_logger('vpn_manager')
        
        # VPN configuration
        self.vpn_configs = self.config.get('vpn', {})
        self.active_connections = {}
        self.connection_history = []
        
        # Setup directories
        DirectoryManager.ensure_directory("config/vpn")
        DirectoryManager.ensure_directory("data/vpn_logs")
        
        self.vpn_dir = Path("config/vpn")
        self.logs_dir = Path("data/vpn_logs")
        
        # Supported VPN types
        self.supported_providers = {
            'tryhackme': self._connect_tryhackme,
            'hackthebox': self._connect_hackthebox,
            'openvpn': self._connect_openvpn,
            'wireguard': self._connect_wireguard,
            'custom': self._connect_custom
        }
        
        self.logger.info("🔒 VPN Manager initialized")

    async def list_available_configs(self) -> Dict[str, Any]:
        """List all available VPN configurations"""
        self.logger.info("📋 Listing available VPN configurations...")
        
        try:
            configs = []
            
            # Scan for OpenVPN configs
            for ovpn_file in self.vpn_dir.glob("*.ovpn"):
                config_info = await self._analyze_ovpn_config(ovpn_file)
                configs.append({
                    'name': ovpn_file.stem,
                    'type': 'openvpn',
                    'file': str(ovpn_file),
                    'status': 'available',
                    **config_info
                })
            
            # Add configured providers
            for provider, provider_config in self.vpn_configs.items():
                if provider in self.supported_providers:
                    configs.append({
                        'name': provider,
                        'type': provider,
                        'status': 'configured',
                        'description': provider_config.get('description', f'{provider} VPN'),
                        'auto_connect': provider_config.get('auto_connect', False)
                    })
            
            result = {
                'total_configs': len(configs),
                'available_configs': configs,
                'active_connections': list(self.active_connections.keys()),
                'supported_providers': list(self.supported_providers.keys())
            }
            
            self.logger.info(f"✅ Found {len(configs)} VPN configurations")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list VPN configs: {e}")
            return {'error': str(e)}

    async def connect_vpn(self, vpn_name: str, provider: str = 'auto') -> Dict[str, Any]:
        """Connect to a VPN"""
        self.logger.info(f"🔌 Connecting to VPN: {vpn_name} ({provider})")
        
        try:
            # Auto-detect provider if not specified
            if provider == 'auto':
                provider = await self._detect_vpn_provider(vpn_name)
            
            if provider not in self.supported_providers:
                return {'error': f'Unsupported VPN provider: {provider}'}
            
            # Check if already connected
            if vpn_name in self.active_connections:
                return {
                    'status': 'already_connected',
                    'connection': self.active_connections[vpn_name]
                }
            
            # Connect using appropriate method
            connection_func = self.supported_providers[provider]
            connection_result = await connection_func(vpn_name)
            
            if connection_result.get('status') == 'connected':
                # Store active connection
                self.active_connections[vpn_name] = {
                    'provider': provider,
                    'connected_at': datetime.now().isoformat(),
                    'process_id': connection_result.get('process_id'),
                    'interface': connection_result.get('interface'),
                    'ip_address': connection_result.get('ip_address')
                }
                
                # Log connection
                await self._log_connection_event('connect', vpn_name, provider, connection_result)
                
                self.logger.info(f"✅ Successfully connected to {vpn_name}")
            
            return connection_result
            
        except Exception as e:
            self.logger.error(f"❌ VPN connection failed: {e}")
            return {'error': str(e), 'status': 'failed'}

    async def disconnect_vpn(self, vpn_name: str) -> Dict[str, Any]:
        """Disconnect from a VPN"""
        self.logger.info(f"🔌 Disconnecting from VPN: {vpn_name}")
        
        try:
            if vpn_name not in self.active_connections:
                return {'error': f'VPN {vpn_name} is not connected'}
            
            connection = self.active_connections[vpn_name]
            
            # Kill VPN process
            if connection.get('process_id'):
                try:
                    os.kill(connection['process_id'], signal.SIGTERM)
                    time.sleep(2)  # Wait for graceful shutdown
                    
                    # Force kill if still running
                    if psutil.pid_exists(connection['process_id']):
                        os.kill(connection['process_id'], signal.SIGKILL)
                except ProcessLookupError:
                    pass  # Process already dead
            
            # Additional cleanup based on provider
            provider = connection.get('provider')
            if provider == 'openvpn':
                await self._cleanup_openvpn(vpn_name)
            elif provider == 'wireguard':
                await self._cleanup_wireguard(vpn_name)
            
            # Remove from active connections
            del self.active_connections[vpn_name]
            
            # Log disconnection
            await self._log_connection_event('disconnect', vpn_name, provider, {'status': 'disconnected'})
            
            self.logger.info(f"✅ Successfully disconnected from {vpn_name}")
            return {'status': 'disconnected', 'vpn_name': vpn_name}
            
        except Exception as e:
            self.logger.error(f"❌ VPN disconnection failed: {e}")
            return {'error': str(e), 'status': 'failed'}

    async def get_connection_status(self, vpn_name: str = None) -> Dict[str, Any]:
        """Get VPN connection status"""
        try:
            if vpn_name:
                # Status for specific VPN
                if vpn_name in self.active_connections:
                    connection = self.active_connections[vpn_name]
                    
                    # Verify connection is still active
                    is_active = await self._verify_connection_active(vpn_name, connection)
                    
                    return {
                        'vpn_name': vpn_name,
                        'status': 'connected' if is_active else 'disconnected',
                        'connection_details': connection if is_active else None,
                        'uptime': self._calculate_uptime(connection.get('connected_at')) if is_active else None
                    }
                else:
                    return {'vpn_name': vpn_name, 'status': 'disconnected'}
            else:
                # Status for all VPNs
                status_list = []
                
                for name, connection in self.active_connections.items():
                    is_active = await self._verify_connection_active(name, connection)
                    
                    status_list.append({
                        'vpn_name': name,
                        'status': 'connected' if is_active else 'disconnected',
                        'provider': connection.get('provider'),
                        'ip_address': connection.get('ip_address'),
                        'uptime': self._calculate_uptime(connection.get('connected_at')) if is_active else None
                    })
                
                return {
                    'active_connections': len([s for s in status_list if s['status'] == 'connected']),
                    'total_configured': len(self.active_connections),
                    'connections': status_list
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get connection status: {e}")
            return {'error': str(e)}

    async def _detect_vpn_provider(self, vpn_name: str) -> str:
        """Auto-detect VPN provider based on name or config"""
        # Check for file extensions
        if vpn_name.endswith('.ovpn'):
            return 'openvpn'
        elif vpn_name.endswith('.conf'):
            return 'wireguard'
        
        # Check for provider keywords
        vpn_lower = vpn_name.lower()
        if 'tryhackme' in vpn_lower or 'thm' in vpn_lower:
            return 'tryhackme'
        elif 'hackthebox' in vpn_lower or 'htb' in vpn_lower:
            return 'hackthebox'
        
        # Check configured providers
        if vpn_name in self.vpn_configs:
            return self.vpn_configs[vpn_name].get('type', 'openvpn')
        
        # Default to OpenVPN
        return 'openvpn'

    async def _connect_tryhackme(self, vpn_name: str) -> Dict[str, Any]:
        """Connect to TryHackMe VPN"""
        try:
            thm_config = self.vpn_configs.get('tryhackme', {})
            
            # Look for TryHackMe OpenVPN config
            ovpn_file = self.vpn_dir / f"{vpn_name}.ovpn"
            if not ovpn_file.exists():
                # Try common TryHackMe filenames
                for pattern in ['tryhackme.ovpn', 'thm.ovpn', f'{vpn_name}.ovpn']:
                    potential_file = self.vpn_dir / pattern
                    if potential_file.exists():
                        ovpn_file = potential_file
                        break
                else:
                    return {'error': 'TryHackMe OpenVPN config not found'}
            
            # Connect using OpenVPN
            return await self._connect_openvpn_file(ovpn_file, 'tryhackme')
            
        except Exception as e:
            return {'error': f'TryHackMe connection failed: {str(e)}'}

    async def _connect_hackthebox(self, vpn_name: str) -> Dict[str, Any]:
        """Connect to HackTheBox VPN"""
        try:
            htb_config = self.vpn_configs.get('hackthebox', {})
            
            # Look for HackTheBox OpenVPN config
            ovpn_file = self.vpn_dir / f"{vpn_name}.ovpn"
            if not ovpn_file.exists():
                # Try common HackTheBox filenames
                for pattern in ['hackthebox.ovpn', 'htb.ovpn', f'{vpn_name}.ovpn']:
                    potential_file = self.vpn_dir / pattern
                    if potential_file.exists():
                        ovpn_file = potential_file
                        break
                else:
                    return {'error': 'HackTheBox OpenVPN config not found'}
            
            # Connect using OpenVPN
            return await self._connect_openvpn_file(ovpn_file, 'hackthebox')
            
        except Exception as e:
            return {'error': f'HackTheBox connection failed: {str(e)}'}

    async def _connect_openvpn(self, vpn_name: str) -> Dict[str, Any]:
        """Connect using OpenVPN"""
        try:
            ovpn_file = self.vpn_dir / f"{vpn_name}.ovpn"
            if not ovpn_file.exists():
                return {'error': f'OpenVPN config file not found: {ovpn_file}'}
            
            return await self._connect_openvpn_file(ovpn_file, 'openvpn')
            
        except Exception as e:
            return {'error': f'OpenVPN connection failed: {str(e)}'}

    async def _connect_openvpn_file(self, ovpn_file: Path, provider: str) -> Dict[str, Any]:
        """Connect using specific OpenVPN file"""
        try:
            # Check if OpenVPN is installed
            if not await self._check_command_exists('openvpn'):
                return {'error': 'OpenVPN is not installed'}
            
            # Prepare log file
            log_file = self.logs_dir / f"openvpn_{ovpn_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            
            # Build OpenVPN command
            cmd = [
                'sudo', 'openvpn',
                '--config', str(ovpn_file),
                '--log', str(log_file),
                '--daemon'
            ]
            
            # Add authentication if configured
            auth_file = self.vpn_dir / f"{ovpn_file.stem}_auth.txt"
            if auth_file.exists():
                cmd.extend(['--auth-user-pass', str(auth_file)])
            
            # Start OpenVPN process
            self.logger.info(f"Starting OpenVPN: {' '.join(cmd)}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait a moment for connection to establish
            await asyncio.sleep(5)
            
            # Check if connection was successful
            if await self._verify_openvpn_connection():
                ip_info = await self._get_vpn_ip_info()
                
                return {
                    'status': 'connected',
                    'provider': provider,
                    'config_file': str(ovpn_file),
                    'log_file': str(log_file),
                    'process_id': process.pid,
                    'interface': 'tun0',  # Common OpenVPN interface
                    'ip_address': ip_info.get('ip'),
                    'connected_at': datetime.now().isoformat()
                }
            else:
                return {'error': 'OpenVPN connection failed to establish'}
            
        except Exception as e:
            return {'error': f'OpenVPN connection error: {str(e)}'}

    async def _connect_wireguard(self, vpn_name: str) -> Dict[str, Any]:
        """Connect using WireGuard"""
        try:
            if not await self._check_command_exists('wg'):
                return {'error': 'WireGuard is not installed'}
            
            conf_file = self.vpn_dir / f"{vpn_name}.conf"
            if not conf_file.exists():
                return {'error': f'WireGuard config file not found: {conf_file}'}
            
            # Start WireGuard
            cmd = ['sudo', 'wg-quick', 'up', str(conf_file)]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                ip_info = await self._get_vpn_ip_info()
                
                return {
                    'status': 'connected',
                    'provider': 'wireguard',
                    'config_file': str(conf_file),
                    'interface': 'wg0',  # Common WireGuard interface
                    'ip_address': ip_info.get('ip'),
                    'connected_at': datetime.now().isoformat()
                }
            else:
                return {'error': f'WireGuard connection failed: {stderr.decode()}'}
            
        except Exception as e:
            return {'error': f'WireGuard connection error: {str(e)}'}

    async def _connect_custom(self, vpn_name: str) -> Dict[str, Any]:
        """Connect using custom VPN script"""
        try:
            custom_config = self.vpn_configs.get('custom', {}).get(vpn_name, {})
            
            if not custom_config:
                return {'error': f'Custom VPN config not found: {vpn_name}'}
            
            connect_script = custom_config.get('connect_script')
            if not connect_script:
                return {'error': 'Custom VPN connect script not specified'}
            
            # Execute custom connect script
            process = await asyncio.create_subprocess_shell(
                connect_script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    'status': 'connected',
                    'provider': 'custom',
                    'script_output': stdout.decode(),
                    'connected_at': datetime.now().isoformat()
                }
            else:
                return {'error': f'Custom VPN script failed: {stderr.decode()}'}
            
        except Exception as e:
            return {'error': f'Custom VPN connection error: {str(e)}'}

    async def _verify_openvpn_connection(self) -> bool:
        """Verify OpenVPN connection is active"""
        try:
            # Check for tun interface
            result = await asyncio.create_subprocess_exec(
                'ip', 'link', 'show',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await result.communicate()
            
            # Look for tun interface
            if 'tun' in stdout.decode():
                return True
            
            return False
            
        except Exception:
            return False

    async def _verify_connection_active(self, vpn_name: str, connection: Dict[str, Any]) -> bool:
        """Verify if a VPN connection is still active"""
        try:
            process_id = connection.get('process_id')
            
            if process_id and psutil.pid_exists(process_id):
                return True
            
            # Additional verification based on provider
            provider = connection.get('provider')
            if provider == 'openvpn':
                return await self._verify_openvpn_connection()
            elif provider == 'wireguard':
                return await self._verify_wireguard_connection()
            
            return False
            
        except Exception:
            return False

    async def _verify_wireguard_connection(self) -> bool:
        """Verify WireGuard connection is active"""
        try:
            result = await asyncio.create_subprocess_exec(
                'sudo', 'wg', 'show',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await result.communicate()
            
            # Check if any WireGuard interfaces are active
            return len(stdout.decode().strip()) > 0
            
        except Exception:
            return False

    async def _get_vpn_ip_info(self) -> Dict[str, Any]:
        """Get VPN IP address information"""
        try:
            # Get external IP
            response = requests.get('https://httpbin.org/ip', timeout=10)
            if response.status_code == 200:
                ip_data = response.json()
                return ip_data
            
            return {}
            
        except Exception:
            return {}

    async def _analyze_ovpn_config(self, ovpn_file: Path) -> Dict[str, Any]:
        """Analyze OpenVPN configuration file"""
        try:
            with open(ovpn_file, 'r') as f:
                content = f.read()
            
            config_info = {
                'protocol': 'tcp' if 'proto tcp' in content else 'udp',
                'port': None,
                'server': None,
                'requires_auth': 'auth-user-pass' in content,
                'cipher': None
            }
            
            # Extract server and port
            for line in content.split('\\n'):
                if line.startswith('remote '):
                    parts = line.split()
                    if len(parts) >= 3:
                        config_info['server'] = parts[1]
                        config_info['port'] = parts[2]
                elif line.startswith('cipher '):
                    config_info['cipher'] = line.split()[1]
            
            return config_info
            
        except Exception as e:
            return {'error': str(e)}

    async def _check_command_exists(self, command: str) -> bool:
        """Check if a command exists in the system"""
        try:
            result = await asyncio.create_subprocess_exec(
                'which', command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await result.communicate()
            return result.returncode == 0
            
        except Exception:
            return False

    def _calculate_uptime(self, connected_at: str) -> str:
        """Calculate connection uptime"""
        try:
            connected_time = datetime.fromisoformat(connected_at)
            uptime = datetime.now() - connected_time
            
            hours, remainder = divmod(uptime.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            
        except Exception:
            return "Unknown"

    async def _log_connection_event(self, event_type: str, vpn_name: str, provider: str, details: Dict[str, Any]):
        """Log VPN connection events"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'vpn_name': vpn_name,
                'provider': provider,
                'details': details
            }
            
            self.connection_history.append(log_entry)
            
            # Save to log file
            log_file = self.logs_dir / f"vpn_connections_{datetime.now().strftime('%Y%m')}.jsonl"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\\n')
            
        except Exception as e:
            self.logger.error(f"Failed to log connection event: {e}")

    async def _cleanup_openvpn(self, vpn_name: str):
        """Cleanup OpenVPN connection"""
        try:
            # Kill any remaining OpenVPN processes
            await asyncio.create_subprocess_exec(
                'sudo', 'pkill', '-f', f'openvpn.*{vpn_name}',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        except Exception:
            pass

    async def _cleanup_wireguard(self, vpn_name: str):
        """Cleanup WireGuard connection"""
        try:
            conf_file = self.vpn_dir / f"{vpn_name}.conf"
            if conf_file.exists():
                await asyncio.create_subprocess_exec(
                    'sudo', 'wg-quick', 'down', str(conf_file),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
        except Exception:
            pass

    async def disconnect_all(self) -> Dict[str, Any]:
        """Disconnect all active VPN connections"""
        self.logger.info("🔌 Disconnecting all VPN connections...")
        
        results = []
        
        for vpn_name in list(self.active_connections.keys()):
            result = await self.disconnect_vpn(vpn_name)
            results.append({
                'vpn_name': vpn_name,
                'result': result
            })
        
        successful = len([r for r in results if r['result'].get('status') == 'disconnected'])
        
        return {
            'total_disconnected': successful,
            'total_attempted': len(results),
            'results': results
        }

    async def auto_connect_startup_vpns(self) -> Dict[str, Any]:
        """Auto-connect VPNs marked for startup connection"""
        self.logger.info("🚀 Auto-connecting startup VPNs...")
        
        results = []
        
        for vpn_name, vpn_config in self.vpn_configs.items():
            if vpn_config.get('auto_connect', False):
                self.logger.info(f"Auto-connecting to {vpn_name}...")
                
                result = await self.connect_vpn(vpn_name)
                results.append({
                    'vpn_name': vpn_name,
                    'result': result
                })
        
        successful = len([r for r in results if r['result'].get('status') == 'connected'])
        
        return {
            'total_connected': successful,
            'total_attempted': len(results),
            'results': results
        }

async def main():
    """Test VPN manager"""
    print("🔒 Testing VPN Manager...")
    
    # Load config
    with open('core/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    try:
        vpn_manager = VPNManager(config)
        
        # List available configs
        configs = await vpn_manager.list_available_configs()
        print(f"Available VPN configs: {configs['total_configs']}")
        
        # Get connection status
        status = await vpn_manager.get_connection_status()
        print(f"Active connections: {status['active_connections']}")
        
        print("✅ VPN Manager test complete")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
