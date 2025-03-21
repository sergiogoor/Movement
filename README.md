![Ícono](./Movement-interface/movement.ico)

Proyecto Sismógrafo Open-Source para Entornos Educativos

📊 Resumen del Proyecto

El proyecto tiene como objetivo desarrollar un sismógrafo open-source y de bajo costo, diseñado para su uso en entornos educativos. Este dispositivo permite explorar conceptos de sismología y fenómenos naturales relacionados, fomentando la educación STEM mediante la experimentación práctica.

Además, el sismógrafo contribuye a la conciencia comunitaria sobre los riesgos naturales y a la preparación frente a desastres. Este esfuerzo se alinea con los Objetivos de Desarrollo Sostenible (ODS), en particular los ODS 4 (Educación de calidad), 11 (Ciudades sostenibles) y 13 (Acción por el clima).

🎨 Características Principales

Diseño Modular: Componentes impresos en 3D utilizando PLA+.

Hardware Open-Source: Integrado con un acelerómetro MPU6050 y microcontrolador ESP8266.

Software Personalizable: Algoritmos de procesamiento y visualización de datos.

Educativo y Accesible: Diseñado para facilitar la comprensión de conceptos complejos en sismología.

Colaborativo: Compatible con redes de monitoreo global.

🔧 Especificaciones Técnicas

Hardware

Microcontrolador: ESP8266

Sensor Principal: Acelerómetro MPU6050 (detecta movimientos en los ejes X, Y, Z)

Estructura: Diseño 3D impreso, con tornillos niveladores y burbuja de nivel para garantizar estabilidad.

Software

Lenguajes: C++ para el microcontrolador y Python para la visualización.

Plataformas: Arduino IDE para la ESP8266 y Python para la interfaz gráfica.

Programa en C++ para la ESP8266

El microcontrolador ESP8266 ejecuta un programa en C++ que:

Captura datos del acelerómetro MPU6050.

Filtra los datos para eliminar ruido.

Código completo en C++

Programa en Python para Visualización

El software en Python permite:

Recibir los datos transmitidos por la ESP8266.

Procesar y graficar los datos en tiempo real.

Exportar los datos para análisis posteriores.

Código completo en Python

🔍 Metodología

Investigación: Estudio de la relación entre cambio climático y sismología.

Diseño Experimental: Selección de componentes y conexión mediante interfaz I2C.

Modelado 3D: Creación y fabricación de piezas con impresora Ender 3.

Integración: Montaje de hardware y desarrollo de software.

Pruebas Experimentales: Validación de sensibilidad y precisión en entornos reales y simulados.

Documentación: Publicación de diseños, códigos y guías para su replicación.

📚 Resultados Destacados

Sensibilidad: Detección de ondas superficiales de baja intensidad (F ≈ 2500 N).

Repetibilidad: Alta fiabilidad en la recopilación de datos.

Aplicación Educativa: Implementado con éxito en ambientes educativos para ilustrar conceptos de geofísica y sismología.

🚀 Cómo Empezar

Requisitos

Hardware: ESP8266, MPU6050, cables, impresora 3D.

Software: Arduino IDE, Python 3.8+, librerías matplotlib y numpy.

Instalación

Descargar el Código: Repositorio en GitHub.

Configurar el Hardware: Ensamble las piezas según la guía disponible.

Cargar el Software:

Use Arduino IDE para cargar el código en C++ a la ESP8266.

Ejecute el programa en Python para visualizar los datos.

Ejecutar Pruebas: Conecte el dispositivo y observe los datos capturados en tiempo real.

📖 Documentación Adicional

[Modelos 3D: Descargar STL.](./STL-seismograph-parts)

[Código Fuente en C++: Ver Archivo.](./Seismograph-code)

[Código Fuente en Python: Ver Archivo.](./Movement-interface/)

[Presentación de tesis.](./Diseño%2C%20Construcción%20e%20Implementación%20de%20un%20Sismógrafo%20Open-Source%20para%20Entornos%20Educativos.pdf)

💬 Contacto

Para más información o consultas:

Alaiur Beitia Pérez: alai.beita.p@gmail.com

Sergio Gómez Orts: sergiogomezorts7@gmail.com


