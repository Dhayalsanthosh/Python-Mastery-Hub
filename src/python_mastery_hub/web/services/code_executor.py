# Location: src/python_mastery_hub/web/services/code_executor.py

"""
Code Executor Service

Provides secure code execution capabilities for user-submitted code,
including sandboxing, resource limits, and result processing.
"""

import asyncio
import subprocess
import tempfile
import os
import signal
import resource
import sys
import traceback
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from python_mastery_hub.web.models.exercise import ProgrammingLanguage
from python_mastery_hub.web.middleware.error_handling import CodeExecutionException
from python_mastery_hub.utils.logging_config import get_logger
from python_mastery_hub.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class ExecutionStatus(str, Enum):
    """Execution status enumeration."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    MEMORY_LIMIT = "memory_limit"
    COMPILE_ERROR = "compile_error"
    RUNTIME_ERROR = "runtime_error"


@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    status: ExecutionStatus
    output: str
    error: Optional[str]
    execution_time: float
    memory_usage: int
    exit_code: int
    stdout: str
    stderr: str


class CodeExecutionError(Exception):
    """Custom exception for code execution errors."""
    
    def __init__(self, message: str, status: ExecutionStatus, details: Optional[Dict] = None):
        self.message = message
        self.status = status
        self.details = details or {}
        super().__init__(self.message)


class SecurityManager:
    """Manages security restrictions for code execution."""
    
    @staticmethod
    def get_restricted_imports() -> List[str]:
        """Get list of restricted Python imports."""
        return [
            "os", "sys", "subprocess", "multiprocessing", "threading",
            "socket", "urllib", "http", "ftplib", "smtplib", "imaplib",
            "poplib", "telnetlib", "ctypes", "marshal", "pickle",
            "shelve", "dbm", "sqlite3", "importlib", "__import__",
            "eval", "exec", "compile", "open", "file", "input", "raw_input"
        ]
    
    @staticmethod
    def get_safe_builtins() -> Dict[str, Any]:
        """Get safe built-in functions for Python execution."""
        safe_builtins = {
            # Safe built-ins
            'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
            'callable', 'chr', 'classmethod', 'complex', 'dict', 'dir', 'divmod',
            'enumerate', 'filter', 'float', 'format', 'frozenset', 'getattr',
            'globals', 'hasattr', 'hash', 'hex', 'id', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max',
            'memoryview', 'min', 'next', 'object', 'oct', 'ord', 'pow',
            'property', 'range', 'repr', 'reversed', 'round', 'set', 'setattr',
            'slice', 'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple',
            'type', 'vars', 'zip'
        }
        
        # Return actual built-in functions
        return {name: getattr(__builtins__, name) for name in safe_builtins if hasattr(__builtins__, name)}
    
    @staticmethod
    def create_restricted_globals() -> Dict[str, Any]:
        """Create restricted global namespace for Python execution."""
        restricted_globals = {
            '__builtins__': SecurityManager.get_safe_builtins(),
            '__name__': '__main__',
            '__doc__': None,
        }
        
        # Add safe modules
        import math
        import random
        import datetime
        import json
        import re
        import string
        import collections
        
        restricted_globals.update({
            'math': math,
            'random': random,
            'datetime': datetime,
            'json': json,
            're': re,
            'string': string,
            'collections': collections,
        })
        
        return restricted_globals
    
    @staticmethod
    def validate_code_safety(code: str, language: ProgrammingLanguage) -> List[str]:
        """Validate code for security issues."""
        issues = []
        
        if language == ProgrammingLanguage.PYTHON:
            # Check for restricted imports
            restricted = SecurityManager.get_restricted_imports()
            for restriction in restricted:
                if f"import {restriction}" in code or f"from {restriction}" in code:
                    issues.append(f"Restricted import detected: {restriction}")
            
            # Check for dangerous function calls
            dangerous_patterns = [
                "__import__", "eval(", "exec(", "compile(", "globals()",
                "locals()", "vars()", "dir(", "getattr(", "setattr(",
                "delattr(", "hasattr("
            ]
            
            for pattern in dangerous_patterns:
                if pattern in code:
                    issues.append(f"Potentially dangerous function call: {pattern}")
            
            # Check for file operations
            file_patterns = ["open(", "file(", "with open"]
            for pattern in file_patterns:
                if pattern in code:
                    issues.append(f"File operation detected: {pattern}")
        
        return issues


class ResourceManager:
    """Manages resource limits for code execution."""
    
    @staticmethod
    def set_resource_limits(
        max_memory_mb: int = 128,
        max_cpu_time: int = 10,
        max_file_size_mb: int = 1
    ):
        """Set resource limits for the current process."""
        try:
            # Memory limit
            max_memory_bytes = max_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))
            
            # CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, (max_cpu_time, max_cpu_time))
            
            # File size limit
            max_file_bytes = max_file_size_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_FSIZE, (max_file_bytes, max_file_bytes))
            
            # Core dump limit (disable)
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            
        except Exception as e:
            logger.warning(f"Failed to set some resource limits: {e}")


class PythonExecutor:
    """Executor for Python code."""
    
    @staticmethod
    async def execute(
        code: str,
        input_data: Optional[str] = None,
        timeout: int = 10,
        memory_limit_mb: int = 128
    ) -> ExecutionResult:
        """Execute Python code safely."""
        start_time = datetime.now()
        
        try:
            # Validate code safety
            security_issues = SecurityManager.validate_code_safety(code, ProgrammingLanguage.PYTHON)
            if security_issues:
                return ExecutionResult(
                    success=False,
                    status=ExecutionStatus.ERROR,
                    output="",
                    error=f"Security violations: {'; '.join(security_issues)}",
                    execution_time=0.0,
                    memory_usage=0,
                    exit_code=1,
                    stdout="",
                    stderr=f"Security violations: {'; '.join(security_issues)}"
                )
            
            # Create temporary file for code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            try:
                # Prepare environment
                env = os.environ.copy()
                env['PYTHONPATH'] = ''
                env['PYTHONDONTWRITEBYTECODE'] = '1'
                
                # Prepare command
                cmd = [sys.executable, temp_file_path]
                
                # Execute with subprocess
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env,
                    preexec_fn=lambda: ResourceManager.set_resource_limits(
                        memory_limit_mb, timeout, 1
                    )
                )
                
                try:
                    # Run with timeout
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(input=input_data.encode() if input_data else None),
                        timeout=timeout
                    )
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    stdout_str = stdout.decode('utf-8', errors='replace')
                    stderr_str = stderr.decode('utf-8', errors='replace')
                    
                    # Determine success and status
                    success = process.returncode == 0
                    status = ExecutionStatus.SUCCESS if success else ExecutionStatus.RUNTIME_ERROR
                    
                    return ExecutionResult(
                        success=success,
                        status=status,
                        output=stdout_str,
                        error=stderr_str if not success else None,
                        execution_time=execution_time,
                        memory_usage=0,  # TODO: Get actual memory usage
                        exit_code=process.returncode,
                        stdout=stdout_str,
                        stderr=stderr_str
                    )
                
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    return ExecutionResult(
                        success=False,
                        status=ExecutionStatus.TIMEOUT,
                        output="",
                        error=f"Execution timed out after {timeout} seconds",
                        execution_time=execution_time,
                        memory_usage=0,
                        exit_code=124,
                        stdout="",
                        stderr=f"Execution timed out after {timeout} seconds"
                    )
            
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
        
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.ERROR,
                output="",
                error=f"Execution error: {str(e)}",
                execution_time=execution_time,
                memory_usage=0,
                exit_code=1,
                stdout="",
                stderr=f"Execution error: {str(e)}"
            )


class JavaScriptExecutor:
    """Executor for JavaScript code."""
    
    @staticmethod
    async def execute(
        code: str,
        input_data: Optional[str] = None,
        timeout: int = 10,
        memory_limit_mb: int = 128
    ) -> ExecutionResult:
        """Execute JavaScript code using Node.js."""
        start_time = datetime.now()
        
        try:
            # Create temporary file for code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
                # Wrap code to handle input
                wrapped_code = f"""
