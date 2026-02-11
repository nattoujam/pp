# pp

Minimal CLI wrapper for [piping-server](https://github.com/nwtgck/piping-server).

`pp` lets you quickly send and receive data between machines using simple commands.

- POSIX `sh` compatible
- Only dependency: `curl`
- Progress bar support
- Self-update
- Configurable server URL (without editing the script)

---

## Install

```sh
curl -fsSL https://raw.githubusercontent.com/nattoujam/pp/refs/heads/master/install.sh | sh
```

Verify installation:
```sh
pp --version
```

## Usage
### Send a file

```sh
pp s CODE -f file.txt
```

### Send from stdin

```sh
echo "hello" | pp s CODE
pp s CODE < file.txt
```

### Receive

```sh
pp r CODE
```

### Receive and save to file

```sh
pp r CODE > file.txt
```

## Server Configuration
### Temporary override (environment variable)

```sh
PIPING_SERVER=https://example.com pp s CODE -f file.txt
```

### Persistent configuration

```sh
pp config set server https://example.com
```

Configuration file location:

```sh
~/.config/nattoujam/pp/config
```

Example config content:

```sh
PIPING_SERVER="https://example.com"
```

## Self Update

Update to the latest version from the repository:

```sh
pp self-update
```

## Version

```sh
pp --version
```

## Requirements

- curl

## Security Notes

`pp` is a thin wrapper around piping-server.

- Data is not encrypted by default.
- Anyone who knows the CODE can access the stream.
- Always use sufficiently random codes.
- Prefer HTTPS servers.
