# Declaramas dos variables numéricas con valores diferentes
num1 = 15
num2 = 4

# Calculamos las operaciones básicas
suma = num1 + num2
resta = num1 - num2
multiplicacion = num1 * num2
division = num1 / num2

# Mostramos los resultados en pantalla
print(f"Suma: {suma}")
print(f"Resta: {resta}")
print(f"Multiplicación: {multiplicacion}")
print(f"División: {division}")


# Creamos variables con nombre y apellido
nombre = "Carlos"
apellido = "Gómez"

# Usamos el operador + para unir el nombre, un espacio y el apellido
nombre_completo = nombre + " " + apellido

# Imprimimos el resultado
print("Nombre completo:", nombre_completo)


# Definimos el número a evaluar
numero = 7

# Usamos el operador módulo % para obtener el residuo de la división entre 2
es_par = (numero % 2 == 0)

# Mostramos el resultado (True si es par, False si es impar)
print(f"¿El número {numero} es par?: {es_par}")

# Definimos dos edades
edad1 = 20
edad2 = 19

# 1. Verificar si son iguales
son_iguales = edad1 == edad2

# 2. Verificar si la primera es mayor
primera_es_mayor = edad1 > edad2

# 3. Verificar si ambas son mayores de 18
ambas_mayores_18 = (edad1 > 18) and (edad2 > 18)

# Imprimimos los valores booleanos resultantes
print("¿Son iguales?:", son_iguales)
print("¿La primera es mayor?:", primera_es_mayor)
print("¿Ambas son mayores de 18?:", ambas_mayores_18)


# Creamos una línea decorativa repitiendo el carácter "=" 40 veces con el operador *
linea_decorativa = "=" * 40

# Imprimimos la línea en pantalla
print(linea_decorativa)


# Definimos PI usando la convención de MAYÚSCULAS para constantes
PI = 3.14159

# Definimos el radio del círculo
radio = 5

# Calculamos el área de un círculo (A = PI * r^2)
area = PI * (radio ** 2)

# Imprimimos el resultado
print(f"El área del círculo con radio {radio} es: {area}")