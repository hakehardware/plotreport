# plotreport

## Installing via Git
Clone the Repo
```git clone https://github.com/hakehardware/plotreport.git```

Move into directory with 
```cd plotreport```

## Create a Virtual Environment
```python3 -m venv .venv```

Windows users may need to use 'python' instead

## Activate the Virtual Environment
Ubuntu
```source .venv/bin/activate```

Windows
```source .venv/Scripts/activate```

## Install the dependencies
```pip install -r requirements.txt```

## Run the script
```python3 -l <log location> -t <file type>```

-l should be the full path to your logs. For windows you may need to escape your path
-t 0 for Docker, 1 for Space Acres, 2 for Advanced CLI

## Examples
Docker

```python3 -l /var/lib/docker/containers/b28cae646cae34eebad38b824fb066014a0e2fc0e0aaee44bdb3fd26ec4c398b/b28cae646cae34eebad38b824fb066014a0e2fc0e0aaee44bdb3fd26ec4c398b-json.log -t 0```

For docker you will need to use the container id which can be found with ```docker ps --no-trunc```

Space Acres

```python3 -l  C:\\Users\\ajnab\\AppData\\Local\\space-acres\\space-acres.log -t 1```

Advanced CLI

```python3 -l ~/log.txt -t 2```
