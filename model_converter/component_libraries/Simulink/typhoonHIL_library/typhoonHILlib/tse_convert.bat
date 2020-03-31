@echo off
:: Parameter %1 is the chosen typhoon version (.VERSION file)
"%APPDATA%\typhoon\%~1\python_portables\python3_portable\Scripts\python.exe" -m model_converter.run --source="Simulink" --model=%2 --device=%3 --compile=%4