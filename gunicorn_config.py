bind = "0.0.0.0:10000"  # Render usa el puerto 10000 por defecto
workers = 4              # Ajusta según el plan de Render (mínimo 1)
timeout = 120            # Tiempo máximo por solicitud
accesslog = "-"          # Logs en stdout (obligatorio en Render)
errorlog = "-"           # Logs de errores en stdout