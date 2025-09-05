# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-09-05

### Added
- Initial release of LLM Benchmark tool
- Real-time resource monitoring (CPU, Memory, GPU usage tracking)
- CV-style console output with detailed metrics and Chinese translations
- Concurrent testing support with configurable concurrency levels
- OpenAI-compatible API endpoint support for both chat and completion modes
- Docker support with GPU acceleration capabilities
- Comprehensive reporting system with both console and JSON output formats
- Support for ShareGPT dataset format
- Progress tracking and error handling
- Detailed documentation including parameter descriptions and report formats
- Resource efficiency analysis and performance metrics
- Time To First Token (TTFT) measurement and analysis
- Throughput and latency statistics
- Token generation rate monitoring

### Features
- **Resource Monitoring**: Real-time CPU, memory, and GPU usage tracking using psutil and pynvml
- **Enhanced Reporting**: Beautiful CV-style console output with comprehensive metrics
- **Concurrent Testing**: Support for multiple concurrent connections with asyncio
- **OpenAI Compatible**: Works with any OpenAI-compatible API endpoint
- **Docker Support**: Easy deployment with GPU acceleration support
- **Comprehensive Metrics**: Detailed performance analysis including TTFT, latency, throughput, and resource usage

### Technical Details
- Built with Python 3.8+ and asyncio for high-performance async operations
- Uses httpx for efficient HTTP client operations
- Implements streaming response handling for real-time token generation monitoring
- Supports both chat completions and text generation modes
- Includes comprehensive error handling and logging
- Modular architecture with separate utilities for different functionalities