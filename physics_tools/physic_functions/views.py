from django.shortcuts import render
from django.http import HttpResponseBadRequest
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64

x = sp.symbols('x')

def generar_grafica(posicion, velocidad, aceleracion):
    x_vals = np.linspace(-10, 10, 400)
    funciones = [
        (posicion, "Posición", '-'),
        (velocidad, "Velocidad", '--'),
        (aceleracion, "Aceleración", '-.')
    ]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for func, label, style in funciones:
        # Convertir la función simbólica a una función numérica
        func_numpy = sp.lambdify(x, func, modules=['numpy'])
        
        # Calcular los valores y
        y_vals = func_numpy(x_vals)
        
        # Asegurarse de que y_vals sea un array 1D
        if np.isscalar(y_vals):
            y_vals = np.full_like(x_vals, y_vals)
        elif isinstance(y_vals, np.ndarray):
            if y_vals.ndim > 1:
                y_vals = y_vals.flatten()
        
        ax.plot(x_vals, y_vals, label=label, linestyle=style)
    
    ax.legend()
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('Posición, Velocidad y Aceleración')
    ax.grid(True)
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    return base64.b64encode(image_png).decode('utf-8')

def calcular_derivadas(request):
    if request.method == 'POST':
        funcion_posicion = request.POST.get('funcion', '').strip()
        
        if not funcion_posicion:
            return HttpResponseBadRequest("Por favor, ingrese una función.")
        
        try:
            # Convertir la expresión a simbólica
            posicion = sp.sympify(funcion_posicion)
            
            # Calcular la velocidad y aceleración
            velocidad = sp.diff(posicion, x)
            aceleracion = sp.diff(velocidad, x)
            
            # Generar la gráfica
            imagen_base64 = generar_grafica(posicion, velocidad, aceleracion)
            
            return render(request, 'resultados.html', {
                'funcion': funcion_posicion,
                'velocidad': sp.simplify(velocidad),
                'aceleracion': sp.simplify(aceleracion),
                'imagen': imagen_base64,
            })
        except sp.SympifyError:
            return HttpResponseBadRequest("La función ingresada no es válida. Por favor, verifique la sintaxis.")
        except ValueError as e:
            return HttpResponseBadRequest(f"Error en los cálculos: {str(e)}")
        except Exception as e:
            return HttpResponseBadRequest(f"Ocurrió un error inesperado: {str(e)}")
    
    return render(request, 'calculadora.html')


def simple_view(request):
    return render(request, 'derivadas/basico.html')