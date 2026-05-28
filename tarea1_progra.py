import psycopg2
from psycopg2 import sql, OperationalError
import sys

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_table_if_not_exists()
    
    def connect(self):
        """Establecer conexion con la base de datos"""
        try:
            self.connection = psycopg2.connect(
                host="localhost",
                database="tarea1",
                user="postgres",
                password="tu_contraseña",
                port="5432"
            )
            self.cursor = self.connection.cursor()
            print("Conectado a la base de datos exitosamente")
        except OperationalError as e:
            print(f"Error al conectar a la base de datos: {e}")
            print("\nPor favor, asegurese de:")
            print("1. PostgreSQL esta instalado y corriendo")
            print("2. La base de datos 'tarea1' existe")
            print("3. Las credenciales son correctas")
            sys.exit(1)
    
    def create_table_if_not_exists(self):
        """Crear la tabla alumno si no existe"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS alumno (
            id SERIAL PRIMARY KEY,
            carnet VARCHAR(15) UNIQUE NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            carrera VARCHAR(150),
            email VARCHAR(150),
            telefono VARCHAR(20),
            fecha_registro DATE DEFAULT CURRENT_DATE
        )
        """
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            print("Tabla 'alumno' verificada/creada exitosamente")
        except OperationalError as e:
            print(f"Error al crear la tabla: {e}")
            sys.exit(1)
    
    def agregar_alumno(self):
        """Agregar un nuevo alumno"""
        print("\n" + "="*50)
        print("AGREGAR NUEVO ALUMNO")
        print("="*50)
        
        carnet = input("Carnet (unico): ").strip()
        if not carnet:
            print("Error: El carnet es obligatorio")
            return
        
        nombre = input("Nombre: ").strip()
        if not nombre:
            print("Error: El nombre es obligatorio")
            return
        
        apellido = input("Apellido: ").strip()
        if not apellido:
            print("Error: El apellido es obligatorio")
            return
        
        carrera = input("Carrera: ").strip()
        email = input("Email: ").strip()
        telefono = input("Telefono: ").strip()
        
        check_query = "SELECT id FROM alumno WHERE carnet = %s"
        self.cursor.execute(check_query, (carnet,))
        if self.cursor.fetchone():
            print(f"Error: Ya existe un alumno con el carnet '{carnet}'")
            return
        
        insert_query = """
        INSERT INTO alumno (carnet, nombre, apellido, carrera, email, telefono)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        try:
            self.cursor.execute(insert_query, (carnet, nombre, apellido, carrera, email, telefono))
            self.connection.commit()
            print(f"Alumno '{nombre} {apellido}' agregado exitosamente")
        except OperationalError as e:
            print(f"Error al agregar alumno: {e}")
            self.connection.rollback()
    
    def modificar_alumno(self):
        """Modificar datos de un alumno por carnet"""
        print("\n" + "="*50)
        print("MODIFICAR ALUMNO")
        print("="*50)
        
        carnet = input("Ingrese el carnet del alumno a modificar: ").strip()
        if not carnet:
            print("Error: El carnet es obligatorio")
            return
        
        check_query = "SELECT id, nombre, apellido, carrera, email, telefono FROM alumno WHERE carnet = %s"
        self.cursor.execute(check_query, (carnet,))
        alumno = self.cursor.fetchone()
        
        if not alumno:
            print(f"Error: No se encontro un alumno con el carnet '{carnet}'")
            return
        
        print(f"\nDatos actuales:")
        print(f"Nombre: {alumno[1]}")
        print(f"Apellido: {alumno[2]}")
        print(f"Carrera: {alumno[3] or 'No especificada'}")
        print(f"Email: {alumno[4] or 'No especificado'}")
        print(f"Telefono: {alumno[5] or 'No especificado'}")
        
        print("\n" + "-"*30)
        print("Deje en blanco para mantener el valor actual")
        print("-"*30)
        
        nuevo_nombre = input(f"Nuevo nombre [{alumno[1]}]: ").strip()
        nuevo_apellido = input(f"Nuevo apellido [{alumno[2]}]: ").strip()
        nueva_carrera = input(f"Nueva carrera [{alumno[3] or ''}]: ").strip()
        nuevo_email = input(f"Nuevo email [{alumno[4] or ''}]: ").strip()
        nuevo_telefono = input(f"Nuevo telefono [{alumno[5] or ''}]: ").strip()
        
        update_query = """
        UPDATE alumno 
        SET nombre = COALESCE(%s, nombre),
            apellido = COALESCE(%s, apellido),
            carrera = COALESCE(%s, carrera),
            email = COALESCE(%s, email),
            telefono = COALESCE(%s, telefono)
        WHERE carnet = %s
        """
        
        values = (
            nuevo_nombre if nuevo_nombre else None,
            nuevo_apellido if nuevo_apellido else None,
            nueva_carrera if nueva_carrera else None,
            nuevo_email if nuevo_email else None,
            nuevo_telefono if nuevo_telefono else None,
            carnet
        )
        
        try:
            self.cursor.execute(update_query, values)
            self.connection.commit()
            print("Alumno modificado exitosamente")
        except OperationalError as e:
            print(f"Error al modificar alumno: {e}")
            self.connection.rollback()
    
    def listar_alumnos(self):
        """Listar todos los alumnos"""
        print("\n" + "="*80)
        print("LISTADO DE ALUMNOS")
        print("="*80)
        
        select_query = "SELECT id, carnet, nombre, apellido, carrera, email, telefono, fecha_registro FROM alumno ORDER BY id"
        
        try:
            self.cursor.execute(select_query)
            alumnos = self.cursor.fetchall()
            
            if not alumnos:
                print("No hay alumnos registrados en la base de datos")
                return
            
            print(f"{'ID':<5} {'Carnet':<15} {'Nombre':<20} {'Apellido':<20} {'Carrera':<20} {'Email':<25} {'Telefono':<15} {'Fecha Registro':<12}")
            print("-"*150)
            
            for alumno in alumnos:
                print(f"{alumno[0]:<5} {alumno[1]:<15} {alumno[2]:<20} {alumno[3]:<20} {alumno[4] or '-':<20} {alumno[5] or '-':<25} {alumno[6] or '-':<15} {alumno[7]}")
            
            print(f"\nTotal de alumnos: {len(alumnos)}")
        except OperationalError as e:
            print(f"Error al listar alumnos: {e}")
    
    def eliminar_alumno(self):
        """Eliminar un alumno por carnet"""
        print("\n" + "="*50)
        print("ELIMINAR ALUMNO")
        print("="*50)
        
        carnet = input("Ingrese el carnet del alumno a eliminar: ").strip()
        if not carnet:
            print("Error: El carnet es obligatorio")
            return
        
        check_query = "SELECT id, nombre, apellido FROM alumno WHERE carnet = %s"
        self.cursor.execute(check_query, (carnet,))
        alumno = self.cursor.fetchone()
        
        if not alumno:
            print(f"Error: No se encontro un alumno con el carnet '{carnet}'")
            return
        
        print(f"\n¿Esta seguro de eliminar al alumno '{alumno[1]} {alumno[2]}'?")
        confirmacion = input("Esta accion no se puede deshacer. Escriba 'SI' para confirmar: ").strip().upper()
        
        if confirmacion != "SI":
            print("Eliminacion cancelada")
            return
        
        delete_query = "DELETE FROM alumno WHERE carnet = %s"
        
        try:
            self.cursor.execute(delete_query, (carnet,))
            self.connection.commit()
            print(f"Alumno '{alumno[1]} {alumno[2]}' eliminado exitosamente")
        except OperationalError as e:
            print(f"Error al eliminar alumno: {e}")
            self.connection.rollback()
    
    def close(self):
        """Cerrar la conexion con la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Conexion con la base de datos cerrada")


def mostrar_menu():
    """Mostrar el menu principal"""
    print("\n" + "="*50)
    print("SISTEMA DE GESTION DE ALUMNOS")
    print("="*50)
    print("1. Agregar alumno")
    print("2. Modificar datos de un alumno")
    print("3. Listar todos los alumnos")
    print("4. Eliminar alumno")
    print("5. Salir")
    print("-"*50)


def main():
    """Funcion principal"""
    db = DatabaseManager()
    
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opcion (1-5): ").strip()
        
        if opcion == "1":
            db.agregar_alumno()
        elif opcion == "2":
            db.modificar_alumno()
        elif opcion == "3":
            db.listar_alumnos()
        elif opcion == "4":
            db.eliminar_alumno()
        elif opcion == "5":
            print("\n¡Hasta luego!")
            db.close()
            break
        else:
            print("Opcion invalida. Por favor, seleccione una opcion entre 1 y 5")
        
        input("\nPresione Enter para continuar...")


if __name__ == "__main__":
    main()