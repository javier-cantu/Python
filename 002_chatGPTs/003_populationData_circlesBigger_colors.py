import matplotlib.pyplot as plt

# Datos
years = [1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100]
populations = ["0.35–0.40", "0.43–0.50", "0.50–0.58", "0.60–0.68", "0.89–0.98", "1.56–1.71", "6.06–6.15", "c. 10–13"]

# Función para limpiar y convertir rangos de población
def clean_population_range(pop_range):
    if 'c. ' in pop_range:
        pop_range = pop_range.replace('c. ', '')
    low, high = pop_range.split('–')
    low = float(low)
    high = float(high) if high.replace('.', '', 1).isdigit() else float(high.split()[0])
    return low, high

# Preparar datos para la visualización
population_low = []
population_high = []

for pop in populations:
    low, high = clean_population_range(pop)
    population_low.append(low)
    population_high.append(high)

# Configurar la figura
fig, ax = plt.subplots(figsize=(12, 6))

# Ajustar la distancia entre los círculos con una variable
horizontal_spacing = 100  # Puedes modificar este valor para ajustar el espaciado
adjusted_years = [year + i * horizontal_spacing for i, year in enumerate(years)]

# Aumentar el tamaño base de los círculos
base_size = 20000  # Este es el factor de escala para los círculos

for i, year in enumerate(adjusted_years):
    # Dibujar círculo para el valor bajo
    ax.scatter(year, 0, s=(population_low[i] / max(population_low)) * base_size, color='cyan', alpha=0.5, edgecolors='none')
    # Dibujar círculo para el valor alto
    ax.scatter(year, 0, s=(population_high[i] / max(population_low)) * base_size, color='magenta', alpha=0.5, edgecolors='none')

ax.set_title('World Population Estimates by Century')
ax.set_xticks(adjusted_years)
ax.set_xticklabels([str(year) for year in years])
ax.set_yticks([])
ax.set_xlabel('Year')
plt.ylim(-1, 1)  # Limitar el rango Y para mejor visualización

# Configurar el color del fondo usando el código hexadecimal proporcionado
ax.set_facecolor('#222831')

# Cambio del color del texto a blanco o a un color claro que contraste
ax.xaxis.label.set_color('#EEEEEE')
ax.yaxis.label.set_color('#EEEEEE')
ax.title.set_color('#EEEEEE')
for label in ax.get_xticklabels():
    label.set_color('#EEEEEE')
for label in ax.get_yticklabels():
    label.set_color('#EEEEEE')

plt.show()
