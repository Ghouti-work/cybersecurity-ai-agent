"""
CAI Runner - Computer Aided Intelligence Agent Runner
Wrapper for running external cybersecurity tools and agents
"""

import asyncio
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import shlex

from loguru import logger
import yaml

from shared_utils import ConfigManager, LoggerManager, DirectoryManager

class CAIRunner:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or ConfigManager.get_instance().config
        self.logger = LoggerManager.setup_logger('cai_runner')
        
        # Tool configurations
        self.tools = {
            'nmap': {
                'command': 'nmap',
                'args': ['-sV', '-sC', '-O'],
                'timeout': 300
            },
            'ffuf': {
                'command': 'ffuf',
                'args': ['-c', '-mc', '200,204,301,302,307,401,403'],
                'timeout': 180
            },
            'gobuster': {
                'command': 'gobuster',
                'args': ['dir', '-e', '-k'],
                'timeout': 120
            },
            'wpscan': {
                'command': 'wpscan',
                'args': ['--enumerate', 'u,p,t,tt'],
                'timeout': 240
            },
            'shodan': {
                'command': 'shodan',
                'args': ['host'],
                'timeout': 30
            }
        }
        
        # Setup directories
        DirectoryManager.ensure_directory("temp/cai_outputs")
        DirectoryManager.ensure_directory("logs/cai_runner")
        
        self.logger.info("🔧 CAI Runner initialized")

    async def run_scan(self, tool: str, target: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run a specific security tool against a target"""
        self.logger.info(f"Running {tool} scan against {target}")
        
        if tool not in self.tools:
            raise ValueError(f"Unsupported tool: {tool}")
        
        try:
            # Check if tool is available
            if not await self._check_tool_availability(tool):
                return await self._simulate_tool_output(tool, target)
            
            # Build command
            command = await self._build_command(tool, target, options or {})
            
            # Execute command
            result = await self._execute_command(command, self.tools[tool]['timeout'])
            
            # Parse and format output
            formatted_result = await self._format_tool_output(tool, target, result)
            
            # Log results
            await self._log_scan_results(tool, target, formatted_result)
            
            return formatted_result
            
        except Exception as e:
            self.logger.error(f"Scan failed: {e}")
            return {
                'tool': tool,
                'target': target,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    async def run_comprehensive_scan(self, target: str) -> Dict[str, Any]:
        """Run a comprehensive scan using multiple tools"""
        self.logger.info(f"Running comprehensive scan against {target}")
        
        results = {
            'target': target,
            'scan_type': 'comprehensive',
            'started_at': datetime.now().isoformat(),
            'tools_used': [],
            'results': {},
            'summary': {},
            'status': 'running'
        }
        
        try:
            # Phase 1: Network Discovery (nmap)
            self.logger.info("Phase 1: Network Discovery")
            nmap_result = await self.run_scan('nmap', target, {
                'args': ['-sn', '--disable-arp-ping']
            })
            results['results']['nmap'] = nmap_result
            results['tools_used'].append('nmap')
            
            # Phase 2: Port Scanning (if target is responsive)
            if nmap_result.get('status') == 'completed':
                self.logger.info("Phase 2: Port Scanning")
                port_scan = await self.run_scan('nmap', target, {
                    'args': ['-sS', '-sV', '-sC', '--top-ports', '1000']
                })
                results['results']['port_scan'] = port_scan
            
            # Phase 3: Web Directory Enumeration (if web ports found)
            if await self._has_web_ports(results):
                self.logger.info("Phase 3: Web Directory Enumeration")
                gobuster_result = await self.run_scan('gobuster', f"http://{target}", {
                    'wordlist': '/usr/share/wordlists/dirb/common.txt'
                })
                results['results']['gobuster'] = gobuster_result
                results['tools_used'].append('gobuster')
            
            # Phase 4: Shodan Intelligence (if available)
            self.logger.info("Phase 4: Threat Intelligence")
            shodan_result = await self.run_scan('shodan', target)
            results['results']['shodan'] = shodan_result
            results['tools_used'].append('shodan')
            
            # Generate comprehensive summary
            results['summary'] = await self._generate_scan_summary(results)
            results['status'] = 'completed'
            results['completed_at'] = datetime.now().isoformat()
            
            self.logger.info(f"Comprehensive scan completed for {target}")
            return results
            
        except Exception as e:
            self.logger.error(f"Comprehensive scan failed: {e}")
            results['status'] = 'failed'
            results['error'] = str(e)
            return results

    async def _check_tool_availability(self, tool: str) -> bool:
        """Check if a tool is available on the system"""
        try:
            result = await asyncio.create_subprocess_exec(
                'which', self.tools[tool]['command'],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            return result.returncode == 0
        except Exception:
            return False

    async def _build_command(self, tool: str, target: str, options: Dict[str, Any]) -> List[str]:
        """Build command array for tool execution"""
        tool_config = self.tools[tool]
        command = [tool_config['command']]
        
        # Add default arguments
        command.extend(tool_config['args'])
        
        # Add custom options
        if 'args' in options:
            command.extend(options['args'])
        
        # Add wordlist for directory enumeration tools
        if tool in ['gobuster', 'ffuf'] and 'wordlist' in options:
            if tool == 'gobuster':
                command.extend(['-w', options['wordlist']])
            elif tool == 'ffuf':
                command.extend(['-w', options['wordlist']])
        
        # Add target
        if tool == 'gobuster':
            command.extend(['-u', target])
        elif tool == 'ffuf':
            command.extend(['-u', f"{target}/FUZZ"])
        else:
            command.append(target)
        
        return command

    async def _execute_command(self, command: List[str], timeout: int) -> Dict[str, Any]:
        """Execute command and return results"""
        try:
            self.logger.debug(f"Executing: {' '.join(command)}")
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                result = {
                    'returncode': process.returncode,
                    'stdout': stdout.decode('utf-8', errors='ignore'),
                    'stderr': stderr.decode('utf-8', errors='ignore'),
                    'command': ' '.join(command),
                    'execution_time': timeout
                }
                
                return result
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TimeoutError(f"Command timed out after {timeout} seconds")
                
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            raise

    async def _format_tool_output(self, tool: str, target: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format tool output into structured data"""
        formatted = {
            'tool': tool,
            'target': target,
            'status': 'completed' if result['returncode'] == 0 else 'failed',
            'timestamp': datetime.now().isoformat(),
            'command': result['command'],
            'raw_output': result['stdout'],
            'error_output': result['stderr'],
            'parsed_data': {}
        }
        
        try:
            if tool == 'nmap':
                formatted['parsed_data'] = await self._parse_nmap_output(result['stdout'])
            elif tool == 'gobuster':
                formatted['parsed_data'] = await self._parse_gobuster_output(result['stdout'])
            elif tool == 'ffuf':
                formatted['parsed_data'] = await self._parse_ffuf_output(result['stdout'])
            elif tool == 'shodan':
                formatted['parsed_data'] = await self._parse_shodan_output(result['stdout'])
            elif tool == 'wpscan':
                formatted['parsed_data'] = await self._parse_wpscan_output(result['stdout'])
                
        except Exception as e:
            self.logger.error(f"Failed to parse {tool} output: {e}")
            formatted['parsed_data'] = {'error': f"Parsing failed: {e}"}
        
        return formatted

    async def _parse_nmap_output(self, output: str) -> Dict[str, Any]:
        """Parse nmap output"""
        parsed = {
            'open_ports': [],
            'services': {},
            'os_detection': '',
            'host_status': 'unknown'
        }
        
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            
            # Parse open ports
            if '/tcp' in line and 'open' in line:
                parts = line.split()
                if len(parts) >= 3:
                    port = parts[0].split('/')[0]
                    service = parts[2] if len(parts) > 2 else 'unknown'
                    parsed['open_ports'].append(port)
                    parsed['services'][port] = service
            
            # Parse host status
            if 'Host is up' in line:
                parsed['host_status'] = 'up'
            elif 'Host seems down' in line:
                parsed['host_status'] = 'down'
        
        return parsed

    async def _parse_gobuster_output(self, output: str) -> Dict[str, Any]:
        """Parse gobuster output"""
        parsed = {
            'directories_found': [],
            'files_found': [],
            'status_codes': {}
        }
        
        lines = output.split('\n')
        for line in lines:
            if line.startswith('/'):
                parts = line.split()
                if len(parts) >= 2:
                    path = parts[0]
                    status = parts[1].strip('()')
                    
                    if path.endswith('/'):
                        parsed['directories_found'].append(path)
                    else:
                        parsed['files_found'].append(path)
                    
                    parsed['status_codes'][path] = status
        
        return parsed

    async def _parse_ffuf_output(self, output: str) -> Dict[str, Any]:
        """Parse ffuf output"""
        parsed = {
            'endpoints_found': [],
            'status_summary': {}
        }
        
        # ffuf outputs JSON by default in newer versions
        try:
            if output.strip().startswith('{'):
                data = json.loads(output)
                if 'results' in data:
                    for result in data['results']:
                        parsed['endpoints_found'].append({
                            'url': result.get('url', ''),
                            'status': result.get('status', 0),
                            'length': result.get('length', 0)
                        })
        except json.JSONDecodeError:
            # Parse text output
            lines = output.split('\n')
            for line in lines:
                if '200' in line or '301' in line or '302' in line:
                    parsed['endpoints_found'].append(line.strip())
        
        return parsed

    async def _parse_shodan_output(self, output: str) -> Dict[str, Any]:
        """Parse shodan output"""
        parsed = {
            'ip_info': {},
            'ports': [],
            'vulnerabilities': [],
            'organization': '',
            'location': ''
        }
        
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            
            if 'IP:' in line:
                parsed['ip_info']['ip'] = line.split('IP:')[1].strip()
            elif 'Organization:' in line:
                parsed['organization'] = line.split('Organization:')[1].strip()
            elif 'Location:' in line:
                parsed['location'] = line.split('Location:')[1].strip()
            elif 'Port:' in line:
                port = line.split('Port:')[1].strip()
                parsed['ports'].append(port)
        
        return parsed

    async def _parse_wpscan_output(self, output: str) -> Dict[str, Any]:
        """Parse wpscan output"""
        parsed = {
            'wordpress_version': '',
            'themes': [],
            'plugins': [],
            'users': [],
            'vulnerabilities': []
        }
        
        lines = output.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if 'WordPress version' in line:
                parsed['wordpress_version'] = line.split(':')[1].strip() if ':' in line else ''
            elif '[+] Enumerating' in line:
                if 'themes' in line.lower():
                    current_section = 'themes'
                elif 'plugins' in line.lower():
                    current_section = 'plugins'
                elif 'users' in line.lower():
                    current_section = 'users'
            elif line.startswith('[+]') and current_section:
                item = line[3:].strip()
                if current_section in parsed:
                    parsed[current_section].append(item)
        
        return parsed

    async def _simulate_tool_output(self, tool: str, target: str) -> Dict[str, Any]:
        """Simulate tool output when tool is not available"""
        logger.warning(f"Tool {tool} not available, simulating output")
        
        simulated_data = {
            'nmap': {
                'open_ports': ['22', '80', '443'],
                'services': {'22': 'ssh', '80': 'http', '443': 'https'},
                'host_status': 'up'
            },
            'gobuster': {
                'directories_found': ['/admin/', '/wp-content/', '/images/'],
                'files_found': ['robots.txt', 'sitemap.xml'],
                'status_codes': {'/admin/': '200', '/wp-content/': '200'}
            },
            'shodan': {
                'ip_info': {'ip': target},
                'organization': 'Unknown',
                'location': 'Unknown'
            }
        }
        
        return {
            'tool': tool,
            'target': target,
            'status': 'simulated',
            'timestamp': datetime.now().isoformat(),
            'command': f'simulated_{tool}',
            'raw_output': f'Simulated output for {tool} against {target}',
            'error_output': '',
            'parsed_data': simulated_data.get(tool, {})
        }

    async def _has_web_ports(self, results: Dict[str, Any]) -> bool:
        """Check if web ports were found in scan results"""
        if 'nmap' in results['results']:
            open_ports = results['results']['nmap'].get('parsed_data', {}).get('open_ports', [])
            web_ports = ['80', '443', '8000', '8080', '8443']
            return any(port in open_ports for port in web_ports)
        return False

    async def _generate_scan_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive scan summary"""
        summary = {
            'total_tools_used': len(results['tools_used']),
            'open_ports_found': 0,
            'web_directories_found': 0,
            'vulnerabilities_identified': 0,
            'risk_level': 'low',
            'key_findings': [],
            'recommendations': []
        }
        
        try:
            # Analyze nmap results
            if 'nmap' in results['results']:
                nmap_data = results['results']['nmap'].get('parsed_data', {})
                summary['open_ports_found'] = len(nmap_data.get('open_ports', []))
                
                # Check for high-risk ports
                high_risk_ports = ['21', '23', '135', '139', '445', '1433', '3389']
                risky_ports = [p for p in nmap_data.get('open_ports', []) if p in high_risk_ports]
                
                if risky_ports:
                    summary['key_findings'].append(f"High-risk ports found: {', '.join(risky_ports)}")
                    summary['risk_level'] = 'high'
            
            # Analyze web enumeration results
            if 'gobuster' in results['results']:
                gobuster_data = results['results']['gobuster'].get('parsed_data', {})
                dirs_found = len(gobuster_data.get('directories_found', []))
                summary['web_directories_found'] = dirs_found
                
                if dirs_found > 5:
                    summary['key_findings'].append(f"Multiple web directories found ({dirs_found})")
            
            # Generate recommendations
            if summary['open_ports_found'] > 10:
                summary['recommendations'].append("Review and minimize exposed services")
            
            if summary['risk_level'] == 'high':
                summary['recommendations'].append("Immediate security review required")
            else:
                summary['recommendations'].append("Regular security monitoring recommended")
                
        except Exception as e:
            logger.error(f"Failed to generate scan summary: {e}")
        
        return summary

    async def _log_scan_results(self, tool: str, target: str, result: Dict[str, Any]):
        """Log scan results to file"""
        try:
            log_dir = Path("logs/cai/scans")
            log_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{tool}_{target.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = log_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            logger.info(f"Scan results logged: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to log scan results: {e}")

    async def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        available = []
        for tool in self.tools.keys():
            if await self._check_tool_availability(tool):
                available.append(tool)
        return available

    async def install_missing_tools(self) -> Dict[str, str]:
        """Attempt to install missing tools (Ubuntu/Debian)"""
        installation_commands = {
            'nmap': 'sudo apt-get install -y nmap',
            'ffuf': 'go install github.com/ffuf/ffuf@latest',
            'gobuster': 'sudo apt-get install -y gobuster',
            'wpscan': 'sudo gem install wpscan',
            'shodan': 'pip3 install shodan'
        }
        
        results = {}
        for tool, install_cmd in installation_commands.items():
            if not await self._check_tool_availability(tool):
                try:
                    # Note: This requires sudo privileges
                    result = await self._execute_command(install_cmd.split(), 300)
                    results[tool] = 'installed' if result['returncode'] == 0 else 'failed'
                except Exception as e:
                    results[tool] = f'error: {e}'
            else:
                results[tool] = 'already_available'
        
        return results

if __name__ == "__main__":
    # Test the CAI runner
    async def test_cai_runner():
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        runner = CAIRunner(config)
        
        # Test tool availability
        available_tools = await runner.get_available_tools()
        print(f"Available tools: {available_tools}")
        
        # Test single scan
        result = await runner.run_scan('nmap', 'google.com')
        print(f"Scan result: {result['status']}")
        
        # Test comprehensive scan
        comp_result = await runner.run_comprehensive_scan('example.com')
        print(f"Comprehensive scan: {comp_result['status']}")
    
    # Uncomment to test
    # asyncio.run(test_cai_runner())