const readline = require('readline');
const rl = readline.createInterface({{
    input: process.stdin,
    output: process.stdout,
    terminal: false
}});

let input_lines = [];
let input_index = 0;

function input() {{
    if (input_index < input_lines.length) {{
        return input_lines[input_index++];
    }}
    return '';
}}

rl.on('line', (line) => {{
    input_lines.push(line);
}});

rl.on('close', () => {{
    try {{
        {code}
    }} catch (error) {{
        console.error(error.message);
        process.exit(1);
    }}
}});
"""
                temp_file.write(wrapped_code)
                temp_file_path = temp_file.name
            
            try:
                # Check if Node.js is available
                node_cmd = ['node', '--version']
                try:
                    await asyncio.create_subprocess_exec(*node_cmd, stdout=asyncio.subprocess.DEVNULL)
                except FileNotFoundError:
                    return ExecutionResult(
                        success=False,
                        status=ExecutionStatus.ERROR,
                        output="",
                        error="Node.js not available",
                        execution_time=0.0,
                        memory_usage=0,
                        exit_code=1,
                        stdout="",
                        stderr="Node.js not available"
                    )
                
                # Execute with Node.js
                cmd = ['node', temp_file_path]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(input=input_data.encode() if input_data else None),
                        timeout=timeout
                    )
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    stdout_str = stdout.decode('utf-8', errors='replace')
                    stderr_str = stderr.decode('utf-8', errors='replace')
                    
                    success = process.returncode == 0
                    status = ExecutionStatus.SUCCESS if success else ExecutionStatus.RUNTIME_ERROR
                    
                    return ExecutionResult(
                        success=success,
                        status=status,
                        output=stdout_str,
                        error=stderr_str if not success else None,
                        execution_time=execution_time,
                        memory_usage=0,
                        exit_code=process.returncode,
                        stdout=stdout_str,
                        stderr=stderr_str
                    )
                
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    return ExecutionResult(
                        success=False,
                        status=ExecutionStatus.TIMEOUT,
                        output="",
                        error=f"Execution timed out after {timeout} seconds",
                        execution_time=execution_time,
                        memory_usage=0,
                        exit_code=124,
                        stdout="",
                        stderr=f"Execution timed out after {timeout} seconds"
                    )
            
            finally:
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass
        
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.ERROR,
                output="",
                error=f"Execution error: {str(e)}",
                execution_time=execution_time,
                memory_usage=0,
                exit_code=1,
                stdout="",
                stderr=f"Execution error: {str(e)}"
            )


class CodeExecutor:
    """Main code executor service."""
    
    def __init__(self):
        self.executors = {
            ProgrammingLanguage.PYTHON: PythonExecutor(),
            ProgrammingLanguage.JAVASCRIPT: JavaScriptExecutor(),
        }
        
        # Execution limits
        self.max_code_length = 50000  # 50KB
        self.default_timeout = 10  # seconds
        self.default_memory_limit = 128  # MB
        
        # Track execution statistics
        self.execution_count = 0
        self.total_execution_time = 0.0
    
    async def execute_code(
        self,
        code: str,
        language: ProgrammingLanguage = ProgrammingLanguage.PYTHON,
        input_data: Optional[str] = None,
        timeout: Optional[int] = None,
        memory_limit_mb: Optional[int] = None
    ) -> ExecutionResult:
        """Execute code with the specified language."""
        
        # Validate inputs
        if not code or not code.strip():
            raise CodeExecutionException("Code cannot be empty", ExecutionStatus.ERROR)
        
        if len(code) > self.max_code_length:
            raise CodeExecutionException(
                f"Code too long (max {self.max_code_length} characters)",
                ExecutionStatus.ERROR
            )
        
        # Set defaults
        timeout = timeout or self.default_timeout
        memory_limit_mb = memory_limit_mb or self.default_memory_limit
        
        # Validate limits
        if timeout > 30:
            timeout = 30
        if memory_limit_mb > 512:
            memory_limit_mb = 512
        
        # Check if language is supported
        if language not in self.executors:
            raise CodeExecutionException(
                f"Language {language.value} not supported",
                ExecutionStatus.ERROR
            )
        
        try:
            # Execute code
            executor = self.executors[language]
            result = await executor.execute(code, input_data, timeout, memory_limit_mb)
            
            # Update statistics
            self.execution_count += 1
            self.total_execution_time += result.execution_time
            
            # Log execution
            logger.info(
                f"Code execution completed: {language.value}, "
                f"success={result.success}, time={result.execution_time:.3f}s"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            raise CodeExecutionException(
                f"Execution failed: {str(e)}",
                ExecutionStatus.ERROR
            )
    
    async def test_code_against_cases(
        self,
        code: str,
        test_cases: List[Dict[str, Any]],
        language: ProgrammingLanguage = ProgrammingLanguage.PYTHON
    ) -> List[Dict[str, Any]]:
        """Test code against multiple test cases."""
        results = []
        
        for i, test_case in enumerate(test_cases):
            try:
                # Execute code with test case input
                result = await self.execute_code(
                    code=code,
                    language=language,
                    input_data=test_case.get('input_data', ''),
                    timeout=test_case.get('timeout', self.default_timeout)
                )
                
                # Compare output
                expected_output = str(test_case.get('expected_output', '')).strip()
                actual_output = result.output.strip()
                
                passed = actual_output == expected_output
                
                test_result = {
                    'test_case_id': test_case.get('id', f'test_{i}'),
                    'passed': passed,
                    'expected_output': expected_output,
                    'actual_output': actual_output,
                    'execution_time': result.execution_time,
                    'error': result.error,
                    'status': result.status.value
                }
                
                results.append(test_result)
            
            except Exception as e:
                test_result = {
                    'test_case_id': test_case.get('id', f'test_{i}'),
                    'passed': False,
                    'expected_output': str(test_case.get('expected_output', '')),
                    'actual_output': '',
                    'execution_time': 0.0,
                    'error': str(e),
                    'status': ExecutionStatus.ERROR.value
                }
                
                results.append(test_result)
        
        return results
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages."""
        return [lang.value for lang in self.executors.keys()]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            'total_executions': self.execution_count,
            'total_execution_time': self.total_execution_time,
            'average_execution_time': (
                self.total_execution_time / self.execution_count 
                if self.execution_count > 0 else 0
            ),
            'supported_languages': self.get_supported_languages()
        }
    
    async def validate_syntax(self, code: str, language: ProgrammingLanguage) -> Dict[str, Any]:
        """Validate code syntax without executing it."""
        
        if language == ProgrammingLanguage.PYTHON:
            try:
                compile(code, '<string>', 'exec')
                return {'valid': True, 'errors': []}
            except SyntaxError as e:
                return {
                    'valid': False,
                    'errors': [{
                        'line': e.lineno,
                        'column': e.offset,
                        'message': e.msg,
                        'type': 'SyntaxError'
                    }]
                }
        
        elif language == ProgrammingLanguage.JAVASCRIPT:
            # For JavaScript, we'd need to run a syntax check
            # This is a simplified implementation
            return {'valid': True, 'errors': []}
        
        return {'valid': False, 'errors': [{'message': 'Language not supported for syntax validation'}]}