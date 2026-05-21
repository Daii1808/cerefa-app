# 🐾 CEREFA App - Backend Gestión

Este es el repositorio oficial para el sistema de gestión del centro de rehabilitación de fauna silvestre **CEREFA**. El backend está desarrollado en **Python con Flask** y se encuentra desplegado de forma automática en **Vercel**.

---

## 🚀 Links del Proyecto en Vivo

* 🔗 **Link Principal:** [cerefa-app.vercel.app](https://cerefa-app-git-main-daii1808s-projects.vercel.app)
* 🧪 **Prueba Operativa de la API:** [cerefa-app.vercel.app/api/test](https://cerefa-app-git-main-daii1808s-projects.vercel.app/api/test)

> 💡 **¿Para qué sirve el link de prueba operativa?**
> Este enlace ejecuta el código de Python en tiempo real dentro de los servidores de Vercel y devuelve un archivo JSON. Nos sirve para verificar que el "enchufe" de Flask está vivo y respondiendo correctamente. Si este link llega a fallar, significa que el último cambio subido rompió el backend.

---

## 🛠️ Guía de Trabajo para el Equipo

Para trabajar en armonía y que Vercel actualice la página web solo sin pisarnos los dedos, sigan estos pasos:

### 1. Clonar el Proyecto por Primera Vez
Si ya eres colaborador del repositorio, abre tu VS Code, abre una terminal en una carpeta vacía y ejecuta:
```bash
git clone [https://github.com/daii1808/cerefa-app.git](https://github.com/daii1808/cerefa-app.git)





2. Encender el Entorno Virtual (Local)
Cada vez que vayas a programar, abre la terminal de VS Code y activa el entorno para cargar las librerías:

PowerShell
.\venv\Scripts\activate




3. Reglas de Oro de los Archivos Raíz (⚠️ PROHIBIDO BORRAR)
Para que el servidor en la nube no explote, nadie debe mover ni eliminar estos dos archivos de la raíz:

vercel.json: Es el mapa que le dice a Vercel cómo redirigir las rutas hacia Flask.

requirements.txt: La lista de compras de las librerías. Debe mantenerse siempre con codificación UTF-8 (la clásica de Linux/Web).

4. Cómo Subir Cambios a Internet (Flujo Diario)
Cuando programes una nueva ruta, modelo o lógica en tu VS Code y verifiques que funciona en local, súbela a internet siguiendo estos 3 clics:

Ve al menú de Source Control (el ícono de las tres pelotitas conectadas en la barra izquierda de VS Code).

Escribe un mensaje corto en la casilla (ej: rutas de ingreso listas).

Haz clic en el botón azul Commit (Confirmar) y luego en Sync Changes (Sincronizar cambios).

¡Y listo! Vercel detectará el empujón en GitHub, borrará la versión antigua en internet y compilará tu código nuevo automáticamente en un par de minutos.


---

Pégalo, guarda con `Ctrl + S`, hazle tu último **Commit** y **Sync Changes** desde las tres pelotit

---

## 🎨 Frontend (React + Vite)
El frontend está integrado en la misma raíz del repositorio. Para trabajar en la interfaz:

1. **Instalar dependencias:**
   Asegúrate de tener instalado [Node.js](https://nodejs.org/). En la raíz del proyecto, ejecuta:
   ```bash
   npm install

   