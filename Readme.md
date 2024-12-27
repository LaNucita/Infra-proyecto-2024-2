# Proyecto INFRAESTRUCTURAS PARALELAS Y DISTRIBUIDAS

Este proyecto consiste en una aplicación web de **Dulcería** dividida en dos partes: un **backend** basado en Flask que gestiona la API y se comunica con la base de datos, y un **frontend** que despliega los templates. Todo el sistema está gestionado y orquestado utilizando **Docker** y **Docker Compose**.

A continuación se detallan los pasos necesarios para construir y desplegar la aplicación en un entorno Dockerizado utilizando Docker Swarm.

## Creadores

- **Manuel Alexander Serna Jaraba -2259345**: Desarrollador del backend.
- **Adrian Felipe Velasquez -2259456**: Responsable de la integración de Docker Swarm.
- **Edgar Fabian Rueda Colonia -2259606**: Responsable subir proyecto a AWS

## Arquitectura del Proyecto

El proyecto está dividido en las siguientes partes:

1. **Backend (Flask API)**: La API de Flask se comunica con una base de datos PostgreSQL y maneja la lógica de negocio.
2. **Frontend**: El frontend es responsable de mostrar los templates y consumir la API de Flask para interactuar con los datos.
3. **Base de Datos (PostgreSQL)**: Se utiliza PostgreSQL como base de datos para almacenar los datos relacionados con las ventas y los productos de la dulcería.

## Comandos para Docker Swarm

### Construcción de imágenes Docker

1. **Construir las imágenes Docker para el backend y frontend**:

   ```bash
   docker build -t backend ./backend
   docker build -t frontend ./frontend
   docker build -t basedatos ./base_datos
   docker swarm init
   docker stack deploy --compose-file docker-compose.yml dulceria-stack
   docker service scale subasta-stack_back=3
