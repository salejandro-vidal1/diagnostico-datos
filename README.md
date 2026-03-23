# diagnostico-datos

# Arquitectura de la solución

GitHub API > miner.py > Redis Message Broker > visualizer.py > Interfaz HTML

# Decisiones de diseño

Para minar GitHub se hizo uso de las API GitHub para escanear los repositorios con más estrellas, cada 10 por página. Para escanear los repositorios por métodos o funciones se usaron expresiones regulares. Una vez escaneado, las palabras se empujan al tópico Redis llamado word_queue.

Redis fue usado como un message broker para poder comunicar miner.py con visualizer.py de manera asincrónica y así poder recibir los mensajes y consumirlos a penas lleguen. Se usó Plotly en HTML para mostrar los datos. El visualizador consume los datos y se los entrega a Plotly por medio de WebSockets para lograr un flujo constante de datos y que Plotly se actulice en tiempo real.

NOTA: Debido a los límites secundarios de GitHub, la aplicación se detiene después de escanear por un tiempo.

# Cómo usar

Debe registrar un Token clásico desde su cuenta de GitHub en la aplicación y reemplazarlo en la línea 13 de miner/main.py donde HEADER ['Authorization'] = f"token {'SU TOKEN AQUÍ!'}"

Una vez hecho eso, debe tener instalado Docker en su equipo y navegar a la carpeta raíz del proyecto y ejecutar

```
docker-compile up --build
```

Después de eso deberá navegar a
```
localhost:8000
```
para visualizar los datos.
